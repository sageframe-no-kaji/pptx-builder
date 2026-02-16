# PPTX Builder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/sageframe-no-kaji/pptx-builder/actions/workflows/test.yml/badge.svg)](https://github.com/sageframe-no-kaji/pptx-builder/actions/workflows/test.yml)

A local-first CLI (and optional Web UI) for converting PDFs and image folders into clean, DPI-controlled PowerPoint slides — no PowerPoint required.

## Why This Exists

- **Privacy**: Process files locally without uploading to online converters
- **Predictable output**: Raster pipeline produces clean slides, unlike fragile "editable" conversion that attempts text extraction
- **Power-tool behavior**: Full control over DPI, aspect ratio, and placement — no surprise auto-fit or re-layout

## Installation

### Via pip (Recommended)

```bash
pip install pptx-builder
```

**System dependencies:**
- `poppler-utils` (for PDF conversion)
  - Debian/Ubuntu: `sudo apt install poppler-utils`
  - macOS: `brew install poppler`

### With Web UI (Optional)

```bash
pip install "pptx-builder[web]"
```

### Docker (Web UI)

```bash
git clone https://github.com/sageframe-no-kaji/pptx-builder.git
cd pptx-builder
docker compose up -d
```

Access web interface at http://localhost:7860

See [DOCKER.md](DOCKER.md) for details.

## Usage

### CLI (Primary Interface)

**Interactive mode:**
```bash
pptx-builder
```

**CLI examples:**
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

**Common options:**
- `-i, --input PATH` - Input file(s) or folder
- `-o, --output NAME` - Output filename (single input only)
- `--dpi DPI` - PDF rendering quality (default: 300)
- `-r, --recursive` - Process subfolders
- `--quiet` - No prompts
- `--force` - Overwrite existing files
- `--verbose` - Enable debug logging
- `-h, --help` - Show all options

### Web UI (Optional)

If you installed with `[web]` extras or via Docker:

```bash
python -m pptx_builder.web
```

Or with Docker:
```bash
docker compose up -d
# Open http://localhost:7860
```

Upload files, select options, download presentation.

## Features

**Supported formats:**
- PDF (multi-page supported)
- Images: PNG, JPG, JPEG, TIFF, WebP, BMP, GIF, ICO, HEIC, HEIF

**Slide sizes:**
- 16:9 Widescreen (13.33" × 7.5") - default
- 4:3 Standard (10" × 7.5")
- Letter (11" × 8.5")
- A4 (11.69" × 8.27")
- Legal (14" × 8.5")
- Tabloid (17" × 11")

**Image placement:**
- **Fit** - No cropping, entire image visible (default)
- **Fill** - No whitespace, may crop edges

**Output:**
- One slide per image/page
- Images sorted alphabetically
- Centered, never stretched
- Compatible with PowerPoint, LibreOffice, Google Slides

## Documentation

**Additional documentation:**
- [DOCKER.md](DOCKER.md) - Docker deployment
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [docs/GRADIO_TUTORIAL.md](docs/GRADIO_TUTORIAL.md) - Web UI technical guide
- [docs/MAN_PAGE_USAGE.md](docs/MAN_PAGE_USAGE.md) - Man page instructions

## Development

**Setup:**
```bash
git clone https://github.com/sageframe-no-kaji/pptx-builder.git
cd pptx-builder
pip install -e .[dev]
```

**Run tests:**
```bash
pytest
pytest --cov=pptx_builder --cov-report=html
```

**Code quality:**
```bash
black src/                           # Format
flake8 src/pptx_builder/            # Lint
mypy src/pptx_builder/              # Type check
```

**Pre-commit hooks:**
```bash
pre-commit install
pre-commit run --all-files
```

## Notes

- PDF rendering: 150-300 DPI recommended (600 DPI is slow)
- Large PDFs (30+ pages) at 300 DPI may take 30-60 seconds
- Temporary files cleaned up automatically
- HEIC/HEIF require `pillow-heif` package (included)

## Author

Created by Andrew Marcus ([GitHub: sageframe-no-kaji](https://github.com/sageframe-no-kaji))

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Issues and pull requests welcome at https://github.com/sageframe-no-kaji/pptx-builder
