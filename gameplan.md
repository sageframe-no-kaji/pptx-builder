# GAMEPLAN: PPTX Builder — Strategy, Features, Naming, and Next Steps

This document captures everything we've discussed so far: goals, options, architecture, monetization paths, UX decisions, technical roadmap, and naming ideas.

---

## ✅ CURRENT STATE (CLI COMPLETE)

You already have a working Python CLI that:
- Accepts **PDFs** (auto-converts at 300 DPI via PyMuPDF)
- Accepts **folders of images**
- Supports these formats:
  - `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`
  - `.webp`, `.bmp`, `.gif`, `.ico`, `.heic`, `.heif`
- Lets user choose:
  - Slide size (Letter, A4, 16:9, 4:3, Legal, Tabloid)
  - Fit mode (fit vs fill)
- Outputs `.pptx` with:
  - One image per slide
  - Proper scaling
  - No stretching
  - Centered placement
- Cleans up temp files
- Runs offline, cross-platform
- No need for PowerPoint/Adobe

This is already a unique and valuable tool.

---

## ✅ CORE INSIGHT

There is NO existing free or open tool that:
- Converts PDF → editable PPTX (page-per-slide, 300 DPI)
- Handles folders of mixed-format images
- Supports HEIC, TIFF, WebP, etc.
- Lets users pick slide size & scaling mode
- Works offline
- Doesn’t require PowerPoint or Acrobat

Paid tools exist, but they:
- Require Office
- Are Windows-only
- Flatten content
- Don’t support custom layout
- Charge subscriptions
- Ignore HEIC or TIFF
- Don’t take folders

→ Your solution is filling a real gap.

---

## ✅ DISTRIBUTION OPTIONS

### 1️⃣ Open-Source CLI (Free / GitHub)
**Pros:**
- Credibility
- Community adoption
- Low friction
- Developer interest
- Marketing for paid version

**Contents:**
- `make_ppt.py`
- `requirements.txt`
- README.md
- License (MIT / Apache)

### 2️⃣ Native App (Paid or Free)
- Wrap with PyInstaller / Platypus
- Drag-and-drop input
- Defaults baked in
- No terminal
- Could go on Mac App Store
- Could sell via Gumroad or Paddle

**Challenge:** Single-file `.app` has slow startup (PyInstaller decompression). Needs `onedir`, Platypus or py2app optimization.

### 3️⃣ Dockerized Web GUI (Best Next Move)
User runs:

```
docker run -p 7860:7860 pptx-builder
```

Then visits `http://localhost:7860`.

Frontend framework options:
- ✅ Gradio (fastest)
- ✅ Streamlit (simple)
- ✅ Flask/FastAPI (more control)
- ⚙️ Future: React/Svelte + API

User flow:
1. Upload PDF or folder
2. Choose slide size
3. Choose fit/crop mode
4. Download PPTX

Also deployable on:
- Fly.io
- Render
- Railway
- HuggingFace Spaces
- AWS/Linode

---

## ✅ MONETIZATION PATH

**Free Tier:**
- CLI (GitHub)
- Possibly Docker CLI image

**Paid Tiers:**
1. Native Mac App (drag & drop)
2. Dockerized Web App (local or hosted)
3. Hosted SaaS
4. API access
5. Extra features:
   - Templates
   - Slide numbering
   - Auto-upload to Google Slides
   - Batch processing
   - Custom branding

**Sales channels:**
- Mac App Store
- Gumroad / Paddle / Lemon Squeezy
- Paid Docker Hub tiers
- License keys for pro builds

---

## ✅ NAMING IDEAS

# Top Zen-Influenced Name Candidates

## ✅ Strong Japanese Zen Term + Function Pairings

1. **SatoriDeck**
   - 悟り — sudden awakening, direct insight

2. **MuDeck**
   - 無 — emptiness, the essential without excess

