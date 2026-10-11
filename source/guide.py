"""
v1.0 (superseded by brand.py, kit.py and guide11.py; output archived in archive/kit-v1.0).
guide11.py still imports the drawing helpers from this file.

Ninety Six Wildcats logo guidelines: a 10-page US Letter (8.5 x 11 in,
portrait) guide, rendered as a print-ready vector PDF plus 200 dpi PNG
pages. Set in the brand's own type (Saira / Saira Condensed).

Layout units are pixels at 200 dpi (1700 x 2200 = 8.5 x 11 in).
Run:  python guide.py   -> wordmarks/final/guidelines/
"""
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import lockups2 as L  # noqa: E402
import final as F  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "v1.0-guidelines")
DPI = 200
W, H = int(8.5 * DPI), int(11 * DPI)   # 1700 x 2200
M = 130                                 # ~0.65 in margins
CW = W - 2 * M                          # content width
N_PAGES = 10

MAROON, CREAM = "#5E1A1D", "#F5EAD5"
INK, BODY, MUTED = "#1C1517", "#4A4043", "#857B7E"
TILE, LINE = "#F2F0ED", "#E2DEDA"
NO = "#B4413A"


def inch(x):
    return x * DPI


# --------------------------------------------------------------------------
# Type (sizes in px at 200 dpi: 33 px is about 12 pt)
# --------------------------------------------------------------------------
class Style:
    def __init__(self, font, size, color, tracking=0.0, upper=False, **axes):
        self.font, self.size, self.color = font, size, color
        self.tracking, self.upper, self.axes = tracking, upper, axes


SAIRA = "Saira[wdth,wght].ttf"
COND = "SairaCondensed-Black.ttf"
H1 = Style(COND, 96, INK, 0.0)
INTRO = Style(SAIRA, 32, BODY, 0.0, wdth=100, wght=400)
NAME = Style(SAIRA, 31, INK, 0.0, wdth=100, wght=700)
DESC = Style(SAIRA, 27, BODY, 0.0, wdth=100, wght=400)
MINW = Style(SAIRA, 25, MUTED, 0.0, wdth=100, wght=500)
FOOT = Style(SAIRA, 21, MUTED, 0.0, wdth=100, wght=500)
SPEC = Style(SAIRA, 27, INK, 0.0, wdth=100, wght=700)

_cache = {}


def shaped(s, st):
    key = (s, st.font, st.size, st.tracking, tuple(sorted(st.axes.items())))
    if key not in _cache:
        T = wm.Text(st.font, s.upper() if st.upper else s, st.size, tracking=st.tracking, **st.axes)
        paths = [T.placed(i) for i in range(len(T.glyphs))]
        width = (T.glyphs[-1]["x"] + T.glyphs[-1]["adv"]) if T.glyphs else 0
        _cache[key] = (paths, width)
    return _cache[key]


def text(c, s, x, y, st, align="left", color=None, alpha=255):
    paths, width = shaped(s, st)
    if align == "right":
        x -= width
    elif align == "center":
        x -= width / 2
    paint = skia.Paint(AntiAlias=True, Color=wm.hexc(color or st.color, alpha))
    c.save()
    c.translate(x, y)
    for p in paths:
        c.drawPath(p, paint)
    c.restore()
    return width


def para(c, s, x, y, width, st, lh=1.45, color=None):
    """Word-wrapped paragraph; returns the y after the last line."""
    words, line = s.split(), ""
    for w_ in words:
        trial = (line + " " + w_).strip()
        if shaped(trial, st)[1] > width and line:
            text(c, line, x, y, st, color=color)
            y += st.size * lh
            line = w_
        else:
            line = trial
    if line:
        text(c, line, x, y, st, color=color)
        y += st.size * lh
    return y


def heading(c, title, intro=None, y=250):
    """Page title and an optional one- or two-sentence intro. Returns y below."""
    text(c, title, M, y, H1)
    y += 44
    if intro:
        y = para(c, intro, M, y + 50, CW * 0.9, INTRO)
    return y


