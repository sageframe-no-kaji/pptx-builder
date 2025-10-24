"""
make_ppt.py
-----------
Build a PowerPoint (.pptx) from either:
  • a PDF (auto-rasterized to PNG at 300 DPI), or
  • a folder of images.

Supported input image formats:
  .png .jpg .jpeg .tif .tiff .webp .bmp .gif (first frame) .ico .heic .heif

Features:
  - Slide size presets: 16:9, 4:3, Letter, A4, Legal, Tabloid
  - Placement modes: "fit" (contain, no crop) or "fill" (cover, may crop)
  - One image per slide, centered, proportional scaling, no stretching
  - Case-insensitive filename sort; non-image files in folders are ignored
  - Temporary files from PDF conversion are cleaned up automatically
"""

from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Iterable, Optional

# Register HEIC/HEIF support before Pillow is used under-the-hood by python-pptx
import pillow_heif  # type: ignore
pillow_heif.register_heif_opener()

# PDF rendering (pure Python, cross-platform)
import fitz  # PyMuPDF

# PPTX generation
from pptx import Presentation
from pptx.util import Inches

# -----------------------------
# Config: allowed image formats
# -----------------------------
ALLOWED_EXTS = {
    ".png", ".jpg", ".jpeg",
    ".tif", ".tiff",
    ".webp", ".bmp",
    ".gif", ".ico",
    ".heic", ".heif",
}

# -----------------------------
# Slide size presets (in inches)
# -----------------------------
SLIDE_SIZES = {
    "1": ("16:9 (13.33\" × 7.5\")", 13.3333333333, 7.5),
    "2": ("4:3  (10\" × 7.5\")",     10.0, 7.5),
    "3": ("Letter  (11\" × 8.5\")",  11.0, 8.5),
    "4": ("A4      (11.69\" × 8.27\")", 11.69, 8.27),
    "5": ("Legal   (14\" × 8.5\")",  14.0, 8.5),
    "6": ("Tabloid (17\" × 11\")",   17.0, 11.0),
}

# -----------------------------
# Prompt helpers
# -----------------------------
def prompt_input_path() -> Path:
    """Ask for a path to a PDF file or a folder of images."""
    while True:
        p = input("Enter a path to a PDF file or a folder of images: ").strip()
        path = Path(p).expanduser().resolve()
        if path.exists():
            return path
        print("✗ Path does not exist. Try again.\n")

def prompt_output_name(default_name: str = "slides") -> str:
    """Ask for an output filename (without or with .pptx)."""
    name = input(f"Enter output filename (without extension) [{default_name}]: ").strip()
    if not name:
        name = default_name
    if not name.lower().endswith(".pptx"):
        name += ".pptx"
    return name

def prompt_slide_size() -> Tuple[float, float, str]:
    """Let the user choose a slide size preset; return (width_in, height_in, label)."""
    print("\nChoose slide size:")
    for k, (label, _, __) in SLIDE_SIZES.items():
        print(f"  {k}) {label}")
    while True:
        choice = input("Enter number (1-6): ").strip()
        if choice in SLIDE_SIZES:
            label, w, h = SLIDE_SIZES[choice]
            return w, h, label
        print("✗ Invalid choice. Please enter a number from the list.\n")

def prompt_fit_mode() -> str:
    """Ask for image placement mode: 'fit' (contain) or 'fill' (cover)."""
    print("\nHow should images be placed?")
    print("  1) Fit whole image (no cropping; background may show)")
    print("  2) Crop to fill (no whitespace; edges may be trimmed)")
    while True:
        c = input("Enter 1 or 2: ").strip()
        if c == "1":
            return "fit"
        if c == "2":
            return "fill"
        print("✗ Invalid choice. Enter 1 or 2.\n")

# -----------------------------
# PDF → PNG (300 DPI)
# -----------------------------
def pdf_to_pngs(pdf_path: Path, dpi: int = 300) -> Tuple[Path, List[Path]]:
    """
    Render each PDF page to a PNG at the given DPI.
    Returns (temp_dir, [png_paths]). Caller is responsible for deleting temp_dir
    (we use TemporaryDirectory context in main).
    """
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("pdf_to_pngs called with a non-PDF path")

    temp_dir = Path(tempfile.mkdtemp(prefix="pdf_pages_"))
    png_paths: List[Path] = []

    with fitz.open(pdf_path) as doc:
        if doc.page_count == 0:
            return temp_dir, []
        for i, page in enumerate(doc, start=1):
            # Render at desired DPI
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            out_path = temp_dir / f"page_{i:04d}.png"
            pix.save(out_path.as_posix())
            png_paths.append(out_path)

    return temp_dir, png_paths

# -----------------------------
# Folder → list of images
# -----------------------------
def list_images(folder: Path) -> List[Path]:
    """
    Return a case-insensitively sorted list of allowed images in a folder.
    Non-image files are ignored. Subfolders are ignored.
    """
    imgs = [p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS]
    imgs.sort(key=lambda p: p.name.lower())
    return imgs

