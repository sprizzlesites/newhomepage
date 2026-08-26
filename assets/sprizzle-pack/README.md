# Sprizzle! font pack

Your specimen sheet, turned into three real fonts. Every glyph is vector, so it stays
crisp at any size — drips and splatter included, since those were part of the artwork.

**92 characters: A–Z, a–z, 1–0, and `!?@#$%^&*()-_=+[]{}\|;:'"<>,./~`**

---

## What's in the box

```
sprizzle-pack/
├── sprizzle.css                       ← the only file you link
├── index.html                         ← specimen + live tester
├── fonts/
│   ├── Sprizzle-Regular.woff2         ← 17 KB, the pink body
│   ├── SprizzleContour-Regular.woff2  ← 40 KB, the dark contour
│   ├── SprizzleEdge-Regular.woff2     ← 22 KB, the cyan edge
│   └── *.ttf                          ← same three, for desktop apps
├── sprizzle-sheet.png                 ← your sheet, white keyed out
├── glyphs/                            ← 92 transparent PNGs, one per character
├── build-1-trace.py                   ← key + cut + trace
└── build-2-fonts.py                   ← assemble the fonts
```

## Quick start

```html
<link rel="stylesheet" href="sprizzle-pack/sprizzle.css">

<h1 class="sprizzle" data-text="Sprizzle!">Sprizzle!</h1>
```

Keep the folder together — the stylesheet points at `fonts/` with relative paths.

### About `data-text`

Three fonts stack to make the wordmark: cyan edge underneath, dark contour, pink body on
top. The upper two are drawn by pseudo-elements, which need a copy of the text. Drop this
at the end of the page and forget about it:

```html
<script>
  document.querySelectorAll(".sprizzle").forEach(function (el) {
    el.dataset.text = el.textContent;
  });
</script>
```

Or use `sprizzle-solid` — one element, no duplication, body and contour only.

## Bounce

Every letter is cut five ways — upright plus four small rotations with a baseline nudge —
and the font's `calt` feature cycles through them as you type. No spans, no script, no
markup. It's deterministic, so a word always renders the same way, and spaces reset the
cycle so each word starts upright.

The variants are composite glyphs pointing at the base outline with a rotation matrix, so
they cost about 12 bytes each rather than a second copy of the artwork — the whole feature
adds ~3 KB per font. All three fonts rotate about the same centre, taken from the body
layer, or the layers would drift apart.

Turn it off with `sprizzle-steady`, or in plain CSS:

```css
font-feature-settings: "calt" 0;
```

## Colours

Sampled from your artwork. Override on `:root` or on a single element.

| Property | Default | Layer |
| --- | --- | --- |
| `--sprizzle-fill-top` | `#ff4f86` | body, gloss |
| `--sprizzle-fill` | `#f20361` | body, mid |
| `--sprizzle-fill-bottom` | `#a31a68` | body, shade |
| `--sprizzle-contour` | `#250658` | dark contour |
| `--sprizzle-edge-gloss` | `#e1e9ff` | edge, highlight |
| `--sprizzle-edge-top` | `#7fd0f5` | edge, upper |
| `--sprizzle-edge` | `#27a7e6` | edge, mid |
| `--sprizzle-edge-bottom` | `#3861b0` | edge, shade |
| `--sprizzle-drop` | `0 .03em .01em rgba(20,0,50,.4)` | drop shadow |

## How the sheet became a font

1. **Key.** The white background is removed by whiteness *and* saturation, so the light
   cyan highlights inside the letters survive while the counters — enclosed white, like
   the middle of an `A` — drop out with the rest of the background.
2. **Cut.** Glyph cells are found from the **pink bodies only**, because the cyan drips
   bridge the gaps between rows and would otherwise fuse them. Cell edges land midway
   between neighbours, so where two rims touch, the shared pixels split evenly.
3. **Trace.** Each cell is separated into three nested masks — pink, pink+dark,
   everything — cleaned of JPEG speckle, upscaled 4×, and vector-traced. That nesting is
   what makes the three fonts stack correctly.
4. **Metrics.** Baselines come from the pink bottoms of the non-descending glyphs in each
   row (drips are cyan, so they don't skew it). Cap height is normalised to 700/1000 em.
   Advances are set off the pink body, so the contour and edge overhang and merge with
   their neighbours the way the original does.

### Four things worth knowing

- **The bleed padding is load-bearing.** Glyph ink deliberately overhangs its advance
  box by up to 0.18em, which is what lets the edges merge between letters. Inside a word
  the neighbours cover that overhang; at the two ends of a run it spills outside the
  element. The gradient layers are painted with `background-clip: text`, and a background
  only covers the element's own box — so without `--sprizzle-bleed` the first and last
  letter get sliced flat. Padding grows the paint area and the negative margin cancels
  the layout shift. The dark contour never showed the bug because it uses a plain
  `color`, which isn't bound to the box.
- **`width: calc(100% - 2 * var(--sprizzle-bleed) + 1px)` on the pseudo-layers is also
  load-bearing.** At a plain `width: 100%` sub-pixel rounding makes the contour and body
  layers wrap a word earlier than the edge layer, splitting the wordmark across two
  lines. `max-content` fixes that case but then the layers refuse to wrap when the text
  legitimately should.

- **The apostrophe is derived.** Your sheet has `"` but no `'`, so `'` is cut from the
  left mark of the double quote.
- **Punctuation grouping is explicit.** In that row the two marks of `"` sit 6px apart
  while `}` and `\` sit 4px apart, so no gap threshold can separate those cases. The
  grouping is stated by hand in `build-1-trace.py` and asserted at build time — worth
  knowing if you ever re-cut the sheet with different spacing.

### If you re-cut it

The source is a 1024px JPEG, so glyphs arrive about 57px tall and the trace inherits some
compression softness. If you still have the artwork at higher resolution, re-export it and
rerun `build-1-trace.py` — the `BANDS` table at the top holds the row coordinates and the
character order, and everything else follows from it. A cleaner source would give
noticeably smoother curves.

## Licence

The artwork and letterforms are yours; nothing here is derived from a third-party font.
