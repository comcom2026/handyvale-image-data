# Browser-Side Image Operations: Measured Reference Data

Reproducible CSV datasets and dependency-free tools describing what happens to an image file when it is thresholded, pixelated, flipped, rotated, cropped, or re-encoded in a browser.

## Why this exists

Most image-tool pages describe features. Fewer publish the numbers behind them. This repository collects measurement tables from the client-side image tools at https://handyvale.com/ into plain CSV so they can be sorted, diffed, plotted, or cited without scraping HTML. The experiments behind the two 2026-11 batches are documented at https://handyvale.com/bulk-threshold-image and https://handyvale.com/bulk-pixelate-effect-image.

## Contents

| Path | What it is |
| --- | --- |
| `data/*.csv` | 15 measurement tables; older files were transcribed from linked pages, four files added on 2026-11-27 were generated from local experiment JSON |
| `docs/tool-inventory.md` | The 48 public pages in the live sitemap, with titles and URLs |
| `docs/measurement-index.md` | Which CSV came from which page, and what each column means |
| `tools/image_facts.py` | Dependency-free Python 3 CLI: reads image headers, reports format, dimensions, bytes, bytes-per-pixel, and alpha support |
| `tools/sweep_summary.py` | Dependency-free Python 3 CLI: prints min/max/mean for numeric columns of a sweep CSV |

## Quick start

```bash
python3 tools/image_facts.py path/to/photo.png
python3 tools/sweep_summary.py data/bulk-threshold-sweep.csv
python3 -c "import csv;print(list(csv.DictReader(open('data/jpeg-quality-vs-psnr.csv'))))"
```

Both tools use only the Python 3 standard library. `image_facts.py` reads only file headers; `sweep_summary.py` reads only the CSVs in `data/`.

## Provenance and limits — read this before citing

- Every older number in `data/` was **transcribed verbatim** from the HTML tables on the linked handyvale.com page. Each CSV has a `source_page` column pointing at the exact page.
- The four 2026-11-27 CSVs were **generated from local experiment JSON files** that produced the linked articles. Timestamps and source pages are recorded in every row.
- The figures describe specific test files, specific encoders, and specific settings. They are observations about those runs, not universal constants. Do not extrapolate them to other images.
- The tool inventory was generated from https://handyvale.com/sitemap.xml on 2026-11-27. Page counts and titles will drift as the site changes.
- `tools/image_facts.py` was smoke-tested locally on 2026-11-09 against six synthetic header files; `tools/sweep_summary.py` was smoke-tested locally on 2026-11-27 against the two new sweep CSVs.

## License

Code: MIT (see `LICENSE`). Data: transcribed or measured as described above, provided as-is for reference.
