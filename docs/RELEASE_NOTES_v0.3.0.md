# PPTX Builder v0.3.0

Output encoding is now configurable, and the defaults have changed.

---

## Breaking change: default output is smaller and lossy

Through v0.2.1 every page was encoded as lossless PNG at 300 DPI. That was not
configurable — the encoder was a literal in the conversion path, unreachable
from the CLI, the interactive prompts, and the web UI alike. A 43-page deck came
out at roughly 83 MB.

The default is now **JPEG at quality 85, 200 DPI**. The same deck is roughly
14 MB.

**If you need the previous behavior**, either is enough:

```bash
pptx-builder -i deck.pdf --format png --dpi 300   # per run
export PPTX_FORMAT=png                            # permanently
```

Nothing about slide sizing, placement, or fit/fill has changed, and output
remains compatible with PowerPoint, LibreOffice, and Google Slides.

---

## New

**`--format {jpeg,png}`** — encoder for rasterized PDF pages. `jpg` is accepted
as an alias.

**`--quality 1-100`** — JPEG quality. Ignored when the format is PNG, so
scripted callers may pass it unconditionally. Values outside the range are
rejected rather than silently clamped.

**Interactive prompt** — the guided flow now asks for encoding, and asks for
quality only when JPEG is selected.

**Web UI** — a page-encoding radio and a JPEG quality slider. The slider hides
itself under PNG rather than sitting there doing nothing.

**Environment variables** — `PPTX_FORMAT`, `PPTX_QUALITY`, and `PPTX_DPI` set
the fall-through for both the CLI and the web UI. `PPTX_MAX_QUALITY` caps what a
web visitor may select, alongside the existing `PPTX_MAX_*` ceilings.

Precedence, lowest to highest: built-in default → environment variable →
explicit flag or widget. A malformed environment value is ignored with a warning
rather than failing the run.

---

## Scope

Encoding applies to **PDF input only**. Image folders are embedded unchanged, in
whatever format you supply — a folder of PNGs still produces PNG slides.

## On choosing an encoder

JPEG is smaller on photographic and gradient-heavy slides, which is what most
presentation decks are. It is not universally smaller: flat-colour diagrams,
screenshots, and hard-edged graphics can compress better under PNG, sometimes
substantially. If output size matters and your decks are graphical rather than
photographic, measure both.

---

## Verification

129 tests, 100% coverage. `black`, `flake8`, and `mypy` clean.