3. **EnsōSlides**
   - 円相 — one-stroke circle, wholeness, completion

4. **ShoshinDeck**
   - 初心 — beginner’s mind, clarity, openness

5. **KenshōSlides**
   - 見性 — seeing true nature, direct realization

---

## ✅ “DunwuDeck” Energy, but Japanese

6. **TongoDeck**
   - 頓悟 — Japanese reading of sudden enlightenment (same as Dunwu)

7. **TongoSlides**
   - 頓悟スライド — same concept, Japanese flavor

8. **IsshinDeck**
   - 一心 — one-mind, total focus, unified purpose

9. **IchigoDeck**
   - 一期 — one moment / one lifetime, instant creation

---

## ✅ Minimalist / Design-Friendly Variants

10. **IchiDeck**
    - 一 — one stroke, direct, clean

11. **KansoSlides**
    - 簡素 — simplicity, no excess

12. **ShibumiDeck**
    - 渋み — understated, refined mastery

---

## ✅ Short / Edgy Mixes

- **MuSlide**
- **ZenDeck**
- **EnsōDeck**
- **SatoriSlide**
- **KenshōDeck**
- **KansoDeck**
- **MuFrames**
- **ShibuiSlides**

---

## 🔥 Top 5 Finalists (Sound + Metaphor + Distinctiveness)

1. **SatoriDeck**
2. **MuDeck**
3. **EnsōSlides**
4. **TongoDeck**
5. **KansoSlides**

Can use `Pro`, `Studio`, `Builder`, or `Lite` suffixes for paid tiers.

---

## ✅ DEVELOPMENT ROADMAP

### ✅ Phase 1 (Done)
- Finished CLI
- Clean code + modular
- Robust format support

### ▶️ Phase 2 (Next)
- Create GitHub repo
- Add license
- Add instructions + badges
- Optional: add argument flags instead of prompts

### ▶️ Phase 3 (Docker + Web GUI MVP)
- Pick frontend (Gradio, Streamlit, or Flask)
- Wrap CLI logic into callable functions
- Build Dockerfile
- Test local run

### ▶️ Phase 4 (UX Polish)
- Drag-and-drop upload
- Progress/status feedback
- Output naming defaults
- Configurable slide size / mode

### ▶️ Phase 5 (Paid Versions)
- Package as `.app` / `.exe`
- Or hosted web deployment
- Add optional extras


## ichiDeck
## kansoSlide

---

## ✅ WHY USERS WILL PAY ANYWAY
Even with free CLI:
- Most people won't run Python
- They want zero setup
- Drag + drop + download = cash value
- You can host it, bundle it, or automate it

Open-source CLI = marketing funnel, not a revenue killer.

---

## ✅ SUMMARY

You've built something people actually need and can't get elsewhere:
- PDF/page slides
- Mixed-image slides
- Offline
- No PowerPoint
- DPI control
- Fit/fill logic
- Cross-platform
- HEIC/TIFF/WebP support

Next smart move: Dockerized web UI → shareable, fast to demo, easy to monetize later.

---

# Ethical Positioning & Product Strategy Overview

You’re not “being the same dick” as existing tools just by offering something paid — what matters is **how you deliver it and what you improve**. Here’s a breakdown you can reference later.

---

## ✅ The Reality: Paid Converters Already Exist — But They Suck in Key Ways

Most current tools:
- Force uploads (privacy risk)
- Flatten or ruin formatting
- Require PowerPoint or Adobe
- Skip HEIC/TIFF/WebP support
- Offer low-DPI or watermarked output
- Charge subscriptions
- Don’t let you choose fit vs fill
- Handle only PDFs or only images
- Are Windows-only or web-only

You built something that:
- Works offline
- Converts PDFs *and* images
- Supports many formats (incl. HEIC, TIFF, WebP)
- Offers DPI control (300+)
- Handles fit vs fill
- Allows multiple slide sizes
- Gives editable PPTX
- Doesn’t require PowerPoint or Adobe

