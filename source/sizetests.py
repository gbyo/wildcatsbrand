"""Minimum-size test sheets: screen (PNG, 1:1 pixels) and print/apparel (PDF, true size)."""
import os
import sys

import skia
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm  # noqa: E402
import brand as BR  # noqa: E402
import kit as K  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "production-tests")
SCREEN_MIN = {"primary": 240, "stacked": 140, "horizontal": 110, "wordmark": 80, "icon": 32}
HB = "/System/Library/Fonts/HelveticaNeue.ttc"


def pil(img):
    return Image.fromarray(img.convert(alphaType=skia.kUnpremul_AlphaType,
                                       colorType=skia.kRGBA_8888_ColorType).toarray()[..., :3])


def render_at(paths, width_px, fg, bg):
    b = K.bounds(paths)
    h = max(1, round(width_px * b.height() / b.width()))
    surf = skia.Surface(width_px + 8, h + 8)
    c = surf.getCanvas()
    c.clear(wm.hexc(bg))
    K.draw(c, paths, fg, (width_px + 8) / 2, (h + 8) / 2, width=width_px)
    return pil(surf.makeImageSnapshot())


def screen_sheet(screen_min=SCREEN_MIN, name="screen-size-test.png"):
    """Each mark at 25% below / at / 25% above its minimum width, 1:1 pixels,
    on white and on maroon, plus an enlarged (nearest-neighbour) copy."""
    f1 = ImageFont.truetype(HB, 26, index=1)
    f2 = ImageFont.truetype(HB, 19)
    blocks = []
    for key, mn in screen_min.items():
        paths = BR.as_paths(BR.MARKS[key]())
        zoom = 2 if mn >= 140 else 4
        cells = []
        for tag, wpx in (("25% below", round(mn * 0.75)), ("minimum", mn), ("25% above", round(mn * 1.25))):
            a = render_at(paths, wpx, K.COLORS["maroon"], K.COLORS["white"])
            b = render_at(paths, wpx, K.COLORS["cream"], K.COLORS["maroon"])
            z = a.resize((a.width * zoom, a.height * zoom), Image.NEAREST)
            cells.append((f"{tag}: {wpx} px", a, b, z, zoom))
        blocks.append((key, mn, cells))
    W = 3300
    H = 40 + sum(80 + max(c[3].height for c in cells) + 50 for _, _, cells in blocks)
    S = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(S)
    y = 30
    for key, mn, cells in blocks:
        d.text((30, y), f"{key.capitalize()}  ·  current minimum {mn} px wide", font=f1, fill=(25, 18, 20))
        y += 44
        x = 30
        rowh = max(c[3].height for c in cells)
        for tag, a, b, z, zoom in cells:
            d.text((x, y), f"{tag}   (actual size, then {zoom}x)", font=f2, fill=(110, 100, 102))
            S.paste(a, (x, y + 30))
            S.paste(b, (x, y + 40 + a.height))
            S.paste(z, (x + a.width + 16, y + 30))
            x += max(a.width + z.width + 70, 420)
        y += rowh + 90
    S.save(os.path.join(OUT, name))


# --------------------------------------------------------------------------
# Print and apparel test artwork (US Letter PDF, drawn at true size)
# --------------------------------------------------------------------------
import guide as G  # noqa: E402

# planning minimums (inches) for v1.1, from the thinnest features in the
# artwork and the process limits below; see the guide's Minimum Sizes page
PROCESS = {
    "print": ("Office and offset printing", "0.15 mm lines, 0.20 mm gaps",
              {"primary": 1.5, "stacked": 1.0, "horizontal": 1.0, "wordmark": 0.8, "icon": 0.3}),
    "screen": ("Screen printing", "0.5 mm lines, 0.75 mm gaps",
               {"primary": 4.5, "horizontal": 3.75, "wordmark": 3.0, "icon": 0.75}),
    "vinyl": ("Vinyl and heat-transfer cutting", "1.0 mm lines and gaps",
              {"stacked": 4.25, "horizontal": 5.0, "wordmark": 4.0, "icon": 1.0}),
    "embroidery": ("Embroidery", "1.0 mm satin stitches, 1.2 mm gaps",
                   {"horizontal": 6.0, "wordmark": 4.75, "icon": 1.25}),
}
CHECKS = {
    "print": ["Print this page at 100% (no 'fit to page') on the printer you normally use.",
              "At the minimum size, NINETY SIX in the primary logo should be readable.",
              "The C and A in WILDCATS and the 9 and 6 in the box should not touch.",
              "If the minimum fails on your printer, use the 25% larger size as your minimum."],
    "screen": ["Send this page to the printer as the test file; ask for a one-color test print or proof.",
               "Check that the gap between C and A and between 9 and 6 stays open after ink spread.",
               "Check that the rails and NINETY SIX in the primary logo hold their full length and weight.",
               "Record the smallest size that passes; that becomes the screen-printing minimum."],
    "vinyl": ["Cut each size once in the vinyl you will use.",
              "Check that the counters in 9 and 6 and the C-A gap weed cleanly without tearing.",
              "Check that small pieces (the inside of the A, the counters) stay attached to the transfer.",
              "Record the smallest size that passes."],
    "embroidery": ["Ask the embroiderer for a sew-out of each size on the garment you will use.",
                   "Digitizers may widen gaps slightly; check the result still matches the artwork.",
                   "Check that the 96 inside the box reads clearly and the box edges stay straight.",
                   "For left-chest logos (about 3.5 in wide), test the icon and the wordmark first.",
                   "Record the smallest size that passes."],
}


