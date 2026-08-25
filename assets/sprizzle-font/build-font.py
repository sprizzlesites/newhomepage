#!/usr/bin/env python3
"""Sprizzle! v3

Base outlines: Bagel Fat One (SIL OFL 1.1) — actual bubble letterforms.

Three fonts, all sharing one set of metrics so they stack pixel-perfectly:
  Sprizzle-Regular  letter bodies
  Sprizzle-Edge     the cyan edge as *filled* shapes, with real per-letter
                    drips on ss01 (a stroke can't make a drip thinner than
                    the stroke, so the edge is pre-expanded instead)
  SprizzleColor     all six layers baked into one COLR/CPAL font

Bounce comes from `calt`: three cut variants per glyph, cycled as you type.
"""
import math, os, random
import pathops
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib.scaleUpem import scale_upem

SRC = "base/Kavoon-Regular.ttf"

NAVY_W, BLUE_W = 30, 44
EDGE_OUT = NAVY_W + BLUE_W
SHADE_D, GLOSS_D, EDGE_D = 44, 36, 34
PAD = 58
BOUNCE = [(0.0, 0), (2.2, 24), (-2.2, -16)]

BLUE   = (0x12, 0xB0, 0xF0)
NAVY   = (0x2B, 0x00, 0x48)
PINK   = (0xFB, 0x00, 0x55)
SHADE  = (0x8E, 0x00, 0x3A)
GLOSS  = (0xFF, 0x8C, 0xB3)
EDGESH = (0x07, 0x7C, 0xB4)

CHARSET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
           " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
           "\u2018\u2019\u201c\u201d\u2013\u2014\u2026\u00b0\u00a3\u20ac\u00a9")
CYCLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?&@$"


def rgba(c):
    return (c[0] / 255, c[1] / 255, c[2] / 255, 1.0)


def to_path(gs, name):
    rec = DecomposingRecordingPen(gs)
    gs[name].draw(rec)
    p = pathops.Path()
    rec.replay(p.getPen())
    p.simplify(fix_winding=True, keep_starting_points=False)
    return p


def moved(p, dx, dy):
    return p.transform(1, 0, 0, 1, dx, dy)


def outset(src, w):
    ring = pathops.Path(); ring.addPath(src)
    ring.stroke(w * 2.0, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4.0)
    ring.convertConicsToQuads(0.05)
    out = pathops.Path(); pathops.union([ring, src], out.getPen())
    out.simplify(fix_winding=True, keep_starting_points=False)
    return out


def crescent(src, dy):
    out = pathops.Path()
    pathops.difference([src], [moved(src, 0, dy)], out.getPen())
    out.simplify(fix_winding=True, keep_starting_points=False)
    return out


def disc(cx, cy, r, n=24):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo((cx + r, cy))
    for i in range(1, n):
        a = 2 * math.pi * i / n
        pen.lineTo((cx + r * math.cos(a), cy + r * math.sin(a)))
    pen.closePath()
    return p


def add_drips(edge, name):
    """Hang 0-2 tapered drips off the real bottom edge of this glyph."""
    b = edge.bounds
    if not b:
        return edge
    x0, y0, x1, y1 = b
    if x1 - x0 < 180:
        return edge
    rnd = random.Random("sprizzle-" + name)
    n = rnd.choice([0, 0, 1, 1, 1, 2])
    if not n:
        return edge
    parts, used = [edge], []
    for _ in range(n):
        for _try in range(14):
            ax = rnd.uniform(x0 + 90, x1 - 90)
            if all(abs(ax - u) > 210 for u in used):
                break
        else:
            continue
        y = y0
        while y < y1 and not edge.contains((ax, y)):
            y += 5
        if y >= y1 - 60 or y > y0 + 110:      # drips only off the lowest edges
            continue
        used.append(ax)
        top = y + 46
        length = rnd.uniform(80, 190)
        bulb = rnd.uniform(27, 37)
        stem = rnd.uniform(17, 23)
        drift = rnd.uniform(-26, 26)
        steps = 16
        for i in range(steps + 1):
            t = i / steps
            parts.append(disc(ax + drift * t * t,
                              top - length * t,
                              stem + (bulb - stem) * (t ** 2.4)))
    out = pathops.Path()
    pathops.union(parts, out.getPen())
    out.simplify(fix_winding=True, keep_starting_points=False)
    return out


def to_glyph(p):
    try:
        p.convertConicsToQuads(0.05)
    except Exception:
        pass
    pen = TTGlyphPen(None)
    p.draw(Cu2QuPen(pen, 0.6))
    return pen.glyph()


