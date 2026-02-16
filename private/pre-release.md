# Agent Task Specification — `pptx-builder` Release & Distribution Hardening (CLI-first, Web-secondary)

## Mission
Transform the current repo into a **clean, community-standard open-source Python tool** that is:
- **CLI-first** (primary interface and credibility anchor)
- **Web-secondary** (Gradio wrapper maintained but not the center)
- **Packaged for PyPI** with modern standards
- **Released on GitHub** with tags + release notes
- **CI-validated** on every push
- **Neutral utility** with **subtle authorship** (credible OSS posture)
- **No feature creep** and **no behavior changes** beyond small compatibility/polish fixes described below

You will execute the tasks below **exactly**, in the order given, with **no scope expansion**.

---

## Ground Rules (Non-Negotiable)
1. **NO new features.** Only packaging, polish, and minor compatibility fixes explicitly listed.
2. **NO behavior changes** to core logic beyond:
   - replacing debug prints with logging (same informational content, gated)
   - cross-platform temp directory fix (remove hardcoded `/tmp`)
   - cleaning repo artifacts
3. **Keep `make_ppt` core logic readable.** Do **not** refactor for refactor’s sake. The file may remain ~600 lines.
4. **CLI-first, Web-secondary**:
   - CLI is the primary entrypoint and should be installable via `pip`.
   - Gradio app remains available but is treated as an optional wrapper.
5. **Neutral branding**:
   - Remove prominent personal branding in the UI header.
   - Keep a subtle “Created by …” credit in footer and README “Author” section.

---

## Target Identity
- **Project (PyPI + repo):** `pptx-builder`
- **CLI command:** `pptx-builder`
- **Version:** `0.1.0` (first public release)
- **License:** MIT
- **Interfaces:**
  - Primary: CLI (`pptx-builder ...`)
  - Secondary: Gradio web UI (`python -m pptx_builder.web` or similar), Docker optional

---

## Acceptance Criteria (Definition of Done)
- Repo contains **no** committed `venv/`, `__pycache__/`, `*.pyc`, or zip artifacts.
- Project installs with:
  - `pip install pptx-builder`
  - `pptx-builder --help` works
- CI runs on push and passes (`pytest` at minimum).
- GitHub release `v0.1.0` exists with clear notes.
- PyPI package `pptx-builder` published and installable.
- README:
  - consistent repo name and URLs
  - CLI-first positioning + examples
  - web UI described as optional
  - “Why this exists” section
  - subtle author credit
- Logging replaces noisy debug prints; `--verbose` enables debug output.
- Web UI no longer hardcodes `/tmp` and remains functional.

---

## Phase 0 — Preconditions / Safety Checks
### 0.1 Ensure clean working tree
- Confirm no uncommitted changes before starting.
- Create a new branch:
  - `release/pptx-builder-0.1.0`

### 0.2 Confirm repository naming alignment
- The repo is currently named `image_2_ppt-dev` in the local tree and README references `pptx-builder`.
- You will unify everything to **`pptx-builder`**:
  - README clone URLs
  - Docker docs
  - Gradio footer links
  - Any doc references

If repo rename on GitHub is required, document steps in release notes and ensure internal references are updated.

---

## Phase 1 — Repo Hygiene (Credibility Baseline)
### 1.1 Remove environment artifacts from repo
Delete from version control and filesystem:
- `venv/`
- `__pycache__/`
- `*.pyc`
- `image_2_ppt-dev.zip` (and any other zip artifacts)

### 1.2 Add/Update `.gitignore`
Create or update `.gitignore` to include at minimum:
- `venv/`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `*.pyo`
- `*.egg-info/`
- `dist/`
- `build/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/` (if ever added)
- `.DS_Store`
- `.env`

### 1.3 Commit
Commit message:
- `chore: remove environment artifacts and add gitignore`

---

## Phase 2 — Structure for Packaging (src layout)
### 2.1 Create src layout
Move code into:

src/pptx_builder/

Proposed structure (minimal, no over-refactor):

