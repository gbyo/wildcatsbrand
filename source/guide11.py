"""
Ninety Six Wildcats Brand Guidelines v1.2: US Letter, print-ready PDF plus
200 dpi PNG pages. Built from brand.py (geometry), kit.py (assets),
templates.py and social.py (applications).
Run:  python guide11.py   -> guidelines/
"""
import math
import os
import sys

import skia
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import brand as BR  # noqa: E402
import kit as K  # noqa: E402
import guide as G  # noqa: E402
import templates as T  # noqa: E402
import social as S  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guidelines")
PAGES_DIR = os.path.join(OUT, "pages")
W, H, M = G.W, G.H, G.M
CW = W - 2 * M
MAROON, CREAM, INK, BODY, MUTED, TILE, LINE = G.MAROON, G.CREAM, G.INK, G.BODY, G.MUTED, G.TILE, G.LINE
SH = BR.SPEC["shear"]
DIM = "#B4413A"          # annotation color (guide only)
C = BR.C

H2 = G.Style(G.COND, 52, INK, 0.0)
SMALLB = G.Style(G.SAIRA, 25, INK, 0.0, wdth=100, wght=600)
NOTE = G.Style(G.SAIRA, 22, DIM, 0.0, wdth=100, wght=600)
TBL = G.Style(G.SAIRA, 25, BODY, 0.0, wdth=100, wght=400)
TBLB = G.Style(G.SAIRA, 25, INK, 0.0, wdth=100, wght=700)
N_PAGES = 19
VERSION = "1.2"


def frame(c, n):
    c.clear(wm.hexc("#FFFFFF"))
    G.text(c, f"Ninety Six Wildcats Brand Guidelines  ·  v{VERSION}", M, H - 80, G.FOOT)
    G.text(c, str(n), W - M, H - 80, G.FOOT, align="right")


def heading(c, title, intro=None, y=250):
    return G.heading(c, title, intro, y=y)


def bullets(c, items, x, y, w, st=G.DESC, gap=14):
    for it in items:
        G.text(c, "•", x, y, st)
        y = G.para(c, it, x + 34, y, w - 34, st, lh=1.4) + gap
    return y


def table(c, rows, x, y, cols, header=True, rh=58):
    """rows: list of lists of strings; cols: list of column x offsets."""
    for r, row in enumerate(rows):
        st = TBLB if (header and r == 0) else TBL
        for k, cell in enumerate(row):
            G.text(c, cell, x + cols[k], y + 38, st)
        y += rh
        G.hairline(c, x, y, x + CW, y)
    return y


class Placed:
    """A mark drawn at a known transform, so construction notes can be
    attached to points in the mark's upright (unsheared) coordinates."""

    def __init__(self, c, paths, x, y, width=None, height=None, color=MAROON):
        self.paths = BR.as_paths(paths)
        b = K.bounds(self.paths)
        self.s = width / b.width() if width else height / b.height()
        self.b, self.x, self.y = b, x, y
        c.save()
        c.translate(x, y)
        c.scale(self.s, self.s)
        c.translate(-b.left(), -b.top())
        paint = skia.Paint(AntiAlias=True, Color=wm.hexc(color))
        for p in self.paths:
            c.drawPath(p, paint)
        c.restore()
        self.w, self.h = b.width() * self.s, b.height() * self.s

    def pt(self, ux, uy):
        """Upright mark coords -> page coords (applies the shear)."""
        sx = ux - SH * uy
        return self.x + (sx - self.b.left()) * self.s, self.y + (uy - self.b.top()) * self.s


def dim_v(c, x, y0, y1, txt, side="left", color=DIM):
    p = skia.Paint(AntiAlias=True, Color=wm.hexc(color), StrokeWidth=2.5)
    c.drawLine(x, y0, x, y1, p)
    c.drawLine(x - 10, y0, x + 10, y0, p)
    c.drawLine(x - 10, y1, x + 10, y1, p)
    if side == "left":
        G.text(c, txt, x - 18, (y0 + y1) / 2 + 8, NOTE, align="right")
    else:
        G.text(c, txt, x + 18, (y0 + y1) / 2 + 8, NOTE)


def dim_h(c, x0, x1, y, txt, above=True, color=DIM):
    p = skia.Paint(AntiAlias=True, Color=wm.hexc(color), StrokeWidth=2.5)
    c.drawLine(x0, y, x1, y, p)
    c.drawLine(x0, y - 10, x0, y + 10, p)
    c.drawLine(x1, y - 10, x1, y + 10, p)
    G.text(c, txt, (x0 + x1) / 2, y - 18 if above else y + 34, NOTE, align="center")


def guide_line(c, x0, y0, x1, y1, color=DIM):
    c.drawLine(x0, y0, x1, y1, skia.Paint(AntiAlias=True, Color=wm.hexc(color, 150), StrokeWidth=2,
                                          PathEffect=skia.DashPathEffect.Make([10, 8], 0)))