# -----------------------------
# Image placement
# -----------------------------
def place_picture_fit(slide, img_path: Path, sw_emu: int, sh_emu: int) -> None:
    """
    Contain: scale proportionally so the whole image is visible; center it.
    Letterboxing/pillarboxing may appear as slide background.
    """
    pic = slide.shapes.add_picture(str(img_path), left=0, top=0)  # insert at native size
    iw, ih = float(pic.width), float(pic.height)
    sw, sh = float(sw_emu), float(sh_emu)

    scale = min(sw / iw, sh / ih)  # contain
    new_w, new_h = iw * scale, ih * scale
    pic.width, pic.height = int(new_w), int(new_h)
    pic.left, pic.top = int((sw - new_w) / 2.0), int((sh - new_h) / 2.0)

def place_picture_fill(slide, img_path: Path, sw_emu: int, sh_emu: int) -> None:
    """
    Cover: scale proportionally so the slide is fully covered; center it.
    Overflow is effectively cropped at slide edges.
    """
    pic = slide.shapes.add_picture(str(img_path), left=0, top=0)  # insert at native size
    iw, ih = float(pic.width), float(pic.height)
    sw, sh = float(sw_emu), float(sh_emu)

    scale = max(sw / iw, sh / ih)  # cover
    new_w, new_h = iw * scale, ih * scale
    pic.width, pic.height = int(new_w), int(new_h)
    pic.left, pic.top = int((sw - new_w) / 2.0), int((sh - new_h) / 2.0)

# -----------------------------
# PPTX builder
# -----------------------------
def build_presentation(
    images: Iterable[Path],
    output_path: Path,
    slide_size_in: Tuple[float, float],
    mode: str,
) -> None:
    """
    Create the PPTX at output_path with given slide size and placement mode.
    mode: 'fit' or 'fill'
    """
    width_in, height_in = slide_size_in
    prs = Presentation()
    prs.slide_width = Inches(width_in)
    prs.slide_height = Inches(height_in)

    sw_emu = int(prs.slide_width)
    sh_emu = int(prs.slide_height)

    for img in images:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        if mode == "fit":
            place_picture_fit(slide, img, sw_emu, sh_emu)
        else:
            place_picture_fill(slide, img, sw_emu, sh_emu)

    prs.save(output_path.as_posix())

# -----------------------------
# Orchestration
# -----------------------------
def main() -> None:
    print("\n=== PPTX Builder (Images & PDFs) ===\n")

    in_path = prompt_input_path()

    # Decide output location default: sibling of the input (file's parent or the folder itself)
    default_dir = in_path.parent if in_path.is_file() else in_path
    out_name = prompt_output_name("slides")
    output_path = (default_dir / out_name).resolve()

    width_in, height_in, size_label = prompt_slide_size()
    mode = prompt_fit_mode()  # 'fit' or 'fill'

    # Prepare list of images; if PDF, render pages at 300 DPI into a temp dir
    tmp_dir_obj: Optional[tempfile.TemporaryDirectory] = None
    images: List[Path] = []

    try:
        if in_path.is_file():
            if in_path.suffix.lower() == ".pdf":
                # Use our own tempdir lifetime control via TemporaryDirectory
                tmp_dir_obj = tempfile.TemporaryDirectory(prefix="pdf_pages_")
                temp_dir = Path(tmp_dir_obj.name)
                # Render PDF pages
                with fitz.open(in_path) as doc:
                    if doc.page_count == 0:
                        print("✗ PDF has no pages. Exiting.")
                        sys.exit(1)
                    print(f"\nConverting PDF → PNG at 300 DPI ({doc.page_count} pages)…")
                    for i, page in enumerate(doc, start=1):
                        pix = page.get_pixmap(dpi=300, alpha=False)
                        out_png = temp_dir / f"page_{i:04d}.png"
                        pix.save(out_png.as_posix())
                        images.append(out_png)
            else:
                print("✗ File provided is not a PDF. Provide a PDF or a folder of images.")
                sys.exit(1)
        else:
            # Folder: pick allowed images only
            images = list_images(in_path)
            if not images:
                print("✗ No supported images found in the folder.")
                sys.exit(1)

        # Summary
        print("\nSummary:")
        print(f"  Input path  : {in_path}")
        print(f"  Items used  : {len(images)} image(s)")
        print(f"  Slide size  : {size_label}")
        print(f"  Placement   : {'Fit whole image (no crop)' if mode=='fit' else 'Crop to fill (cover)'}")
        print(f"  Output file : {output_path}\n")

        # Build PPTX
        build_presentation(images, output_path, (width_in, height_in), mode)
        print(f"✅ Presentation saved to: {output_path}")

    finally:
        # Clean up temp directory if we created one for PDF pages
        if tmp_dir_obj is not None:
            tmp_dir_obj.cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
