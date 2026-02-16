# Complete Gradio Tutorial: Building a Web UI for Python CLI Tools

**A Deep Dive into the PPTX Builder Web Interface**

This tutorial walks through every aspect of how we built a Gradio web UI for the `make_ppt.py` CLI tool. By the end, you'll understand exactly how Gradio works and be able to build your own web interfaces.

---

## Table of Contents

1. [What is Gradio?](#what-is-gradio)
2. [Why Gradio for This Project?](#why-gradio-for-this-project)
3. [Architecture Overview](#architecture-overview)
4. [Breaking Down app.py](#breaking-down-apppy)
5. [File Upload/Download Mechanics](#file-uploaddownload-mechanics)
6. [State Management & Cleanup](#state-management--cleanup)
7. [Docker Integration](#docker-integration)
8. [Security Considerations](#security-considerations)
9. [From Zero to Working App](#from-zero-to-working-app)
10. [Extending the Application](#extending-the-application)

---

## What is Gradio?

**Gradio** is a Python library that lets you create web UIs for Python functions with minimal code. Instead of writing HTML, CSS, JavaScript, and managing a web server, you:

1. Write your Python function
2. Add Gradio decorators/config
3. Get a working web app

### Core Concept

```python
import gradio as gr

def my_function(input_text):
    return input_text.upper()

# Create a web UI with one text input and one text output
demo = gr.Interface(fn=my_function, inputs="text", outputs="text")
demo.launch()
```

That's it. Gradio automatically:
- Creates HTML forms
- Handles HTTP requests
- Manages websockets for real-time updates
- Provides file upload/download
- Handles errors gracefully

### When to Use Gradio vs Building Custom Web Apps

**Use Gradio when:**
- You have a working Python function/script
- You need a quick UI for demos, prototypes, or internal tools
- You don't need complex routing or multi-page apps
- File processing is the main interaction

**Build custom (Flask/FastAPI/React) when:**
- You need multiple pages and complex navigation
- Custom branding/UI is critical
- You need fine-grained control over every pixel
- Authentication/user management is complex

---

## Why Gradio for This Project?

Our `make_ppt.py` already worked perfectly from CLI:

```bash
python make_ppt.py -i my_file.pdf --dpi 300
```

We wanted:
1. **Drag-and-drop file upload** (better than CLI for most users)
2. **No installation** required (Docker + web browser)
3. **Download button** for the result
4. **Quick development** (hours, not days)

Gradio gave us all of this without writing a single line of HTML/CSS/JavaScript.

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│   User's Browser (localhost:7860)          │
│                                             │
│  ┌─────────────┐      ┌─────────────┐     │
│  │ File Upload │      │  Download   │     │
│  │   Widget    │      │   Button    │     │
│  └─────────────┘      └─────────────┘     │
└─────────────────────────────────────────────┘
              ↓                    ↑
         HTTP POST            HTTP GET
              ↓                    ↑
┌─────────────────────────────────────────────┐
│   Gradio Server (Python app.py)             │
│                                             │
│  1. Receives file from browser              │
│  2. Saves to /tmp (Docker tmpfs)            │
│  3. Calls process_files()                   │
│  4. Returns path to generated .pptx         │
│  5. Gradio serves file back to browser      │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│   make_ppt.py (Your existing code)          │
│                                             │
│  - convert_pdf_to_images()                  │
│  - build_presentation()                     │
│  - All the PPTX logic                       │
└─────────────────────────────────────────────┘
```

**Key Insight:** We didn't rewrite `make_ppt.py`. We imported its functions and wrapped them with Gradio UI.

---

## Breaking Down app.py

Let's go through `app.py` section by section, understanding every design decision.

### Part 1: Imports and Constants

```python
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
    pdf_first_page_size_inches,
    SLIDE_SIZES,
)
```

**Why these imports?**
- `gradio as gr` - The core library
- `tempfile` - Create temporary directories for processing
- `shutil` - Delete temp directories when done
- `atexit` - Ensure cleanup happens even if app crashes
- `Path` - Modern file path handling (better than `os.path`)
- `time` - For timestamp-based cleanup

**Critical:** We import functions from `make_ppt.py`, not rewriting them. This is **code reuse**.

### Part 2: UI Configuration Dictionary

```python
# Slide size options for dropdown
SLIDE_SIZE_OPTIONS = {
    "16:9 (Widescreen)": (13.3333333333, 7.5),
    "4:3 (Standard)": (10.0, 7.5),
    "Letter (11\" x 8.5\")": (11.0, 8.5),
    "A4 (11.69\" x 8.27\")": (11.69, 8.27),
    "Legal (14\" x 8.5\")": (14.0, 8.5),
    "Tabloid (17\" x 11\")": (17.0, 11.0),
}
```

**Why a dictionary?**
- Keys = User-friendly labels shown in dropdown
- Values = Actual dimensions passed to `build_presentation()`
- Gradio dropdowns work with any list/dict

**Pattern:** Separate UI labels from internal values. Users see "16:9 (Widescreen)", code gets `(13.333, 7.5)`.

### Part 3: Security Limits

```python
# Security limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file
MAX_FILES = 100  # Max 100 files per upload
```

**Why hardcode limits?**
- Prevent abuse (someone uploads 10GB)
- Protect server resources
- Fail fast with clear error messages

**Best Practice:** Always validate input size before processing.

### Part 4: Temporary File Management

```python
# Track temp directories for cleanup
TEMP_DIRS = []

def cleanup_temp_files():
    """Clean up all temporary directories on exit."""
    for temp_dir in TEMP_DIRS:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    TEMP_DIRS.clear()

def cleanup_old_files():
    """Remove temp directories older than 1 hour."""
    cutoff = time.time() - 3600  # 1 hour ago
    for item in Path("/tmp").glob("pptx_builder_*"):
        if item.is_dir() and item.stat().st_mtime < cutoff:
            shutil.rmtree(item, ignore_errors=True)

# Register cleanup on exit
atexit.register(cleanup_temp_files)
```

**Why track temp directories?**
- Gradio processes files in `/tmp/gradio/random_hash/`
- We create additional temp dirs for PDF conversion
- Without cleanup, `/tmp` fills up

**Pattern Explained:**
1. `TEMP_DIRS` = Global list tracking what we created
2. `cleanup_temp_files()` = Delete everything we created (called on exit)
3. `cleanup_old_files()` = Delete old files from previous runs (called on startup)
4. `atexit.register()` = Python guarantee: run this function before program ends

**Docker tmpfs:** In our Docker Compose, `/tmp` is a RAM disk that auto-clears on restart. This is **defense in depth** - cleanup code + tmpfs.

### Part 5: The Core Processing Function

```python
def process_files(
    files: List[gr.File],
    slide_size: str,
    fit_mode: str,
    dpi: int = 150
) -> Optional[str]:
    """
    Process uploaded files and create PowerPoint presentation.

    Args:
        files: List of uploaded files (PDFs or images)
        slide_size: Selected slide size preset
        fit_mode: "Fit whole image" or "Crop to fill"
        dpi: DPI for PDF conversion

    Returns:
        Path to generated PPTX file or None on error
    """
    if not files:
        return None
```

**Function signature breakdown:**
- `files: List[gr.File]` - Gradio passes uploaded files as a list
- `slide_size: str` - The dropdown selection (e.g., "16:9 (Widescreen)")
- `fit_mode: str` - Radio button selection
- `dpi: int = 150` - Slider value
- Returns `str` or `None` - **Critical:** Return a file path, Gradio serves it automatically

**Gradio Convention:** Input parameters match UI elements (we'll see this in the `gr.Blocks` section).

### Part 6: Input Validation

```python
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
```

**Important Details:**

1. **Gradio file format:** Uploaded files are file paths (strings), not file objects
   - `file` is a string like `/tmp/gradio/abc123/myfile.pdf`
   - That's why we do `Path(file)`, not `file.name`

2. **`gr.Error()` vs exceptions:**
   - `raise gr.Error("message")` = User-friendly error in UI (red box)
   - `raise Exception("message")` = Generic error, might show stack trace
   - **Always use `gr.Error()` for validation failures**

3. **Print statements for debugging:**
   - Gradio is a web app, `print()` goes to Docker logs
   - View with `docker logs -f pptx-builder`
   - Production: Replace with `logging` module

### Part 7: File Processing Logic

```python
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
                print(f"[DEBUG] Converting PDF at {dpi} DPI")
                # Convert PDF to images
                pdf_images = convert_pdf_to_images(file_path, dpi=dpi)
                print(f"[DEBUG] Got {len(pdf_images)} images from PDF")
                image_files.extend(pdf_images)
            else:
                # Direct image files
                print(f"[DEBUG] Adding image file directly")
                image_files.append(file_path)

        if not image_files:
            print("[DEBUG] No image files to process")
            return None

        # Sort images
        image_files.sort(key=lambda p: p.name.lower())
        print(f"[DEBUG] Total images: {len(image_files)}")

        # Create output PPTX
        output_path = temp_dir / "presentation.pptx"
        print(f"[DEBUG] Building presentation: {output_path}")

        build_presentation(
            images=image_files,
            output_path=output_path,
            slide_width_in=width_in,
            slide_height_in=height_in,
            mode=mode
        )

        print(f"[DEBUG] Presentation created successfully")
        return str(output_path)
```

**Design Pattern: Collect → Process → Return**

1. **Collect:** Loop through all uploads, convert PDFs to images
2. **Process:** Call the original `build_presentation()` function
3. **Return:** Return the output file path as a string

**Why `str(output_path)`?**
- Gradio expects string paths for file downloads
- `Path` objects don't work directly

**Reusing CLI code:**
- `convert_pdf_to_images()` - Already written in `make_ppt.py`
- `build_presentation()` - Already written in `make_ppt.py`
- We didn't duplicate any logic!

### Part 8: Error Handling

```python
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception occurred: {e}")
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        raise gr.Error(f"Error: {str(e)}")
```

**Error handling strategy:**

1. **Log to console** (for developers):
   ```python
   print(f"[ERROR] Exception occurred: {e}")
   print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
   ```

2. **Show user-friendly message**:
   ```python
   raise gr.Error(f"Error: {str(e)}")
   ```

**Why both?**
- Developers see full traceback in `docker logs`
- Users see clean error message in browser
- Never expose stack traces to users (security risk)

### Part 9: Building the Gradio UI

```python
with gr.Blocks(title="PPTX Builder") as app:
    gr.Markdown(
        """
        # PPTX Builder

        Convert PDFs and images to PowerPoint presentations at 150 DPI.

        **Supported formats:** PDF, PNG, JPG, JPEG, TIFF, WebP, BMP, GIF, ICO, HEIC, HEIF
        """
    )
```

**`gr.Blocks` vs `gr.Interface`:**

- `gr.Interface` - Quick and simple, one function → one UI
- `gr.Blocks` - Full control over layout, multiple functions, custom HTML

**Markdown support:** Any string in triple quotes gets rendered as Markdown in the UI.

### Part 10: Layout with Rows and Columns

```python
    with gr.Row():
        with gr.Column():
            # Left column - inputs
            files = gr.File(...)
            slide_size = gr.Dropdown(...)
            fit_mode = gr.Radio(...)
            dpi = gr.Slider(...)
            submit_btn = gr.Button(...)

        with gr.Column():
            # Right column - outputs
            output = gr.File(label="Download PPTX")
            gr.Markdown("""...""")
```

**Layout components:**
- `gr.Row()` - Horizontal layout (left/right split)
- `gr.Column()` - Vertical layout (stacked)
- Nesting: `Row( Column(), Column() )` = 2-column layout

**Pattern:** Inputs on left, outputs on right (standard UI convention).

### Part 11: UI Widgets Explained

#### File Upload Widget

```python
files = gr.File(
    label="Upload PDF or Images",
    file_count="multiple",
    file_types=[
        ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff",
        ".webp", ".bmp", ".gif", ".ico", ".heic", ".heif"
    ]
)
```

**Properties:**
- `label` - Text shown above widget
- `file_count="multiple"` - Allow multiple files (vs `"single"`)
- `file_types` - Browser filter (only shows these extensions)

**Security note:** File type validation happens **client-side** (browser) and **server-side** (our code checks extensions). Never trust client-side validation alone.

#### Dropdown Widget

```python
slide_size = gr.Dropdown(
    choices=list(SLIDE_SIZE_OPTIONS.keys()),
    value="16:9 (Widescreen)",
    label="Slide Size"
)
```

**Properties:**
- `choices` - List of options (we use dict keys)
- `value` - Default selection
- Returns: The selected string (e.g., "16:9 (Widescreen)")

#### Radio Button Widget

```python
fit_mode = gr.Radio(
    choices=["Fit whole image", "Crop to fill"],
    value="Fit whole image",
    label="Image Placement"
)
```

**Radio vs Dropdown:**
- Radio: All options visible (2-5 choices)
- Dropdown: Compact for many choices (6+)

#### Slider Widget

```python
dpi = gr.Slider(
    minimum=150,
    maximum=600,
    value=150,
    step=50,
    label="PDF Conversion DPI"
)
```

**Properties:**
- `minimum`, `maximum` - Range bounds
- `value` - Default position
- `step` - Increment (150, 200, 250, ...)

**UX tip:** Steps of 50 prevent overwhelming users with too many options (150 vs 151 vs 152...).

### Part 12: Connecting UI to Function

```python
    submit_btn.click(
        fn=process_files,
        inputs=[files, slide_size, fit_mode, dpi],
        outputs=output
    )
```

**This is where the magic happens!**

- `submit_btn.click()` - Event trigger (user clicks button)
- `fn=process_files` - Function to call
- `inputs=[...]` - Widget values passed to function (in order)
- `outputs=output` - Where to display the result

**How Gradio connects them:**

1. User clicks button
2. Gradio collects values from `files`, `slide_size`, `fit_mode`, `dpi` widgets
3. Calls `process_files(files_value, slide_size_value, fit_mode_value, dpi_value)`
4. Takes returned string (file path)
5. Displays download button in `output` widget

**Critical:** Parameter order in `inputs=[]` must match function signature!

```python
def process_files(files, slide_size, fit_mode, dpi):  # Order matters!
    ...

submit_btn.click(
    fn=process_files,
    inputs=[files, slide_size, fit_mode, dpi],  # Same order!
    outputs=output
)
```

### Part 13: Launching the App

```python
if __name__ == "__main__":
    # Clean up old temp files on startup
    cleanup_old_files()

    # Launch Gradio
    app.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,        # Port number
        share=False              # Don't create public ngrok link
    )
```

**Launch options:**

- `server_name="0.0.0.0"` - **Critical for Docker!**
  - `127.0.0.1` = Only localhost (won't work in Docker)
  - `0.0.0.0` = All network interfaces (Docker can forward to host)

- `server_port=7860` - The port number
  - Must match `docker-compose.yml`: `"7860:7860"`

- `share=False` - Gradio can create public URLs via ngrok
  - `True` = Anyone on internet can access (risky!)
  - `False` = Local only (secure)

**Production consideration:** For public deployment, use reverse proxy (nginx) instead of `share=True`.

---

## File Upload/Download Mechanics

### How File Upload Works (Under the Hood)

```
User Browser                  Gradio Server
     │                              │
     │  1. User picks file         │
     │     "my_doc.pdf"            │
     │                              │
     │  2. HTTP POST (multipart)   │
     ├────────────────────────────>│
     │     Base64 encoded file     │  3. Gradio saves to:
     │                              │     /tmp/gradio/abc123/my_doc.pdf
     │                              │
     │  4. Returns file path        │
     │<─────────────────────────────┤
     │     "/tmp/gradio/.../my_doc" │
     │                              │
```

**In your function:**

```python
def process_files(files: List[gr.File], ...):
    for file in files:
        # 'file' is already a file path string!
        file_path = Path(file)  # /tmp/gradio/abc123/my_doc.pdf

        # File already exists on disk
        with open(file_path, 'rb') as f:
            data = f.read()
```

**Common mistake:**

```python
# WRONG - Gradio gives you paths, not file objects
file.read()  # AttributeError: str has no attribute 'read'

# RIGHT
with open(file, 'rb') as f:
    f.read()
```

### How File Download Works

**Pattern:**

1. Your function creates a file
2. Return the file path as a string
3. Gradio automatically serves it

```python
def my_function(...):
    output_path = Path("/tmp/result.pptx")

    # Create the file
    with open(output_path, 'wb') as f:
        f.write(data)

    # Return path to Gradio
    return str(output_path)  # Must be string!
```

**Gradio's download widget:**

```python
output = gr.File(label="Download PPTX")

submit_btn.click(
    fn=my_function,
    inputs=[...],
    outputs=output  # File path → Download button
)
```

**What Gradio does:**

1. Receives file path from your function
2. Creates a download link in the UI
3. Serves the file when user clicks
4. Original filename preserved (or you can customize)

---

## State Management & Cleanup

### The Problem: Stateless HTTP

Each HTTP request is independent. The server doesn't "remember" previous requests. This creates challenges:

1. **Uploaded files disappear** after request completes
2. **Temporary files pile up** if not cleaned
3. **Memory leaks** if tracking global state incorrectly

### Our Solution: Temporary Directories

```python
# Global list tracks what we've created
TEMP_DIRS = []

def process_files(...):
    # Create temp dir for THIS request
    temp_dir = Path(tempfile.mkdtemp(prefix="pptx_builder_", dir="/tmp"))

    # Track it globally
    TEMP_DIRS.append(temp_dir)

    try:
        # ...processing...
        return str(output_path)
    except Exception as e:
        # Cleanup happens automatically via atexit
        raise gr.Error(str(e))
```

**Cleanup strategies:**

1. **On exit:** `atexit.register(cleanup_temp_files)`
   - Runs when Python process ends
   - Guarantees cleanup even on crashes

2. **On startup:** `cleanup_old_files()`
   - Removes files from previous runs
   - Handles cases where atexit didn't run (kill -9, power loss)

3. **Docker tmpfs:** `/tmp` mounted as RAM disk
   - Automatic cleanup on container restart
   - Fast (no disk I/O)
   - Limited space (2GB in our config)

### Why Not Clean Up Immediately?

```python
def process_files(...):
    temp_dir = create_temp()
    output = temp_dir / "result.pptx"

    build_presentation(output)

    # DON'T DO THIS!
    shutil.rmtree(temp_dir)  # File deleted before user can download!

    return str(output)  # Returns path to deleted file!
```

**The problem:** Gradio serves the file **after** your function returns. If you delete it, download fails.

**Solution:** Let cleanup happen later (atexit or scheduled job).

---

## Docker Integration

### Dockerfile Breakdown

```dockerfile
FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
```

**Why `python:3.11-slim`?**
- **slim** = Minimal Debian (smaller than full image)
- **Not alpine** = Binary wheels work (faster pip install)

**Why `poppler-utils`?**
- Provides `pdftoppm` command
- Required by `pdf2image` library
- Without it: PDF conversion fails silently

**Cleanup pattern:**
```bash
&& rm -rf /var/lib/apt/lists/*
```
- Removes apt cached files
- Reduces image size by ~100MB
- Best practice for Docker images

### Working Directory and Files

```dockerfile
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir gradio>=4.0.0

COPY make_ppt.py .
COPY app.py .
```

**Layer optimization:**

1. Copy `requirements.txt` first
2. Run `pip install`
3. Copy code last

**Why this order?**
- Docker caches layers
- Code changes frequently, dependencies don't
- Changing code doesn't rebuild dependencies

**`--no-cache-dir`:**
- Prevents pip from storing downloaded packages
- Reduces image size
- Slows rebuilds but saves space

### Security: Non-Root User

```dockerfile
RUN useradd -m -u 1000 appuser && \
    mkdir -p /tmp && \
    chown -R appuser:appuser /app /tmp

USER appuser
```

**Why run as non-root?**
- Principle of least privilege
- If attacker escapes Python, they're limited
- Can't install system packages or modify OS

**UID 1000:**
- Matches typical user UID on host
- Prevents permission issues with mounted volumes
- Standard convention

### Environment and Launch

```dockerfile
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["python", "-u", "app.py"]
```

**`PYTHONUNBUFFERED=1`:**
- Makes print() appear immediately in logs
- Without it, Python buffers output
- Critical for debugging with `docker logs`

**`python -u`:**
- Redundant with PYTHONUNBUFFERED (both unbuffer)
- Belt and suspenders approach

**`EXPOSE 7860`:**
- Documentation only (doesn't actually open port)
- Real port mapping happens in docker-compose.yml

### docker-compose.yml Configuration

```yaml
services:
  pptx-builder:
    build: .
    container_name: pptx-builder
    ports:
      - "7860:7860"
```

**Port mapping:**
- `"7860:7860"` = host:container
- Left (7860) = Access on localhost:7860
- Right (7860) = Gradio listens on this inside container

**Temporary storage:**

```yaml
    tmpfs:
      - /tmp:size=2G,mode=1777
```

**tmpfs explained:**
- RAM-based filesystem (not disk)
- Automatically cleared on restart
- Fast (no disk I/O)
- Size limit prevents filling all RAM

**Mode 1777:**
- Sticky bit set
- Anyone can create files
- Only owner can delete their files
- Same as /tmp on Linux

**Resource limits:**

```yaml
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

**Why limit resources?**
- Prevent one container hogging all CPU/RAM
- Predictable performance
- PDF conversion at 300 DPI can spike CPU

**Choosing limits:**
- 2 CPUs = Parallel PDF page rendering
- 2GB RAM = 1GB for tmpfs + 1GB for Python
- Tune based on your typical workload

### Network Configuration

```yaml
    networks:
      - default
    restart: unless-stopped
```

**`restart: unless-stopped`:**
- Container auto-restarts if it crashes
- Doesn't restart if you manually stopped it
- Good for dev (vs `always` which is annoying)

---

## Security Considerations

### Input Validation

```python
# 1. File count limit
if len(files) > MAX_FILES:
    raise gr.Error(f"Too many files. Maximum {MAX_FILES} files allowed.")

# 2. File size limit
for file in files:
    file_path = Path(file)
    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise gr.Error(f"File too large: {file_path.name}. Maximum 50MB per file.")
```

**Why both limits?**
- File count: Prevent 10,000 tiny files (DoS via file handles)
- File size: Prevent 1 huge file (DoS via disk/memory)

**Best practice:** Fail fast and loud. Check limits before expensive operations.

### Path Traversal Prevention

```python
# Safe - uses Gradio's controlled directory
file_path = Path(file)  # /tmp/gradio/abc123/file.pdf

# UNSAFE - don't let users specify paths
user_input = request.get("path")  # ../../../../etc/passwd
open(user_input)  # Security hole!
```

**Gradio's protection:**
- Files saved to random directory (`/tmp/gradio/abc123/`)
- User can't control the path
- Path traversal (`../`) doesn't work

**Still vulnerable:**
- Custom code that builds paths from user input
- Always validate/sanitize any user-provided filenames

### Docker Isolation

```dockerfile
USER appuser  # Run as non-root
```

**Defense in depth:**

1. **Application level:** Input validation in Python
2. **Container level:** Non-root user limits damage
3. **Filesystem level:** tmpfs prevents persistence
4. **Network level:** Only port 7860 exposed

**What attacker can't do (even with code execution):**
- Modify `/etc/passwd` (not root)
- Install packages (not root)
- Read other containers' data (isolated network)
- Persist malware (tmpfs clears on restart)

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

**Prevents:**
- Fork bomb (CPU)
- Memory exhaustion (RAM)
- Infinite loops consuming 100% CPU

**Example attack:**

```python
# Malicious uploaded Python file
while True:
    data = [1] * 1000000  # Try to allocate infinite RAM
```

**Docker kills it when memory hits 2GB limit.**

---

## From Zero to Working App

Let's build a minimal Gradio app from scratch to cement concepts.

### Step 1: Simple Function

```python
# my_app.py
def process_text(input_text):
    """Convert text to uppercase."""
    return input_text.upper()
```

### Step 2: Add Gradio Interface

```python
import gradio as gr

def process_text(input_text):
    return input_text.upper()

# Create UI
demo = gr.Interface(
    fn=process_text,
    inputs=gr.Textbox(label="Enter text"),
    outputs=gr.Textbox(label="Result"),
    title="Text Processor"
)

demo.launch()
```

**Run it:**
```bash
python my_app.py
```

**You get:** Web UI at http://localhost:7860

### Step 3: Add File Processing

```python
import gradio as gr
from pathlib import Path

def process_file(file):
    """Count lines in uploaded file."""
    if file is None:
        return "No file uploaded"

    path = Path(file)
    with open(path) as f:
        lines = len(f.readlines())

    return f"File has {lines} lines"

demo = gr.Interface(
    fn=process_file,
    inputs=gr.File(label="Upload text file"),
    outputs=gr.Textbox(label="Line count"),
    title="Line Counter"
)

demo.launch()
```

### Step 4: Return a File

```python
import gradio as gr
from pathlib import Path
import tempfile

def process_file(file):
    """Create uppercase version of file."""
    if file is None:
        return None

    # Read input
    input_path = Path(file)
    with open(input_path) as f:
        content = f.read()

    # Create output
    output_path = Path(tempfile.mkdtemp()) / "output.txt"
    with open(output_path, 'w') as f:
        f.write(content.upper())

    return str(output_path)

demo = gr.Interface(
    fn=process_file,
    inputs=gr.File(label="Upload text file"),
    outputs=gr.File(label="Download result"),
    title="Uppercase Converter"
)

demo.launch()
```

**Key lesson:** Return file path (string) → Gradio creates download button automatically.

### Step 5: Advanced Layout with gr.Blocks

```python
import gradio as gr

def process_text(input_text, make_upper, repeat_count):
    result = input_text
    if make_upper:
        result = result.upper()
    result = result * repeat_count
    return result

with gr.Blocks() as demo:
    gr.Markdown("# Advanced Text Processor")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Input")
            uppercase_checkbox = gr.Checkbox(label="Make uppercase", value=True)
            repeat_slider = gr.Slider(minimum=1, maximum=10, value=1, label="Repeat")
            submit_btn = gr.Button("Process")

        with gr.Column():
            text_output = gr.Textbox(label="Output")

    submit_btn.click(
        fn=process_text,
        inputs=[text_input, uppercase_checkbox, repeat_slider],
        outputs=text_output
    )

demo.launch()
```

**Progression:**
1. Simple function
2. Simple interface
3. File handling
4. Advanced layout

**You now understand 90% of Gradio!**

---

## Extending the Application

### Add Progress Bar for Long Operations

```python
import gradio as gr
import time

def slow_process(file, progress=gr.Progress()):
    progress(0, desc="Starting...")
    time.sleep(1)

    progress(0.5, desc="Processing PDF...")
    # ... PDF conversion ...
    time.sleep(2)

    progress(0.9, desc="Building PPTX...")
    # ... build presentation ...
    time.sleep(1)

    progress(1.0, desc="Complete!")
    return output_path

submit_btn.click(
    fn=slow_process,
    inputs=[files],
    outputs=output
)
```

**User sees:**
```
Processing PDF... [████████░░] 50%
```

### Add Example Files

```python
with gr.Blocks() as app:
    # ...existing UI...

    gr.Examples(
        examples=[
            ["example1.pdf", "16:9 (Widescreen)", "Fit whole image", 150],
            ["example2.pdf", "4:3 (Standard)", "Crop to fill", 300],
        ],
        inputs=[files, slide_size, fit_mode, dpi],
    )
```

**Users can click examples to pre-fill form.**

### Add Authentication

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    auth=("admin", "secretpassword")  # Simple auth
)
```

**Production:** Use OAuth or existing auth system instead.

### Add Custom CSS

```python
with gr.Blocks(css=".my-button { background-color: blue; }") as app:
    submit_btn = gr.Button("Submit", elem_classes="my-button")
```

**Full custom themes:** Create custom `gr.themes.Base()` subclass.

### Add API Endpoint

```python
# Gradio automatically creates API at /api/predict
# Access programmatically:
import requests

response = requests.post(
    "http://localhost:7860/api/predict",
    json={"data": ["input_text"]}
)
```

**Use case:** Integrate Gradio app into other Python code.

---

## Summary: Key Takeaways

### What We Built

✅ **Drag-and-drop UI** for existing CLI tool
✅ **No rewriting** of core logic
✅ **Dockerized** for easy deployment
✅ **Secure** with resource limits and input validation
✅ **Fast development** (hours, not days)

### Core Gradio Patterns

1. **Function first, UI second:**
   - Write your logic as a Python function
   - Add Gradio UI wrapper
   - Don't mix business logic with UI code

2. **Input validation early:**
   - Check file sizes/counts first
   - Use `gr.Error()` for user-facing errors
   - Log detailed errors for debugging

3. **File handling:**
   - Uploaded files are paths (strings)
   - Return file paths for downloads
   - Clean up temporary files

4. **State management:**
   - Gradio functions are stateless
   - Use temp files for persistence
   - Clean up with atexit/scheduled jobs

5. **Docker + Gradio:**
   - `server_name="0.0.0.0"` required
   - tmpfs for temporary storage
   - Non-root user for security

### When to Use Gradio

**Perfect for:**
- Internal tools and dashboards
- ML model demos
- Data processing pipelines
- Prototypes and MVPs
- Wrapping existing CLIs

**Not ideal for:**
- Multi-page applications
- Complex user management
- High-traffic public services (use FastAPI + React)
- Real-time collaboration

### Next Steps

1. **Read the code:** Open `app.py` and trace through a request
2. **Modify it:** Change the DPI slider range, add new slide sizes
3. **Build your own:** Take a Python script you have and add Gradio
4. **Deploy it:** Docker Compose makes deployment trivial

### Resources

- [Gradio Documentation](https://gradio.app/docs)
- [Gradio GitHub Examples](https://github.com/gradio-app/gradio/tree/main/demo)
- [This project](../) - Working example you can study

---

**You now have a complete mental model of how Gradio works!** The best way to learn is to modify this code and see what breaks. Happy building! 🚀
