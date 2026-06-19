# Design

Source of truth for visual decisions. Derived from the ATM brand system (atmarcus.net).

## Theme

Light. Ground (#f5f2ed) as the page background — warm paper, not white. A single dark (Ink) section used for the header to frame the tool. No dark-mode toggle; the surface is light by default and intentional about it.

## Color

### Core Palette

| Token | Value | Role |
|-------|-------|------|
| `--color-ink` | `#1a1a1a` | Headlines, primary text, wordmark |
| `--color-ink-light` | `#4a4a4a` | Body paragraphs, prose |
| `--color-ink-muted` | `#7a7a7a` | Labels, captions, metadata, nav |
| `--color-ground` | `#f5f2ed` | Page background |
| `--color-ground-warm` | `#ebe6dd` | Cards, hover states, secondary surfaces |
| `--color-white` | `#faf8f4` | Elevated surfaces (form panel) |
| `--color-accent` | `#c45a2d` | Terracotta — links, buttons, focus states. Only interactive color. |
| `--color-rule` | `#d0c9be` | Borders, dividers, separators |

### Dark Surface (header block only)

| Token | Value | Role |
|-------|-------|------|
| `--color-dark-bg` | `#1a1a1a` | Header background |
| `--color-dark-text` | `#c8c2b8` | Primary text on dark |
| `--color-dark-prose` | `#b0a99e` | Body/prose on dark |
| `--color-dark-muted` | `#888888` | Labels, metadata on dark |
| `--color-dark-rule` | `#333333` | Dividers on dark |

### Rules

- Never `#ffffff` or `#000000`. Closest: `#faf8f4` and `#1a1a1a`.
- Terracotta is the only interactive color. If it's terracotta, it's clickable.
- No gradient text, no gradient backgrounds, no glassmorphism.
- Extended accents (plum, ochre, steel, sage) are not used on this surface — no multi-category content.

## Typography

### Font Stack

```css
--font-display: 'DM Serif Display', Georgia, serif;
--font-body:    'IBM Plex Sans', -apple-system, sans-serif;
--font-mono:    'IBM Plex Mono', 'Courier New', monospace;
```

Loaded via Google Fonts: DM Serif Display (400, 400 italic), IBM Plex Sans (300, 400, 500, 600), IBM Plex Mono (400, 500).

### Scale

| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| App name / H1 | Display | `2rem` | 400 | Never bold — serif carries weight |
| Section heading / H2 | Display | `1.4rem` | 400 | — |
| Section label | Body | `0.8rem` | 600 | Uppercase, `0.12em` tracking, Ink Muted |
| Body prose | Body | `1.05rem` | 400 | Ink Light, line-height 1.7, max 640px |
| UI labels | Body | `0.9rem` | 500 | Ink |
| Tagline / italic | Display italic | `1rem` | 400 | Authorial voice |
| Tags / metadata | Mono | `0.72rem` | 400 | Lowercase, `0.04em` tracking, Ink Muted |
| CLI / code | Mono | `0.88rem` | 400 | — |
| CTA / nav | Mono | `0.85rem` | 500 | Terracotta |
| Footer | Mono | `0.72rem` | 400 | Ink Muted |

### Rules

- Display never bold.
- Body line-height: 1.7. Headline line-height: 1.15–1.25.
- Prose max-width: 640px.
- No underlines on links — terracotta color + hover-to-ink transition identifies them.
- `text-wrap: balance` on h1–h2.

## Spacing & Layout

```
--max-width:  960px;
--gutter:     clamp(1.5rem, 5vw, 3rem);
```

Page is centered at 960px. Header spans full width (dark band) with content constrained inside. Form panel is white (#faf8f4) surface on the ground background.

Sections breathe — minimum 2.5rem vertical padding between major blocks.

## Components

### Header

Dark section (Ink background). Left: app name in Display + tagline in Display italic, both Ground-colored. Right: CLI install hint — label in Mono (Dark Muted), code block in Mono on a slightly lighter dark surface.

### Form Panel

White (#faf8f4) surface, 1px Rule border, 2px radius. Left column: controls. Right column: output + brief explainer. Two-column at ≥720px, single column below.

### Button (primary)

Terracotta fill, white text (IBM Plex Sans 500), no border, 2px radius. Hover: Umber (#6b3a2a). No gradient, no box shadow + border combo.

### Input / Dropdown / Slider

1px Rule border, 2px radius, white fill. Focus: 2px solid Terracotta, no outer glow. No shadow.

### Radio / Checkbox

accent-color: Terracotta. Label: IBM Plex Sans 400, Ink Light. Selected label: Ink, weight 500.

### File Upload

Rule border, dashed, 2px radius. Ground Warm on hover. No gradient fill.

### Info Strip

Three-item row between header and form. Ground Warm background, 1px Rule border. Mono for labels, Body for descriptions. No cards, no shadows — flat row.

### CLI Code Block

Mono, 0.88rem. Dark surface background (#252525). Ground-colored text. 2px radius. No border.

### Footer

Centered, Mono 0.72rem, Ink Muted. One line: attribution + GitHub link in Terracotta.

### Links

Terracotta → Ink on hover, 0.2s ease. No underline.

## Motion

Minimal. Form inputs: no transition. Button: `background-color 0.2s ease` on hover. File dropzone: `background-color 0.15s ease` on hover/drag. No entrance animations, no stagger, no transforms. The tool's job is zero latency, not choreography.

```css
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
```

## Border Radius

2px maximum on all elements. Not bubbly — architectural.

## Z-index Scale

```
--z-dropdown:  100;
--z-sticky:    200;
--z-modal:     400;
--z-toast:     600;
--z-tooltip:   800;
```

## Absolute Bans (from ATM system)

- No side-stripe borders
- No gradient text
- No glassmorphism
- No gradient backgrounds
- No box-shadow + border combo on the same element
- No border-radius above 3px
