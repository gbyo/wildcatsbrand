"""
Wordmark toolkit: shape text with HarfBuzz, turn it into editable skia paths,
customise glyphs (per-letter transforms, swashes, joins), merge everything
with path boolean ops, and render PNG / SVG boards.
"""
import os
import math
import hashlib

import skia
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), "fonts")
CACHE = os.path.join(HERE, ".cache")
os.makedirs(CACHE, exist_ok=True)

MAROON = "#5E1A1D"
MAROON_DEEP = "#320B0B"
MAROON_TOP = "#973333"
CREAM = "#F5EAD5"
INK = "#151112"
WHITE = "#FFFFFF"


def hexc(h, a=255):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------
def font_file(name, **axes):
    """Return a static TTF path for `name` (a file in fonts/), instancing
    variable axes if given (e.g. wght=900, wdth=125)."""
    src = os.path.join(FONTS, name)
    if not axes:
        return src
    key = hashlib.md5((name + repr(sorted(axes.items()))).encode()).hexdigest()[:10]
    out = os.path.join(CACHE, f"{key}.ttf")
    if not os.path.exists(out):
        f = TTFont(src)
        inst = instancer.instantiateVariableFont(f, axes)
        inst.save(out)
    return out


class Text:
    """Shaped text as a list of per-glyph paths in font units scaled to `size`."""

    def __init__(self, font, text, size=400, features=None, tracking=0.0, **axes):
        self.path_file = font_file(font, **axes)
        blob = hb.Blob.from_file_path(self.path_file)
        face = hb.Face(blob)
        hbfont = hb.Font(face)
        upem = face.upem
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hbfont, buf, features or {"kern": True, "liga": True})
        tf = skia.Typeface.MakeFromFile(self.path_file)
        sfont = skia.Font(tf, size)
        sc = size / upem
        self.glyphs = []
        x = 0.0
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            p = sfont.getPath(info.codepoint)
            if p is None:
                p = skia.Path()
            # skia glyph paths are y-down already
            gx = x + pos.x_offset * sc
            gy = -pos.y_offset * sc
            self.glyphs.append(dict(ch=text[info.cluster], path=p, x=gx, y=gy,
                                    adv=pos.x_advance * sc, gid=info.codepoint))
            x += pos.x_advance * sc + tracking * size
        self.size = size
        self.metrics = sfont.getMetrics()
        cap = TTFont(self.path_file)
        os2 = cap["OS/2"] if "OS/2" in cap else None
        self.cap_height = (getattr(os2, "sCapHeight", 0) or 0.7 * upem) * sc
        self.x_height = (getattr(os2, "sxHeight", 0) or 0.5 * upem) * sc

    def glyph(self, i):
        return self.glyphs[i]

    def move(self, i, dx=0, dy=0):
        self.glyphs[i]["x"] += dx
        self.glyphs[i]["y"] += dy
        return self

    def shift_from(self, i, dx):
        for g in self.glyphs[i:]:
            g["x"] += dx
        return self

    def transform(self, i, m):
        """Apply a skia.Matrix to glyph i in its local coords."""
        g = self.glyphs[i]
        p = skia.Path(g["path"])
        p.transform(m)
        g["path"] = p
        return self

    def scale_glyph(self, i, sx, sy=None, anchor="baseline"):
        sy = sx if sy is None else sy
        b = self.glyphs[i]["path"].computeTightBounds()
        ax = b.centerX()
        ay = 0 if anchor == "baseline" else b.centerY()
        m = skia.Matrix()
        m.setScale(sx, sy, ax, ay)
        return self.transform(i, m)

    def placed(self, i):
        g = self.glyphs[i]
        p = skia.Path(g["path"])
        p.offset(g["x"], g["y"])
        return p

    def paths(self):
        return [self.placed(i) for i in range(len(self.glyphs))]

    def union(self):
        return union(self.paths())


# --------------------------------------------------------------------------
# Path utilities
# --------------------------------------------------------------------------
def union(paths):
    """Union of paths, merged one pair at a time.

    skia's OpBuilder can drop holes from inputs that are themselves the
    result of earlier boolean ops (even-odd paths), e.g. a counter cut into
    a letter, so it isn't used here."""
    out = None
    for p in paths:
        if out is None:
            out = skia.Path(p)
            continue
        r = skia.Op(out, p, skia.PathOp.kUnion_PathOp)
        if r is not None:
            out = r
    return out if out is not None else skia.Path()


