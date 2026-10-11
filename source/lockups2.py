"""
Round 5: deeper exploration of the three chosen lockup families.
  L1  Banner Rules     — NINETY SIX / 96 set between rules, tied to WILDCATS
  L3  Number Tab       — a 96 tab paired with WILDCATS
  L6  Justified Stack  — NINETY SIX and WILDCATS set to one width
Every lockup is composed upright and slanted as one piece, so rules, tabs and
letters share exactly the same angle. Single colour throughout.
Run:  python lockups2.py   → wordmarks/lockups2/
"""
import os
import sys

import skia
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "lockups2")
K = -0.12  # house slant (applied to whole lockup)


# --------------------------------------------------------------------------
# Building blocks (all upright; slant applied at the end)
# --------------------------------------------------------------------------
def B(p):
    return p.computeTightBounds()


def move(p, dx, dy):
    return wm.transformed(p, skia.Matrix.Translate(dx, dy))


def fit_h(p, h):
    b = B(p)
    m = skia.Matrix()
    m.setScale(h / b.height(), h / b.height(), b.left(), b.top())
    return wm.transformed(p, m)


def fit_w(p, w):
    b = B(p)
    m = skia.Matrix()
    m.setScale(w / b.width(), w / b.width(), b.left(), b.top())
    return wm.transformed(p, m)


def put(p, left=None, right=None, cx=None, top=None, bottom=None, cy=None):
    b = B(p)
    dx = (left - b.left()) if left is not None else (right - b.right()) if right is not None \
        else (cx - b.centerX()) if cx is not None else 0
    dy = (top - b.top()) if top is not None else (bottom - b.bottom()) if bottom is not None \
        else (cy - b.centerY()) if cy is not None else 0
    return move(p, dx, dy)


def slant(p, k=K):
    return wm.skew(p, k)


def open_A(T):
    """Saira Condensed Black's A has a hairline counter that tapers to a point
    and fills in at normal sizes. Cut a slightly wider, flat-topped counter
    (about as wide as the B's) so the A stays open. Outer shape unchanged."""
    k = T.size / 400.0
    for g in T.glyphs:
        if g["ch"] == "A":
            cut = skia.Path()
            cut.moveTo(93 * k, -220 * k)
            cut.lineTo(113 * k, -220 * k)
            cut.lineTo(123 * k, -104 * k)
            cut.lineTo(83 * k, -104 * k)
            cut.close()
            g["path"] = wm.op(g["path"], cut, "diff")
    return T


# Hand-tuned pair spacing for WILDCATS (font units at size 400). The L's
# open foot and the C's aperture read wide; T–S is a touch loose.
WILDCATS_KERN = {"LD": -14, "DC": -4, "CA": -10, "TS": -6}


def word_cond():
    T = open_A(wm.Text("SairaCondensed-Black.ttf", "WILDCATS", 400, tracking=0.02))
    for i in range(1, len(T.glyphs)):
        pair = T.glyphs[i - 1]["ch"] + T.glyphs[i]["ch"]
        if pair in WILDCATS_KERN:
            T.shift_from(i, WILDCATS_KERN[pair])
    return T.union(), T.cap_height


def word_wide(italic=False):
    f = "Archivo-Italic[wdth,wght].ttf" if italic else "Archivo[wdth,wght].ttf"
    T = wm.Text(f, "WILDCATS", 400, tracking=0.01, wdth=115, wght=900)
    return T.union(), T.cap_height


def label(text="NINETY SIX", tracking=0.22, wght=800, wdth=110):
    return wm.Text("Saira[wdth,wght].ttf", text, 200, tracking=tracking, wdth=wdth, wght=wght).union()


def label_cond(text="NINETY SIX", tracking=0.06):
    return wm.Text("SairaCondensed-Black.ttf", text, 200, tracking=tracking).union()


def nums(text="96"):
    return wm.Text("SairaCondensed-Black.ttf", text, 400, tracking=0.0).union()


def script(text="Ninety Six"):
    return wm.grow(wm.Text("Damion-Regular.ttf", text, 300, tracking=-0.01).union(), 4)


