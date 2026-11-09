# Browser-Side Image Operations: Measured Reference Data

Reproducible reference datasets about what actually happens to an image file when you
flip, rotate, crop, resize, quantize, or re-encode it in a browser — plus a small
dependency-free tool for inspecting image headers.

Everything here runs locally. No upload, no account, no network access required.

## Why this exists

Most image-tool pages describe features. Fewer publish the numbers behind them.
This repository collects the published measurement tables from the client-side
image tools at https://handyvale.com/ into plain CSV so they can be sorted,
diffed, plotted, or cited without scraping HTML.

## Contents

| Path | What it is |
| --- | --- |
| `data/*.csv` | 11 transcribed measurement tables, 64 data rows in total |
| `docs/tool-inventory.md` | The 31 public pages of the tool set, with their titles and URLs |
| `docs/measurement-index.md` | Which CSV came from which page, and what each column means |
| `tools/image_facts.py` | Dependency-free Python 3 CLI: reads image headers, reports format, dimensions, bytes, bytes-per-pixel, and alpha support |

## Quick start

```bash
python3 tools/image_facts.py path/to/photo.png
python3 tools/image_facts.py --json path/to/photo.jpg --after rotate90
python3 -c "import csv;print(list(csv.DictReader(open('data/jpeg-quality-vs-psnr.csv'))))"
```

`image_facts.py` reads only the file header — it never decodes pixels and never
needs Pillow, OpenCV, or any third-party package. Supported containers: PNG,
JPEG, GIF, BMP, WebP (VP8 / VP8L / VP8X).

## Example output

Actual output from a local smoke test on a 2 x 2 RGBA PNG (not a real photo):

```
file             a.png
format           PNG
dimensions       2 x 2
pixels           4
bytes            75
bytes_per_pixel  18.75
alpha            yes (colour type 6)
source           IHDR
```

## Provenance and limits — read this before citing

- Every number in `data/` was **transcribed verbatim** from the HTML tables on the
  linked handyvale.com page. It was **not independently re-measured** by this
  repository. Each CSV has a `source_page` column pointing at the exact page.
- The figures describe specific test files, specific encoders, and specific
  quality settings. They are observations about those runs, not universal
  constants. Do not extrapolate them to other images.
- The tool inventory in `docs/` was generated from
  https://handyvale.com/sitemap.xml on 2026-11-09. Page counts and titles will
  drift as the site changes.
- `tools/image_facts.py` is original code in this repository. It was smoke-tested
  locally on 2026-11-09 against six synthetic header files (PNG, JPEG, GIF, BMP,
  WebP VP8X, WebP VP8L); all six returned the expected dimensions. Those test
  files are not included in this repository.

## Rebuilding the CSV files

The CSVs are checked in directly so the repository is usable without a network
connection. To refresh them, re-scrape the `source_page` URLs and replace the
rows — keep the `source_page` column intact.

## License

Code: MIT (see `LICENSE`). Data: transcribed from the linked pages and provided
as-is for reference; see the provenance note above.