def image(c, path, x, y, w=None, h=None, outline=False):
    im = Image.open(path).convert("RGB")
    if w and not h:
        h = w * im.height / im.width
    if h and not w:
        w = h * im.width / im.height
    im = im.resize((int(w), int(h)), Image.LANCZOS)
    sk = skia.Image.fromarray(__import__("numpy").dstack([__import__("numpy").asarray(im),
                                                          __import__("numpy").full((im.height, im.width), 255,
                                                                                   "uint8")]))
    c.drawImageRect(sk, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    if outline:
        G.outline(c, x, y, w, h, r=1)
    return w, h


TPL = T.OUT


def tpl(name, kind="example"):
    return os.path.join(TPL, name, f"wildcats-{name}-{kind}.png")


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def p_cover(c, n):
    K.gradient(c, 0, 0, W, H)
    K.draw(c, BR.as_paths(BR.primary()), CREAM, W / 2, 1000, width=1240)
    G.text(c, "Brand guidelines", M, H - 150, G.Style(G.SAIRA, 30, CREAM, 0.22, True, wdth=100, wght=700))
    G.text(c, f"Version {VERSION}", W - M, H - 150, G.Style(G.SAIRA, 30, CREAM, 0.16, True, wdth=100, wght=500),
           align="right", alpha=170)


def p_overview(c, n):
    frame(c, n)
    y = heading(c, "Brand Overview",
                "The Ninety Six Wildcats identity is a small set of logos built from one typeface family, "
                "one slant, and two colors. It's designed to work the same on a hallway TV, a phone, a "
                "shirt, and a printed page.") + 40
    G.rect(c, M, y, CW, 520, MAROON, 8)
    K.draw(c, BR.as_paths(BR.primary()), CREAM, M + CW * 0.36, y + 260, width=640)
    K.draw(c, BR.as_paths(BR.icon()), CREAM, M + CW * 0.84, y + 260, height=150)
    y += 600
    G.text(c, "Building blocks", M, y, H2)
    y += 40
    items = [("WILDCATS", "Saira Condensed Black, slanted, with a few custom adjustments."),
             ("NINETY SIX", "The town and school name, set smaller above WILDCATS."),
             ("The 96 box", "The school's number in a slanted box. Used as the icon and for team logos."),
             ("The slant", "Every logo and graphic panel leans at the same angle: 6.84 degrees."),
             ("Maroon and cream", "The two school colors. Black and white for one-color printing.")]
    for k, (a, b) in enumerate(items):
        G.text(c, a, M, y + 50, SMALLB)
        G.text(c, b, M + 330, y + 50, G.DESC)
        y += 70
        G.hairline(c, M, y + 10, W - M, y + 10)
    y += 110
    G.text(c, "Principles", M, y, H2)
    bullets(c, ["Use the supplied logo files. Don't retype or redraw the logos.",
                "One color per logo, with strong contrast against the background.",
                "Keep it simple: no mascots, paw prints, shields, outlines, shadows, or extra logos."],
            M, y + 70, CW)


def p_architecture(c, n):
    frame(c, n)
    y = heading(c, "Brand Architecture",
                "The school has two levels of identity. Use the Wildcats logos for anything about school "
                "spirit. Use the Ninety Six High School name for official and academic material.") + 40
    gap = 40
    tw = (CW - gap) / 2
    th = 420
    G.rect(c, M, y, tw, th, MAROON, 8)
    K.draw(c, BR.as_paths(BR.horizontal()), CREAM, M + tw / 2, y + th / 2, width=tw * 0.72)
    G.rect(c, M + tw + gap, y, tw, th, TILE, 8)
    K.draw(c, BR.as_paths(BR.institutional("stacked")), MAROON, M + tw + gap + tw / 2, y + th / 2,
           width=tw * 0.55)
    yy = y + th + 70
    G.text(c, "Wildcats identity", M, yy, G.NAME)
    bullets(c, ["Athletics and team graphics", "School spirit, events, and student activities",
                "School TVs and social media", "Apparel and merchandise", "Posters and flyers"],
            M, yy + 50, tw)
    G.text(c, "Ninety Six High School", M + tw + gap, yy, G.NAME)
    bullets(c, ["Official letters and notices", "Forms and administrative communication",
                "Academic materials", "Graduation programs and diplomas", "Formal correspondence"],
            M + tw + gap, yy + 50, tw)
    yy += 430
    G.text(c, "Rules", M, yy, H2)
    bullets(c, ["The Ninety Six High School mark is set upright in Saira Bold. It does not use the slant, the "
                "athletic lettering, or slant panels.",
                "Formal documents may include the 96 icon small, but never a WILDCATS logo.",
                "Don't place the two identities side by side as equals. Pick the one that fits the audience."],
            M, yy + 70, CW)


def p_primary(c, n):
    frame(c, n)
    y = heading(c, "Primary Marks", "Use one of these two logos whenever possible.") + 40
    G.rect(c, M, y, CW, 520, MAROON, 8)
    K.draw(c, BR.as_paths(BR.primary()), CREAM, W / 2, y + 270, width=940)
    G.caption(c, M, y + 590, CW, "Primary logo", "Use for TV slides, posters, signs, and the back of shirts.",
              "1.5 in (240 px)")
    y += 790
    G.rect(c, M, y, CW, 380, TILE, 8)
    K.draw(c, BR.as_paths(BR.horizontal()), MAROON, W / 2, y + 190, width=940)
    G.caption(c, M, y + 450, CW, "Horizontal logo",
              "Use when space is short or narrow, such as web headers, letterhead, and small merchandise.",
              "1 in (110 px)")


def p_secondary(c, n):
    frame(c, n)
    y = heading(c, "Secondary Marks") + 60
    gap = 40
    tw = (CW - gap) / 2
    th = 520
    for i, (name, fn, frac, use, mn) in enumerate([
            ("Stacked logo", BR.stacked, 0.72, "Use in square spaces, social media posts, and on the back of "
             "shirts. NINETY SIX is set in Saira Condensed Black, stretched to the width of WILDCATS.",
             "1 in (140 px)"),
            ("Icon", BR.icon, 0.42, "Use for profile pictures, website icons, sleeves, and stickers.",
             "0.3 in (32 px)")]):
        x = M + i * (tw + gap)
        G.rect(c, x, y, tw, th, MAROON, 8)
        K.draw(c, BR.as_paths(fn()), CREAM, x + tw / 2, y + th / 2, width=tw * frac, height=th * 0.56)
        G.caption(c, x, y + th + 64, tw - 20, name, use, mn)
    y += th + 360
    G.rect(c, M, y, CW, 360, TILE, 8)
    K.draw(c, BR.as_paths(BR.wordmark()), MAROON, W / 2, y + 180, width=800)
    G.caption(c, M, y + 430, CW, "Wordmark", "Use when 96 already appears nearby or space is very limited.",
              "0.8 in (80 px)")


def p_construction_primary(c, n):
    frame(c, n)
    y = heading(c, "Logo Construction: Primary",
                "All measurements are ratios of C, the cap height of WILDCATS, so the logo can be rebuilt at "
                "any size. Use the supplied files; this page is for reference and quality checks.") + 70
    G.rect(c, M, y, CW, 560, TILE, 8)
    P = Placed(c, BR.primary(), M + 230, y + 150, width=1000)
    w = BR.wildcats()
    x0, x1 = BR.cap_extents(w)
    lab = BR.fit_h(BR.label_ninety_six(), BR.SPEC["label_height"] * C)
    lab = BR.put(lab, cx=(x0 + x1) / 2, bottom=-C - BR.SPEC["label_gap"] * C)
    lb = lab.computeTightBounds()
    t = BR.SPEC["rail_weight"] * C
    g = BR.SPEC["rail_gap"] * C
    cy = lb.centerY()
    # C: cap height (left of W)
    dim_v(c, P.x - 60, P.pt(x0, -C)[1], P.pt(x0, 0)[1], "C")
    # label height and gap (right side)
    xr = P.x + P.w + 50
    dim_v(c, xr, P.pt(0, lb.top())[1], P.pt(0, lb.bottom())[1], "0.24C", side="right")
    dim_v(c, xr, P.pt(0, lb.bottom())[1], P.pt(0, -C)[1], "0.19C", side="right")
    # rail weight (left end of left rail)
    rl = P.pt(x0, cy)
    dim_v(c, rl[0] - 30, P.pt(x0, cy - t / 2)[1], P.pt(x0, cy + t / 2)[1], "0.073C")
    # rail gap (above the right end of the left rail)
    a_ = P.pt(lb.left() - g, cy)
    b_ = P.pt(lb.left(), cy)
    dim_h(c, a_[0], b_[0], P.pt(0, lb.top())[1] - 34, "0.19C")
    # rail ends line up with the top corners of W and S
    for xx in (x0, x1):
        top = P.pt(xx, cy)
        bot = P.pt(xx, -C)
        guide_line(c, top[0], top[1], bot[0], bot[1] + 10)
    G.text(c, "Dashed lines: rail ends line up with the top corners of W and S", M + 40, y + 520, NOTE)
    y += 640
    rows = [["Element", "Specification"],
            ["Slant", "Whole logo sheared 0.12 (6.84 degrees), leaning right"],
            ["WILDCATS", "Saira Condensed Black, tracking +20/1000 em, custom A (see next page)"],
            ["NINETY SIX", "Saira ExtraBold (width 110), tracking +220/1000 em, height 0.24C"],
            ["NINETY SIX position", "0.19C above WILDCATS, centered between the rail ends"],
            ["Rails", "Weight 0.073C (same as NINETY SIX strokes), 0.19C from NINETY SIX"],
            ["Overall size", "5.43C wide by 1.44C tall"]]
    table(c, rows, M, y, [0, 380])


def p_construction_box(c, n):
    frame(c, n)
    y = heading(c, "Logo Construction: 96 Box",
                "The 96 box is the same shape everywhere: in the icon, the horizontal logo, and every team "
                "logo. Only its size changes. H is the height of the box.") + 70
    G.rect(c, M, y, CW, 640, TILE, 8)
    Hb = C
    bx, bw = BR.box(Hb)
    P = Placed(c, BR.icon(), M + 170, y + 150, height=340)
    # H
    dim_v(c, P.x - 50, P.pt(0, -Hb)[1], P.pt(0, 0)[1], "H")
    # width 1.17H along the top edge
    dim_h(c, P.pt(0, -Hb)[0], P.pt(bw, -Hb)[0], P.y - 34, "1.17H")
    # numeral height
    nh = BR.SPEC["box_numerals"] * Hb
    dim_v(c, P.x + P.w + 40, P.pt(0, -Hb / 2 - nh / 2)[1], P.pt(0, -Hb / 2 + nh / 2)[1], "0.64H", side="right")
    # side padding at the bottom left
    pad = BR.SPEC["box_pad_x"] * Hb
    nb = BR.fit_h(BR.numerals(), nh).computeTightBounds()
    p0 = P.pt(0, -Hb / 2)
    p1 = P.pt(pad, -Hb / 2)
    dim_h(c, P.pt(0, 0)[0], P.pt(pad, 0)[0], P.y + P.h + 34, "0.17H", above=False)
    # slant offset at the right edge
    tr = P.pt(bw, -Hb)
    br_ = P.pt(bw, 0)
    guide_line(c, tr[0], tr[1], tr[0], br_[1] + 20)
    dim_h(c, br_[0], tr[0], P.y + P.h + 34, "0.12H", above=False)
    # horizontal logo: box-to-name gap
    Q = Placed(c, BR.horizontal(), M + 840, y + 250, width=560)
    ox = -BR.SPEC["box_to_name"] * C - bw
    g0, g1 = Q.pt(ox + bw, -C), Q.pt(0, -C)
    dim_h(c, g0[0], g1[0], Q.y - 34, "0.17C")
    G.para(c, "In the horizontal and team logos, the box is as tall as the lettering (H = C) and sits "
              "0.17C from it, baselines aligned.", M + 840, y + 470, 560, G.MINW, lh=1.35)
    y += 720
    rows = [["Element", "Specification"],
            ["Box", "Width 1.17H, height H, same 0.12 slant as the lettering"],
            ["Numerals", "Saira Condensed Black, 0.64H tall, 0.17H from each side, centered"],
            ["Horizontal logo", "Box height = C. Box sits 0.17C left of WILDCATS, baselines aligned"],
            ["Icon", "The box on its own. Width 1.29H including the slant"],
            ["Spacing pairs", "L-D -35, D-C -10, C-A -10, T-S -15 (1/1000 em)"],
            ["Custom A", "Opened counter: flat top 0.073C wide, so the A doesn't fill in when small"]]
    table(c, rows, M, y, [0, 380])


def p_teams(c, n):
    frame(c, n)
    y = heading(c, "Team and Group Logos",
                "Teams, clubs, and groups use the horizontal logo with their name in place of WILDCATS. "
                "Files for each team are in logos/teams. To add a group, follow these rules.") + 50
    rules = [("One word", "One line. Box height = C."),
             ("Two or more words", "Two lines. Split where the two lines come out closest in length."),
             ("Line spacing", "0.26C between lines. Box height = 2.26C, so it matches both lines."),
             ("Ampersand", "Use &, not \"and\". It stays at the end of the first line (TRACK & / FIELD)."),
             ("Long names", "No line may be longer than 7C (about 1.3x WILDCATS). If it is, use the "
                            "group's usual initials."),
             ("Abbreviations", "Only when a name is too long. All caps, no periods (NHS, FBLA, FFA)."),
             ("Short names", "Allowed as they are (GOLF, NHS). The box doesn't change."),
             ("Teams and clubs", "Same construction for both. The name is the only difference."),
             ("Levels", "JV, varsity, boys, and girls are not part of the logo. Put them in nearby text.")]
    for a, b in rules:
        G.text(c, a, M, y + 36, SMALLB)
        y = G.para(c, b, M + 360, y + 36, CW - 360, G.DESC, lh=1.35) - 10
        G.hairline(c, M, y + 6, W - M, y + 6)
        y += 6
    y += 70
    G.rect(c, M, y, CW, 380, MAROON, 8)
    s = 0.42
    K.draw(c, BR.as_paths(BR.team(["CROSS", "COUNTRY"])), CREAM, M + CW * 0.26, y + 190, width=CW * 0.40,
           height=230)
    K.draw(c, BR.as_paths(BR.team(["TRACK &", "FIELD"])), CREAM, M + CW * 0.74, y + 190, width=CW * 0.40,
           height=230)


def p_team_examples(c, n):
    frame(c, n)
    y = heading(c, "Team Logo Examples",
                "All examples use one size of lettering. National Honor Society is too long for two "
                "lines, so it uses its initials.") + 40
    names = ["Football", "Soccer", "Volleyball", "Cross Country", "Track & Field", "Student Council",
             "Marching Band", "Academic Team", "NHS"]
    marks = [BR.as_paths(BR.team(nm)) for nm in names]
    gap = 26
    tw = (CW - gap) / 2
    th = 236
    s = min(min(tw * 0.80 / K.bounds(p).width(), th * 0.70 / K.bounds(p).height()) for p in marks)
    for i, (nm, p) in enumerate(zip(names, marks)):
        col, row = i % 2, i // 2
        x = M + col * (tw + gap)
        yy = y + row * (th + gap)
        dark = (row + col) % 2 == 0
        G.rect(c, x, yy, tw, th, MAROON if dark else TILE, 8)
        b = K.bounds(p)
        K.draw(c, p, CREAM if dark else MAROON, x + tw / 2, yy + th / 2, width=b.width() * s)
    G.text(c, "National Honor Society  →  NHS", M + tw + gap + 30, y + 4 * (th + gap) + th / 2 + 10, SMALLB)


def p_clear_space(c, n):
    frame(c, n)
    y = heading(c, "Clear Space",
                "Keep other text, images, and page edges at least x away from every logo. For the icon "
                "and team logos, x is half the height of the box.") + 60
    th = 620
    G.rect(c, M, y, CW, th, TILE, 8)
    P = Placed(c, BR.primary(), M + CW / 2 - 400, y + th / 2 - 106, width=800)
    unit = 0.5 * C * P.s
    r = skia.Rect.MakeXYWH(P.x - unit, P.y - unit, P.w + 2 * unit, P.h + 2 * unit)
    c.drawRect(r, skia.Paint(AntiAlias=True, Color=wm.hexc(MAROON, 150), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=2.5, PathEffect=skia.DashPathEffect.Make([12, 9], 0)))
    for (ux, uy) in [(r.left(), r.top()), (r.right() - unit, r.bottom() - unit)]:
        c.drawRect(skia.Rect.MakeXYWH(ux, uy, unit, unit), skia.Paint(Color=wm.hexc(MAROON, 40)))
        G.text(c, "x", ux + unit / 2, uy + unit / 2 + 10, G.Style(G.SAIRA, 30, MAROON, 0, wdth=100, wght=700),
               align="center")
    G.text(c, "Primary logo: x = 0.5C (half the height of WILDCATS)", M, y + th + 60, G.DESC)
    y += th + 140
    gap = 40
    tw = (CW - gap) / 2
    for i, (fn, txt, hh) in enumerate([(BR.icon, "Icon and team logos: x = 0.5H", 150),
                                       (BR.horizontal, "Horizontal: x = 0.5C", 70)]):
        x = M + i * (tw + gap)
        G.rect(c, x, y, tw, 440, TILE, 8)
        b = K.bounds(BR.as_paths(fn()))
        mw = b.width() * hh / b.height()
        P = Placed(c, fn(), x + tw / 2 - mw / 2, y + 220 - hh / 2, height=hh)
        unit = 0.5 * C * P.s
        r = skia.Rect.MakeXYWH(P.x - unit, P.y - unit, P.w + 2 * unit, P.h + 2 * unit)
        c.drawRect(r, skia.Paint(AntiAlias=True, Color=wm.hexc(MAROON, 150), Style=skia.Paint.kStroke_Style,
                                 StrokeWidth=2.5, PathEffect=skia.DashPathEffect.Make([12, 9], 0)))
        G.text(c, txt, x, y + 500, G.DESC)


def p_min_sizes(c, n):
    frame(c, n)
    y = heading(c, "Minimum Sizes",
                "Below these widths, the thinnest gaps in the logo (between C and A, and between 9 and 6) "
                "close up. Screen sizes were checked on screen. Print sizes are calculated; apparel sizes are "
                "planning values to confirm with a test print or sew-out.") + 40
    rows = [["Logo", "Screen", "Print", "Screen print", "Vinyl", "Embroidery"],
            ["Primary", "240 px", "1.5 in", "4.5 in", "6 in", "Not advised"],
            ["Horizontal", "110 px", "1 in", "3.75 in", "5 in", "6 in"],
            ["Stacked", "140 px", "1 in", "3.25 in", "4.25 in", "5 in"],
            ["Wordmark", "80 px", "0.8 in", "3 in", "4 in", "4.75 in"],
            ["Icon", "32 px", "0.3 in", "0.75 in", "1 in", "1.25 in"]]
    y = table(c, rows, M, y, [0, 300, 520, 740, 1000, 1200], rh=64)
    y += 50
    G.text(c, "Changes from v1.0", M, y, H2)
    y = bullets(c, ["Horizontal logo: print minimum raised from 0.75 in to 1 in.",
                    "Wordmark: print minimum raised from 0.6 in to 0.8 in.",
                    "Apparel minimums are new. On a left chest (about 3.5 in wide), use the icon, or test the "
                    "wordmark with a sew-out first.",
                    "Screen minimums were tested and stay the same."], M, y + 70, CW)
    y += 30
    G.text(c, "Shown at actual print size (print this page at 100%)", M, y + 20, SMALLB)
    y += 70
    x = M
    for fn, inches in ((BR.primary, 1.5), (BR.horizontal, 1.0), (BR.stacked, 1.0), (BR.wordmark, 0.8),
                       (BR.icon, 0.3)):
        P = Placed(c, fn(), x, y, width=G.inch(inches))
        G.text(c, f"{inches:g} in", x, y + 200, G.MINW)
        x += G.inch(inches) + 60
    G.text(c, "Test sheets: production-tests/screen-size-test.png and print-and-apparel-size-tests.pdf",
           M, y + 290, G.MINW)


def p_colors(c, n):
    frame(c, n)
    y = heading(c, "Colors",
                "Maroon and cream are the school colors. Black and white are for one-color printing. The "
                "gradient is for TV screens and other digital backgrounds only.") + 40
    gap = 26
    t = (CW - 4 * gap) / 5
    sw = [("Maroon", "#5E1A1D", "94, 26, 29", True), ("Cream", "#F5EAD5", "245, 234, 213", False),
          ("Black", "#000000", "0, 0, 0", True), ("White", "#FFFFFF", "255, 255, 255", False),
          ("TV gradient", "#973333 to #320B0B", "", True)]
    for i, (nm, hx, rgb, dark) in enumerate(sw):
        x = M + i * (t + gap)
        if nm == "TV gradient":
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(x, y, t, 380))
            K.gradient(c, x, y, t, 380)
            c.restore()
        else:
            G.rect(c, x, y, t, 380, hx, 0)
        if not dark:
            G.outline(c, x, y, t, 380, r=0)
        G.text(c, nm, x, y + 430, SMALLB)
        G.text(c, hx if nm != "TV gradient" else "#973333 top", x, y + 468, G.MINW)
        G.text(c, ("RGB " + rgb) if rgb else "#320B0B bottom", x, y + 502, G.MINW)
    y += 600
    G.text(c, "Contrast", M, y, H2)
    rows = [["Combination", "Contrast ratio", "Use"],
            ["Cream on maroon", "10.7 : 1", "Yes, the main combination"],
            ["Maroon on cream or white", "10.7 / 12.8 : 1", "Yes"],
            ["Cream or white on TV gradient", "6.2 : 1 at the lightest point", "Yes, for logos and text"],
            ["Maroon on TV gradient", "1.4 : 1 at the darkest point", "No"],
            ["Maroon on black", "1.6 : 1", "No"],
            ["Cream on white", "1.2 : 1", "No"]]
    y = table(c, rows, M, y + 30, [0, 560, 960], rh=58)
    y += 60
    G.text(c, "Print color", M, y, H2)
    G.para(c, "CMYK and Pantone values haven't been set yet. Before the first large print or apparel order, "
              "have the printer match maroon and cream to a physical sample (a printed proof or a fabric "
              "swatch), then add the approved values to this page. Don't guess them from the screen colors.",
           M, y + 60, CW, G.DESC, lh=1.45)