# --------------------------------------------------------------------------
# Drawing helpers
# --------------------------------------------------------------------------
def rect(c, x, y, w, h, color, r=0):
    p = skia.Paint(AntiAlias=True, Color=wm.hexc(color))
    if r:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), p)
    else:
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)


def outline(c, x, y, w, h, r=8):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r),
                skia.Paint(AntiAlias=True, Color=wm.hexc(LINE), Style=skia.Paint.kStroke_Style, StrokeWidth=2))


def hairline(c, x0, y0, x1, y1, color=LINE, w=2):
    c.drawLine(x0, y0, x1, y1, skia.Paint(AntiAlias=True, Color=wm.hexc(color), StrokeWidth=w))


def gradient_rect(c, x, y, w, h):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y), skia.Point(0, y + h)], [wm.hexc(wm.MAROON_TOP), wm.hexc(wm.MAROON_DEEP)])))


def mark(c, fn_or_paths, color, cx, cy, width=None, height=None, matrix=None):
    paths = fn_or_paths if isinstance(fn_or_paths, list) else F.paths_of(fn_or_paths)
    if matrix is not None:
        paths = [wm.transformed(p, matrix) for p in paths]
    F.draw(c, paths, color, cx, cy, width=width, height=height)
    b = F.bounds(paths)
    s = width / b.width() if width else height / b.height()
    if width and height:
        s = min(width / b.width(), height / b.height())
    return paths, s


def badge(c, x, y, ok=True, r=21):
    """Round check / cross badge centred at x, y."""
    col = MAROON if ok else NO
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=wm.hexc(col)))
    k = r / 17
    p = skia.Path()
    if ok:
        p.moveTo(x - 8 * k, y + 0.5 * k)
        p.lineTo(x - 2.5 * k, y + 6 * k)
        p.lineTo(x + 8.5 * k, y - 6 * k)
    else:
        p.moveTo(x - 6.5 * k, y - 6.5 * k)
        p.lineTo(x + 6.5 * k, y + 6.5 * k)
        p.moveTo(x + 6.5 * k, y - 6.5 * k)
        p.lineTo(x - 6.5 * k, y + 6.5 * k)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=wm.hexc("#FFFFFF"), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=3.4 * k, StrokeCap=skia.Paint.kRound_Cap,
                             StrokeJoin=skia.Paint.kRound_Join))


def caption(c, x, y, w, name, use, minimum=None):
    """Logo name, what it's for, and its minimum width, stacked under a tile."""
    text(c, name, x, y, NAME)
    y = para(c, use, x, y + 46, w, DESC, lh=1.4)
    if minimum:
        text(c, "Minimum width: " + minimum, x, y + 2, MINW)


def frame(c, n):
    c.clear(wm.hexc("#FFFFFF"))
    text(c, "Ninety Six Wildcats Logo Guidelines", M, H - 80, FOOT)
    text(c, str(n), W - M, H - 80, FOOT, align="right")


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def p1(c, n):
    gradient_rect(c, 0, 0, W, H)
    mark(c, L.l1a, CREAM, W / 2, 1000, width=1240)
    text(c, "Logo guidelines", M, H - 150, Style(SAIRA, 30, CREAM, 0.22, True, wdth=100, wght=700))
    text(c, "Version 1.0", W - M, H - 150, Style(SAIRA, 30, CREAM, 0.16, True, wdth=100, wght=500),
         align="right", alpha=170)


def p2(c, n):
    frame(c, n)
    y = heading(c, "Primary Logos", "Use one of these two logos whenever possible.") + 40
    rect(c, M, y, CW, 600, MAROON, 8)
    mark(c, L.l1a, CREAM, W / 2, y + 310, width=1040)
    caption(c, M, y + 670, CW, "Primary logo", "Use for TV slides, posters, signs, and shirts.",
            "1.5 in (240 px)")
    y += 880
    rect(c, M, y, CW, 460, TILE, 8)
    mark(c, L.l3a, MAROON, W / 2, y + 230, width=1020)
    caption(c, M, y + 530, CW, "Horizontal logo",
            "Use when space is short or narrow, such as web headers, letterhead, and small merchandise.",
            "0.75 in (110 px)")


