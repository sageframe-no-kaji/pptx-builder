#!/usr/bin/env python3
"""Gradio Web UI for PPTX Builder"""

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
from ._icon_data import ICON_DATA_URI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SLIDE_SIZE_OPTIONS = {
    "16:9 (Widescreen)": (13.3333333333, 7.5),
    "4:3 (Standard)": (10.0, 7.5),
    'Letter (11" x 8.5")': (11.0, 8.5),
    'A4 (11.69" x 8.27")': (11.69, 8.27),
    'Legal (14" x 8.5")': (14.0, 8.5),
    'Tabloid (17" x 11")': (17.0, 11.0),
}

MAX_FILE_SIZE = 50 * 1024 * 1024
MAX_FILES = 100
TEMP_DIRS: List[Path] = []


def cleanup_temp_files():
    for temp_dir in TEMP_DIRS:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    TEMP_DIRS.clear()


def cleanup_old_files():
    temp_base = Path(tempfile.gettempdir())
    current_time = time.time()
    for item in temp_base.glob("pptx_builder_*"):
        if item.is_dir():
            if current_time - item.stat().st_mtime > 3600:
                shutil.rmtree(item, ignore_errors=True)


atexit.register(cleanup_temp_files)


def process_files(
    files: List[str],
    slide_size: str,
    fit_mode: str,
    dpi: int = 150,
    output_name: str = "",
) -> Optional[str]:
    if not files:
        return None

    logger.debug(f"Processing {len(files)} file(s)")

    if len(files) > MAX_FILES:
        raise gr.Error(f"Too many files. Maximum {MAX_FILES} files allowed.")

    for file in files:
        file_path = Path(file)
        if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
            raise gr.Error(
                f"File too large: {file_path.name}. Maximum 50MB per file."
            )

    temp_dir = Path(tempfile.mkdtemp(prefix="pptx_builder_"))
    TEMP_DIRS.append(temp_dir)

    try:
        width_in, height_in = SLIDE_SIZE_OPTIONS[slide_size]

        if len(files) == 1 and Path(files[0]).suffix.lower() == ".pdf":
            width_in, height_in = pdf_first_page_size_inches(Path(files[0]))
            logger.debug(
                f"Auto-detected PDF aspect ratio: {width_in:.2f}x{height_in:.2f}"
            )

        mode = "fit" if fit_mode == "Fit whole image" else "fill"
        image_files = []

        for file in files:
            file_path = Path(file)
            if file_path.suffix.lower() == ".pdf":
                pdf_images = convert_pdf_to_images(file_path, dpi=dpi)
                image_files.extend(pdf_images)
            else:
                image_files.append(file_path)

        if not image_files:
            return None

        image_files.sort(key=lambda p: p.name.lower())

        if output_name and output_name.strip():
            output_filename = output_name.strip()
            if not output_filename.lower().endswith(".pptx"):
                output_filename += ".pptx"
        elif len(files) == 1:
            output_filename = Path(files[0]).stem + ".pptx"
        else:
            output_filename = "presentation.pptx"

        output_path = temp_dir / output_filename

        build_presentation(
            images=image_files,
            output_path=output_path,
            slide_width_in=width_in,
            slide_height_in=height_in,
            mode=mode,
            show_progress=False,
        )

        return str(output_path)

    except Exception as e:
        import traceback

        logger.error(f"Exception occurred: {e}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        raise gr.Error(f"Error: {str(e)}")


# ──────────────────────────────────────────────────────────────────────────────
# HTML blocks
# ──────────────────────────────────────────────────────────────────────────────

_FONTS_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600&display=swap" rel="stylesheet">
"""

_HEADER = f"""
<div class="atm-header">
  <div class="atm-header-inner">
    <div class="atm-header-left">
      <div class="atm-header-brand">
        <img src="{ICON_DATA_URI}" alt="" class="atm-icon" aria-hidden="true">
        <div>
          <h1 class="atm-title">PPTX Builder</h1>
          <p class="atm-tagline">Convert PDFs and images into PowerPoint presentations.</p>
        </div>
      </div>
    </div>
    <div class="atm-header-right">
      <span class="atm-cli-label">prefer the cli?</span>
      <code class="atm-cli-code">pip install sageframe-pptx-builder</code>
    </div>
  </div>
</div>
"""

_INFO_STRIP = """
<div class="atm-info-strip-wrap">
  <div class="atm-info-strip">
    <div class="atm-info-item">
      <strong class="atm-info-label">Private by design.</strong><span
      class="atm-info-desc">Files processed in-memory and deleted after one hour.
      Nothing stored or logged.</span>
    </div>
    <div class="atm-info-item">
      <strong class="atm-info-label">Open source.</strong><span class="atm-info-desc">A <a href="https://sageframe.net" target="_blank" class="atm-link">Sageframe</a> project &mdash; <a href="https://github.com/sageframe-no-kaji/pptx-builder" target="_blank" class="atm-link atm-link-nowrap">view&nbsp;source&nbsp;on&nbsp;GitHub&nbsp;&rarr;</a></span>
    </div>
    <div class="atm-info-item">
      <strong class="atm-info-label">Demo limits.</strong><span class="atm-info-desc">50&nbsp;MB per file &middot; 100 files max. <a href="https://github.com/sageframe-no-kaji/pptx-builder" target="_blank" class="atm-link atm-link-nowrap">Self-host&nbsp;&rarr;</a> for no limits and 100% privacy.</span>
    </div>
  </div>
</div>
"""

_HOW_IT_WORKS = """
<div class="atm-how">
  <h3 class="atm-how-title">How it works</h3>
  <ol class="atm-how-list">
    <li>Upload one or more PDFs or images</li>
    <li>Choose a slide size and image placement</li>
    <li>Click <em>Create presentation</em></li>
    <li>Download your PPTX file</li>
  </ol>
  <p class="atm-how-note">
    A single PDF auto-detects its aspect ratio.
    Multiple files sort alphabetically by filename.
  </p>
  <p class="atm-how-note">Temp files are deleted automatically after one hour.</p>
</div>
"""

_FOOTER = """
<div class="atm-footer">
  <p>
    Created by Andrew T.&nbsp;Marcus
    &nbsp;&middot;&nbsp;
    <a href="https://sageframe.net" target="_blank" class="atm-footer-link">sageframe.net</a>
    &nbsp;&middot;&nbsp;
    <a href="https://github.com/sageframe-no-kaji/pptx-builder"
       target="_blank"
       class="atm-footer-link">View source on GitHub &rarr;</a>
  </p>
</div>
"""

# ──────────────────────────────────────────────────────────────────────────────
# ATM Brand System — CSS
# ──────────────────────────────────────────────────────────────────────────────

custom_css = """
/* ================================================================
   Design tokens
   ================================================================ */
:root {
  --ink:          #1a1a1a;
  --ink-light:    #4a4a4a;
  --ink-muted:    #7a7a7a;
  --ground:       #f5f2ed;
  --ground-warm:  #ebe6dd;
  --white:        #faf8f4;
  --accent:       #c45a2d;
  --umber:        #6b3a2a;
  --rule:         #d0c9be;
  --dark-bg:      #1a1a1a;
  --dark-text:    #c8c2b8;
  --dark-prose:   #b0a99e;
  --dark-muted:   #888888;
  --dark-surface: #252525;

  --display: 'DM Serif Display', Georgia, serif;
  --body:    'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono:    'IBM Plex Mono', 'Courier New', monospace;

  --max-w:  960px;
  --gutter: clamp(1.25rem, 4vw, 2.5rem);
}

/* ================================================================
   Base reset — override Gradio defaults
   ================================================================ */
html, body {
  background: var(--ground) !important;
  font-family: var(--body) !important;
  color: var(--ink-light) !important;
  margin: 0 !important;
  padding: 0 !important;
}

.gradio-container {
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
  background: var(--ground) !important;
  min-height: 100vh;
}

.gradio-container > .main,
.gradio-container > .main > .wrap,
.gradio-container > .main > .contain {
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
  background: var(--ground) !important;
  gap: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

/* ================================================================
   Header — Ink dark band
   ================================================================ */
.atm-header {
  background: var(--dark-bg);
  width: 100%;
  margin: 0;
}

.atm-header-inner {
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 2rem var(--gutter);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 2rem;
  box-sizing: border-box;
}

.atm-header-left {
  flex: 1;
  min-width: 0;
}

.atm-header-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.atm-icon {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 8px;
  display: block;
}

.atm-title {
  font-family: var(--display) !important;
  font-size: 2rem;
  font-weight: 400;
  color: var(--ground) !important;
  margin: 0 0 0.4rem 0;
  line-height: 1.15;
  letter-spacing: -0.01em;
  text-wrap: balance;
}

.atm-tagline {
  font-family: var(--display) !important;
  font-style: italic;
  font-size: 1rem;
  color: var(--dark-prose) !important;
  margin: 0;
  line-height: 1.4;
}

.atm-header-right {
  text-align: right;
  flex-shrink: 0;
  padding-top: 0.25rem;
}

.atm-cli-label {
  display: block;
  font-family: var(--mono);
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  color: var(--dark-muted);
  margin-bottom: 0.45rem;
}

.atm-cli-code {
  display: inline-block;
  font-family: var(--mono) !important;
  font-size: 0.8rem;
  font-weight: 400;
  background: var(--dark-surface);
  color: var(--dark-text);
  padding: 0.45rem 0.85rem;
  border-radius: 2px;
  white-space: nowrap;
  border: none;
  user-select: all;
}

/* ================================================================
   Info strip
   ================================================================ */
.atm-info-strip-wrap {
  background: var(--ground);
  border-bottom: 1px solid var(--rule);
}

.atm-info-strip {
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 1rem var(--gutter);
  display: flex;
  gap: 3rem;
  box-sizing: border-box;
}

.atm-info-item {
  flex: 1;
  font-size: 0.85rem;
  line-height: 1.55;
}

.atm-info-label {
  font-family: var(--body);
  font-weight: 600;
  color: var(--ink);
  margin-right: 0.3em;
}

.atm-info-desc {
  font-family: var(--body);
  color: var(--ink-muted);
}

.atm-link {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.2s ease;
}
.atm-link:hover { color: var(--ink); }
.atm-link-nowrap { white-space: nowrap; }

/* ================================================================
   Main content panel — white surface
   ================================================================ */
#main-content {
  max-width: var(--max-w) !important;
  width: calc(100% - 2 * var(--gutter)) !important;
  margin: 2rem auto 0 !important;
  background: var(--white) !important;
  border: 1px solid var(--rule) !important;
  border-radius: 2px !important;
  padding: 2rem !important;
  box-sizing: border-box !important;
  gap: 1.5rem !important;
  box-shadow: none !important;
}

/* Accepted formats tag line */
.atm-formats {
  font-family: var(--mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.04em;
  color: var(--ink-muted) !important;
  margin: 0 0 0.5rem !important;
  line-height: 1.5;
}

/* ================================================================
   Gradio form element overrides
   ================================================================ */

/* Labels */
#main-content label,
#main-content .label-wrap > span {
  font-family: var(--body) !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  color: var(--ink) !important;
  letter-spacing: normal !important;
  text-transform: none !important;
}

/* Text inputs */
#main-content input[type="text"],
#main-content input[type="number"],
#main-content input[type="search"],
#main-content textarea {
  font-family: var(--body) !important;
  font-size: 0.9rem !important;
  background: var(--white) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule) !important;
  border-radius: 2px !important;
  box-shadow: none !important;
  outline: none !important;
  transition: border-color 0.15s ease !important;
}
#main-content input[type="text"]:focus,
#main-content input[type="number"]:focus,
#main-content textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: none !important;
}

