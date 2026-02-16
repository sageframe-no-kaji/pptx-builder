"""
Tests for pptx_builder.core

Run with: pytest test_make_ppt.py
"""

import pytest
from pptx_builder.core import (
    list_images,
    detect_input_type,
    confirm_overwrite,
    emu_to_float_inches,
    build_presentation,
    ALLOWED_EXTS,
    SLIDE_SIZES,
)


class TestImageListing:
    """Test image file detection and listing"""

    def test_list_images_filters_correctly(self, tmp_path):
        """Should only return supported image formats"""
        # Create test files
        (tmp_path / "image.png").touch()
        (tmp_path / "photo.jpg").touch()
        (tmp_path / "document.txt").touch()  # Should be ignored
        (tmp_path / "data.json").touch()  # Should be ignored

        images = list_images(tmp_path)

        assert len(images) == 2
        assert all(img.suffix.lower() in ALLOWED_EXTS for img in images)

    def test_list_images_case_insensitive(self, tmp_path):
        """Should handle uppercase extensions"""
        (tmp_path / "IMAGE.PNG").touch()
        (tmp_path / "PHOTO.JPG").touch()

        images = list_images(tmp_path)

        assert len(images) == 2

    def test_list_images_sorted_alphabetically(self, tmp_path):
        """Should sort filenames case-insensitively"""
        (tmp_path / "zebra.png").touch()
        (tmp_path / "Apple.jpg").touch()
        (tmp_path / "banana.png").touch()

        images = list_images(tmp_path)

        names = [img.name.lower() for img in images]
        assert names == sorted(names)