def _layout():
    """Lay out every process into pages. Returns a list of pages; each page is
    a list of (kind, data) drawing instructions in 200-dpi page coordinates."""
    W, H, M = G.W, G.H, G.M
    CW = W - 2 * M
    bottom = H - 170
    pages = []
    for n, (key, (title, limits, mins)) in enumerate(PROCESS.items(), 1):
        page = [("title", (f"Size test {n}: {title}", f"Planning limits used: {limits}. "
                           "Print at 100%. Sizes are logo widths."))]
        y = 330
        for mark, mn in mins.items():
            paths = BR.as_paths(BR.MARKS[mark]())
            b = K.bounds(paths)
            factors = (0.75, 1.0, 1.25) if key == "print" else (0.8, 1.0, 1.2)
            items = []
            for tag, f in zip(("smaller", "minimum", "larger"), factors):
                w_ = G.inch(mn * f)
                if w_ <= CW:
                    items.append((tag, mn * f, w_, w_ * b.height() / b.width()))
            # rows of items that fit the width
            rows, row, x = [], [], 0
            for it in items:
                adv = max(it[2] + 80, 330)
                if row and x + it[2] > CW:
                    rows.append(row)
                    row, x = [], 0
                row.append((x, it))
                x += adv
            rows.append(row)
            block_h = 40 + sum(max(it[3] for _, it in r) + 110 for r in rows)
            if y + block_h > bottom:
                pages.append(page)
                page = [("title", (f"Size test {n}: {title} (continued)", ""))]
                y = 330
            page.append(("label", (f"{mark.capitalize()}   minimum {mn:g} in", y)))
            y += 40
            for r in rows:
                rh = max(it[3] for _, it in r)
                for x, (tag, inches, w_, h_) in r:
                    page.append(("mark", (paths, M + x, y, w_, h_, f"{tag}  {inches:.2f} in")))
                y += rh + 110
        checks_h = 60 + 52 * len(CHECKS[key])
        if y + checks_h > bottom:
            pages.append(page)
            page = [("title", (f"Size test {n}: {title} (continued)", ""))]
            y = 330
        page.append(("checks", (key, max(y + 20, bottom - checks_h))))
        pages.append(page)
    return pages


def _draw_page(c, page):
    W, H, M = G.W, G.H, G.M
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=wm.hexc("#FFFFFF")))
    for kind, d in page:
        if kind == "title":
            G.text(c, d[0], M, 190, G.Style(G.COND, 72, G.INK))
            if d[1]:
                G.text(c, d[1], M, 250, G.DESC)
        elif kind == "label":
            G.text(c, d[0], M, d[1], G.NAME)
        elif kind == "mark":
            paths, x, y, w_, h_, cap = d
            K.draw(c, paths, K.COLORS["black"], x + w_ / 2, y + h_ / 2, width=w_)
            G.text(c, cap, x, y + h_ + 40, G.MINW)
        elif kind == "checks":
            key, y = d
            G.text(c, "What to check", M, y, G.NAME)
            for line in CHECKS[key]:
                y = G.para(c, "\u2022  " + line, M, y + 50, W - 2 * M, G.DESC, lh=1.3) - 30
    G.text(c, "Ninety Six Wildcats production test", M, H - 80, G.FOOT)
    G.text(c, "Planning limits, not validated results. Record what passes physically.",
           W - M, H - 80, G.FOOT, align="right")


def print_tests(out, png_dir=None):
    pages = _layout()
    stream = skia.FILEWStream(out)
    with skia.PDF.MakeDocument(stream) as doc:
        for page in pages:
            with doc.page(612, 792) as c:
                c.scale(612 / G.W, 792 / G.H)
                _draw_page(c, page)
    stream.flush()
    if png_dir:
        for k, page in enumerate(pages, 1):
            surf = skia.Surface(G.W, G.H)
            _draw_page(surf.getCanvas(), page)
            surf.makeImageSnapshot().save(os.path.join(png_dir, f"test-{k}.png"), skia.kPNG)
    return len(pages)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    screen_sheet()
    print("screen sheet")
    print_tests(os.path.join(OUT, "print-and-apparel-size-tests.pdf"), png_dir=sys.argv[1] if len(sys.argv) > 1 else None)
    print("print tests")