def p_type(c, n):
    frame(c, n)
    y = heading(c, "Typography",
                "Everything uses the Saira family, which is free on Google Fonts and works in Google Docs, "
                "Slides, and Canva. The logos are artwork; never recreate them by typing.") + 60
    specs = [("Display headline", G.Style(G.COND, 110, MAROON, 0.01), "GAME DAY",
              "Saira Condensed Black, all caps, line spacing 0.9"),
             ("Section heading", G.Style(G.SAIRA, 60, INK, 0.0, wdth=100, wght=700), "Fall Schedule",
              "Saira Bold, title case"),
             ("Body text", G.Style(G.SAIRA, 34, BODY, 0.0, wdth=100, wght=400),
              "Practice starts Monday at 3:30 in the main gym.", "Saira Regular, 10 to 12 pt, line spacing 1.4"),
             ("Labels and details", G.Style(G.SAIRA, 26, INK, 0.12, True, wdth=100, wght=600),
              "Friday  ·  7:30 PM  ·  Home", "Saira SemiBold, all caps, letter spacing +12%")]
    for nm, st, sample, spec in specs:
        G.hairline(c, M, y, W - M, y)
        G.text(c, nm, M, y + 50, SMALLB)
        G.text(c, sample, M + 430, y + 40 + st.size * 0.8, st)
        G.text(c, spec, M + 430, y + 70 + st.size * 0.8 + 30, G.MINW)
        y += 120 + st.size
    G.hairline(c, M, y, W - M, y)
    y += 90
    G.text(c, "Logo type (for reference only)", M, y, H2)
    bullets(c, ["WILDCATS, 96, and team names: Saira Condensed Black, slanted 6.84 degrees, with custom "
                "spacing and a modified A.",
                "NINETY SIX in the primary logo: Saira ExtraBold at width 110 (only available in the "
                "variable font).",
                "Headlines in layouts stay upright. The slant belongs to the logos and the slant panels."],
            M, y + 70, CW)


