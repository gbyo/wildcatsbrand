"""
v1.0 (superseded by kit.py; output archived in archive/kit-v1.0).

Final Wildcats logo kit.

Marks (all single colour, built in lockups2.py):
  primary     L1-A  NINETY SIX between rules over WILDCATS
  horizontal  L3-A  96 tab + WILDCATS
  icon        L3-F  96 tab (profile photos, favicons, sleeves)
  stacked     L6-C  NINETY SIX / WILDCATS justified stack
  wordmark          WILDCATS on its own

Exports to wordmarks/final/:
  logos/<mark>/<mark>_<colour>.svg   vector, transparent
  logos/<mark>/<mark>_<colour>.png   high-res PNG, transparent
  profile/                           1080×1080 profile photos (circle-safe)
  tv/                                1920×1080 TV slides
  guidelines/                        logo guidelines (built by guide.py)
Run:  python final.py
"""
import os
import sys

import skia
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import lockups2 as L  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "v1.0-kit")

COLOURS = {
    "maroon": "#5E1A1D",
    "cream": "#F5EAD5",
    "black": "#000000",
    "white": "#FFFFFF",
}


def wordmark():
    w, _ = L.word_cond()
    return L.slant(w)


MARKS = [
    # key, label, builder, png width, use, min size
    ("primary", "Primary — Banner Rules", L.l1a, 3000,
     "TV slides, posters, signage, front of shirts", "240 px / 1.5 in wide"),
    ("horizontal", "Horizontal — Number Tab", L.l3a, 3000,
     "Narrow and small spaces, letterhead, web headers, merch", "110 px / 0.75 in wide"),
    ("icon", "Icon — 96 Tab", L.l3f, 2000,
     "Profile photos, favicons, sleeves, stickers", "32 px / 0.3 in wide"),
    ("stacked", "Stacked — Justified", L.l6c, 3000,
     "Square-ish spaces, social posts, back of shirts", "140 px / 1 in wide"),
    ("wordmark", "Wordmark — WILDCATS", wordmark, 3000,
     "When 96 already appears nearby, or space is very tight", "80 px / 0.6 in wide"),
]


def paths_of(fn):
    return L.as_paths(fn())


def bounds(paths):
    b = None
    for p in paths:
        t = p.computeTightBounds()
        b = t if b is None else skia.Rect(min(b.left(), t.left()), min(b.top(), t.top()),
                                           max(b.right(), t.right()), max(b.bottom(), t.bottom()))
    return b


def draw(canvas, paths, colour, cx, cy, width=None, height=None):
    b = bounds(paths)
    s = width / b.width() if width else height / b.height()
    if width and height:
        s = min(width / b.width(), height / b.height())
    canvas.save()
    canvas.translate(cx, cy)
    canvas.scale(s, s)
    canvas.translate(-b.centerX(), -b.centerY())
    paint = skia.Paint(AntiAlias=True, Color=wm.hexc(colour))
    for p in paths:
        canvas.drawPath(p, paint)
    canvas.restore()


def png_transparent(paths, colour, width, out, pad=0.03):
    b = bounds(paths)
    W = width
    inner = W * (1 - 2 * pad)
    s = inner / b.width()
    H = int(round(b.height() * s + 2 * pad * W))
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    draw(c, paths, colour, W / 2, H / 2, width=inner)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def gradient(c, W, H):
    wm.gradient_bg(c, W, H)


def profile(paths, fg, bg, out, grad=False, size=1080, frac=0.56):
    surf = skia.Surface(size, size)
    c = surf.getCanvas()
    if grad:
        gradient(c, size, size)
    else:
        c.clear(wm.hexc(bg))
    # sized to sit comfortably inside a circular crop
    draw(c, paths, fg, size / 2, size / 2, width=size * frac, height=size * frac)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def tv(paths, fg, out, frac=0.62):
    surf = skia.Surface(1920, 1080)
    c = surf.getCanvas()
    gradient(c, 1920, 1080)
    draw(c, paths, fg, 960, 540, width=1920 * frac, height=1080 * 0.6)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def to_pil(img):
    return Image.fromarray(img.convert(alphaType=skia.kUnpremul_AlphaType,
                                       colorType=skia.kRGBA_8888_ColorType).toarray()[..., :3])


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    for key, label, fn, pw, use, mins in MARKS:
        paths = paths_of(fn)
        d = os.path.join(ROOT, "logos", key)
        os.makedirs(d, exist_ok=True)
        for cname, hx in COLOURS.items():
            wm.save_svg([(p, hx) for p in paths], os.path.join(d, f"wildcats_{key}_{cname}.svg"), pad=0)
            png_transparent(paths, hx, pw, os.path.join(d, f"wildcats_{key}_{cname}.png"))
        print("logos", key)

    pd = os.path.join(ROOT, "profile")
    os.makedirs(pd, exist_ok=True)
    icon = paths_of(L.l3f)
    profile(icon, COLOURS["cream"], COLOURS["maroon"], os.path.join(pd, "profile_96_cream_on_maroon.png"))
    profile(icon, COLOURS["cream"], None, os.path.join(pd, "profile_96_cream_on_gradient.png"), grad=True)
    profile(icon, COLOURS["maroon"], COLOURS["cream"], os.path.join(pd, "profile_96_maroon_on_cream.png"))
    profile(icon, COLOURS["white"], COLOURS["black"], os.path.join(pd, "profile_96_white_on_black.png"))
    stacked = paths_of(L.l3d)
    profile(stacked, COLOURS["cream"], COLOURS["maroon"],
            os.path.join(pd, "profile_96_wildcats_cream_on_maroon.png"), frac=0.76)
    print("profile")

    td = os.path.join(ROOT, "tv")
    os.makedirs(td, exist_ok=True)
    tv(paths_of(L.l1a), COLOURS["cream"], os.path.join(td, "tv_primary.png"))
    tv(paths_of(L.l3a), COLOURS["cream"], os.path.join(td, "tv_horizontal.png"), frac=0.66)
    tv(paths_of(L.l6c), COLOURS["cream"], os.path.join(td, "tv_stacked.png"), frac=0.50)
    print("tv")

    # team and group logos: 96 box + team name, plus a profile picture each
    for key, lines in L.TEAMS:
        d = os.path.join(ROOT, "logos", "teams", key)
        os.makedirs(d, exist_ok=True)
        paths = L.as_paths(L.team_tab(lines))
        for cname, hx in COLOURS.items():
            wm.save_svg([(p, hx) for p in paths], os.path.join(d, f"96_{key}_{cname}.svg"), pad=0)
            png_transparent(paths, hx, 3000, os.path.join(d, f"96_{key}_{cname}.png"))
        profile(L.as_paths(L.team_stacked(lines)), COLOURS["cream"], COLOURS["maroon"],
                os.path.join(d, f"96_{key}_profile.png"), frac=0.70)
    print("teams")

    print("guidelines: run guide.py")
