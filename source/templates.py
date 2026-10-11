"""
Application templates for the Ninety Six Wildcats identity (v1.1), all built
with one secondary graphic device: Slant Panels, parallelograms at the logo's
shear (0.12, 6.84 deg) taken from the 96 box.

  Panel types   tag    small solid panel holding a short upright label
                band   wide panel that runs off one or both page edges
                frame  photo container
Each template is saved as an example (with sample text) and a blank
background (panels and logo only) for adding text in Canva, Slides, etc.
Run:  python templates.py   -> templates/
"""
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import brand as BR  # noqa: E402
import kit as K  # noqa: E402
import guide as G  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
SH = BR.SPEC["shear"]
MAROON, CREAM, BLACK, WHITE = K.COLORS["maroon"], K.COLORS["cream"], K.COLORS["black"], K.COLORS["white"]
PHOTO = "#2B1012"           # placeholder tone for photo frames (replaced by a photo in use)


# --------------------------------------------------------------------------
# Type styles (sizes in px of the canvas being drawn)
# --------------------------------------------------------------------------
def display(size, color):
    return G.Style(G.COND, size, color, 0.01)


def heading(size, color):
    return G.Style(G.SAIRA, size, color, 0.0, wdth=100, wght=700)


def body(size, color):
    return G.Style(G.SAIRA, size, color, 0.0, wdth=100, wght=400)


def label(size, color):
    return G.Style(G.SAIRA, size, color, 0.12, True, wdth=100, wght=600)


def lines(c, txt, x, y, st, lh=0.92, align="left"):
    for k, ln in enumerate(txt.split("\n")):
        G.text(c, ln, x, y + k * st.size * lh, st, align=align)
    return y + (len(txt.split("\n")) - 1) * st.size * lh


# --------------------------------------------------------------------------
# Slant Panels
# --------------------------------------------------------------------------
def panel_path(x, y, w, h):
    """Parallelogram: bottom edge x..x+w at y+h, top edge shifted right by SH*h."""
    p = skia.Path()
    p.moveTo(x + SH * h, y)
    p.lineTo(x + w + SH * h, y)
    p.lineTo(x + w, y + h)
    p.lineTo(x, y + h)
    p.close()
    return p


def panel(c, x, y, w, h, color):
    c.drawPath(panel_path(x, y, w, h), skia.Paint(AntiAlias=True, Color=wm.hexc(color)))


def frame(c, x, y, w, h, label_color=CREAM):
    """Photo frame placeholder."""
    panel(c, x, y, w, h, PHOTO)
    st = label(max(14, int(h * 0.035)), label_color)
    G.text(c, "Photo", x + SH * h * 0.5 + w / 2, y + h / 2 + st.size * 0.35, st, align="center",
           alpha=110)


def tag(c, txt, x, y, h, bg, fg):
    """Tag: text cap height 50% of the panel height, side padding 35%."""
    st = G.Style(G.COND, h * 0.5 / 0.688, fg, 0.02)
    tw = G.shaped(txt.upper(), st)[1]
    w = tw + 0.7 * h
    panel(c, x, y, w, h, bg)
    G.text(c, txt.upper(), x + 0.35 * h + SH * h * 0.5, y + h * 0.75, st)
    return w


def gradient(c, W, H):
    K.gradient(c, 0, 0, W, H)


def logo(c, fn, color, x, y, width=None, height=None):
    """Place a mark by its top-left corner."""
    paths = BR.as_paths(fn() if callable(fn) else fn)
    b = K.bounds(paths)
    s = width / b.width() if width else height / b.height()
    K.draw(c, paths, color, x + b.width() * s / 2, y + b.height() * s / 2, width=b.width() * s)
    return b.width() * s, b.height() * s


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------
def tv_slide(c, W, H, blank=False):
    gradient(c, W, H)
    m = 120                                   # inside 6% title-safe area
    frame(c, 1150, -10, 900, H + 20)
    logo(c, BR.horizontal, CREAM, m, H - m - 52, height=52)
    if blank:
        return
    tag(c, "This Friday", m, 190, 62, CREAM, MAROON)
    lines(c, "HOMECOMING\nPEP RALLY", m, 410, display(168, CREAM))
    G.text(c, "2:45 PM  ·  Main Gym", m, 650, heading(52, CREAM))
    G.para(c, "Wear maroon and bring your loudest voice. Seniors sit on the floor.", m, 730, 860,
           body(36, "#EBD9C6"))