/* Dropdown / select */
#main-content .wrap,
#main-content select {
  font-family: var(--body) !important;
  font-size: 0.9rem !important;
  background: var(--white) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule) !important;
  border-radius: 2px !important;
  box-shadow: none !important;
}
#main-content .wrap:focus-within {
  border-color: var(--accent) !important;
}

/* Slider track + thumb */
#main-content input[type="range"] {
  accent-color: var(--accent);
}
#main-content input[type="range"]::-webkit-slider-runnable-track {
  background: var(--rule) !important;
  border-radius: 2px !important;
  height: 3px !important;
}
#main-content input[type="range"]::-webkit-slider-thumb {
  background: var(--accent) !important;
  border: none !important;
  box-shadow: none !important;
  width: 16px !important;
  height: 16px !important;
  border-radius: 50% !important;
  margin-top: -6px !important;
}
#main-content input[type="range"]::-moz-range-track {
  background: var(--rule) !important;
  border-radius: 2px !important;
  height: 3px !important;
}
#main-content input[type="range"]::-moz-range-thumb {
  background: var(--accent) !important;
  border: none !important;
  box-shadow: none !important;
  width: 16px !important;
  height: 16px !important;
  border-radius: 50% !important;
}

/* Radio */
#main-content input[type="radio"] {
  accent-color: var(--accent) !important;
}

