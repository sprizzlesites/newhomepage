# Sprizzle! font pack

A bubble-graffiti display face built to match the **Sprizzle!** wordmark: glossy pink
body, dark contour, thick cyan edge with a shaded underside, drop shadow, real tapered
drips, and letters that tilt and ride the baseline the way hand lettering does.

**A–Z, a–z, 0–9 and punctuation. Bounce and drips are baked into the font.**

Drop the folder in any repo, link one stylesheet, add one class. No build step,
no CDN, no JavaScript required.

---

## What's in the box

```
sprizzle-font/
├── sprizzle.css                       ← the only file you link
├── index.html                         ← specimen + live tester (open it locally)
├── build-font.py                      ← the generator, if you want to re-cut it
├── fonts/
│   ├── Sprizzle-Regular.woff2         ← 15 KB, the letter bodies
│   ├── Sprizzle-Edge.woff2            ← 24 KB, the cyan edge + drips
│   ├── SprizzleColor-Regular.woff2    ← 101 KB, all six layers baked in
│   └── *.ttf                          ← same three, for desktop apps
└── OFL.txt                            ← licence, ship this with the fonts
```

## Quick start

```html
<link rel="stylesheet" href="sprizzle-font/sprizzle.css">

<h1 class="sprizzle" data-text="Sprizzle!">Sprizzle!</h1>
```

`sprizzle.css` points at `fonts/` with relative paths, so keep the folder intact.
If you split it up, edit the two `@font-face` blocks at the top.

---

## Three ways to render it

### 1. `.sprizzle` — the full look *(recommended)*

Two fonts stacked: `Sprizzle Edge` paints the cyan edge and drips as filled shapes,
`Sprizzle` paints the glossy body on top. They share one set of metrics, so they line
up exactly at any size. The second layer is drawn by a
pseudo-element, which needs a copy of the text in `data-text`:

```html
<h1 class="sprizzle" data-text="Sprizzle!">Sprizzle!</h1>
```

Don't want to write it twice? One line at the end of the page fills it in:

```html
<script>
  document.querySelectorAll(".sprizzle").forEach(function (el) {
    el.dataset.text = el.textContent;
  });
</script>
```

### 2. `.sprizzle-simple` — one element, one outline

No duplication, no pseudo-element. You lose the thin dark line between the body
and the edge.

```html
<h1 class="sprizzle-simple">Sprizzle!</h1>
```

### 3. `.sprizzle-baked` — colour inside the font file

`SprizzleColor-Regular.woff2` is a COLR/CPAL colour font: all six layers — cyan edge,
shaded underside, dark contour, body, inner shade, top gloss — live in the font itself. Nothing to duplicate, nothing to stroke — but the palette is
fixed and the file is bigger.

```html
<h1 class="sprizzle-baked">Sprizzle!</h1>
```

### Modifiers

Stack these on any of the three modes:

| Class | What it does |
| --- | --- |
| `sprizzle-drips` | tapered drips hung off each letter's real bottom edge (`ss01`) |
| `sprizzle-tilt` | rotates the whole wordmark 2.5° |
| `sprizzle-steady` | turns the bounce off |

```html
<h1 class="sprizzle sprizzle-drips sprizzle-tilt" data-text="Sprizzle!">Sprizzle!</h1>
```

## Bounce and drips

Both are OpenType features, not CSS tricks. Every letter is cut three ways — upright, tilted up, tilted down — and the font's
`calt` (contextual alternates) feature cycles through them as you type. It's on by
default in every browser, needs no markup, and is deterministic: the same word
always renders the same way. Spaces and punctuation reset the cycle, so each word
starts upright.

and each letter carries a second cut with drips, on `ss01`. Because the drip lives in
the edge font only, it renders as solid cyan with no pink bleeding into it — a stroke
could never do that, since a stroked drip can't be thinner than the stroke.

```css
font-feature-settings: "calt" 0;              /* no bounce */
font-feature-settings: "calt" 1, "ss01" 1;    /* bounce + drips */
```

---

## Changing the colours

Modes 1 and 2 read five custom properties. Override them on `:root` for the whole
site, or on one element:

| Property | Default | What it does |
| --- | --- | --- |
| `--sprizzle-fill` | `#fb0055` | letter body, mid tone |
| `--sprizzle-fill-top` | `#ff7ba5` | gloss at the top |
| `--sprizzle-fill-bottom` | `#c2003f` | shade at the bottom |
| `--sprizzle-shadow` | `#2b0048` | dark contour |
| `--sprizzle-edge` | `#12b0f0` | cyan edge, and the drips |
| `--sprizzle-inner-w` | `0.058em` | contour weight |
| `--sprizzle-edge-w` | `0.148em` | edge weight, mode 2 only |
| `--sprizzle-drop` | `0 0.05em 0 rgba(10,0,25,.85)` | drop shadow |

```css
.hero-title {
  --sprizzle-fill: #ffd400;
  --sprizzle-fill-top: #fdffb0;
  --sprizzle-fill-bottom: #d18f00;
  --sprizzle-shadow: #1b3b00;
  --sprizzle-edge: #7bff2e;
  --sprizzle-edge-w: 0.16em;
}
```

Weights are in `em`, so the edge stays proportional at every size. The defaults
are tuned to match the original wordmark — the font's side bearings are spaced
for a `0.136em` edge, so going much past `0.18em` will start to merge neighbouring
letters.

Mode 3 ignores these; its colours are inside the font file.

## Notes

- Looks best above about 24px. It's a display face, not body copy.
- No kerning table — the spacing is built into the glyph metrics. The layout
  features are `calt` (bounce) and `ss01` (drips).
- Both fonts also work as plain desktop fonts. Install the `.ttf` and pick
  "Sprizzle" or "Sprizzle Color" in any app.
- GitHub Pages serves `.woff2` with the right MIME type out of the box.

## Browser support

| | Modes 1 & 2 | Mode 3 (baked colour) |
| --- | --- | --- |
| Chrome / Edge | yes | yes |
| Firefox | yes | yes |
| Safari (macOS) | yes | yes |
| Safari (iOS) | yes | falls back to flat pink on some versions |

COLRv0 colour fonts are supported across the major desktop browsers, but iOS
Safari has been reported to drop support in newer versions — the text stays
perfectly readable, it just renders in one colour. If you need the layered look
everywhere, use mode 1 or 2.

## Licence

Outlines are derived from **Kavoon** by Sorkin Type Co, licensed under the
SIL Open Font License 1.1 with Reserved Font Name "Kavoon". This pack is a
derivative work, renamed as the licence requires, and is released under the same
licence. Keep `OFL.txt` next to the font files when you redistribute.

The edge expansion, drips, layering, spacing, palette, bounce alternates, colour
tables and CSS in this pack are new work
and are covered by the same OFL terms.
