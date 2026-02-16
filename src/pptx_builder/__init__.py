"""
pptx-builder - Convert PDFs and images to PowerPoint presentations
"""

__version__ = "0.1.0"

from .core import build_presentation, convert_pdf_to_images, list_images

__all__ = ["build_presentation", "convert_pdf_to_images", "list_images", "__version__"]