def p_panels(c, n):
    frame(c, n)
    y = heading(c, "Slant Panels",
                "Slant panels are the one graphic device in the identity. They're parallelograms at the same "
                "angle as the 96 box, so layouts feel like Ninety Six Wildcats even when the logo is small.") + 50
    # construction: a box beside a panel
    G.rect(c, M, y, CW, 470, TILE, 8)
    hb = 220
    P = Placed(c, BR.icon(), M + 120, y + 125, height=hb)
    T.panel(c, M + 520, y + 125, 760, hb, MAROON)
    dim_h(c, M + 520, M + 520 + SH * hb, y + 100, "0.12 x height")
    G.text(c, "Same slant as the 96 box: the top edge shifts right by 0.12 x the panel's height (6.84 degrees).",
           M + 40, y + 420, G.MINW)
    y += 540
    gap = 26
    tw = (CW - 3 * gap) / 4
    for i, (nm, desc) in enumerate([("Tag", "Holds a short label: GAME DAY, FINAL. Upright text, cap "
                                            "height half the panel's height."),
                                    ("Number box", "Holds one number: a date or a score. Numerals 64% of its "
                                                   "height, like the 96 box, but upright."),
                                    ("Band", "A wide panel that runs off one or both page edges. Holds text "
                                             "or a logo."),
                                    ("Frame", "A photo container on TV slides and posters. The photo fills "
                                              "it; never add a border.")]):
        x = M + i * (tw + gap)
        G.rect(c, x, y, tw, 300, TILE, 8)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x, y, tw, 300))
        if i == 0:
            T.tag(c, "Game day", x + 50, y + 120, 64, MAROON, CREAM)
        elif i == 1:
            sc = S.Scene(300)
            sc.panel_text("Date", "10/24", x + 50, y + 100, 100, MAROON, CREAM, numerals=True)
            S.draw(c, sc)
        elif i == 2:
            T.panel(c, x - 30, y + 110, tw * 0.8, 90, MAROON)
        else:
            T.frame(c, x + 50, y + 60, tw - 120, 180)
        c.restore()
        G.text(c, nm, x, y + 360, G.NAME)
        G.para(c, desc, x, y + 405, tw - 10, G.DESC, lh=1.35)
    y += 680
    G.text(c, "Rules", M, y, H2)
    bullets(c, ["Always lean right at 6.84 degrees. Never rotate, flip, or round the corners.",
                "Solid maroon, cream, black, or white, or a photo. No outlines, gradients, or shadows.",
                "Up to three panels per layout, not counting the date boxes in a schedule. Don't use panels "
                "on formal documents."], M, y + 70, CW)