class TestInputDetection:
    """Test input type detection (PDF vs folder vs unknown)"""

    def test_detect_pdf(self, tmp_path):
        """Should detect PDF files"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()

        assert detect_input_type(pdf_file) == "pdf"

    def test_detect_folder_with_images(self, tmp_path):
        """Should detect folder with images"""
        (tmp_path / "image.png").touch()

        assert detect_input_type(tmp_path) == "folder"

    def test_detect_empty_folder(self, tmp_path):
        """Should return unknown for empty folder"""
        assert detect_input_type(tmp_path) == "unknown"

    def test_detect_unknown_file(self, tmp_path):
        """Should return unknown for non-PDF files"""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        assert detect_input_type(txt_file) == "unknown"


class TestSlidePresets:
    """Test slide size presets"""

    def test_all_presets_valid(self):
        """All slide presets should have valid dimensions"""
        for key, (label, width, height) in SLIDE_SIZES.items():
            assert isinstance(width, (int, float))
            assert isinstance(height, (int, float))
            assert width > 0
            assert height > 0
            assert len(label) > 0

    def test_standard_sizes_included(self):
        """Common sizes should be available"""
        labels = [label for label, _, _ in SLIDE_SIZES.values()]

        assert any("16:9" in label for label in labels)
        assert any("4:3" in label for label in labels)
        assert any("Letter" in label for label in labels)
        assert any("A4" in label for label in labels)


class TestAllowedExtensions:
    """Test allowed file extensions"""

    def test_common_formats_supported(self):
        """Common image formats should be supported"""
        required = {".png", ".jpg", ".jpeg"}
        assert required.issubset(ALLOWED_EXTS)

    def test_heic_supported(self):
        """HEIC format should be supported"""
        assert ".heic" in ALLOWED_EXTS or ".heif" in ALLOWED_EXTS

    def test_extensions_lowercase(self):
        """All extensions should be lowercase for comparison"""
        assert all(ext.islower() for ext in ALLOWED_EXTS)


# Integration test (requires PIL)
class TestIntegration:
    """Integration tests requiring actual image processing"""

    @pytest.mark.integration
    def test_create_simple_presentation(self, tmp_path):
        """End-to-end test creating a simple presentation"""
        from PIL import Image

        # Create test image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(img_path)

        # Create presentation
        output = tmp_path / "output.pptx"
        build_presentation(
            images=[img_path],
            output_path=output,
            slide_width_in=10.0,
            slide_height_in=7.5,
            mode="fit",
        )

        assert output.exists()
        assert output.stat().st_size > 0

    @pytest.mark.integration
    def test_multiple_images_presentation(self, tmp_path):
        """Test creating presentation with multiple images"""
        from PIL import Image

        # Create multiple test images
        images = []
        for i, color in enumerate(["red", "green", "blue"]):
            img_path = tmp_path / f"image_{i}.png"
            img = Image.new("RGB", (100, 100), color=color)
            img.save(img_path)
            images.append(img_path)

        # Create presentation
        output = tmp_path / "multi.pptx"
        build_presentation(
            images=images,
            output_path=output,
            slide_width_in=10.0,
            slide_height_in=7.5,
            mode="fill",
        )

        assert output.exists()
        assert output.stat().st_size > 0

    @pytest.mark.integration
    def test_heic_format_supported(self, tmp_path):
        """Test that HEIC format is in allowed extensions"""
        # HEIC requires pillow-heif which might not be installed
        # Just test that it's in the allowed list
        assert ".heic" in ALLOWED_EXTS or ".heif" in ALLOWED_EXTS


class TestUtilities:
    """Test utility functions"""

    def test_emu_to_float_inches_conversion(self):
        """Should correctly convert EMU to inches"""
        # 914400 EMU = 1 inch
        assert abs(emu_to_float_inches(914400) - 1.0) < 0.001
        assert abs(emu_to_float_inches(1828800) - 2.0) < 0.001
        assert abs(emu_to_float_inches(0) - 0.0) < 0.001

    def test_confirm_overwrite_force_mode(self, tmp_path):
        """Force mode should always return True"""
        existing_file = tmp_path / "existing.pptx"
        existing_file.touch()

        assert confirm_overwrite(existing_file, force=True) is True

    def test_confirm_overwrite_quiet_mode(self, tmp_path):
        """Quiet mode with existing file should not prompt (returns True)"""
        existing_file = tmp_path / "existing.pptx"
        existing_file.touch()

        assert confirm_overwrite(existing_file, quiet=True) is True

    def test_confirm_overwrite_nonexistent_file(self, tmp_path):
        """Non-existent file should always return True"""
        nonexistent = tmp_path / "new_file.pptx"

        assert confirm_overwrite(nonexistent, quiet=True) is True
        assert confirm_overwrite(nonexistent, force=True) is True


class TestBuildPresentation:
    """Test presentation building functionality"""

    @pytest.mark.integration
    def test_build_presentation_fit_mode(self, tmp_path):
        """Test presentation building with fit mode"""
        from PIL import Image

        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (200, 100), color="blue")
        img.save(img_path)

        output = tmp_path / "fit_test.pptx"
        build_presentation(
            images=[img_path],
            output_path=output,
            slide_width_in=10.0,
            slide_height_in=7.5,
            mode="fit",
        )

        assert output.exists()
        # PPTX should have reasonable minimum size
        assert output.stat().st_size > 10000

    @pytest.mark.integration
    def test_build_presentation_fill_mode(self, tmp_path):
        """Test presentation building with fill mode"""
        from PIL import Image

        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (300, 200), color="green")
        img.save(img_path)

        output = tmp_path / "fill_test.pptx"
        build_presentation(
            images=[img_path],
            output_path=output,
            slide_width_in=10.0,
            slide_height_in=7.5,
            mode="fill",
        )

        assert output.exists()
        assert output.stat().st_size > 10000

    @pytest.mark.integration
    def test_build_presentation_custom_dimensions(self, tmp_path):
        """Test presentation with custom slide dimensions"""
        from PIL import Image

        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="yellow")
        img.save(img_path)

        # Test A4 size
        output = tmp_path / "a4_test.pptx"
        build_presentation(
            images=[img_path],
            output_path=output,
            slide_width_in=11.69,
            slide_height_in=8.27,
            mode="fit",
        )

        assert output.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