def composite(ref, ang, dy, cx, cy):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    g = Glyph(); g.numberOfContours = -1
    c = GlyphComponent()
    c.glyphName = ref
    c.transform = [[ca, sa], [-sa, ca]]
    c.x = round(cx - (ca * cx - sa * cy))
    c.y = round(cy - (sa * cx + ca * cy) + dy)
    c.flags = 0x004
    g.components = [c]
    return g


def clone(ref):
    g = Glyph(); g.numberOfContours = -1
    c = GlyphComponent(); c.glyphName = ref; c.x = 0; c.y = 0; c.flags = 0x004
    g.components = [c]
    return g


def fix_metrics(f):
    """lsb in hmtx must match each outline's real xMin or the rasterizer
    shifts the glyph by the difference — which knocks the edge off-centre."""
    glyf = f["glyf"]
    for n in f.getGlyphOrder():
        g = glyf[n]
        g.recalcBounds(glyf)
        aw = f["hmtx"][n][0]
        f["hmtx"][n] = (aw, g.xMin if g.numberOfContours != 0 else 0)


def sync(f):
    f.setGlyphOrder(list(dict.fromkeys(f["glyf"].glyphOrder)))
    f["maxp"].numGlyphs = len(f.getGlyphOrder())


def base_font():
    f = TTFont(SRC)
    o = Options()
    o.layout_features = []
    o.name_IDs = ["*"]; o.name_legacy = True; o.name_languages = ["*"]
    o.notdef_outline = True; o.glyph_names = True
    o.drop_tables += ["DSIG"]
    s = Subsetter(options=o); s.populate(text=CHARSET); s.subset(f)
    if f["head"].unitsPerEm != 1000:
        scale_upem(f, 1000)
    return f


FEA_CALT = """
languagesystem DFLT dflt;
languagesystem latn dflt;
@C0 = [%s];
@C1 = [%s];
@C2 = [%s];
feature calt {
    sub @C0 @C0' by @C1;
    sub @C1 @C0' by @C2;
} calt;
"""

FEA_DRIP = """
languagesystem DFLT dflt;
languagesystem latn dflt;
@CLEAN = [%s];
@DRIP = [%s];
@C0 = [%s];
@C1 = [%s];
@C2 = [%s];
feature ss01 {
    sub @CLEAN by @DRIP;
} ss01;
feature calt {
    sub @C0 @C0' by @C1;
    sub @C1 @C0' by @C2;
} calt;
"""


# ---------------------------------------------------------------- geometry
src = base_font()
gs = src.getGlyphSet()
order = [n for n in src.getGlyphOrder()]
cmap = src.getBestCmap()
cyc = [cmap[ord(c)] for c in CYCLE if ord(c) in cmap]

body, edge, edrip, adv, ctr = {}, {}, {}, {}, {}
for n in order:
    p = to_path(gs, n)
    aw, lsb = src["hmtx"][n]
    dx = PAD + max(0, -lsb)
    p = moved(p, dx, 0)
    body[n] = p
    b = p.bounds
    right = math.ceil(b[2]) if b else 0
    adv[n] = max(aw + dx + PAD, right + PAD)
    ctr[n] = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) if b else (0, 0)
    if p.segments:
        e = outset(p, EDGE_OUT)
        edge[n] = e
        edrip[n] = add_drips(e, n)

live = [n for n in order if n in edge and n != ".notdef"]
GROW_UP = EDGE_OUT + 40
GROW_DN = EDGE_OUT + 300


def dress(f):
    for n in order:
        f["hmtx"][n] = (adv[n], f["hmtx"][n][1])
    h, o2 = f["hhea"], f["OS/2"]
    h.ascender += GROW_UP; h.descender -= GROW_DN
    o2.usWinAscent += GROW_UP; o2.usWinDescent += GROW_DN
    o2.sTypoAscender += GROW_UP; o2.sTypoDescender -= GROW_DN


def bounce(f, names, suffixes, tag=""):
    g, hm = f["glyf"], f["hmtx"]
    for n in names:
        cx, cy = ctr[n]
        for i, (ang, dy) in enumerate(BOUNCE):
            if i == 0:
                continue
            for suf in suffixes:
                s, d = n + tag + suf, f"{n}{tag}.b{i}{suf}"
                g[d] = composite(s, ang, dy, cx, cy)
                hm[d] = hm[n]