def p3(c, n):
    frame(c, n)
    y = heading(c, "Additional Logos") + 60
    gap = 40
    tw = (CW - gap) / 2
    th = 640
    for i, (name, fn, frac, use, minimum) in enumerate([
            ("Stacked logo", L.l6c, 0.72, "Use in square spaces, social media posts, and on the back of shirts.",
             "1 in (140 px)"),
            ("Icon", L.l3f, 0.42, "Use for profile pictures, website icons, sleeves, and stickers.",
             "0.3 in (32 px)")]):
        x = M + i * (tw + gap)
        rect(c, x, y, tw, th, MAROON, 8)
        mark(c, fn, CREAM, x + tw / 2, y + th / 2, width=tw * frac, height=th * 0.56)
        caption(c, x, y + th + 64, tw - 20, name, use, minimum)
    y += th + 300
    rect(c, M, y, CW, 440, TILE, 8)
    mark(c, F.wordmark, MAROON, W / 2, y + 220, width=900)
    caption(c, M, y + 510, CW, "Wordmark", "Use when 96 already appears nearby or space is very limited.",
            "0.6 in (80 px)")


def p4(c, n):
    frame(c, n)
    y = heading(c, "Clear Space and Minimum Size",
                "Leave space around the logo equal to half the height of the letters in WILDCATS (shown as x). "
                "Don't place other text or images inside this area.") + 30
    th = 600
    rect(c, M, y, CW, th, TILE, 8)
    cx, cy = W / 2, y + th / 2 + 10
    paths, s = mark(c, L.l1a, MAROON, cx, cy, width=780)
    _, h = L.word_cond()
    unit = 0.5 * h * s
    b = F.bounds(paths)
    bw, bh = b.width() * s, b.height() * s
    r = skia.Rect.MakeXYWH(cx - bw / 2 - unit, cy - bh / 2 - unit, bw + 2 * unit, bh + 2 * unit)
    c.drawRect(r, skia.Paint(AntiAlias=True, Color=wm.hexc(MAROON, 150), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=2.5, PathEffect=skia.DashPathEffect.Make([12, 9], 0)))
    for (ux, uy) in [(r.left(), r.top()), (r.right() - unit, r.bottom() - unit)]:
        c.drawRect(skia.Rect.MakeXYWH(ux, uy, unit, unit), skia.Paint(Color=wm.hexc(MAROON, 40)))
        text(c, "x", ux + unit / 2, uy + unit / 2 + 10, Style(SAIRA, 30, MAROON, 0, wdth=100, wght=700),
             align="center")
    y += th + 130
    text(c, "Minimum Sizes", M, y, Style(COND, 52, INK, 0.0))
    text(c, "When this page is printed at 100%, each logo below is shown at its smallest allowed size.",
         M, y + 50, DESC)
    rows = [("Primary logo", L.l1a, 1.5, "1.5 in (240 px)"), ("Stacked logo", L.l6c, 1.0, "1 in (140 px)"),
            ("Horizontal logo", L.l3a, 0.75, "0.75 in (110 px)"), ("Wordmark", F.wordmark, 0.6, "0.6 in (80 px)"),
            ("Icon", L.l3f, 0.3, "0.3 in (32 px)")]
    y += 100
    for name, fn, inches, label in rows:
        hairline(c, M, y, W - M, y)
        mark(c, fn, MAROON, M + inch(inches) / 2, y + 57, width=inch(inches))
        text(c, name, M + 480, y + 67, Style(SAIRA, 28, INK, 0, wdth=100, wght=600))
        text(c, label, W - M, y + 67, DESC, align="right")
        y += 114
    hairline(c, M, y, W - M, y)


