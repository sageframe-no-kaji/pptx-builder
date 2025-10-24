# PPTX Builder — Images & PDFs → PowerPoint (300 DPI)

A single-purpose command-line tool that takes **either** a folder of images **or** a PDF file, then builds a `.pptx` with one slide per page/image. No PowerPoint app is needed to create presentations — only to open the result.

---

## ✅ Features

### 🔹 Input Options
- **PDF file**
  → Automatically converted to PNGs at **300 DPI** (via PyMuPDF)
- **Folder of images**
  → Non-image files are ignored

### 🔹 Supported Image Formats
.png · .jpg · .jpeg · .tif · .tiff
.webp · .bmp · .gif · .ico · .heic · .heif
(Animated GIFs use only the first frame.)

### 🔹 Slide Size Presets
You can choose at runtime:
1. 16:9 (13.33" × 7.5")
2. 4:3 (10" × 7.5")
3. Letter (11" × 8.5")
4. A4 (11.69" × 8.27")
5. Legal (14" × 8.5")
6. Tabloid (17" × 11")

### 🔹 Image Placement Modes
Choose one per run:
1. **Fit whole image**
   - No cropping
   - No stretching
   - Letterboxing/pillarboxing if needed
2. **Crop to fill**
   - Full coverage
   - Proportional scaling
   - Edges may be trimmed

### 🔹 Output
- One slide per image or PDF page
- Images are centered and never stretched
- Sorted alphabetically (case-insensitive)
- Exports `.pptx` to your chosen location
- Temporary PNGs from PDF conversion are auto-deleted

---

## ✅ Requirements

Create and activate a virtual environment (recommended), then install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**requirements.txt**
```
python-pptx
Pillow
pymupdf
pillow-heif
```

---

## ✅ Usage

Run the script:

```
python3 make_ppt.py
```

You’ll be prompted for:
1. Path to a PDF or a folder with images
2. Output filename
3. Slide size
4. Placement mode (fit or fill)

When finished, you’ll see something like:

```
✅ Presentation saved to: /path/to/YourFile.pptx
```

---

## ✅ Example

```
python3 make_ppt.py
Enter a path to a PDF file or a folder of images: /Users/me/Desktop/images
Enter output filename (without extension) [slides]: MyDeck
Choose slide size:
  1) 16:9 ...
Enter number (1-6): 1
How should images be placed?
  1) Fit whole image ...
  2) Crop to fill ...
Enter 1 or 2: 1
✅ Presentation saved to: /Users/me/Desktop/images/MyDeck.pptx
```

---

## ✅ Notes
- PDFs are rasterized at 300 DPI using PyMuPDF
- HEIC/HEIF support provided by `pillow-heif`
- Non-image files in folders are silently ignored
- No stretching — images are always scaled proportionally
- Temporary PDF conversions are cleaned up automatically
- `Ctrl+C` exits cleanly

---

## ✅ Packaging (Optional)
Create a standalone binary (Mac/Linux/Windows) with:

```
pyinstaller --onefile make_ppt.py
```

Output will appear in the `dist/` folder.

---

## ✅ Summary
Use this script when you want fast, clean conversion of images or PDFs into PPTX slides — with correct sizing, scaling, and zero manual setup. Just run it, follow prompts, and you're done.