def rule_pair(center_item, x0, x1, th, gap):
    """Two rules either side of an item, spanning x0..x1, centred on its middle."""
    b = B(center_item)
    cy = b.centerY()
    return wm.union([wm.rect(x0, cy - th / 2, (b.left() - gap) - x0, th),
                     wm.rect(b.right() + gap, cy - th / 2, x1 - (b.right() + gap), th)])


# --------------------------------------------------------------------------
# L1  Banner Rules
# --------------------------------------------------------------------------
def l1a():  # classic: NINETY SIX above between rules
    w, h = word_cond()
    b = B(w)
    lab = put(fit_h(label(), 0.24 * h), cx=b.centerX(), bottom=b.top() - 0.18 * h)
    r = rule_pair(lab, b.left(), b.right(), 0.06 * h, 0.13 * h)
    return slant(wm.union([w, lab, r]))


def l1b():  # label beneath the word
    w, h = word_cond()
    b = B(w)
    lab = put(fit_h(label(), 0.24 * h), cx=b.centerX(), top=b.bottom() + 0.18 * h)
    r = rule_pair(lab, b.left(), b.right(), 0.06 * h, 0.13 * h)
    return slant(wm.union([w, lab, r]))


def l1c():  # 96 numerals between the rules
    w, h = word_cond()
    b = B(w)
    n = put(fit_h(nums(), 0.42 * h), cx=b.centerX(), bottom=b.top() - 0.16 * h)
    r = rule_pair(n, b.left(), b.right(), 0.075 * h, 0.14 * h)
    return slant(wm.union([w, n, r]))


def l1d():  # framed: label rules above + a full rule below
    w, h = word_cond()
    b = B(w)
    lab = put(fit_h(label(), 0.24 * h), cx=b.centerX(), bottom=b.top() - 0.18 * h)
    r = rule_pair(lab, b.left(), b.right(), 0.06 * h, 0.13 * h)
    low = wm.rect(b.left(), b.bottom() + 0.18 * h, b.width(), 0.06 * h)
    return slant(wm.union([w, lab, r, low]))


def l1e():  # wide upright word
    w, h = word_wide()
    b = B(w)
    lab = put(fit_h(label(), 0.36 * h), cx=b.centerX(), bottom=b.top() - 0.24 * h)
    r = rule_pair(lab, b.left(), b.right(), 0.08 * h, 0.16 * h)
    return wm.union([w, lab, r])


def l1f():  # script accent between the rules
    w, h = word_cond()
    b = B(w)
    s = put(fit_h(script(), 0.50 * h), cx=b.centerX(), bottom=b.top() - 0.10 * h)
    r = rule_pair(s, b.left(), b.right(), 0.06 * h, 0.12 * h)
    r = move(r, 0, 0.06 * h)  # sit the rules on the script's x-height middle
    # the script is already slanted: shift it to where the slant puts its
    # centre, instead of slanting it a second time
    s = move(s, K * B(s).centerY(), 0)
    return slant(wm.union([w, r])), s


# --------------------------------------------------------------------------
# L3  Number Tab
# --------------------------------------------------------------------------
def tab_with(num_h_frac, h, pad, solid=True, stroke=0.07):
    n = fit_h(nums(), num_h_frac * h)
    nb = B(n)
    tw = nb.width() + 2 * pad * h
    tab = wm.rect(0, -h, tw, h)
    n = put(n, cx=tw / 2, cy=-h / 2)
    if solid:
        return wm.op(tab, n, "diff"), tw
    ringp = wm.op(tab, wm.rect(stroke * h, -h + stroke * h, tw - 2 * stroke * h, h - 2 * stroke * h), "diff")
    return wm.union([ringp, n]), tw


def l3a():  # tab leading, refined spacing
    w, h = word_cond()
    b = B(w)
    tab, tw = tab_with(0.64, h, 0.17)
    tab = move(tab, b.left() - 0.17 * h - tw, 0)
    return slant(wm.union([tab, w]))


def l3b():  # tab trailing
    w, h = word_cond()
    b = B(w)
    tab, tw = tab_with(0.64, h, 0.17)
    tab = move(tab, b.right() + 0.17 * h, 0)
    return slant(wm.union([w, tab]))


