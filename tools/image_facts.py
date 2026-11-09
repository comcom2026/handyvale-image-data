#!/usr/bin/env python3
"""Read image container headers and report facts, without decoding pixels.

Supports PNG, JPEG, GIF, BMP and WebP (VP8 / VP8L / VP8X).
Standard library only. The file is opened read-only and only the header bytes
are consumed; nothing is uploaded or modified.

Usage:
    python3 image_facts.py IMAGE [IMAGE ...]
    python3 image_facts.py --json photo.png --after rotate90

--after accepts flip, rotate90, rotate180 and reports the dimensions the file
would have after that operation (useful when deciding whether a re-encode is
even necessary).
"""

import argparse
import json
import os
import struct
import sys


class HeaderError(Exception):
    pass


def _u16be(b):
    return struct.unpack(">H", b)[0]


def _u32be(b):
    return struct.unpack(">I", b)[0]


def _u16le(b):
    return struct.unpack("<H", b)[0]


def _u32le(b):
    return struct.unpack("<I", b)[0]


def _png(head, nbytes):
    if not head.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HeaderError("bad PNG signature")
    if len(head) < 33 or head[12:16] != b"IHDR":
        raise HeaderError("PNG IHDR not found in first bytes")
    w = _u32be(head[16:20])
    h = _u32be(head[20:24])
    depth = head[24]
    ctype = head[25]
    names = {0: "grayscale", 2: "truecolour", 3: "indexed",
             4: "grayscale+alpha", 6: "truecolour+alpha"}
    return {
        "format": "PNG",
        "width": w, "height": h,
        "alpha": "yes (colour type %d)" % ctype if ctype in (4, 6)
                 else "possibly (tRNS chunk)" if ctype in (0, 2, 3) else "no",
        "bit_depth": depth,
        "colour_type": "%d (%s)" % (ctype, names.get(ctype, "unknown")),
        "source": "IHDR",
    }


def _jpeg(head, nbytes):
    if not head.startswith(b"\xff\xd8"):
        raise HeaderError("bad JPEG SOI")
    i = 2
    exif = False
    end = min(len(head), 262144)
    while i + 3 < end:
        if head[i] != 0xFF:
            i += 1
            continue
        marker = head[i + 1]
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if i + 4 > end:
            break
        seglen = _u16be(head[i + 2:i + 4])
        if seglen < 2 or i + 2 + seglen > end:
            break
        if marker == 0xE1 and head[i + 4:i + 10] == b"Exif\x00\x00":
            exif = True
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        if marker in sof:
            h = _u16be(head[i + 5:i + 7])
            w = _u16be(head[i + 7:i + 9])
            comps = head[i + 9]
            return {
                "format": "JPEG",
                "width": w, "height": h,
                "alpha": "no (JPEG has no alpha channel)",
                "components": comps,
                "exif": exif,
                "source": "SOF%d" % (marker - 0xC0),
            }
        i += 2 + seglen
    raise HeaderError("no JPEG SOF marker found")


def _gif(head, nbytes):
    if head[:6] not in (b"GIF87a", b"GIF89a"):
        raise HeaderError("bad GIF signature")
    return {
        "format": "GIF",
        "width": _u16le(head[6:8]), "height": _u16le(head[8:10]),
        "alpha": "1-bit transparency possible",
        "source": "Logical Screen Descriptor",
    }


def _bmp(head, nbytes):
    if head[:2] != b"BM":
        raise HeaderError("bad BMP signature")
    dib = _u32le(head[14:18])
    if dib >= 40 and len(head) >= 26:
        w = struct.unpack("<i", head[18:22])[0]
        h = struct.unpack("<i", head[22:26])[0]
    elif dib == 12 and len(head) >= 22:
        w = _u16le(head[18:20]); h = _u16le(head[20:22])
    else:
        raise HeaderError("unsupported BMP DIB header size %d" % dib)
    return {
        "format": "BMP",
        "width": abs(w), "height": abs(h),
        "alpha": "possible in 32-bit BITMAPV4/V5 only",
        "top_down": h < 0,
        "source": "DIB header (%d bytes)" % dib,
    }