def p5(c, n):
    frame(c, n)
    y = heading(c, "Profile Pictures",
                "Use the 96 icon for social media profile pictures. Files sized for a circular crop "
                "(1080 x 1080 px) are in the profile folder.")
    opts = [("Cream on maroon", MAROON, CREAM, False), ("Cream on gradient", None, CREAM, True),
            ("Maroon on cream", CREAM, MAROON, False), ("White on black", "#000000", "#FFFFFF", False)]
    d = 500
    col_cx = [M + CW / 4, M + 3 * CW / 4]
    row_cy = [y + 120 + d / 2, y + 120 + d / 2 + d + 190]
    for i, (name, bg, fg, grad) in enumerate(opts):
        cx, cy = col_cx[i % 2], row_cy[i // 2]
        c.save()
        clip = skia.Path()
        clip.addCircle(cx, cy, d / 2)
        c.clipPath(clip, doAntiAlias=True)
        if grad:
            gradient_rect(c, cx - d / 2, cy - d / 2, d, d)
        else:
            rect(c, cx - d / 2, cy - d / 2, d, d, bg)
        c.restore()
        if bg in (CREAM, "#FFFFFF"):
            c.drawCircle(cx, cy, d / 2, skia.Paint(AntiAlias=True, Color=wm.hexc(LINE),
                                                   Style=skia.Paint.kStroke_Style, StrokeWidth=2))
        mark(c, L.l3f, fg, cx, cy, width=d * 0.56, height=d * 0.56)
        text(c, name, cx, cy + d / 2 + 66, Style(SAIRA, 28, INK, 0, wdth=100, wght=600), align="center")


def p6(c, n):
    frame(c, n)
    y = heading(c, "Colors",
                "Maroon and cream are the main school colors. Use black or white when printing in one color, "
                "such as screen printing or embroidery. The gradient is for TV screens and other digital use.")
    y += 50
    gap = 30

    def swatch(x, yy, w, h, name, lines, dark, grad=False, big=False):
        if grad:
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, yy, w, h), 8, 8), doAntiAlias=True)
            gradient_rect(c, x, yy, w, h)
            c.restore()
        else:
            rect(c, x, yy, w, h, lines[0][1], 8)
        if not dark:
            outline(c, x, yy, w, h)
        fg = CREAM if dark else INK
        sub = "#E3CFC2" if dark else BODY
        info = Style(SAIRA, 24, sub, 0.0, wdth=100, wght=500)
        text(c, name, x + 36, yy + h - 40 - 38 * len(lines) - 26, Style(SAIRA, 40 if big else 34, fg, 0.0,
                                                                         wdth=100, wght=700))
        for k, (lab, val) in enumerate(lines):
            text(c, f"{lab}  {val}", x + 36, yy + h - 40 - 38 * (len(lines) - 1 - k), info)

    tw = (CW - gap) / 2
    swatch(M, y, tw, 700, "Maroon", [("HEX", "#5E1A1D"), ("RGB", "94, 26, 29")], True, big=True)
    swatch(M + tw + gap, y, tw, 700, "Cream", [("HEX", "#F5EAD5"), ("RGB", "245, 234, 213")], False, big=True)
    y += 700 + gap
    t3 = (CW - 2 * gap) / 3
    swatch(M, y, t3, 600, "TV gradient", [("Top", "#973333"), ("Bottom", "#320B0B")], True, grad=True)
    swatch(M + t3 + gap, y, t3, 600, "Black", [("HEX", "#000000"), ("RGB", "0, 0, 0")], True)
    swatch(M + 2 * (t3 + gap), y, t3, 600, "White", [("HEX", "#FFFFFF"), ("RGB", "255, 255, 255")], False)