def l3c():  # open box tab: outlined box, solid 96
    w, h = word_cond()
    b = B(w)
    tab, tw = tab_with(0.60, h, 0.20, solid=False, stroke=0.075)
    tab = move(tab, b.left() - 0.17 * h - tw, 0)
    return slant(wm.union([tab, w]))


def l3d():  # stacked: tab centred over the word (square spaces)
    w, h = word_cond()
    b = B(w)
    th = 0.85 * h
    tab, tw = tab_with(0.66, th, 0.17)
    tab = move(tab, b.centerX() - tw / 2, b.top() - 0.20 * h)
    return slant(wm.union([tab, w]))


def l3e():  # wide upright word + square tab
    w, h = word_wide()
    b = B(w)
    tab, tw = tab_with(0.64, h, 0.16)
    tab = move(tab, b.left() - 0.17 * h - tw, 0)
    return wm.union([tab, w])


def l3f():  # the tab alone — icon / avatar / favicon
    _, h = word_cond()
    tab, tw = tab_with(0.64, h, 0.17)
    return slant(tab)


# --------------------------------------------------------------------------
# L6  Justified Stack
# --------------------------------------------------------------------------
def l6a():  # wide stack, refined spacing
    w, h = word_wide()
    b = B(w)
    lab = put(fit_w(label(tracking=0.10, wght=900), b.width()), left=b.left(), bottom=b.top() - 0.24 * h)
    return wm.union([w, lab])


def l6b():  # weight contrast: lighter, airier top line
    w, h = word_wide()
    b = B(w)
    lab = put(fit_w(label(tracking=0.42, wght=700), b.width()), left=b.left(), bottom=b.top() - 0.24 * h)
    return wm.union([w, lab])


def l6c():  # condensed italic stack
    w, h = word_cond()
    b = B(w)
    lab = put(fit_w(label_cond(tracking=0.12), b.width()), left=b.left(), bottom=b.top() - 0.12 * h)
    return slant(wm.union([w, lab]))


def l6d():  # divider rule between the lines
    w, h = word_wide()
    b = B(w)
    th = 0.06 * h
    rule = wm.rect(b.left(), b.top() - 0.30 * h - th, b.width(), th)
    lab = put(fit_w(label(tracking=0.42, wght=800), b.width()), left=b.left(),
              bottom=B(rule).top() - 0.30 * h)
    return wm.union([w, rule, lab])


def l6e():  # flipped: WILDCATS over NINETY SIX
    w, h = word_wide()
    b = B(w)
    lab = put(fit_w(label(tracking=0.42, wght=800), b.width()), left=b.left(), top=b.bottom() + 0.24 * h)
    return wm.union([w, lab])


def l6f():  # wide italic stack
    w, h = word_wide()
    b = B(w)
    lab = put(fit_w(label(tracking=0.30, wght=900), b.width()), left=b.left(), bottom=b.top() - 0.22 * h)
    return slant(wm.union([w, lab]), -0.16)


# --------------------------------------------------------------------------
# Team logos: the 96 box with a team or group name in place of WILDCATS
# --------------------------------------------------------------------------
def team_line(name):
    """One line of team name, set exactly like WILDCATS."""
    T = open_A(wm.Text("SairaCondensed-Black.ttf", name, 400, tracking=0.02))
    return T.union(), T.cap_height


def team_tab(lines):
    """96 box + team name. `lines` is one or two strings; with two, the
    name stacks and the box grows to the height of both lines."""
    if isinstance(lines, str):
        lines = [lines]
    paths, h = [], None
    gap = 0
    for k, ln in enumerate(lines):
        p, h = team_line(ln)
        gap = 0.26 * h
        dy = -(len(lines) - 1 - k) * (h + gap)
        paths.append(move(p, -B(p).left(), dy))
    hb = len(lines) * h + (len(lines) - 1) * gap
    if len(lines) == 1:
        tab, tw = tab_with(0.64, h, 0.17)
    else:
        tab, tw = tab_with(0.60, hb, 0.13)
    tab = move(tab, -0.17 * h - tw, 0)
    return slant(wm.union([tab] + paths))


