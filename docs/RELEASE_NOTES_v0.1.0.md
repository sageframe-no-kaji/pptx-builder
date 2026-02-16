# Release v0.1.0 - PPTX Builder

**First public release** of PPTX Builder, a local-first CLI (and optional Web UI) for converting PDFs and image folders into clean, DPI-controlled PowerPoint slides.

## Installation

### CLI (Primary Interface)

```bash
pip install sageframe-pptx-builder
```

**System dependencies:**
- `poppler-utils` (for PDF conversion)
  - Debian/Ubuntu: `sudo apt install poppler-utils`
  - macOS: `brew install poppler`

### Web UI (Optional)

```bash
pip install "sageframe-pptx-builder[web]"
python -m pptx_builder.web
```

Or use Docker:
```bash
docker pull ghcr.io/sageframe-no-kaji/pptx-builder:0.1.0
docker compose up -d
# Access at http://localhost:7860
```

## Features

### Core Functionality

- **CLI-first design**: Install via pip, run with `pptx-builder` command
- **Local processing**: No cloud uploads, complete privacy
- **Format support**: PDF (multi-page), PNG, JPG, JPEG, TIFF, WebP, BMP, GIF, ICO, HEIC, HEIF
- **No PowerPoint required**: Pure Python implementation using python-pptx

### DPI Control

- Configurable DPI for PDF rendering (default: 300)
- Range: 150-600 DPI supported
- Higher DPI = sharper output, slower processing

### Image Placement Modes

- **Fit**: Preserve entire image, no cropping (may show background)
- **Fill**: Cover entire slide, may crop edges to maintain aspect ratio
- No stretching or distortion in either mode

### Slide Size Support

- 16:9 Widescreen (13.33" × 7.5") - default
- 4:3 Standard (10" × 7.5")
- Letter (11" × 8.5")
- A4 (11.69" × 8.27")
- Legal (14" × 8.5")
- Tabloid (17" × 11")

### Output Quality

- One slide per image/page
- Centered placement
- Aspect ratio preservation
- Compatible with PowerPoint, LibreOffice, Google Slides

## Usage

### CLI Examples

```bash
# Convert PDF
pptx-builder -i document.pdf

# Custom output name
pptx-builder -i document.pdf -o slides.pptx

# Higher DPI (slower, sharper)
pptx-builder -i document.pdf --dpi 600

# Process folder of images
pptx-builder -i photos/

# Batch process
pptx-builder -i file1.pdf file2.pdf --quiet --force

# Process folder recursively
pptx-builder -i images/ --recursive

# Verbose logging
pptx-builder -i document.pdf --verbose
```

### Web UI

```bash
python -m pptx_builder.web
# Open http://localhost:7860
```

Upload files, select options, download presentation.

## Known Limitations

- **System dependency**: Requires `poppler-utils` for PDF processing
- **PDF performance**: Large PDFs (30+ pages) at 300 DPI may take 30-60 seconds
- **High DPI slowdown**: 600 DPI processing is significantly slower than 150-300 DPI
- **Memory usage**: High-resolution PDFs require proportional memory

## Why This Exists

- **Privacy**: Process sensitive documents locally without online converters
- **Predictable output**: Raster pipeline produces clean slides vs fragile "editable" conversion
- **Power-tool behavior**: Full control over DPI, aspect ratio, placement - no surprise auto-fit

## What's New in v0.1.0

### Packaging & Distribution

- ✅ Modern Python packaging (PEP 621) with `pyproject.toml`
- ✅ Published to PyPI as `sageframe-pptx-builder`
- ✅ CLI entrypoint: `pptx-builder` command
- ✅ Optional web UI extras: `pip install "sageframe-pptx-builder[web]"`
- ✅ Src layout (`src/pptx_builder/`) for clean packaging

### Code Quality

- ✅ Python logging instead of debug prints
- ✅ `--verbose` flag for debug output
- ✅ Cross-platform temp directory handling (no hardcoded `/tmp`)
- ✅ GitHub Actions CI (Python 3.8 & 3.11)
- ✅ Dev extras with pytest, black, flake8, mypy

### Documentation

- ✅ CLI-first README with pip install instructions
- ✅ "Why this exists" section
- ✅ Web UI positioned as optional
- ✅ Docker deployment guide

### Docker

- ✅ Dockerfile uses package install (`pip install .[web]`)
- ✅ Consistent with PyPI distribution

## Migration from Development Version

If you were using the development version (`make_ppt.py`):

**Old:**
```bash
python make_ppt.py -i document.pdf
```

**New:**
```bash
pip install sageframe-pptx-builder
pptx-builder -i document.pdf
```

All command-line options remain the same. The package name is now `pptx_builder` for imports:

```python
from pptx_builder import build_presentation, convert_pdf_to_images
```

## Links

- **PyPI**: https://pypi.org/project/sageframe-pptx-builder/
- **GitHub**: https://github.com/sageframe-no-kaji/pptx-builder
- **Issues**: https://github.com/sageframe-no-kaji/pptx-builder/issues
- **Documentation**: See [README.md](../README.md) and [DOCKER.md](../DOCKER.md)

## Author

Created by Andrew Marcus ([GitHub: sageframe-no-kaji](https://github.com/sageframe-no-kaji))

## License

MIT License - see [LICENSE](../LICENSE)
