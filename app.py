#!/usr/bin/env python3
"""
Gradio Web UI for PPTX Builder
Simple interface for converting PDFs and images to PowerPoint
"""

import gradio as gr
import tempfile
import shutil
import atexit
from pathlib import Path
from typing import Optional, List
import time

from make_ppt import (
    build_presentation,
    convert_pdf_to_images,
)

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
    temp_base = Path("/tmp")
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

    print(f"[DEBUG] Processing {len(files)} file(s)")

    # Security: Limit number of files
    if len(files) > MAX_FILES:
        raise gr.Error(f"Too many files. Maximum {MAX_FILES} files allowed.")

    # Security: Check file sizes
    for file in files:
        print(f"[DEBUG] Checking file: {file}")
        file_path = Path(file)
        if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
            raise gr.Error(f"File too large: {file_path.name}. Maximum 50MB per file.")

    # Create temp directory for processing
    temp_dir = Path(tempfile.mkdtemp(prefix="pptx_builder_", dir="/tmp"))
    TEMP_DIRS.append(temp_dir)
    print(f"[DEBUG] Created temp dir: {temp_dir}")

    try:
        # Get slide dimensions
        width_in, height_in = SLIDE_SIZE_OPTIONS[slide_size]
        mode = "fit" if fit_mode == "Fit whole image" else "fill"
        print(f"[DEBUG] Slide size: {width_in}x{height_in}, mode: {mode}")

        image_files = []

        # Process each uploaded file
        for file in files:
            file_path = Path(file)
            print(f"[DEBUG] Processing file: {file_path}")

            # Handle PDFs
            if file_path.suffix.lower() == ".pdf":
                print("[DEBUG] Converting PDF at {} DPI".format(dpi))
                # Convert PDF to images
                pdf_images = convert_pdf_to_images(file_path, dpi=dpi)
                print(f"[DEBUG] Got {len(pdf_images)} images from PDF")
                image_files.extend(pdf_images)
            else:
                # Direct image files
                print("[DEBUG] Adding image file directly")
                image_files.append(file_path)

        if not image_files:
            print("[DEBUG] No image files to process")
            return None

        # Sort images
        image_files.sort(key=lambda p: p.name.lower())
        print(f"[DEBUG] Total images: {len(image_files)}")

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
        print(f"[DEBUG] Building presentation: {output_path}")

        build_presentation(
            images=image_files,
            output_path=output_path,
            slide_width_in=width_in,
            slide_height_in=height_in,
            mode=mode,
        )

        print("[DEBUG] Presentation created successfully")
        return str(output_path)

    except Exception as e:
        import traceback

        print(f"[ERROR] Exception occurred: {e}")
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
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
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    margin-top: 20px;
    color: #1a1a1a;
    border: 1px solid #dee2e6;
}
.footer a {
    color: #ed1e24;
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
with gr.Blocks(title="PPTX Builder - Tyro Sageframe") as app:
    with gr.Column(elem_id="main-content"):
        # Header with logo
        gr.HTML("""
            <div class="logo-container">
                <svg xmlns="http://www.w3.org/2000/svg" \
                     viewBox="0 0 301 301">
                  <defs>
                    <style>
                      .st0 { fill: #050606; }
                      .st1 { fill: #ed1e24; }
                      .st2 { stroke: #000; stroke-linecap: square; \
stroke-width: 23px; fill: none; stroke-miterlimit: 10; }
                      .st3 { stroke: #050606; fill: none; \
stroke-miterlimit: 10; }
                    </style>
                  </defs>
                  <path class="st3" \
d="M150.5,292.5c-78.3,0-142-63.7-142-142S72.2,8.5,150.5,8.5s142,63.7,\
142,142-63.7,142-142,142Z"/>
                  <path class="st0" \
d="M150.5,0c-40.2,0-78,15.7-106.4,44.1C15.7,72.5,0,110.3,0,150.5s15.7,\
78,44.1,106.4c28.4,28.4,66.2,44.1,106.4,44.1s78-15.7,106.4-44.1,44.1-66.2,\
44.1-106.4-15.7-78-44.1-106.4C228.5,15.7,190.7,0,150.5,0h0Z"/>
                  <path class="st1" \
d="M150.5,17c73.7,0,133.5,59.8,133.5,133.5s-59.8,133.5-133.5,133.5S17,\
224.2,17,150.5,76.8,17,150.5,17"/>
                  <g>
                    <line class="st2" x1="150.1" y1="33.2" x2="150.1" y2="278.4"/>
                    <line class="st2" x1="74.7" y1="98" x2="188.2" y2="213.8"/>
                    <line class="st2" x1="74.7" y1="252.6" x2="150.1" y2="177.3"/>
                    <line class="st2" x1="150.1" y1="22.6" x2="226.3" y2="98"/>
                    <line class="st2" x1="74.7" y1="98" x2="150.1" y2="22.6"/>
                  </g>
                </svg>
                <h1>PPTX Builder</h1>
            </div>
            """)

        gr.Markdown("""
            Convert PDFs and images to PowerPoint presentations at 150 DPI.

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
                Created by <strong>Tyro Sageframe</strong> |
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
