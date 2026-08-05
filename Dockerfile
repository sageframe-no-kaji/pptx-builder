FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only pyproject.toml first for dependency caching
COPY pyproject.toml .

# Create minimal package structure for dependency installation
RUN mkdir -p src/pptx_builder && \
    touch src/pptx_builder/__init__.py

# Install dependencies (this layer will be cached)
RUN pip install --no-cache-dir .[web]

# Now copy actual source code
COPY src/ src/

# Reinstall package (fast, dependencies already cached).
#
# Clear the build cache and egg-info left by the dependency-priming install
# above first. That install ran against an empty stub __init__.py, and
# setuptools' build_py only re-copies a source file when its mtime is newer
# than the cached copy in build/lib. COPY preserves source mtimes, so a source
# tree older than the image layer silently ships the stub — the package
# installs, reports the right version to pip, and exposes nothing.
RUN rm -rf build src/*.egg-info && \
    pip install --no-cache-dir --force-reinstall --no-deps .[web] && \
    python -c "import pptx_builder; assert pptx_builder.__version__, 'empty __init__ shipped'"

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /tmp && \
    chown -R appuser:appuser /app /tmp

# Switch to non-root user
USER appuser

# Set Python unbuffered mode for logging
ENV PYTHONUNBUFFERED=1

# Expose Gradio port
EXPOSE 7860

# Run the Gradio web interface
CMD ["python", "-u", "-m", "pptx_builder.web"]
