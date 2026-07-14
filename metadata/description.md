# PPTX Builder — description

A local-first converter that turns PDFs and image folders into clean, DPI-controlled PowerPoint presentations without uploading a single file.

Online converters require you to upload your documents and then hand back fragile "editable" results that fall apart on anything complex. PPTX Builder refuses both: it processes entirely on your own machine and produces consistent raster output you control. It renders PDFs or organizes image folders into one-slide-per-page decks with configurable DPI, a range of aspect ratios and paper sizes, and fit-or-fill placement, handling batch and recursive folders. The primary interface is a pip-installable Python CLI, with an optional Gradio web UI and a Docker deployment carrying environment-variable limits for self-hosted instances. The problem it solves is small and common — private, predictable document-to-slides conversion — and it solves it without asking you to trust a server.

Python 3.8+ with python-pptx, Pillow, PyMuPDF, pdf2image, pillow-heif, and tqdm; optional Gradio web UI; Docker-deployable with poppler-utils. Published to PyPI as sageframe-pptx-builder (v0.2.1), with a live demo at pptx.sageframe.net.