def op(a, b, kind):
    k = {"union": skia.PathOp.kUnion_PathOp, "diff": skia.PathOp.kDifference_PathOp,
         "intersect": skia.PathOp.kIntersect_PathOp, "xor": skia.PathOp.kXOR_PathOp}[kind]
    r = skia.Op(a, b, k)
    return r if r is not None else skia.Path()


def transformed(p, m):
    q = skia.Path(p)
    q.transform(m)
    return q


def skew(p, sx=-0.2, pivot_y=0.0):
    m = skia.Matrix()
    m.setSkew(sx, 0, 0, pivot_y)
    return transformed(p, m)


def stroke_to_path(p, width, cap="round", join="round"):
    paint = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=width)
    paint.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap,
                        "square": skia.Paint.kSquare_Cap}[cap])
    paint.setStrokeJoin({"round": skia.Paint.kRound_Join, "miter": skia.Paint.kMiter_Join,
                         "bevel": skia.Paint.kBevel_Join}[join])
    out = skia.Path()
    paint.getFillPath(p, out)
    return out


def grow(p, r, join="round"):
    """Offset outward by r (outline expansion)."""
    if r <= 0:
        return p
    return union([p, stroke_to_path(p, 2 * r, join=join)])


def shrink(p, r):
    """Offset inward by r."""
    if r <= 0:
        return p
    return op(p, stroke_to_path(p, 2 * r), "diff")


