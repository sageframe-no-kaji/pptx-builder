# Contributing to PPTX Builder

Thank you for considering contributing to PPTX Builder! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version)
- Example files (if applicable)

### Suggesting Enhancements

Feature requests are welcome! Please:
- Check existing issues first to avoid duplicates
- Clearly describe the feature and its use case
- Explain why this would be useful to other users

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Test thoroughly** — ensure your changes work as expected
4. **Update documentation** — modify README.md if needed
5. **Follow the existing code style**:
   - Use descriptive variable names
   - Add docstrings to functions
   - Keep functions focused and single-purpose
   - Follow PEP 8 style guidelines
6. **Submit the PR** with a clear description of changes

### Code Style

- Use 4 spaces for indentation (no tabs)
- Follow PEP 8 naming conventions
- Add type hints where appropriate
- Keep lines under 100 characters when possible
- Use descriptive variable names (`image_path` not `ip`)

### Testing

Before submitting a PR, test with:
- Various image formats (PNG, JPG, HEIC, etc.)
- Different PDF files (single/multi-page)
- Different slide sizes
- Both fit and fill modes
- CLI and interactive modes

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/pptx-builder.git
cd pptx-builder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make changes and test
pptx-builder
```

## Questions?

Feel free to open an issue at https://github.com/sageframe-no-kaji/pptx-builder/issues for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