src/pptx_builder/init.py
src/pptx_builder/core.py        # moved from make_ppt.py (or keep name make_ppt.py if preferred)
src/pptx_builder/cli.py         # thin wrapper that calls core.main()
src/pptx_builder/web.py         # Gradio app moved from app.py

Rules:
- Keep the core file mostly intact.
- If you rename `make_ppt.py` → `core.py`, keep function names stable.
- Keep `main()` in core and ensure CLI calls it.

### 2.2 Preserve backward compatibility for internal imports
- Update Gradio `from make_ppt import ...` imports to the new module path.
- Ensure tests import from the new module path.

### 2.3 Remove `__pycache__` and verify nothing reintroduced.

### 2.4 Commit
Commit message:
- `refactor: adopt src layout and package structure`

---

## Phase 3 — Modern Packaging (`pyproject.toml`) + Entrypoint
### 3.1 Add `pyproject.toml`
Create a modern packaging configuration (PEP 621) with:
- name: `pptx-builder`
- version: `0.1.0`
- requires-python: `>=3.8`
- license: MIT
- readme: `README.md`
- dependencies: from existing `requirements.txt` (and web deps from requirements-web if needed)
- entrypoint script:
  - `pptx-builder = pptx_builder.cli:main`

### 3.2 Dependency strategy
- Keep dependencies minimal and correct:
  - core deps in main `dependencies`
  - optional web deps under `[project.optional-dependencies]` (e.g., `web = ["gradio>=4"]`)
- If the project wants a single install that includes web, include gradio in base deps. Otherwise default to optional.
**Policy for this task:** CLI-first, so:
- Core install should not require Gradio.
- Web UI should be installable via `pip install pptx-builder[web]`.

### 3.3 Remove or reconcile legacy packaging
- If `setup.cfg` becomes redundant, remove it.
- Ensure only one source of packaging truth remains.

### 3.4 Validate editable install and entrypoint
Run:
- `pip install -e .`
- `pptx-builder --help`

### 3.5 Commit
Commit message:
- `feat: add pyproject packaging and console entrypoint`

---

## Phase 4 — Logging (Replace debug prints) + Verbose Flag
### 4.1 Replace noisy debug prints in PDF conversion
In core module:
- Replace `print("[DEBUG ...]")` with `logging`.
- Create module logger:
  - `logger = logging.getLogger(__name__)`

### 4.2 Add `--verbose` flag
In CLI parsing:
- Add `--verbose` to enable `logging.basicConfig(level=logging.DEBUG)` (or INFO, but DEBUG preferred given existing debug detail).
- Default logging level: WARNING.
- Keep user-facing status messages that are not debug (e.g., “Converting PDF → PPTX”) unless `--quiet` is set.

### 4.3 Ensure `--quiet` and `--verbose` interactions are sane
- If `--quiet`, suppress non-critical output.
- If both `--quiet` and `--verbose`, prefer quiet for user-facing prints but still allow logging at debug if required; document behavior in README.

### 4.4 Commit
Commit message:
- `refactor: replace debug prints with logging and add verbose flag`

---

## Phase 5 — Cross-Platform Temp Directory Fix (Web UI)
### 5.1 Remove hardcoded `/tmp` usage
In Gradio module:
Replace:
- `tempfile.mkdtemp(..., dir="/tmp")`
with:
- `tempfile.mkdtemp(prefix="pptx_builder_")`

### 5.2 Temp cleanup policy
- Keep existing cleanup behavior (atexit + cleanup old dirs).
- If cleanup_old_files scans `/tmp`, update it to use Python temp directory root:
  - `tempfile.gettempdir()`
and scan there.

### 5.3 Commit
Commit message:
- `fix: make temp directory handling cross-platform`

---

## Phase 6 — Docker Rationalization (Optional, but do it cleanly)
### 6.1 Make Docker install consistent with packaging
Update Dockerfile so it installs the package (not raw scripts), using one of:
- `pip install .[web]` (preferred)
or
- copy `pyproject.toml` and `src/` then install.

### 6.2 Dependency layering
- Avoid separate `pip install gradio...` layer if it can be included in extras.
- Keep poppler-utils install.

### 6.3 Commit
Commit message:
- `refactor: align Docker build with packaged install`