def calt_fea(f, names, extra=()):
    allc = list(names) + list(extra)
    addOpenTypeFeaturesFromString(f, FEA_CALT % (
        " ".join(allc),
        " ".join(n + ".b1" for n in allc),
        " ".join(n + ".b2" for n in allc)))


# ---------------------------------------------------------------- 1. bodies
f1 = base_font()
for n in order:
    f1["glyf"][n] = to_glyph(body[n])
dress(f1)
bounce(f1, live, [""])
sync(f1)
calt_fea(f1, cyc)
fix_metrics(f1)
f1.save("v3_body.ttf")

# ---------------------------------------------------------------- 2. edge
f2 = base_font()
for n in order:
    f2["glyf"][n] = to_glyph(edge[n]) if n in edge else to_glyph(body[n])
for n in live:
    f2["glyf"][n + ".d"] = to_glyph(edrip[n])
    f2["hmtx"][n + ".d"] = (adv[n], 0)
dress(f2)
for n in live:
    f2["hmtx"][n + ".d"] = (adv[n], f2["hmtx"][n + ".d"][1])
bounce(f2, live, [""])
bounce(f2, live, [""], tag=".d")
sync(f2)
drips = [n + ".d" for n in cyc]
addOpenTypeFeaturesFromString(f2, FEA_DRIP % (
    " ".join(cyc), " ".join(drips),
    " ".join(cyc + drips),
    " ".join(n + ".b1" for n in cyc + drips),
    " ".join(n + ".b2" for n in cyc + drips)))
fix_metrics(f2)
f2.save("v3_edge.ttf")

# ---------------------------------------------------------------- 3. colour
f3 = base_font()
g3, h3 = f3["glyf"], f3["hmtx"]
for n in order:
    g3[n] = to_glyph(body[n])
dress(f3)
for n in live:
    for suf, p in ((".blue", edge[n]),
                   (".bsh", crescent(edge[n], EDGE_D)),
                   (".navy", outset(body[n], NAVY_W)),
                   (".shade", crescent(body[n], SHADE_D)),
                   (".gloss", crescent(body[n], -GLOSS_D)),
                   (".dblue", edrip[n]),
                   (".dbsh", crescent(edrip[n], EDGE_D))):
        g3[n + suf] = to_glyph(p)
        h3[n + suf] = (adv[n], 0)
    g3[n + ".d"] = clone(n)
    h3[n + ".d"] = (adv[n], 0)

bounce(f3, live, ["", ".blue", ".bsh", ".navy", ".shade", ".gloss"])
bounce(f3, live, [""], tag=".d")   # .d reuses the clean inner layers
for n in live:
    for i in (1, 2):
        for suf in (".dblue", ".dbsh"):
            cx, cy = ctr[n]
            ang, dy = BOUNCE[i]
            g3[f"{n}.d.b{i}{suf}"] = composite(n + suf, ang, dy, cx, cy)
            h3[f"{n}.d.b{i}{suf}"] = (adv[n], 0)
sync(f3)

layers = {}
for n in live:
    for t in ("", ".b1", ".b2"):
        g = n + t
        layers[g] = [(g + ".blue", 0), (g + ".bsh", 5), (g + ".navy", 1),
                     (g, 2), (g + ".shade", 3), (g + ".gloss", 4)]
        d = n + ".d" + t
        layers[d] = [(n + t + ".dblue" if t == "" else f"{n}.d{t}.dblue", 0),
                     (n + t + ".dbsh" if t == "" else f"{n}.d{t}.dbsh", 5),
                     (g + ".navy", 1), (g, 2), (g + ".shade", 3), (g + ".gloss", 4)]

f3["CPAL"] = buildCPAL([[rgba(BLUE), rgba(NAVY), rgba(PINK),
                         rgba(SHADE), rgba(GLOSS), rgba(EDGESH)]])
f3["COLR"] = buildCOLR(layers, version=0)
addOpenTypeFeaturesFromString(f3, FEA_DRIP % (
    " ".join(cyc), " ".join(drips),
    " ".join(cyc + drips),
    " ".join(n + ".b1" for n in cyc + drips),
    " ".join(n + ".b2" for n in cyc + drips)))
fix_metrics(f3)
f3.save("v3_color.ttf")

for p in ("v3_body.ttf", "v3_edge.ttf", "v3_color.ttf"):
    t = TTFont(p); t.flavor = "woff2"; t.save(p.replace(".ttf", ".woff2"))
    print(p, len(t.getGlyphOrder()), "glyphs,",
          round(os.path.getsize(p.replace(".ttf", ".woff2")) / 1024, 1), "KB woff2")