def p_tv(c, n):
    frame(c, n)
    y = heading(c, "Digital and TV",
                "Hallway TVs are read from a distance and for only a few seconds. Keep slides short and "
                "large.") + 40
    w_, h_ = image(c, tpl("tv-slide"), M, y, w=CW)
    # safe area overlay
    sx = CW / 1920
    r = skia.Rect.MakeXYWH(M + 96 * sx, y + 54 * sx, (1920 - 192) * sx, (1080 - 108) * sx)
    c.drawRect(r, skia.Paint(AntiAlias=True, Color=wm.hexc("#FFFFFF", 160), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=2, PathEffect=skia.DashPathEffect.Make([10, 8], 0)))
    G.text(c, "Dashed line: 5% safe area", M, y + h_ + 40, G.MINW)
    y += h_ + 110
    bullets(c, ["Size 1920 x 1080 px. Use the TV gradient (#973333 to #320B0B) or solid maroon.",
                "Keep all text and logos inside the 5% safe area; some TVs crop the edges.",
                "Cream or white text only. Headlines at least 120 px, details at least 40 px.",
                "One message per slide: a headline, one line of details, at most one sentence.",
                "The horizontal logo sits small in the bottom left. Don't repeat it in the headline.",
                "Blank backgrounds are in templates/tv-slide."], M, y, CW)