/* File upload zone */
#main-content .upload-container,
#main-content [data-testid="file"],
#main-content .file-preview-holder {
  border: 1px dashed var(--rule) !important;
  border-radius: 2px !important;
  background: var(--white) !important;
  transition: background-color 0.15s ease, border-color 0.15s ease !important;
}
#main-content .upload-container:hover,
#main-content [data-testid="file"]:hover {
  border-color: var(--accent) !important;
  background: var(--ground-warm) !important;
}

/* Primary button */
#main-content button.primary,
.primary-btn {
  font-family: var(--body) !important;
  font-size: 0.93rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em !important;
  background: var(--accent) !important;
  color: var(--white) !important;
  border: none !important;
  border-radius: 2px !important;
  box-shadow: none !important;
  transform: none !important;
  transition: background-color 0.15s ease !important;
}
#main-content button.primary:hover,
.primary-btn:hover {
  background: var(--umber) !important;
  box-shadow: none !important;
  transform: none !important;
}
#main-content button.primary:focus-visible {
  outline: 2px solid var(--accent) !important;
  outline-offset: 2px !important;
}

/* Secondary / other buttons */
#main-content button:not(.primary) {
  font-family: var(--body) !important;
  border-radius: 2px !important;
  box-shadow: none !important;
}

/* ================================================================
   How it works sidebar
   ================================================================ */
