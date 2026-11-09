# Measurement Index

Every CSV in `data/` carries a `source_page` column. Numbers are transcribed
verbatim from that page's HTML table; they were not re-measured here.

| CSV | Rows | Source page | Column names |
| --- | --- | --- | --- |
| `crop-aspect-ratio-bytes.csv` | 5 | https://handyvale.com/photo-cropper | `Crop to`, `Pixels kept`, `Bytes`, `% of original bytes`, `% of original pixels`, `source_page` |
| `crop-aspect-ratio-pixels.csv` | 4 | https://handyvale.com/photo-cropper | `Crop to`, `Resulting size`, `Pixels kept`, `Pixels thrown away`, `% thrown away`, `source_page` |
| `flip-format-matrix.csv` | 5 | https://handyvale.com/how-to-flip-an-image | `You put in`, `You can get out`, `Worth knowing`, `source_page` |
| `jpeg-quality-vs-psnr.csv` | 7 | https://handyvale.com/resize-photo-for-instagram | `Quality`, `Bytes`, `Step cost`, `PSNR`, `Step gain`, `source_page` |
| `jpeg-rotation-generation-loss.csv` | 4 | https://handyvale.com/rotate-picture-online | `Generation (each = one rotate + one quality-90 export)`, `Pixels beyond ±2 levels`, `Share of 12,000,000`, `JPG size`, `source_page` |
| `png-palette-quantization.csv` | 5 | https://handyvale.com/png-size-reducer | `Palette`, `Bytes`, `% of orig.`, `Bytes cut`, `Changed`, `Max`, `Mean`, `source_page` |
| `png-to-jpg-file-size.csv` | 12 | https://handyvale.com/batch-convert-png-to-jpg | `File`, `PNG`, `JPG q92`, `Change`, `source_page` |
| `png-to-jpg-quality-sweep.csv` | 4 | https://handyvale.com/batch-convert-png-to-jpg | `File`, `q60`, `q75`, `q85`, `q92`, `q95`, `source_page` |
| `print-dpi-pixel-reference.csv` | 7 | https://handyvale.com/image-resolution-changer | `Print size`, `300 dpi`, `200 dpi`, `150 dpi`, `source_page` |
| `resampling-kernel-cost.csv` | 4 | https://handyvale.com/image-resolution-changer | `Kernel`, `PNG bytes`, `JPEG q90 bytes`, `Back to 12 MP fidelity`, `Max error of 255`, `source_page` |
| `resolution-scaling-cost.csv` | 7 | https://handyvale.com/image-resolution-changer | `Output pixels`, `Pixel count`, `× pixels`, `PNG bytes`, `JPEG q90 bytes`, `× JPEG`, `source_page` |

Total data rows: **64** (measured).

## Caveats

- Values are tied to the specific test images, encoders and quality settings used on the source pages.
- Percentages and byte counts are as printed on the source pages; no rounding was applied by this repository.
- If a source page changes, the CSV is a snapshot and may no longer match.