def p_social(c, n):
    frame(c, n)
    y = heading(c, "Social Media",
                "Five post layouts and a story, built from the same parts. Each comes as an example, a blank, "
                "and an editable PowerPoint file in templates/social.") + 40
    items = [(k, sfx) for k, _, sfx, _ in S.EXAMPLES if sfx == "example"] + [("story", "example")]
    gap = 20
    hh = (CW - gap * (len(items) - 1)) / (0.8 * (len(items) - 1) + 0.5625)
    x = M
    for key, sfx in items:
        w_, _ = image(c, S.path_for(key, sfx), x, y, h=hh)
        G.text(c, S.NAMES[key], x, y + hh + 40, G.MINW)
        x += w_ + gap
    y += hh + 110
    d = 150
    profiles = [("Main account", "wildcats-profile-icon-cream-on-maroon.png"),
                ("Football", "teams/wildcats-profile-football.png"),
                ("Cross Country", "teams/wildcats-profile-cross-country.png"),
                ("Marching Band", "teams/wildcats-profile-marching-band.png"),
                ("Academic Team", "teams/wildcats-profile-academic-team.png"),
                ("NHS", "teams/wildcats-profile-nhs.png")]
    for i, (nm, f) in enumerate(profiles):
        im = os.path.join(os.path.dirname(OUT), "social", "profile", f)
        cx = M + d / 2 + i * (d + 90)
        c.save()
        clip = skia.Path()
        clip.addCircle(cx, y + d / 2, d / 2)
        c.clipPath(clip, doAntiAlias=True)
        image(c, im, cx - d / 2, y, w=d)
        c.restore()
        G.text(c, nm, cx, y + d + 40, G.MINW, align="center")
    y += d + 110
    bullets(c, ["Posts are 1080 x 1350 px. Instagram's profile grid crops square posts at the sides.",
                "The number box holds one number, a date or a score. Words go outside it.",
                "Maroon for spirit and athletics; cream for academic and family news. Let photos fill their "
                "space; don't box them in.",
                "Keep text out of the top and bottom 250 px of stories, where the app covers it.",
                "Profile pictures: the 96 box with the team's one-word name, or a short form the team already "
                "uses (XC). Clubs without one get the full name. The main account uses the 96 alone.",
                "Never shrink a team logo or the primary logo into a profile picture: at 32 px it can't be read."],
            M, y, CW)