.atm-how {
  padding-top: 0.5rem;
}

.atm-how-title {
  font-family: var(--display) !important;
  font-size: 1.2rem !important;
  font-weight: 400 !important;
  color: var(--ink) !important;
  margin: 0 0 0.8rem !important;
  line-height: 1.2;
  text-wrap: balance;
}

.atm-how-list {
  font-family: var(--body);
  font-size: 0.9rem;
  color: var(--ink-light);
  line-height: 1.75;
  padding-left: 1.25rem;
  margin: 0 0 1rem 0;
}

.atm-how-list em {
  font-style: italic;
  color: var(--ink);
}

.atm-how-note {
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.025em;
  color: var(--ink-muted);
  margin: 0.4rem 0 0;
  line-height: 1.55;
}

/* ================================================================
   Footer
   ================================================================ */
.atm-footer {
  max-width: var(--max-w);
  margin: 1.75rem auto 2.5rem;
  padding: 0 var(--gutter);
  text-align: center;
  box-sizing: border-box;
}

.atm-footer p {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--ink-muted);
  margin: 0;
  letter-spacing: 0.025em;
}

.atm-footer-link {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.2s ease;
}
.atm-footer-link:hover { color: var(--ink); }

/* ================================================================
   Gradio noise suppression
   ================================================================ */

/* Remove all spacing between top-level blocks */
.gradio-container > .main > .contain {
  gap: 0 !important;
  padding: 0 !important;
}

/* The outer column wrapper inside .contain has gap: 16px — zero it */
.gradio-container .contain > div[class*="column"],
.gradio-container .contain > .column {
  gap: 0 !important;
  row-gap: 0 !important;
}

/* Collapse ALL block padding in the outer container */
.gradio-container > .main > .contain > .block,
.gradio-container > .main > .contain > div {
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

/* Remove Gradio's own borders/shadows from the inner panels */
#main-content > .gap,
#main-content .block {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 0 !important;
}

/* Gradio adds padding to rows; keep it zero */
#main-content .row {
  gap: 2rem !important;
}

/* Suppress Gradio's form section borders */
#main-content fieldset,
#main-content .form {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 0 !important;
  gap: 1.25rem !important;
}

