"""
Ninety Six Wildcats identity, v1.1: the single source of truth for logo
geometry. Every mark is built from the numbers in SPEC, all expressed as
ratios of C, the cap height of WILDCATS (or of H, the height of the 96 box),
so any mark can be rebuilt at any size without eyeballing.

Marks:  primary, horizontal, stacked, wordmark, icon,
        team(name) / team_square(name), institutional(layout)
All marks are composed upright and sheared as one piece (SPEC["shear"]).
"""
import math
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402

COND = "SairaCondensed-Black.ttf"
SAIRA = "Saira[wdth,wght].ttf"
SIZE = 400.0                 # working font size; C = 0.688 * SIZE

SPEC = {
    # slant: horizontal shear applied to the whole lockup
    "shear": 0.12,                       # = 6.84 degrees
    # WILDCATS and team names: Saira Condensed Black
    "tracking_em": 0.020,                # +20/1000 em
    "kern_em": {"LD": -0.035, "DC": -0.010, "CA": -0.010, "TS": -0.015},
    # custom A: flat-topped counter (font units at 1000/em, from baseline)
    "a_counter": {"top_y": 0.550, "bottom_y": 0.260, "top_x": (0.2325, 0.2825),
                  "bottom_x": (0.2075, 0.3075)},
    # primary: NINETY SIX + rails over WILDCATS
    "label_height": 0.24,                # NINETY SIX ink height, x C
    "label_tracking_em": 0.22,           # Saira, weight 800, width 110
    "label_gap": 0.19,                   # NINETY SIX above WILDCATS cap line, x C
    "rail_weight": 0.073,                # = NINETY SIX stroke weight, x C
    "rail_gap": 0.19,                    # rail to NINETY SIX, x C
    # 96 box (H = box height)
    "box_numerals": 0.64,                # numeral height, x H
    "box_pad_x": 0.17,                   # numeral ink to box edge, x H
    "box_to_name": 0.17,                 # box to WILDCATS / team name, x C
    # stacked: NINETY SIX justified to the width of WILDCATS
    "stack_tracking_em": 0.12,           # Saira Condensed Black
    "stack_gap": 0.12,                   # x C
    # team names
    "line_gap": 0.26,                    # between stacked name lines, x C
    "max_line": 7.0,                     # longest allowed name line, x C
    "square_box": 0.85,                  # box height in square layouts, x C
    "square_gap": 0.20,                  # box to name in square layouts, x C
    # clear space
    "clear_space": 0.5,                  # x C (x H for the icon)
}

_k = SIZE / 400.0


# --------------------------------------------------------------------------
# Path helpers
# --------------------------------------------------------------------------
def B(p):
    return p.computeTightBounds()


def move(p, dx, dy):
    return wm.transformed(p, skia.Matrix.Translate(dx, dy))


def scale_about(p, s, x=0.0, y=0.0):
    m = skia.Matrix()
    m.setScale(s, s, x, y)
    return wm.transformed(p, m)


def fit_h(p, h):
    b = B(p)
    return scale_about(p, h / b.height(), b.left(), b.top())


def fit_w(p, w):
    b = B(p)
    return scale_about(p, w / b.width(), b.left(), b.top())


def put(p, left=None, right=None, cx=None, top=None, bottom=None, cy=None):
    b = B(p)
    dx = (left - b.left()) if left is not None else (right - b.right()) if right is not None \
        else (cx - b.centerX()) if cx is not None else 0
    dy = (top - b.top()) if top is not None else (bottom - b.bottom()) if bottom is not None \
        else (cy - b.centerY()) if cy is not None else 0
    return move(p, dx, dy)


def shear(p, k=None):
    return wm.skew(p, -(SPEC["shear"] if k is None else k))


def cap_height():
    return 0.688 * SIZE


C = cap_height()