def p7(c, n):
    frame(c, n)
    y = heading(c, "Fonts",
                "The logos use two fonts from the Saira family. Both are free to use, including on "
                "merchandise, under the SIL Open Font License. The font files are included in the logo kit.")
    y += 160
    text(c, "Saira Condensed Black", M, y, SPEC)
    para(c, "Used for WILDCATS and 96. Letters in the logo are slanted 7 degrees, and the A has a slightly "
            "wider opening than the standard font so it stays readable at small sizes.", M, y + 42, CW, DESC)
    word, _ = L.team_line("WILDCATS 96")
    m = skia.Matrix()
    m.setScale(236 / 400, 236 / 400)
    paths = [wm.transformed(word, m)]
    c.save()
    c.translate(M + 26, y + 300)
    sk = skia.Matrix()
    sk.setSkew(-0.12, 0)
    c.concat(sk)
    for p in paths:
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=wm.hexc(MAROON)))
    c.restore()
    text(c, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", M, y + 410, Style(COND, 62, INK, 0.03))
    text(c, "0123456789", M, y + 490, Style(COND, 62, INK, 0.03))
    y += 640
    hairline(c, M, y, W - M, y)
    y += 150
    text(c, "Saira ExtraBold", M, y, SPEC)
    text(c, "Used for NINETY SIX, with wide letter spacing.", M, y + 42, DESC)
    text(c, "NINETY SIX", M, y + 190, Style(SAIRA, 104, MAROON, 0.22, True, wdth=110, wght=800))
    text(c, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", M, y + 290, Style(SAIRA, 48, INK, 0.04, wdth=110, wght=800))
    text(c, "abcdefghijklmnopqrstuvwxyz  0123456789", M, y + 370, Style(SAIRA, 48, BODY, 0.0, wdth=100, wght=400))


def p8(c, n):
    frame(c, n)
    y0 = heading(c, "Logo Do's and Don'ts") + 70
    prim = F.paths_of(L.l1a)
    gap = 40
    tw = (CW - gap) / 2
    th = 370
    step = th + 175

    def tile(col, row, bg, draw, ok, line):
        x = M + col * (tw + gap)
        y = y0 + row * step
        rect(c, x, y, tw, th, bg, 8)
        draw(x + tw / 2, y + th / 2)
        badge(c, x + 21, y + th + 50, ok)
        para(c, line, x + 60, y + th + 60, tw - 60, Style(SAIRA, 27, INK, 0, wdth=100, wght=600), lh=1.35)

    def stretched(cx, cy):
        m = skia.Matrix()
        m.setScale(1.45, 0.72)
        mark(c, prim, MAROON, cx, cy, width=520, matrix=m)

    def effects(cx, cy):
        word = wm.union(prim)
        ringp = wm.op(wm.grow(word, 22), wm.grow(word, 12), "diff")
        shadow = wm.transformed(word, skia.Matrix.Translate(26, 26))
        b = F.bounds([word])
        s = 400 / b.width()
        for p, col in [(shadow, "#2A0A0C"), (ringp, "#E0B04A"), (word, CREAM)]:
            c.save()
            c.translate(cx, cy)
            c.scale(s, s)
            c.translate(-b.centerX(), -b.centerY())
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=wm.hexc(col)))
            c.restore()

    # each row pairs a do (left) with a don't (right)
    tile(0, 0, MAROON, lambda cx, cy: mark(c, prim, CREAM, cx, cy, width=430), True,
         "Do use the logo files provided.")
    tile(1, 0, TILE, stretched, False, "Don't stretch or squash the logo.")
    tile(0, 1, TILE, lambda cx, cy: mark(c, L.l3a, MAROON, cx, cy, width=480), True,
         "Do use the horizontal logo in small or narrow spaces.")
    tile(1, 1, MAROON, effects, False, "Don't add outlines, shadows, or other effects.")
    tile(0, 2, MAROON, lambda cx, cy: mark(c, L.l3f, CREAM, cx, cy, height=190), True,
         "Do use the icon in square spaces.")
    tile(1, 2, MAROON, lambda cx, cy: mark(c, prim, "#7E3338", cx, cy, width=430), False,
         "Don't use colors outside the school palette or with low contrast.")


def arrow(c, x0, y, x1, color=MUTED):
    p = skia.Path()
    p.moveTo(x0, y)
    p.lineTo(x1, y)
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=wm.hexc(color), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=5, StrokeCap=skia.Paint.kRound_Cap))
    h = skia.Path()
    h.moveTo(x1 - 26, y - 20)
    h.lineTo(x1 + 2, y)
    h.lineTo(x1 - 26, y + 20)
    c.drawPath(h, skia.Paint(AntiAlias=True, Color=wm.hexc(color), Style=skia.Paint.kStroke_Style,
                             StrokeWidth=5, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))


