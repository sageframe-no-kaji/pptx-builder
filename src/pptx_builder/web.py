#!/usr/bin/env python3
"""
Gradio Web UI for PPTX Builder
Simple interface for converting PDFs and images to PowerPoint
"""

import gradio as gr
import logging
import tempfile
import shutil
import atexit
from pathlib import Path
from typing import Optional, List
import time

from .core import (
    build_presentation,
    convert_pdf_to_images,
    pdf_first_page_size_inches,
)

# Set up module logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Slide size options for dropdown
SLIDE_SIZE_OPTIONS = {
    "16:9 (Widescreen)": (13.3333333333, 7.5),
    "4:3 (Standard)": (10.0, 7.5),
    'Letter (11" x 8.5")': (11.0, 8.5),
    'A4 (11.69" x 8.27")': (11.69, 8.27),
    'Legal (14" x 8.5")': (14.0, 8.5),
    'Tabloid (17" x 11")': (17.0, 11.0),
}

# Security limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file
MAX_FILES = 100  # Max 100 files per upload

# Track temp directories for cleanup
TEMP_DIRS: List[Path] = []


def cleanup_temp_files():
    """Clean up all temporary directories on exit."""
    for temp_dir in TEMP_DIRS:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    TEMP_DIRS.clear()


def cleanup_old_files():
    """Remove temp directories older than 1 hour."""
    temp_base = Path(tempfile.gettempdir())
    current_time = time.time()

    for item in temp_base.glob("pptx_builder_*"):
        if item.is_dir():
            # Remove if older than 1 hour
            if current_time - item.stat().st_mtime > 3600:
                shutil.rmtree(item, ignore_errors=True)


# Register cleanup on exit
atexit.register(cleanup_temp_files)