def social_post(c, W, H, blank=False):
    c.clear(wm.hexc(MAROON))
    frame(c, -120, -10, 1000, 480)
    logo(c, lambda: BR.team("Football"), CREAM, 80, H - 80 - 58, height=58)
    if blank:
        return
    tag(c, "Game day", 80, 520, 56, CREAM, MAROON)
    lines(c, "WILDCATS\nVS. OPPONENT", 80, 700, display(112, CREAM), lh=0.95)
    G.text(c, "Friday  ·  7:30 PM  ·  Home", 80, 870, heading(40, "#EBD9C6"))


def story(c, W, H, blank=False):
    gradient(c, W, H)
    m = 80
    frame(c, -100, 880, 1260, 520)
    logo(c, BR.icon, CREAM, W / 2 - 60, H - 260 - 93, width=120)   # clear of the reply bar
    if blank:
        return
    tag(c, "Save the date", m, 280, 60, CREAM, MAROON)
    lines(c, "SPIRIT\nWEEK", m, 540, display(210, CREAM), lh=0.9)
    G.text(c, "Oct 20 – 24", m, 820, heading(56, CREAM))
    G.para(c, "A different theme every day. Full list on the school website.", m, 1480, W - 2 * m,
           body(40, "#EBD9C6"))


def schedule(c, W, H, blank=False):
    c.clear(wm.hexc(MAROON))
    m = 80
    logo(c, lambda: BR.team("Volleyball"), CREAM, m, 90, height=78)
    panel(c, -40, H - 120, W + 80, 120, BLACK)
    if blank:
        return
    G.text(c, "2026 SEASON SCHEDULE", m, 250, label(30, "#EBD9C6"))
    games = [("Aug 25", "Opponent School", "Home", "6:00"), ("Aug 28", "Opponent School", "Away", "6:00"),
             ("Sep 2", "Opponent School", "Home", "5:30"), ("Sep 9", "Opponent School", "Away", "6:00"),
             ("Sep 11", "Opponent School", "Home", "6:00"), ("Sep 16", "Opponent School", "Home", "5:30"),
             ("Sep 23", "Opponent School", "Away", "6:00"), ("Sep 30", "Senior Night", "Home", "6:00")]
    y = 320
    for d, opp, ha, t in games:
        tag(c, d, m, y, 58, CREAM if ha == "Home" else BLACK, MAROON if ha == "Home" else CREAM)
        G.text(c, ("vs. " if ha == "Home" else "at ") + opp, m + 250, y + 42, heading(36, CREAM))
        G.text(c, f"{t} PM", W - m, y + 42, body(34, "#EBD9C6"), align="right")
        y += 98
    G.text(c, "Home games in cream", m, H - 48, label(24, "#EBD9C6"))
    G.text(c, "NINETY SIX WILDCATS", W - m, H - 48, label(24, CREAM), align="right")


def poster(c, W, H, blank=False):
    """11 x 17 in at 200 dpi."""
    c.clear(wm.hexc(CREAM))
    m = 170
    panel(c, -60, 0, W + 120, 760, MAROON)
    logo(c, BR.primary, CREAM, m, 230, width=1180)
    frame(c, m, 1580, W - 2 * m, 980, CREAM)
    panel(c, -60, H - 230, W + 120, 230, MAROON)
    if blank:
        return
    tag(c, "Friday, Nov 7", m, 900, 110, MAROON, CREAM)
    lines(c, "FALL SPIRIT\nNIGHT", m, 1230, display(270, MAROON), lh=0.9)
    G.para(c, "Food trucks, the marching band, and the first look at this year's teams. "
              "Free for students and families.", m, 2680, W - 2 * m, body(54, "#4A1517"))
    G.text(c, "6:00 PM  ·  Wildcat Stadium", m, 2960, heading(64, MAROON))
    G.text(c, "NINETY SIX HIGH SCHOOL", m, H - 95, label(44, CREAM))
    G.text(c, "Website or contact info", W - m, H - 95, body(44, "#EBD9C6"), align="right")