# --------------------------------------------------------------------------
# Lettering
# --------------------------------------------------------------------------
def _open_A(T):
    a = SPEC["a_counter"]
    for g in T.glyphs:
        if g["ch"] == "A":
            cut = skia.Path()
            cut.moveTo(a["top_x"][0] * SIZE, -a["top_y"] * SIZE)
            cut.lineTo(a["top_x"][1] * SIZE, -a["top_y"] * SIZE)
            cut.lineTo(a["bottom_x"][1] * SIZE, -a["bottom_y"] * SIZE)
            cut.lineTo(a["bottom_x"][0] * SIZE, -a["bottom_y"] * SIZE)
            cut.close()
            g["path"] = wm.op(g["path"], cut, "diff")
    return T


def name_line(text):
    """A line of WILDCATS-style lettering, upright, baseline at y=0, x from 0."""
    T = _open_A(wm.Text(COND, text, SIZE, tracking=SPEC["tracking_em"]))
    for i in range(1, len(T.glyphs)):
        pair = T.glyphs[i - 1]["ch"] + T.glyphs[i]["ch"]
        if pair in SPEC["kern_em"]:
            T.shift_from(i, SPEC["kern_em"][pair] * SIZE)
    p = T.union()
    return move(p, -B(p).left(), 0)


def wildcats():
    return name_line("WILDCATS")


def cap_extents(p):
    """Left/right ink extents of a line within its top 20% (the cap line),
    used to align rails with the outer corners of the letters."""
    pts = [q for c, _ in wm.flatten(p, 1.0) for q in c if q[1] <= -0.80 * C]
    return min(x for x, _ in pts), max(x for x, _ in pts)


def label_ninety_six():
    T = wm.Text(SAIRA, "NINETY SIX", 200, tracking=SPEC["label_tracking_em"], wdth=110, wght=800)
    return T.union()


def numerals():
    return wm.Text(COND, "96", SIZE, tracking=0.0).union()


# --------------------------------------------------------------------------
# The 96 box
# --------------------------------------------------------------------------
def box(H):
    """Upright 96 box of height H, occupying x 0..w, y -H..0. Returns (path, w)."""
    n = fit_h(numerals(), SPEC["box_numerals"] * H)
    w = B(n).width() + 2 * SPEC["box_pad_x"] * H
    n = put(n, cx=w / 2, cy=-H / 2)
    return wm.op(wm.rect(0, -H, w, H), n, "diff"), w


# --------------------------------------------------------------------------
# Marks (all returned sheared)
# --------------------------------------------------------------------------
def primary():
    w = wildcats()
    x0, x1 = cap_extents(w)
    top = -C
    lab = fit_h(label_ninety_six(), SPEC["label_height"] * C)
    lab = put(lab, cx=(x0 + x1) / 2, bottom=top - SPEC["label_gap"] * C)
    lb = B(lab)
    t, g = SPEC["rail_weight"] * C, SPEC["rail_gap"] * C
    cy = lb.centerY()
    rails = [wm.rect(x0, cy - t / 2, lb.left() - g - x0, t),
             wm.rect(lb.right() + g, cy - t / 2, x1 - lb.right() - g, t)]
    return shear(wm.union([w, lab] + rails))


def wordmark():
    return shear(wildcats())


def horizontal():
    return team("WILDCATS")


def icon():
    p, _ = box(C)
    return shear(p)


def stacked():
    w = wildcats()
    b = B(w)
    lab = wm.Text(COND, "NINETY SIX", 200, tracking=SPEC["stack_tracking_em"]).union()
    lab = put(fit_w(lab, b.width()), left=b.left(), bottom=-C - SPEC["stack_gap"] * C)
    return shear(wm.union([w, lab]))


