# Sprizzle — scroll-scrubbed landing page

Single-file landing page (`index.html`) that scrubs a background video through
five service "zones" as you scroll. No build step, no dependencies — ready for
GitHub Pages as-is (serve the repo root; `.nojekyll` is included).

## Files

- `index.html` — everything: markup, styles, and the scrub engine.
- `assets/bg-desktop.mp4` / `assets/bg-mobile.mp4` — scrub-optimized re-encodes
  (a keyframe on every frame, so `currentTime` seeking is instant). These are
  what the page loads.
- `desktop video (1).mp4` / `mobile video.mp4` — the original uploads, kept
  untouched. Not referenced by the page; safe to delete if you want a leaner repo.

## Wiring the real project links

Search `index.html` for `TODO(spryte)` — five placeholder links, one per zone
(`data-oss="sprizzle-ide"`, `sprizzle-vsts`, `roxy-js`, `peachmint`,
`freaksploit`). Replace each `href="#todo-…"` with the real repo URL. A small
script guard swallows clicks only while an href still starts with `#`, so the
links go live the moment you paste real URLs.

## Tuning the zone timing

The scroll-to-video-time tables live near the top of the `<script>` block
(`SHARES` and `TIME_RANGES`, in seconds, per video). Adjust those if you ever
swap the footage.