def tapered_stroke(pts, w0, w1, wmax, n=200, profile=None):
    """Brush stroke along a cubic Bezier given 4 control points with a
    width profile (start width, end width, peak width)."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
    left, right = [], []

    def B(t):
        u = 1 - t
        return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
                u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)

    def D(t):
        u = 1 - t
        return (3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2),
                3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2))
    for i in range(n + 1):
        t = i / n
        if profile:
            w = profile(t)
        else:
            # smooth swell: thin → peak at 35% → thin
            a = math.sin(math.pi * min(1, t / 0.7) * 0.5) if t < 0.35 else 1
            w = w0 + (wmax - w0) * math.sin(math.pi * t) ** 0.8 * (1 - t) + (w1) * t
        px, py = B(t)
        dx, dy = D(t)
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((px + nx * w / 2, py + ny * w / 2))
        right.append((px - nx * w / 2, py - ny * w / 2))
    path = skia.Path()
    path.moveTo(*left[0])
    for q in left[1:]:
        path.lineTo(*q)
    for q in reversed(right):
        path.lineTo(*q)
    path.close()
    return path


def rect(x, y, w, h, r=0):
    p = skia.Path()
    if r:
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    else:
        p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def flatten(p, step=2.0):
    """Path → list of (points, closed) polylines (curves sampled finely)."""
    contours, cur, closed = [], [], False
    it = skia.Path.Iter(p, False)
    V = skia.Path.Verb

    def seg(n):
        return max(4, int(n / step))
    while True:
        verb, pts = it.next()
        if verb == V.kDone_Verb:
            break
        P = [(q.x(), q.y()) for q in pts]
        if verb == V.kMove_Verb:
            if cur:
                contours.append((cur, closed))
            cur, closed = [P[0]], False
        elif verb == V.kLine_Verb:
            cur.append(P[1])
        elif verb in (V.kQuad_Verb, V.kConic_Verb):
            if verb == V.kConic_Verb:
                qs = skia.Path.ConvertConicToQuads(pts[0], pts[1], pts[2], it.conicWeight(), 2)
                qs = [(q.x(), q.y()) for q in qs]
                quads = [(qs[k], qs[k + 1], qs[k + 2]) for k in range(0, len(qs) - 2, 2)]
            else:
                quads = [tuple(P[:3])]
            for a, b, c in quads:
                n = seg(math.dist(a, b) + math.dist(b, c))
                for k in range(1, n + 1):
                    t = k / n
                    u = 1 - t
                    cur.append((u * u * a[0] + 2 * u * t * b[0] + t * t * c[0],
                                u * u * a[1] + 2 * u * t * b[1] + t * t * c[1]))
        elif verb == V.kCubic_Verb:
            a, b, c, d = P[:4]
            n = seg(math.dist(a, b) + math.dist(b, c) + math.dist(c, d))
            for k in range(1, n + 1):
                t = k / n
                u = 1 - t
                cur.append((u ** 3 * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t ** 3 * d[0],
                            u ** 3 * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t ** 3 * d[1]))
        elif verb == V.kClose_Verb:
            closed = True
    if cur:
        contours.append((cur, closed))
    return contours


def warp(p, fn, step=2.0):
    """Apply a point function (x, y) → (x, y) to a path (flattened)."""
    res = skia.Path()
    for pts, closed in flatten(p, step):
        q = [fn(x, y) for x, y in pts]
        res.moveTo(*q[0])
        for xy in q[1:]:
            res.lineTo(*xy)
        if closed:
            res.close()
    res.setFillType(p.getFillType())
    return res


def arc_warp(p, width, amount, cx=None):
    """Bend a path along an arc (positive amount = arch upward at centre)."""
    b = p.computeTightBounds()
    cx = b.centerX() if cx is None else cx
    half = width / 2
    return warp(p, lambda x, y: (x, y - amount * (1 - ((x - cx) / half) ** 2)))


def svg_string(p):
    """Serialise a skia.Path to SVG path data."""
    out = []
    it = skia.Path.Iter(p, False)
    V = skia.Path.Verb
    while True:
        verb, pts = it.next()
        if verb == V.kDone_Verb:
            break
        f = lambda q: f"{q.x():.2f} {q.y():.2f}"
        if verb == V.kMove_Verb:
            out.append("M" + f(pts[0]))
        elif verb == V.kLine_Verb:
            out.append("L" + f(pts[1]))
        elif verb == V.kQuad_Verb:
            out.append("Q" + f(pts[1]) + " " + f(pts[2]))
        elif verb == V.kConic_Verb:
            quads = skia.Path.ConvertConicToQuads(pts[0], pts[1], pts[2], it.conicWeight(), 2)
            for k in range(1, len(quads) - 1, 2):
                out.append("Q" + f(quads[k]) + " " + f(quads[k + 1]))
        elif verb == V.kCubic_Verb:
            out.append("C" + f(pts[1]) + " " + f(pts[2]) + " " + f(pts[3]))
        elif verb == V.kClose_Verb:
            out.append("Z")
    return "".join(out)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def fit_matrix(bounds, W, H, margin_x, margin_y, max_scale=None):
    bw, bh = bounds.width(), bounds.height()
    s = min((W - 2 * margin_x) / bw, (H - 2 * margin_y) / bh)
    if max_scale:
        s = min(s, max_scale)
    m = skia.Matrix()
    m.setTranslate(-bounds.centerX(), -bounds.centerY())
    m.postScale(s, s)
    m.postTranslate(W / 2, H / 2)
    return m, s


def gradient_bg(canvas, W, H, top=MAROON_TOP, bottom=MAROON_DEEP):
    paint = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, H)], [hexc(top), hexc(bottom)]))
    canvas.drawRect(skia.Rect.MakeWH(W, H), paint)


def render_layers(layers, W, H, bg, out=None, margin=0.14, gradient=False, bounds=None,
                  max_scale=None, label=None, label_color=None):
    """layers: list of (path, color_hex) drawn in order, sharing one fit."""
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    if gradient:
        gradient_bg(c, W, H)
    else:
        c.clear(hexc(bg))
    if bounds is None:
        b = None
        for p, _ in layers:
            tb = p.computeTightBounds()
            b = tb if b is None else skia.Rect(min(b.left(), tb.left()), min(b.top(), tb.top()),
                                                max(b.right(), tb.right()), max(b.bottom(), tb.bottom()))
        bounds = b
    m, s = fit_matrix(bounds, W, H, W * margin, H * margin, max_scale)
    c.save()
    c.concat(m)
    for p, col in layers:
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=hexc(col)))
    c.restore()
    if label:
        f = skia.Font(skia.Typeface("Helvetica Neue"), H * 0.028)
        c.drawString(label, W * 0.03, H - H * 0.04, f,
                     skia.Paint(AntiAlias=True, Color=hexc(label_color or "#888888", 200)))
    img = surf.makeImageSnapshot()
    if out:
        img.save(out, skia.kPNG)
    return img


def save_svg(layers, out, pad=40):
    b = None
    for p, _ in layers:
        tb = p.computeTightBounds()
        b = tb if b is None else skia.Rect(min(b.left(), tb.left()), min(b.top(), tb.top()),
                                            max(b.right(), tb.right()), max(b.bottom(), tb.bottom()))
    x, y, w, h = b.left() - pad, b.top() - pad, b.width() + 2 * pad, b.height() + 2 * pad
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}">']
    for p, col in layers:
        rule = "evenodd" if p.getFillType() == skia.PathFillType.kEvenOdd else "nonzero"
        parts.append(f'<path fill="{col}" fill-rule="{rule}" d="{svg_string(p)}"/>')
    parts.append("</svg>")
    open(out, "w").write("\n".join(parts))