def process_files(
    files: List[str],
    slide_size: str,
    fit_mode: str,
    dpi: int = 150,
    output_name: str = "",
) -> Optional[str]:
    """
    Process uploaded files and create PowerPoint presentation.

    Args:
        files: List of uploaded file paths (strings)
        slide_size: Selected slide size preset
        fit_mode: "Fit whole image" or "Crop to fill"
        dpi: DPI for PDF conversion
        output_name: Custom output filename (optional)

    Returns:
        Path to generated PPTX file or None on error
    """
    if not files:
        return None

    logger.debug(f"Processing {len(files)} file(s)")

    # Security: Limit number of files
    if len(files) > MAX_FILES:
        raise gr.Error(f"Too many files. Maximum {MAX_FILES} files allowed.")

    # Security: Check file sizes
    for file in files:
        logger.debug(f"Checking file: {file}")
        file_path = Path(file)
        if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
            raise gr.Error(f"File too large: {file_path.name}. Maximum 50MB per file.")

    # Create temp directory for processing
    temp_dir = Path(tempfile.mkdtemp(prefix="pptx_builder_"))
    TEMP_DIRS.append(temp_dir)
    logger.debug(f"Created temp dir: {temp_dir}")

    try:
        # Get slide dimensions
        width_in, height_in = SLIDE_SIZE_OPTIONS[slide_size]

        # Auto-detect aspect ratio for single PDF
        if len(files) == 1 and Path(files[0]).suffix.lower() == ".pdf":
            width_in, height_in = pdf_first_page_size_inches(Path(files[0]))
            logger.debug(f"Auto-detected PDF aspect ratio: {width_in:.2f}x{height_in:.2f}")

        mode = "fit" if fit_mode == "Fit whole image" else "fill"
        logger.debug(f"Slide size: {width_in}x{height_in}, mode: {mode}")

        image_files = []

        # Process each uploaded file
        for file in files:
            file_path = Path(file)
            logger.debug(f"Processing file: {file_path}")

            # Handle PDFs
            if file_path.suffix.lower() == ".pdf":
                logger.debug("Converting PDF at {} DPI".format(dpi))
                # Convert PDF to images
                pdf_images = convert_pdf_to_images(file_path, dpi=dpi)
                logger.debug(f"Got {len(pdf_images)} images from PDF")
                image_files.extend(pdf_images)
            else:
                # Direct image files
                logger.debug("Adding image file directly")
                image_files.append(file_path)

        if not image_files:
            logger.debug("No image files to process")
            return None

        # Sort images
        image_files.sort(key=lambda p: p.name.lower())
        logger.debug(f"Total images: {len(image_files)}")

        # Create output PPTX with appropriate name
        if output_name and output_name.strip():
            # Use custom name if provided
            output_filename = output_name.strip()
            if not output_filename.lower().endswith(".pptx"):
                output_filename = output_filename + ".pptx"
        elif len(files) == 1:
            # Single file: use input filename
            first_file = Path(files[0])
            output_filename = first_file.stem + ".pptx"
        else:
            # Multiple files: use generic name
            output_filename = "presentation.pptx"

        output_path = temp_dir / output_filename
        logger.debug(f"Building presentation: {output_path}")

        build_presentation(
            images=image_files,
            output_path=output_path,
            slide_width_in=width_in,
            slide_height_in=height_in,
            mode=mode,
            show_progress=False,  # No terminal progress in web UI
        )

        logger.debug("Presentation created successfully")
        return str(output_path)

    except Exception as e:
        import traceback

        logger.error(f"Exception occurred: {e}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise gr.Error(f"Error: {str(e)}")


# Custom CSS for branding
custom_css = """
.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    padding: 25px;
    background: linear-gradient(135deg, #1a1a1a 0%, #ed1e24 100%);
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.logo-container svg {
    width: 60px;
    height: 60px;
}
.logo-container h1 {
    color: white;
    margin: 0;
    font-size: 2em;
    font-weight: 600;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}
.footer {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #ed1e24 0%, #c41a1f 100%);
    border-radius: 10px;
    margin-top: 20px;
    color: white;
    border: 1px solid #c41a1f;
}
.footer a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
}
.footer a:hover {
    color: #c41a1f;
    text-decoration: underline;
}
#main-content {
    max-width: 1200px;
    margin: 0 auto;
}

/* Primary button styling - red theme */
.primary-btn, button.primary {
    background: linear-gradient(135deg, #ed1e24 0%, #c41a1f 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 4px rgba(237, 30, 36, 0.3) !important;
    transition: all 0.2s ease !important;
}
.primary-btn:hover, button.primary:hover {
    background: linear-gradient(135deg, #c41a1f 0%, #a01519 100%) !important;
    box-shadow: 0 4px 8px rgba(237, 30, 36, 0.4) !important;
    transform: translateY(-1px);
}

/* Radio button styling - red when selected */
input[type="radio"]:checked {
    accent-color: #ed1e24 !important;
    background-color: #ed1e24 !important;
}
.radio-group label {
    transition: all 0.2s ease;
}
input[type="radio"]:checked + label {
    color: #ed1e24 !important;
    font-weight: 500;
}

/* Slider styling - red accent */
input[type="range"]::-webkit-slider-thumb {
    background: #ed1e24 !important;
}
input[type="range"]::-moz-range-thumb {
    background: #ed1e24 !important;
}
input[type="range"]::-webkit-slider-runnable-track {
    background: linear-gradient(to right, #ed1e24 0%, #1a1a1a 100%) !important;
}

/* Input focus states - red accent */
input:focus, textarea:focus, select:focus {
    border-color: #ed1e24 !important;
    box-shadow: 0 0 0 2px rgba(237, 30, 36, 0.2) !important;
}

/* Dropdown hover */
.dropdown:hover {
    border-color: #ed1e24 !important;
}
"""

# Create Gradio interface
with gr.Blocks(title="PPTX Builder") as app:
    with gr.Column(elem_id="main-content"):
        # Red gradient header
        gr.HTML("""
        <div class="logo-container">
            <div>
                <h1>PPTX Builder</h1>
                <p style="margin: 10px 0 0 0; font-style: italic; color: white; font-size: 1.1em;">Convert PDFs and images to PowerPoint presentations</p>
            </div>
        </div>
        """)

        gr.Markdown("""
            **Supported formats:** PDF, PNG, JPG, JPEG, TIFF, WebP, BMP, GIF, ICO, HEIC, HEIF
            """)

    with gr.Row():
        with gr.Column():
            files = gr.File(
                label="Upload PDF or Images",
                file_count="multiple",
                file_types=[
                    ".pdf",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".tif",
                    ".tiff",
                    ".webp",
                    ".bmp",
                    ".gif",
                    ".ico",
                    ".heic",
                    ".heif",
                ],
            )

            slide_size = gr.Dropdown(
                choices=list(SLIDE_SIZE_OPTIONS.keys()),
                value="16:9 (Widescreen)",
                label="Slide Size",
            )

            fit_mode = gr.Radio(
                choices=["Fit whole image", "Crop to fill"],
                value="Fit whole image",
                label="Image Placement",
            )

            dpi = gr.Slider(
                minimum=150, maximum=600, value=150, step=50, label="PDF Conversion DPI"
            )

            output_name = gr.Textbox(
                label="Output Filename (optional)",
                placeholder="Leave empty to use input filename",
                value="",
            )

            submit_btn = gr.Button("Create Presentation", variant="primary")

        with gr.Column():
            output = gr.File(label="Download PPTX")

            gr.Markdown("""
                ### How it works:
                1. Upload one or more PDFs or images
                2. Choose slide size and placement mode
                3. Click "Create Presentation"
                4. Download your PPTX file

                **Note:** Temp files are cleaned up automatically after 1 hour.
                """)

    # Connect interface
    submit_btn.click(
        fn=process_files,
        inputs=[files, slide_size, fit_mode, dpi, output_name],
        outputs=output,
    )

    # Footer with branding
    gr.HTML("""
        <div class="footer">
            <p>
                Created by Andrew T. Marcus |
                <a href="https://github.com/sageframe-no-kaji" \
target="_blank">GitHub</a> |
                <a href="https://github.com/sageframe-no-kaji/pptx-builder" \
target="_blank">Source Code</a>
            </p>
        </div>
        """)

if __name__ == "__main__":
    # Clean up old files on startup
    cleanup_old_files()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        allowed_paths=[str(Path(__file__).parent)],
        css=custom_css,
    )