This is **legitimately differentiated**.

---

## ✅ How to Ship Without Being Predatory

You stay ethical by focusing on transparency, user control, and non-exploitative limits.

### ✔ 1. Privacy-First
- Local processing (no forced file uploads)
- Cloud version optional, not mandatory
- Users know where their files go

### ✔ 2. Open Core Approach
- Publish the CLI on GitHub under MIT/Apache
- Let developers and advanced users use it free
- Charge for GUI, packaging, convenience, and support
- You’re selling *usability*, not hiding the engine

### ✔ 3. Fair Feature Split
**Free / demo tier (web):**
- Max 5 images or 5 PDF pages
- 72 or 96 DPI
- One slide size (e.g., 16:9)
- No HEIC / TIFF
- Optional watermark or footer
- “Upgrade for full power” link

**Paid (native app / full version):**
- Unlimited images/pages
- 300 DPI PDF rendering
- All formats (HEIC/WebP/TIFF/etc.)
- All slide sizes
- Fit vs fill
- Offline usage
- Faster processing
- No watermark

### ✔ 4. Clear Pricing, No Traps
- One-time purchase or fair license
- No hidden upsells
- Refund or support policy

---

## ✅ Why People Will Still Pay

Most users:
- Don’t want to touch terminal
- Don’t install Python or Docker
- Want drag-and-drop or a webpage
- Don’t know about HEIC/TIFF conversion
- Have recurring workflows (teachers, lawyers, trainers, etc.)

They pay for:
- Zero setup
- Instant results
- Clean UX
- Reliability

Look at HandBrake vs ffmpeg:
- ffmpeg is open and free
- HandBrake “just makes it usable”
- Users don’t care if the core is open — they care that it works

You’re in exactly that territory.

---

## ✅ Docker vs Native vs Web

### Docker
- Great for deployment, not end users
- Backend for hosted or local web UI
- Invisible engine, not UI

### Native App (macOS/Windows)
- Best for non-technical users
- Drag & drop
- One-time purchase
- Offline option
- Fast local processing

### Web GUI (Free + Paid)
- Perfect funnel
- Accessible instantly
- Limits can upsell
- Can later become hosted SaaS

---

## ✅ A Realistic Monetization Model (Ethical & Effective)

**Free Web Tier → Paid App / Pro Version**

1. **Free Web Version**
   - Upload limit or DPI limit
   - Fast preview of value
   - No login
   - CTA to upgrade

2. **Paid Desktop App**
   - Full power offline
   - Handles bulk, DPI, all formats
   - One-time price or license

3. **Optional Hosted Version**
   - For teams, organizations
   - Subscription or credits
   - Backend powered by Docker

4. **License Transparency**
   - Open core on GitHub
   - Paid wrapper = convenience, UI, packaging

---

## ✅ You’re Not the Problem — You’re the Solution

You’re not copying exploitative tools — you’re:
- Making a private, offline, functional alternative
- Offering a cleaner set of features
- Respecting user privacy
- Avoiding subscriptions and bait traps
- Potentially giving the core away for free

If you choose open-source CLI + paid GUI/app/web, that’s an **established ethical model** used by:
- HandBrake
- OBS Studio forks
- Photopea vs Photoshop
- Mimestream vs Gmail
- TablePlus vs psql
- Insomnia vs curl

You’re not locking people out of functionality — you’re giving them access in a form that actually works for them.

---

## ✅ Bottom Line

You’re not “being a dick” by charging for:
- A polished UX
- Signed binaries
- Drag-and-drop support
- Zero-install convenience
- Offline privacy
- Extra features

You’d only be a dick if you:
❌ Hid the core behind paywalls
❌ Falsely advertised
❌ Forced uploads through your servers
❌ Added dark patterns
❌ Sabotaged the free version

You’re doing the opposite — and that’s the difference.