# --------------------------------------------------------------------------
# Team / group extension
# --------------------------------------------------------------------------
def team_lines(name):
    """Apply the naming rules. Returns (lines, ok, note)."""
    words = name.upper().replace(" AND ", " & ").split()
    if len(words) == 1:
        lines = words
    else:
        best = None
        for i in range(1, len(words)):
            a, b = " ".join(words[:i]), " ".join(words[i:])
            if b.startswith("&"):          # keep & at the end of the first line
                continue
            wa, wb = B(name_line(a)).width(), B(name_line(b)).width()
            score = max(wa, wb)
            if best is None or score < best[0]:
                best = (score, [a, b])
        lines = best[1]
    widths = [B(name_line(ln)).width() / C for ln in lines]
    ok = max(widths) <= SPEC["max_line"] + 1e-6
    note = "" if ok else f"line {max(widths):.1f}C exceeds {SPEC['max_line']}C: use an approved short form"
    return lines, ok, note


def _name_block(lines):
    paths = []
    for k, ln in enumerate(lines):
        dy = -(len(lines) - 1 - k) * (C + SPEC["line_gap"] * C)
        paths.append(move(name_line(ln), 0, dy))
    height = len(lines) * C + (len(lines) - 1) * SPEC["line_gap"] * C
    return paths, height


def team(name_or_lines):
    """96 box + name. The box is the icon, scaled to the height of the name."""
    lines = team_lines(name_or_lines)[0] if isinstance(name_or_lines, str) else name_or_lines
    paths, Hb = _name_block(lines)
    bx, bw = box(Hb)
    bx = move(bx, -SPEC["box_to_name"] * C - bw, 0)
    return shear(wm.union([bx] + paths))


def team_square(name_or_lines):
    """Box centred over the name: for profile pictures and square spaces."""
    lines = team_lines(name_or_lines)[0] if isinstance(name_or_lines, str) else name_or_lines
    paths = []
    for k, ln in enumerate(lines):
        p = name_line(ln)
        dy = -(len(lines) - 1 - k) * (C + SPEC["line_gap"] * C)
        paths.append(move(p, -B(p).width() / 2, dy))
    word = wm.union(paths)
    Hb = SPEC["square_box"] * C
    bx, bw = box(Hb)
    bx = move(bx, -bw / 2, B(word).top() - SPEC["square_gap"] * C)
    return shear(wm.union([bx, word]))


# --------------------------------------------------------------------------
# Institutional mark (upright, typographic)
# --------------------------------------------------------------------------
def institutional(layout="line"):
    def line(t, track):
        return wm.Text(SAIRA, t, SIZE, tracking=track, wdth=100, wght=700).union()
    if layout == "line":
        return line("NINETY SIX HIGH SCHOOL", 0.12)
    a, b = line("NINETY SIX", 0.12), line("HIGH SCHOOL", 0.12)
    wa, wb = B(a).width(), B(b).width()
    # justify: track the shorter line out to the longer one
    if wa < wb:
        a = wm.Text(SAIRA, "NINETY SIX", SIZE, tracking=0.12 + (wb - wa) / (9 * SIZE), wdth=100,
                    wght=700).union()
    else:
        b = wm.Text(SAIRA, "HIGH SCHOOL", SIZE, tracking=0.12 + (wa - wb) / (10 * SIZE), wdth=100,
                    wght=700).union()
    a = put(a, left=0, bottom=0)
    hb = B(b).height()
    b = put(b, left=0, top=0.55 * hb)
    return wm.union([a, b])


MARKS = {
    "primary": primary, "horizontal": horizontal, "stacked": stacked,
    "wordmark": wordmark, "icon": icon,
}


def as_paths(p):
    return list(p) if isinstance(p, (list, tuple)) else [p]


if __name__ == "__main__":
    print("C =", C, " shear angle =", round(math.degrees(math.atan(SPEC["shear"])), 2), "deg")
    for k, f in MARKS.items():
        b = B(f())
        print(f"{k:11s} width {b.width() / C:5.2f}C  height {b.height() / C:5.2f}C  ratio {b.width() / b.height():5.2f}")
    for n in ["Football", "Cross Country", "Track & Field", "Student Council", "National Honor Society",
              "Marching Band", "Academic Team", "NHS"]:
        print(n, team_lines(n))
