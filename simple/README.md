# make_ppt.py — Build a PPTX from a folder of images (PNG/JPG) with your chosen slide size and fit mode

This single-file Python CLI will:
- Prompt for an **image folder** (reads `.png`, `.jpg`, `.jpeg`)
- Prompt for an **output filename**
- Let you choose a **slide size** (16:9, 4:3, Letter, A4, Legal, Tabloid)
- Ask how to place images:
  1) **Fit whole image** (no cropping, no stretching; letterbox/pillarbox if needed)
  2) **Crop to fill** (no whitespace; proportional crop if aspect ratios differ)
- Create one **blank slide per image**, centered, ordered by filename

> Requires: `python-pptx` (and its dependency `Pillow`).
> Recommended: run inside a virtual environment.
> Example:
>     python3 -m venv venv
>     source venv/bin/activate
>     pip install python-pptx Pillow
>     python3 make_ppt.py

Or install with:
```
pip install -r requirements.txt
```

---

# Quick tips
# ----------
# • To include subfolders or additional formats, adjust ALLOWED_EXTS and list_images().
# • To change default background color (shown in 'fit' mode), set the slide background fill via python-pptx API.
# • To support natural sorting (e.g., 1, 2, 10), you can add a small natural sort key.
# • To package as a standalone app on macOS:
#       pip install pyinstaller
#       pyinstaller --onefile --windowed make_ppt.py
#   Then run the binary in dist/:  ./make_ppt