---

## Phase 7 — CI (GitHub Actions)
### 7.1 Add workflow
Create:
- `.github/workflows/test.yml`

Minimum:
- checkout
- setup python (3.11 and 3.8 matrix if feasible; at least 3.11)
- install dev deps (prefer `pip install -e .[dev]` if you add dev extras; otherwise requirements-dev)
- run `pytest`

### 7.2 Badges
Add CI badge to README (once workflow path is stable).

### 7.3 Commit
Commit message:
- `ci: add GitHub Actions test workflow`

---

## Phase 8 — README Hardening (CLI-first)
### 8.1 Fix naming inconsistencies
Ensure README references:
- `pptx-builder` everywhere
- correct GitHub repo URL (update all links)
- correct docker compose instructions (repo name consistent)

### 8.2 Add a sharp opening positioning sentence
At top, add:
> A local-first CLI (and optional Web UI) for converting PDFs and image folders into clean, DPI-controlled PowerPoint slides — no PowerPoint required.

### 8.3 Add “Why this exists”
Short, practical bullets:
- privacy vs online converters
- predictable raster pipeline vs fragile “editable” conversion
- power-tool behavior (no surprise auto-fit)

### 8.4 Installation sections
- Primary: `pip install pptx-builder`
- Web optional: `pip install "pptx-builder[web]"` or Docker
- System deps: poppler-utils

### 8.5 Usage sections
- CLI examples first
- Web UI second
- Docker optional third

### 8.6 Authorship (subtle)
- Add “Author” section near bottom:
  - “Created by Andrew Marcus (GitHub: sageframe-no-kaji)” (or equivalent)
- In Web UI:
  - Remove name from header.
  - Keep footer credit (subtle).

### 8.7 Commit
Commit message:
- `docs: polish README for CLI-first positioning and consistency`

---

## Phase 9 — Release Tagging + GitHub Release
### 9.1 Ensure version is `0.1.0` everywhere
- single source of truth in `pyproject.toml`

### 9.2 Create tag
- `v0.1.0`

### 9.3 Draft GitHub release notes
Include:
- CLI-first install + usage
- Optional web UI + docker
- DPI control, fit/fill, aspect ratio preservation
- No PowerPoint required
- Known limitations (poppler dependency, large PDFs slow at high DPI)

### 9.4 Publish release

---

## Phase 10 — Publish to PyPI (Immediate)
### 10.1 Build
Run:
- `python -m build`

Verify `dist/` contains:
- wheel
- sdist

### 10.2 Upload
Use `twine upload dist/*` to PyPI.

### 10.3 Verify install
In a clean venv:
- `pip install pptx-builder`
- `pptx-builder --help`
- Run a minimal smoke test on a PDF and a folder of images.

### 10.4 Post-publish cleanup
- Add PyPI badge to README.
- Update release notes with PyPI install command.

---

## Final Deliverables Checklist
- [ ] Repo clean (no venv, no pycache, no zips)
- [ ] src layout in place
- [ ] pyproject.toml present, setup.cfg removed or reconciled
- [ ] CLI command `pptx-builder` works after pip install
- [ ] Web UI available as optional extra and docker builds successfully
- [ ] Debug prints replaced by logging with `--verbose`
- [ ] Temp directory handling cross-platform
- [ ] GitHub Actions CI passing
- [ ] README consistent, CLI-first, includes “Why”
- [ ] GitHub Release `v0.1.0` published
- [ ] PyPI package published and verified install

---

## Execution Notes (Agent Operating Procedure)
- Work on branch `release/pptx-builder-0.1.0`.
- Make small commits per phase; do not bundle everything into one commit.
- After each phase, run:
  - `pytest`
  - `pip install -e .`
  - `pptx-builder --help`
- Do not introduce unrelated formatting churn.
- Do not refactor core logic beyond necessary module moves and import adjustments.

---

## Stop Condition
When all deliverables are complete and verified, open a PR titled:
- `Release: pptx-builder v0.1.0`

Include:
- Summary of changes by phase
- Test evidence
- PyPI publish confirmation
- Link to GitHub Release

END.