def p_print(c, n):
    frame(c, n)
    y = heading(c, "Print and Apparel") + 50
    hh = 490
    x = M
    xs = []
    for name in ("event-poster-11x17", "letterhead"):
        xs.append(x)
        w_, _ = image(c, tpl(name), x, y, h=hh, outline=True)
        x += w_ + 30
    xs.append(x)
    image(c, tpl("tshirt-concept"), x, y, h=hh)
    y += hh + 50
    for xx, t in zip(xs, ("Poster 11 x 17 in", "Letterhead 8.5 x 11 in", "T-shirt concept")):
        G.text(c, t, xx, y, G.MINW)
    y += 70
    G.text(c, "Print", M, y, G.NAME)
    y = bullets(c, ["Use the PDF or SVG logo files. PNGs are for screens and documents only.",
                    "Use 0.25 in or more of margin on anything that's trimmed."], M, y + 50, CW)
    G.text(c, "Apparel", M, y + 20, G.NAME)
    bullets(c, ["Print in one ink color: maroon or cream on the shirt color, or white or black.",
                "Left chest (about 3.5 in): the icon. Full front or back: the primary or stacked logo, "
                "10 to 12 in wide.",
                "Check minimum sizes for the method (screen print, vinyl, embroidery) and ask the vendor for a "
                "proof or sew-out. Test artwork is in production-tests."], M, y + 70, CW)


def p_dos(c, n):
    frame(c, n)
    y0 = heading(c, "Do's and Don'ts") + 60
    prim = BR.as_paths(BR.primary())
    gap = 40
    tw = (CW - gap) / 2
    th = 280
    step = th + 150

    def tile(col, row, bg, draw, ok, line):
        x = M + col * (tw + gap)
        y = y0 + row * step
        if bg:
            G.rect(c, x, y, tw, th, bg, 8)
        draw(x + tw / 2, y + th / 2)
        G.badge(c, x + 21, y + th + 50, ok)
        G.para(c, line, x + 60, y + th + 60, tw - 60, G.Style(G.SAIRA, 26, INK, 0, wdth=100, wght=600), lh=1.3)

    def stretched(cx, cy):
        m = skia.Matrix()
        m.setScale(1.45, 0.72)
        K.draw(c, [wm.transformed(p, m) for p in prim], MAROON, cx, cy, width=520)

    def effects(cx, cy):
        word = wm.union(prim)
        ringp = wm.op(wm.grow(word, 22), wm.grow(word, 12), "diff")
        shadow = wm.transformed(word, skia.Matrix.Translate(26, 26))
        K.draw(c, [shadow], "#2A0A0C", cx + 6, cy + 6, width=400)
        K.draw(c, [ringp], "#E0B04A", cx, cy, width=400 * K.bounds([ringp]).width() / K.bounds([word]).width())
        K.draw(c, [word], CREAM, cx, cy, width=400)

    def typed(cx, cy):
        G.text(c, "NINETY SIX WILDCATS", cx, cy + 20, G.Style("Saira[wdth,wght].ttf", 56, MAROON, 0.0,
                                                               wdth=125, wght=900), align="center")

    def on_grad(cx, cy):
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(cx - tw / 2, cy - th / 2, tw, th))
        K.gradient(c, cx - tw / 2, cy - th / 2, tw, th)
        c.restore()
        K.draw(c, prim, MAROON, cx, cy, width=420)

    tile(0, 0, MAROON, lambda cx, cy: K.draw(c, prim, CREAM, cx, cy, width=420), True,
         "Do use the supplied logo files.")
    tile(1, 0, TILE, stretched, False, "Don't stretch, squash, or re-slant the logo.")
    tile(0, 1, TILE, lambda cx, cy: K.draw(c, BR.as_paths(BR.horizontal()), MAROON, cx, cy, width=480), True,
         "Do use the horizontal logo in small or narrow spaces.")
    tile(1, 1, MAROON, effects, False, "Don't add outlines, shadows, or other effects.")
    tile(0, 2, MAROON, lambda cx, cy: K.draw(c, BR.as_paths(BR.icon()), CREAM, cx, cy, height=170), True,
         "Do use the icon for profile pictures and square spaces.")
    tile(1, 2, TILE, typed, False, "Don't type the logo out in a font.")
    tile(0, 3, MAROON, lambda cx, cy: K.draw(c, BR.as_paths(BR.team("Soccer")), CREAM, cx, cy, width=440), True,
         "Do use the team logo files for teams and clubs.")
    tile(1, 3, None, on_grad, False, "Don't use maroon on the gradient, or other low-contrast pairs.")


