"""
Builds the v1.1 logo files and profile pictures into the repository root.

logos/<mark>/wildcats-<mark>-<color>.{svg,pdf,png}
logos/teams/<team>/wildcats-team-<team>-<layout>-<color>.{svg,pdf,png}
logos/institutional/ninetysix-hs-<layout>-<color>.{svg,pdf,png}
social/profile/...png      1080 x 1080 profile pictures
Run:  python kit.py
"""
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import brand as BR  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLORS = {"maroon": "#5E1A1D", "cream": "#F5EAD5", "black": "#000000", "white": "#FFFFFF"}
GRAD_TOP, GRAD_BOTTOM = "#973333", "#320B0B"

TEAMS = [
    # sports
    "Football", "Soccer", "Basketball", "Baseball", "Softball", "Volleyball", "Wrestling", "Tennis",
    "Golf", "Cheer", "Cross Country", "Track & Field",
    # clubs and groups
    "Marching Band", "Student Council", "Academic Team", "NHS",
]


def slug(name):
    return name.lower().replace("&", "and").replace(" ", "-")


def bounds(paths):
    b = None
    for p in paths:
        t = p.computeTightBounds()
        b = t if b is None else skia.Rect(min(b.left(), t.left()), min(b.top(), t.top()),
                                           max(b.right(), t.right()), max(b.bottom(), t.bottom()))
    return b


def draw(c, paths, color, cx, cy, width=None, height=None):
    b = bounds(paths)
    if width and height:
        s = min(width / b.width(), height / b.height())
    else:
        s = width / b.width() if width else height / b.height()
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.translate(-b.centerX(), -b.centerY())
    paint = skia.Paint(AntiAlias=True, Color=wm.hexc(color))
    for p in paths:
        c.drawPath(p, paint)
    c.restore()
    return s


def gradient(c, x, y, w, h):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y), skia.Point(0, y + h)], [wm.hexc(GRAD_TOP), wm.hexc(GRAD_BOTTOM)])))


def export_mark(paths, color, base, png_width=3000, pdf_width_in=6.0):
    """SVG (exact), PDF (vector), PNG (transparent) for one mark in one color."""
    wm.save_svg([(p, color) for p in paths], base + ".svg", pad=0)
    b = bounds(paths)
    # PNG with 3% padding
    pad = 0.03
    inner = png_width * (1 - 2 * pad)
    s = inner / b.width()
    H = int(round(b.height() * s + 2 * pad * png_width))
    surf = skia.Surface(png_width, H)
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    draw(c, paths, color, png_width / 2, H / 2, width=inner)
    surf.makeImageSnapshot().save(base + ".png", skia.kPNG)
    # PDF: artboard = artwork bounds at a nominal width, vector
    Wpt = pdf_width_in * 72
    Hpt = Wpt * b.height() / b.width()
    stream = skia.FILEWStream(base + ".pdf")
    with skia.PDF.MakeDocument(stream) as doc:
        with doc.page(Wpt, Hpt) as c:
            draw(c, paths, color, Wpt / 2, Hpt / 2, width=Wpt)
    stream.flush()
    del stream


def profile(paths, fg, bg, out, frac=0.56, size=1080, grad=False):
    surf = skia.Surface(size, size)
    c = surf.getCanvas()
    if grad:
        gradient(c, 0, 0, size, size)
    else:
        c.clear(wm.hexc(bg))
    draw(c, paths, fg, size / 2, size / 2, width=size * frac, height=size * frac)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def build():
    os.makedirs(ROOT, exist_ok=True)
    # core marks
    for key, fn in BR.MARKS.items():
        paths = BR.as_paths(fn())
        d = os.path.join(ROOT, "logos", key)
        os.makedirs(d, exist_ok=True)
        for cname, hx in COLORS.items():
            export_mark(paths, hx, os.path.join(d, f"wildcats-{key}-{cname}"),
                        png_width=2000 if key == "icon" else 3000, pdf_width_in=2.0 if key == "icon" else 6.0)
        print("logos", key)
    # institutional
    d = os.path.join(ROOT, "logos", "institutional")
    os.makedirs(d, exist_ok=True)
    for layout in ("line", "stacked"):
        paths = BR.as_paths(BR.institutional(layout))
        for cname, hx in COLORS.items():
            export_mark(paths, hx, os.path.join(d, f"ninetysix-hs-{layout}-{cname}"),
                        pdf_width_in=6.0 if layout == "line" else 3.0)
    print("logos institutional")
    # teams
    for name in TEAMS:
        lines, ok, note = BR.team_lines(name)
        assert ok, f"{name}: {note}"
        d = os.path.join(ROOT, "logos", "teams", slug(name))
        os.makedirs(d, exist_ok=True)
        for layout, fn in (("horizontal", BR.team), ("square", BR.team_square)):
            paths = BR.as_paths(fn(lines))
            for cname, hx in COLORS.items():
                export_mark(paths, hx, os.path.join(d, f"wildcats-team-{slug(name)}-{layout}-{cname}"),
                            pdf_width_in=6.0 if layout == "horizontal" else 3.0)
    print("logos teams")
    # social profile pictures
    d = os.path.join(ROOT, "social", "profile")
    os.makedirs(os.path.join(d, "teams"), exist_ok=True)
    ic = BR.as_paths(BR.icon())
    profile(ic, COLORS["cream"], COLORS["maroon"], os.path.join(d, "wildcats-profile-icon-cream-on-maroon.png"))
    profile(ic, COLORS["cream"], None, os.path.join(d, "wildcats-profile-icon-cream-on-gradient.png"), grad=True)
    profile(ic, COLORS["maroon"], COLORS["cream"], os.path.join(d, "wildcats-profile-icon-maroon-on-cream.png"))
    profile(ic, COLORS["white"], COLORS["black"], os.path.join(d, "wildcats-profile-icon-white-on-black.png"))
    profile(BR.as_paths(BR.team_square(["WILDCATS"])), COLORS["cream"], COLORS["maroon"],
            os.path.join(d, "wildcats-profile-wildcats-cream-on-maroon.png"), frac=0.70)
    for name in TEAMS:
        profile(BR.as_paths(BR.team_square(name)), COLORS["cream"], COLORS["maroon"],
                os.path.join(d, "teams", f"wildcats-profile-{slug(name)}.png"), frac=0.70)
    print("social profiles")
    # README header: the team system with BRAND as the name
    d = os.path.join(ROOT, ".github")
    os.makedirs(d, exist_ok=True)
    for cname in ("maroon", "cream"):
        wm.save_svg([(p, COLORS[cname]) for p in BR.as_paths(BR.team("BRAND"))],
                    os.path.join(d, f"readme-header-96-brand-{cname}.svg"), pad=0)
    print("readme header")


if __name__ == "__main__":
    build()