def _webp(head, nbytes):
    if head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        raise HeaderError("bad WebP RIFF signature")
    fourcc = head[12:16]
    payload = head[20:]
    if fourcc == b"VP8X":
        if len(payload) < 10:
            raise HeaderError("truncated VP8X")
        w = int.from_bytes(payload[4:7], "little") + 1
        h = int.from_bytes(payload[7:10], "little") + 1
        return {"format": "WebP", "width": w, "height": h,
                "alpha": "yes" if payload[0] & 0x10 else "no",
                "source": "VP8X"}
    if fourcc == b"VP8L":
        if len(payload) < 5 or payload[0] != 0x2F:
            raise HeaderError("bad VP8L signature")
        bits = int.from_bytes(payload[1:5], "little")
        return {"format": "WebP", "width": (bits & 0x3FFF) + 1,
                "height": ((bits >> 14) & 0x3FFF) + 1,
                "alpha": "yes (lossless)", "source": "VP8L"}
    if fourcc == b"VP8 ":
        if len(payload) < 10 or payload[3:6] != b"\x9d\x01\x2a":
            raise HeaderError("bad VP8 keyframe header")
        w = _u16le(payload[6:8]) & 0x3FFF
        h = _u16le(payload[8:10]) & 0x3FFF
        return {"format": "WebP", "width": w, "height": h,
                "alpha": "no (lossy VP8)", "source": "VP8"}
    raise HeaderError("unknown WebP chunk %r" % fourcc)


def inspect(path):
    nbytes = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(262144)
    if len(head) < 12:
        raise HeaderError("file too small to contain an image header")
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        fn = _png
    elif head.startswith(b"\xff\xd8"):
        fn = _jpeg
    elif head[:6] in (b"GIF87a", b"GIF89a"):
        fn = _gif
    elif head[:2] == b"BM":
        fn = _bmp
    elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        fn = _webp
    else:
        raise HeaderError("unrecognised image container")
    info = fn(head, nbytes)
    pixels = info["width"] * info["height"]
    info["file"] = os.path.basename(path)
    info["bytes"] = nbytes
    info["pixels"] = pixels
    info["bytes_per_pixel"] = round(nbytes / pixels, 4) if pixels else None
    return info


def after_operation(info, operation):
    w, h = info["width"], info["height"]
    if operation == "flip":
        nw, nh = w, h
    elif operation == "rotate90":
        nw, nh = h, w
    elif operation == "rotate180":
        nw, nh = w, h
    else:
        raise ValueError(operation)
    return {"operation": operation, "width": nw, "height": nh,
            "pixels": nw * nh, "dimensions_changed": (nw, nh) != (w, h)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="image files to inspect")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--after", choices=["flip", "rotate90", "rotate180"],
                    help="also report dimensions after this operation")
    args = ap.parse_args(argv)
    results, failed = [], False
    for path in args.files:
        try:
            info = inspect(path)
            if args.after:
                info["after"] = after_operation(info, args.after)
            results.append(info)
        except (OSError, HeaderError) as exc:
            failed = True
            results.append({"file": os.path.basename(path), "error": str(exc)})
    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        for r in results:
            print("-" * 56)
            if "error" in r:
                print("file %s\nERROR: %s" % (r["file"], r["error"]))
                continue
            keys = ["file", "format", "width", "height", "pixels", "bytes",
                    "bytes_per_pixel", "alpha", "bit_depth", "colour_type",
                    "components", "exif", "top_down", "source"]
            for k in keys:
                if k in r:
                    label = {"width": "dimensions", "height": None}.get(k, k)
                    if k == "width":
                        print("%-16s %d x %d" % ("dimensions", r["width"], r["height"]))
                    elif k != "height":
                        print("%-16s %s" % (k, r[k]))
            if "after" in r:
                a = r["after"]
                print("%-16s %s -> %d x %d (%s)" % (
                    "after", a["operation"], a["width"], a["height"],
                    "swapped" if a["dimensions_changed"] else "unchanged"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