def p_files(c, n):
    frame(c, n)
    y = heading(c, "Files and Naming",
                "Every logo comes in maroon, cream, black, and white, as SVG, PDF, and PNG. File names "
                "follow one pattern so they're easy to find.") + 50
    tree = [("logos/primary/", "wildcats-primary-<color>.svg, .pdf, .png"),
            ("logos/horizontal/", "wildcats-horizontal-<color>"),
            ("logos/stacked/", "wildcats-stacked-<color>"),
            ("logos/wordmark/", "wildcats-wordmark-<color>"),
            ("logos/icon/", "wildcats-icon-<color>"),
            ("logos/teams/<team>/", "wildcats-team-<team>-<horizontal or square>-<color>"),
            ("logos/institutional/", "ninetysix-hs-<line or stacked>-<color>"),
            ("social/profile/", "wildcats-profile-<variant>.png"),
            ("templates/<template>/", "wildcats-<template>-<example or blank>.png"),
            ("templates/social/", "wildcats-social-<layout>-<example or blank>.png, .pptx"),
            ("production-tests/", "Size test sheets"),
            ("guidelines/", "This document, page images, and audits"),
            ("fonts/", "Saira font files and licenses"),
            ("source/", "Scripts that rebuild every file")]
    a_ = G.Style("Saira[wdth,wght].ttf", 25, INK, 0.0, wdth=100, wght=600)
    b_ = G.Style("Saira[wdth,wght].ttf", 25, BODY, 0.0, wdth=100, wght=400)
    G.rect(c, M, y, CW, 58 * len(tree) + 100, TILE, 8)
    G.text(c, "ninety-six-wildcats-brand/", M + 40, y + 62, a_)
    for k, (d, f) in enumerate(tree):
        G.text(c, d, M + 80, y + 120 + k * 58, a_)
        G.text(c, f, M + 520, y + 120 + k * 58, b_)
    y += 58 * len(tree) + 170
    rows = [["Format", "Use for"],
            ["SVG", "Websites, Canva, Google Slides, and sending to vendors"],
            ["PDF", "Printing, sign shops, and apparel vendors"],
            ["PNG", "Documents, slides, and social media (transparent background)"]]
    y = table(c, rows, M, y, [0, 260])
    y += 50
    G.para(c, "Color names in files: maroon, cream, black, white. Team names are lowercase with hyphens "
              "(cross-country, track-and-field).", M, y, CW, G.DESC, lh=1.4)


PAGES = [p_cover, p_overview, p_architecture, p_primary, p_secondary, p_construction_primary,
         p_construction_box, p_teams, p_team_examples, p_clear_space, p_min_sizes, p_colors, p_type,
         p_panels, p_tv, p_social, p_print, p_dos, p_files]
NAMES = ["cover", "overview", "architecture", "primary-marks", "secondary-marks", "construction-primary",
         "construction-box", "team-logos", "team-examples", "clear-space", "minimum-sizes", "colors",
         "typography", "slant-panels", "digital-tv", "social", "print-apparel", "dos-and-donts", "files"]


if __name__ == "__main__":
    os.makedirs(PAGES_DIR, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for f in os.listdir(PAGES_DIR):
        if not only and f.endswith(".png"):
            os.remove(os.path.join(PAGES_DIR, f))
    for i, (fn, name) in enumerate(zip(PAGES, NAMES), 1):
        if only and i not in only:
            continue
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        c.clear(wm.hexc("#FFFFFF"))
        fn(c, i)
        surf.makeImageSnapshot().save(os.path.join(PAGES_DIR, f"{i:02d}_{name}.png"), skia.kPNG)
    if not only:
        stream = skia.FILEWStream(os.path.join(OUT, f"Wildcats_Brand_Guidelines_v{VERSION}.pdf"))
        with skia.PDF.MakeDocument(stream) as doc:
            for i, fn in enumerate(PAGES, 1):
                with doc.page(612, 792) as c:
                    c.scale(612 / W, 792 / H)
                    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=wm.hexc("#FFFFFF")))
                    fn(c, i)
        stream.flush()
    print("saved", OUT)