def tee(c, W, H, blank=False):
    """T-shirt concept: front (left chest icon) and back (primary)."""
    c.clear(wm.hexc("#E8E3DD"))

    def shirt(cx, top, s, color):
        p = skia.Path()
        pts = [(-250, 40), (-130, -40), (-55, -55), (0, 0), (55, -55), (130, -40), (250, 40), (205, 150),
               (155, 120), (160, 520), (-160, 520), (-155, 120), (-205, 150)]
        p.moveTo(cx + pts[0][0] * s, top + pts[0][1] * s)
        for x, y in pts[1:]:
            p.lineTo(cx + x * s, top + y * s)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=wm.hexc(color)))
        neck = skia.Path()
        neck.addOval(skia.Rect.MakeXYWH(cx - 55 * s, top - 75 * s, 110 * s, 80 * s))
        c.drawPath(neck, skia.Paint(AntiAlias=True, Color=wm.hexc("#E8E3DD")))
    s = 1.5
    shirt(W * 0.27, 230, s, MAROON)
    shirt(W * 0.73, 230, s, MAROON)
    # front: left-chest icon (wearer's left = viewer's right), about 3.5 in on a real shirt
    logo(c, BR.icon, CREAM, W * 0.27 + 45 * s, 230 + 60 * s, width=62 * s)
    # back: primary logo across the shoulders, about 11 in wide on a real shirt
    logo(c, BR.primary, CREAM, W * 0.73 - 120 * s, 230 + 70 * s, width=240 * s)
    st = label(26, "#5A4B4E")
    G.text(c, "Front: 96 icon, left chest", W * 0.27, H - 60, st, align="center")
    G.text(c, "Back: primary logo", W * 0.73, H - 60, st, align="center")


def letterhead(c, W, H, blank=False):
    """US Letter at 200 dpi."""
    c.clear(wm.hexc(WHITE))
    m = 150
    logo(c, lambda: BR.institutional("stacked"), MAROON, m, 150, height=110)
    c.drawRect(skia.Rect.MakeXYWH(m, 330, W - 2 * m, 4), skia.Paint(Color=wm.hexc(MAROON)))
    G.text(c, "Street Address  ·  City, State ZIP  ·  Phone  ·  Website", m, H - 110, body(26, "#857B7E"))
    if blank:
        return
    G.text(c, "Date", m, 470, body(32, "#1C1517"))
    y = G.para(c, "Dear Families,", m, 560, W - 2 * m, body(32, "#1C1517"))
    for p in ["This is sample body text set in Saira Regular at 11 pt with 1.45 line spacing. "
              "Formal letters, academic material and administrative notices use the Ninety Six High "
              "School mark, not the athletic WILDCATS logos.",
              "Keep letters simple: one color for the mark, black text, and generous margins. "
              "The slant panels and athletic logos are not used on formal documents."]:
        y = G.para(c, p, m, y + 30, W - 2 * m, body(32, "#1C1517"), lh=1.45)
    G.para(c, "Sincerely,", m, y + 60, W - 2 * m, body(32, "#1C1517"))


TEMPLATES = [
    # name, function, size, print?
    ("tv-slide", tv_slide, (1920, 1080), False),
    ("social-post", social_post, (1080, 1080), False),
    ("instagram-story", story, (1080, 1920), False),
    ("team-schedule", schedule, (1080, 1350), False),
    ("event-poster-11x17", poster, (2200, 3400), True),
    ("tshirt-concept", tee, (1800, 1300), False),
    ("letterhead", letterhead, (1700, 2200), True),
]


def render(fn, W, H, out, blank=False):
    surf = skia.Surface(W, H)
    fn(surf.getCanvas(), W, H, blank=blank)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def render_pdf(fn, W, H, out, blank=False, dpi=200):
    stream = skia.FILEWStream(out)
    with skia.PDF.MakeDocument(stream) as doc:
        with doc.page(W * 72 / dpi, H * 72 / dpi) as c:
            c.scale(72 / dpi, 72 / dpi)
            fn(c, W, H, blank=blank)
    stream.flush()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn, (W, H), is_print in TEMPLATES:
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        render(fn, W, H, os.path.join(d, f"wildcats-{name}-example.png"))
        if name != "tshirt-concept":
            render(fn, W, H, os.path.join(d, f"wildcats-{name}-blank.png"), blank=True)
        if is_print:
            render_pdf(fn, W, H, os.path.join(d, f"wildcats-{name}-example.pdf"))
            render_pdf(fn, W, H, os.path.join(d, f"wildcats-{name}-blank.pdf"), blank=True)
        print(name)
