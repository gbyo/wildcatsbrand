"""
Builds the logo files and profile pictures into the repository root.

logos/<mark>/wildcats-<mark>-<color>.{svg,pdf,png}
logos/teams/<team>/wildcats-team-<team>-<layout>-<color>.{svg,pdf,png}
logos/institutional/ninetysix-hs-<layout>-<color>.{svg,pdf,png}
social/profile/...png      1080 x 1080 profile pictures (v1.2 avatar layouts)
Run:  python kit.py
"""
import os
import sys

import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import brand as BR  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLORS = {"maroon": "#5E1A1D", "cream": "#F5EAD5", "black": "#000000", "white": "#FFFFFF"}
GRAD_TOP, GRAD_BOTTOM = "#973333", "#320B0B"

TEAMS = [
    # athletics department, for anything that covers every sport
    "Athletics",
    # sports
    "Football", "Soccer", "Basketball", "Baseball", "Softball", "Volleyball", "Wrestling",
    "Golf", "Cheer", "Cross Country", "Track & Field",
    # clubs and groups
    "Band", "Marching Band", "Indoor Percussion", "Drama", "Student Council", "SGA", "Academic Team",
    "Beta Club", "NHS", "NEHS", "NTHS", "FCA", "FFA", "Fishing Team", "Shooting Club",
]

# Profile-picture labels for names of two or more words: the short form the
# team already goes by. One-word names label themselves. Names with no entry
# here get the full-name avatar layout instead. Don't invent abbreviations.
AVATAR_LABELS = {"Cross Country": "XC", "Track & Field": "TRACK", "Marching Band": "BAND"}

# Avatar layout, as fractions of the picture's width (see avatar()).
AVATAR = {
    "icon_reach": 0.80,      # 96 alone: box corners at 80% of the radius
    "box": 0.40,             # 96 + label: box height, centred at box_y
    "box_y": 0.385,
    "label_y": 0.735,        # label centre
    "label_cap": 0.19,       # largest label cap height, so short labels never outweigh the 96
    "label_min": 0.09,       # smallest label cap height (readable at 62 px, the story tray)
    "name_box": 0.22,        # full-name layout: box height and box-to-name gap
    "name_gap": 0.05,
    "reach": 0.86,           # label and name stay within 86% of the radius
}


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


def avatar_label(name):
    if name in AVATAR_LABELS:
        return AVATAR_LABELS[name]
    return name.upper() if len(name.split()) == 1 else None


_outline = {}


def _fit_circle(paths, cx, cy, r):
    """Largest scale at which paths, centred on (cx, cy), stay inside a
    circle of radius r around the centre of a unit-sized picture."""
    key = id(paths[0])
    if key not in _outline:
        pts = np.array([q for p in paths for cont, _ in wm.flatten(p, 2.0) for q in cont])
        b = bounds(paths)
        _outline[key] = (paths, pts - [b.centerX(), b.centerY()])
    rel = _outline[key][1]
    lo, hi = 0.0, 1.0
    while np.max(np.hypot(*(rel * hi + [cx - 0.5, cy - 0.5]).T)) <= r:
        hi *= 2
    for _ in range(40):
        mid = (lo + hi) / 2
        if np.max(np.hypot(*(rel * mid + [cx - 0.5, cy - 0.5]).T)) <= r:
            lo = mid
        else:
            hi = mid
    return lo


def _lines(lines):
    """Centred lines of WILDCATS lettering, sheared like the logos."""
    paths = []
    for k, ln in enumerate(lines):
        p = BR.name_line(ln)
        dy = -(len(lines) - 1 - k) * (BR.C + BR.SPEC["line_gap"] * BR.C)
        paths.append(BR.move(p, -BR.B(p).width() / 2, dy))
    return [BR.shear(wm.union(paths))]


def avatar(name, fg, bg, out, size=1080, grad=False):
    """Profile picture for a circular crop, built to be read at 32-180 px.
      name=None   the 96 alone, as large as the circle allows
      label       the 96 box large, the team's one-word label under it
      otherwise   the full team name under a smaller box"""
    A = AVATAR
    surf = skia.Surface(size, size)
    c = surf.getCanvas()
    if grad:
        gradient(c, 0, 0, size, size)
    else:
        c.clear(wm.hexc(bg))
    ic = BR.as_paths(BR.icon())
    ih = bounds(ic).height()
    if name is None:
        s = _fit_circle(ic, 0.5, 0.5, 0.5 * A["icon_reach"])
        draw(c, ic, fg, size / 2, size / 2, height=ih * s * size)
    elif avatar_label(name):
        word = _lines([avatar_label(name)])
        s = min(A["label_cap"] / BR.C, _fit_circle(word, 0.5, A["label_y"], 0.5 * A["reach"]))
        assert s * BR.C >= A["label_min"], f"{name}: label too long for a profile picture; add a short form " \
                                           "to AVATAR_LABELS"
        draw(c, ic, fg, size / 2, A["box_y"] * size, height=A["box"] * size)
        draw(c, word, fg, size / 2, A["label_y"] * size, height=bounds(word).height() * s * size)
    else:
        word = _lines(BR.team_lines(name)[0])
        wb = bounds(word)
        bh, gap = A["name_box"], A["name_gap"]
        s = 0.30 / BR.C
        while s > 0:                         # largest name that fits with the box stacked above it
            top = 0.5 - (bh + gap + wb.height() * s) / 2
            wy = top + bh + gap + wb.height() * s / 2
            if _fit_circle(word, 0.5, wy, 0.5 * A["reach"]) >= s and \
                    _fit_circle(ic, 0.5, top + bh / 2, 0.5 * A["reach"]) >= bh / ih:
                break
            s -= 0.002 / BR.C
        draw(c, ic, fg, size / 2, (top + bh / 2) * size, height=bh * size)
        draw(c, word, fg, size / 2, wy * size, height=wb.height() * s * size)
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
    avatar(None, COLORS["cream"], COLORS["maroon"], os.path.join(d, "wildcats-profile-icon-cream-on-maroon.png"))
    avatar(None, COLORS["cream"], None, os.path.join(d, "wildcats-profile-icon-cream-on-gradient.png"), grad=True)
    avatar(None, COLORS["maroon"], COLORS["cream"], os.path.join(d, "wildcats-profile-icon-maroon-on-cream.png"))
    avatar(None, COLORS["white"], COLORS["black"], os.path.join(d, "wildcats-profile-icon-white-on-black.png"))
    for name in TEAMS:
        avatar(name, COLORS["cream"], COLORS["maroon"], os.path.join(d, "teams", f"wildcats-profile-{slug(name)}.png"))
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