def p_teams(c, n):
    frame(c, n)
    y = heading(c, "Team Logos",
                "Teams and groups can use the 96 box with their own name in place of WILDCATS. "
                "Use the same font, slant, and spacing as the horizontal logo.") + 40
    th = 380
    rect(c, M, y, CW, th, MAROON, 8)
    # same scale on both sides, so the box and letters match exactly
    _, s = mark(c, L.l3a, CREAM, M + CW * 0.26, y + th / 2, width=560)
    arrow(c, M + CW * 0.50 - 40, y + th / 2, M + CW * 0.50 + 40, color="#C9A9A0")
    soccer = L.as_paths(L.team_tab(["SOCCER"]))
    mark(c, soccer, CREAM, M + CW * 0.75, y + th / 2, width=F.bounds(soccer).width() * s)
    y += th + 130
    text(c, "How to Make a Team Logo", M, y, Style(COND, 52, INK, 0.0))
    y += 70
    steps = ["Start with the 96 box from the horizontal logo.",
             "Replace WILDCATS with the team or group name in capital letters.",
             "Use Saira Condensed Black, slanted 7 degrees, at the same height as the box.",
             "For names with two words, stack the words on two lines and make the box as tall as both lines.",
             "If a file for the team is already in the logos/teams folder, use it instead of making a new one."]
    for k, st in enumerate(steps, 1):
        text(c, f"{k}.", M, y, NAME)
        y = para(c, st, M + 50, y, CW - 50, DESC, lh=1.4) + 14
    y += 40
    th = 380
    rect(c, M, y, CW, th, TILE, 8)
    mark(c, L.as_paths(L.team_tab(["CROSS", "COUNTRY"])), MAROON, W / 2, y + th / 2, height=250)
    caption(c, M, y + th + 64, CW, "Two-line team logo",
            "Use for names with two words, such as Cross Country or Track & Field.")


def p_team_examples(c, n):
    frame(c, n)
    y = heading(c, "Team Logo Examples",
                "Files for each team are in the logos/teams folder, in maroon, cream, black, and white, "
                "with a profile picture for each team.") + 50
    teams = [L.as_paths(L.team_tab(lines)) for _, lines in L.TEAMS]
    gap = 28
    tw = (CW - gap) / 2
    th = 176
    # one shared scale so the letters are the same size in every tile
    s = min(min(tw * 0.80 / F.bounds(p).width(), th * 0.74 / F.bounds(p).height()) for p in teams)
    for i, paths in enumerate(teams):
        col, row = i % 2, i // 2
        x = M + col * (tw + gap)
        yy = y + row * (th + gap)
        dark = (row + col) % 2 == 0
        rect(c, x, yy, tw, th, MAROON if dark else TILE, 8)
        b = F.bounds(paths)
        mark(c, paths, CREAM if dark else MAROON, x + tw / 2, yy + th / 2, width=b.width() * s)


PAGES = [p1, p2, p3, p_teams, p_team_examples, p4, p5, p6, p7, p8]
NAMES = ["cover", "primary-logos", "additional-logos", "team-logos", "team-logo-examples",
         "clear-space-and-minimum-size", "profile-pictures", "colors", "fonts", "dos-and-donts"]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".png") or f.endswith(".pdf"):
            os.remove(os.path.join(OUT, f))
    for i, (fn, name) in enumerate(zip(PAGES, NAMES), 1):
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        c.clear(wm.hexc("#FFFFFF"))
        fn(c, i)
        surf.makeImageSnapshot().save(os.path.join(OUT, f"{i:02d}_{name}.png"), skia.kPNG)
    # PDF at true US Letter size: 612 x 792 pt
    pdf = os.path.join(OUT, "Wildcats_Logo_Guidelines.pdf")
    stream = skia.FILEWStream(pdf)
    with skia.PDF.MakeDocument(stream) as doc:
        for i, fn in enumerate(PAGES, 1):
            with doc.page(612, 792) as c:
                c.scale(612 / W, 792 / H)
                c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=wm.hexc("#FFFFFF")))
                fn(c, i)
    stream.flush()
    del stream
    print("saved", OUT)