def team_stacked(lines):
    """96 box centred over the team name (profile pictures, square spaces)."""
    if isinstance(lines, str):
        lines = [lines]
    paths, h = [], None
    for k, ln in enumerate(lines):
        p, h = team_line(ln)
        dy = -(len(lines) - 1 - k) * 1.26 * h
        paths.append(move(p, -B(p).centerX(), dy))
    word = wm.union(paths)
    b = B(word)
    th = 0.85 * h
    tab, tw = tab_with(0.66, th, 0.17)
    tab = move(tab, -tw / 2, b.top() - 0.20 * h)
    return slant(wm.union([tab, word]))


TEAMS = [
    ("football", ["FOOTBALL"]), ("soccer", ["SOCCER"]), ("basketball", ["BASKETBALL"]),
    ("baseball", ["BASEBALL"]), ("softball", ["SOFTBALL"]), ("volleyball", ["VOLLEYBALL"]),
    ("wrestling", ["WRESTLING"]), ("tennis", ["TENNIS"]), ("golf", ["GOLF"]),
("cheer", ["CHEER"]), ("cross-country", ["CROSS", "COUNTRY"]),
    ("track-and-field", ["TRACK &", "FIELD"]), ("band", ["BAND"]),
]


FAMILIES = [
    ("L1", "Banner Rules", [
        ("L1-A", "Classic", l1a), ("L1-B", "Label below", l1b), ("L1-C", "96 between rules", l1c),
        ("L1-D", "Framed", l1d), ("L1-E", "Wide upright", l1e), ("L1-F", "Script accent", l1f)]),
    ("L3", "Number Tab", [
        ("L3-A", "Tab leading", l3a), ("L3-B", "Tab trailing", l3b), ("L3-C", "Open box", l3c),
        ("L3-D", "Stacked", l3d), ("L3-E", "Wide upright", l3e), ("L3-F", "Icon only", l3f)]),
    ("L6", "Justified Stack", [
        ("L6-A", "Bold stack", l6a), ("L6-B", "Weight contrast", l6b), ("L6-C", "Condensed italic", l6c),
        ("L6-D", "Divider rule", l6d), ("L6-E", "Flipped", l6e), ("L6-F", "Wide italic", l6f)]),
]


def as_paths(r):
    """Variants return a path, or a tuple of paths (all one colour)."""
    return list(r) if isinstance(r, tuple) else [r]


def pil(img):
    return Image.fromarray(img.convert(alphaType=skia.kUnpremul_AlphaType,
                                       colorType=skia.kRGBA_8888_ColorType).toarray()[..., :3])


PANELS = [("maroon", wm.CREAM, True, None), ("cream", wm.MAROON, False, wm.CREAM),
          ("mono", wm.INK, False, wm.WHITE)]


def family_sheet(code, name, variants):
    W, H = 700, 400
    f1 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 22, index=1)
    rows = []
    for vid, vname, fn in variants:
        paths = as_paths(fn())
        row = Image.new("RGB", (3 * W, H))
        for k, (pn, fg, grad, bg) in enumerate(PANELS):
            layers = [(p, fg) for p in paths]
            row.paste(pil(wm.render_layers(layers, W, H, bg, margin=0.15, gradient=grad)), (k * W, 0))
            wm.save_svg(layers, os.path.join(OUT, f"{vid}_{vname.lower().replace(' ', '_')}_{pn}.svg"))
        ImageDraw.Draw(row).text((20, 16), f"{vid}  {vname}", font=f1, fill=(245, 234, 213))
        rows.append(row)
    S = Image.new("RGB", (3 * W, H * len(rows) + 8 * (len(rows) - 1)), (24, 8, 9))
    for i, r in enumerate(rows):
        S.paste(r, (0, i * (H + 8)))
    out = os.path.join(OUT, f"{code}_{name.lower().replace(' ', '_')}_variations.png")
    S.save(out)
    return out


if __name__ == "__main__":
    for code, name, variants in FAMILIES:
        print(family_sheet(code, name, variants))