/* Suppress Gradio's panel backgrounds */
#main-content .panel,
#main-content .component-wrap {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* Hide Gradio's built-in <footer> element (not our .atm-footer div) */
footer {
  display: none !important;
}

/* Ensure our footer div is always visible */
.atm-footer {
  display: block !important;
}

/* Kill gap between atm-header, atm-info-strip-wrap, and main blocks */
.gradio-container .prose,
.gradio-container > .main > .contain > div:not(#main-content) {
  margin: 0 !important;
  padding: 0 !important;
}

/* File upload — Gradio 6 dropzone button (class "boundedheight" is unique to this element) */
button.boundedheight {
  width: 100% !important;
  border: 1px dashed var(--rule) !important;
  border-radius: 2px !important;
  background: var(--white) !important;
  color: var(--ink-muted) !important;
  transition: background-color 0.15s ease, border-color 0.15s ease !important;
}
button.boundedheight:hover {
  border-color: var(--accent) !important;
  background: var(--ground-warm) !important;
}

/* ================================================================
   Reduced motion
   ================================================================ */
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}

/* ================================================================
   Responsive
   ================================================================ */
@media (max-width: 720px) {
  .atm-header-inner {
    flex-direction: column;
    gap: 1.25rem;
  }
  .atm-header-right { text-align: left; }

  .atm-info-strip {
    flex-direction: column;
    gap: 0.6rem;
  }

  #main-content {
    width: calc(100% - 2rem) !important;
    margin: 1.25rem auto 0 !important;
    padding: 1.25rem !important;
  }

  .atm-footer {
    margin: 1.5rem auto 2rem;
  }
}
"""

# ──────────────────────────────────────────────────────────────────────────────
# Gradio interface
# ──────────────────────────────────────────────────────────────────────────────

_THEME = gr.themes.Default().set(
    body_background_fill="#f5f2ed",
    body_text_color="#4a4a4a",
    body_text_color_subdued="#7a7a7a",
    background_fill_primary="#faf8f4",
    background_fill_secondary="#ebe6dd",
    border_color_primary="#d0c9be",
    color_accent="#c45a2d",
    button_primary_background_fill="#c45a2d",
    button_primary_background_fill_hover="#6b3a2a",
    button_primary_text_color="#faf8f4",
    button_primary_border_color="transparent",
    button_primary_border_color_hover="transparent",
    input_background_fill="#faf8f4",
    input_border_color="#d0c9be",
    input_border_color_focus="#c45a2d",
)

with gr.Blocks(title="PPTX Builder") as app:

    gr.HTML(_HEADER)
    gr.HTML(_INFO_STRIP)

    with gr.Column(elem_id="main-content"):
        gr.HTML('<p class="atm-formats">Accepts &nbsp;PDF &middot; PNG &middot; JPG &middot; TIFF &middot; WebP &middot; BMP &middot; GIF &middot; ICO &middot; HEIC &middot; HEIF</p>')

        with gr.Row():
            with gr.Column():
                files = gr.File(
                    label="Upload files",
                    file_count="multiple",
                    height=240,
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
                    label="Slide size",
                )
                fit_mode = gr.Radio(
                    choices=["Fit whole image", "Crop to fill"],
                    value="Fit whole image",
                    label="Image placement",
                )
                dpi = gr.Slider(
                    minimum=150,
                    maximum=600,
                    value=150,
                    step=50,
                    label="PDF conversion DPI",
                )
                output_name = gr.Textbox(
                    label="Output filename",
                    placeholder="Leave empty to use the input filename",
                    value="",
                )
                submit_btn = gr.Button("Create presentation", variant="primary")

            with gr.Column():
                gr.HTML(_HOW_IT_WORKS)
                output = gr.File(label="Download PPTX")

        submit_btn.click(
            fn=process_files,
            inputs=[files, slide_size, fit_mode, dpi, output_name],
            outputs=output,
        )

    gr.HTML(_FOOTER)


def launch_app():
    cleanup_old_files()
    _pkg_dir = Path(__file__).parent
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        allowed_paths=[str(_pkg_dir)],
        favicon_path=str(_pkg_dir / "favicon.ico"),
        theme=_THEME,
        css=custom_css,
        head=_FONTS_HEAD,
        footer_links=[],
    )


if __name__ == "__main__":
    launch_app()
