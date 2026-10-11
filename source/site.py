"""
Builds the data and images for the GitHub Pages site (index.html at the
repository root).

  site/data.js        asset list the page reads (logos, teams, templates, pages)
  site/thumbs/        small previews of templates and guideline pages
  site/og.png         1200 x 630 link-preview image
Run after kit.py, templates.py and guide11.py:  python site.py
"""
import json
import os
import sys

import skia
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand as BR  # noqa: E402
import kit as K  # noqa: E402
import templates as T  # noqa: E402
import guide11 as G11  # noqa: E402

ROOT = K.ROOT
SITE = os.path.join(ROOT, "site")

MARKS = [
    ("primary", "Primary", "TV slides, posters, signs, and the back of shirts.", "1.5 in / 240 px", "wildcats"),
    ("horizontal", "Horizontal", "Narrow or small spaces: web headers, letterhead, merchandise.", "1 in / 110 px",
     "wildcats"),
    ("stacked", "Stacked", "Square spaces and social media posts.", "1 in / 140 px", "wildcats"),
    ("wordmark", "Wordmark", "When 96 already appears nearby, or space is very limited.", "0.8 in / 80 px",
     "wildcats"),
    ("icon", "Icon", "Profile pictures, website icons, sleeves, stickers, left chest.", "0.3 in / 32 px",
     "wildcats"),
]
SCHOOL = [
    ("hs-line", "School mark, one line", "Official letters, forms, and academic material.", "1.5 in / 240 px",
     "logos/institutional/ninetysix-hs-line-{color}"),
    ("hs-stacked", "School mark, stacked", "Official letters, forms, graduation programs.", "1 in / 140 px",
     "logos/institutional/ninetysix-hs-stacked-{color}"),
]
DISPLAY = {"NHS": "NHS", "Track & Field": "Track & Field"}
TEMPLATE_INFO = {
    "tv-slide": ("TV slide", "1920 x 1080 px"),
    "social-post": ("Social post", "1080 x 1080 px"),
    "instagram-story": ("Instagram story", "1080 x 1920 px"),
    "team-schedule": ("Team schedule", "1080 x 1350 px"),
    "event-poster-11x17": ("Event poster", "11 x 17 in"),
    "tshirt-concept": ("T-shirt concept", "Front and back"),
    "letterhead": ("Letterhead", "8.5 x 11 in"),
}
PAGE_TITLES = ["Cover", "Brand overview", "Brand architecture", "Primary marks", "Secondary marks",
               "Construction: primary", "Construction: 96 box", "Team and group logos", "Team logo examples",
               "Clear space", "Minimum sizes", "Colors", "Typography", "Slant panels", "Digital and TV",
               "Social media", "Print and apparel", "Do's and don'ts", "Files and naming"]


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def thumb(src, dst, width):
    im = Image.open(src).convert("RGB")
    h = round(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(dst, quality=84, optimize=True)
    return rel(dst), width, h


def og_image(out):
    W, H = 1200, 630
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    K.gradient(c, 0, 0, W, H)
    K.draw(c, BR.as_paths(BR.primary()), K.COLORS["cream"], W / 2, H / 2 - 10, width=760)
    surf.makeImageSnapshot().save(out, skia.kPNG)


def build():
    os.makedirs(os.path.join(SITE, "thumbs"), exist_ok=True)
    marks = [dict(id=k, name=n, use=u, min=m, group="Wildcats logos",
                  path=f"logos/{k}/wildcats-{k}-{{color}}") for k, n, u, m, _ in MARKS]
    marks += [dict(id=k, name=n, use=u, min=m, group="Ninety Six High School", path=p)
              for k, n, u, m, p in SCHOOL]

    teams = []
    for name in K.TEAMS:
        s = K.slug(name)
        lines, _, _ = BR.team_lines(name)
        teams.append(dict(
            id=s, name=DISPLAY.get(name, name.title()), lines=len(lines),
            horizontal=f"logos/teams/{s}/wildcats-team-{s}-horizontal-{{color}}",
            square=f"logos/teams/{s}/wildcats-team-{s}-square-{{color}}",
            profile=f"social/profile/teams/wildcats-profile-{s}.png"))

    profiles = [dict(name=n, path=f"social/profile/{f}") for n, f in [
        ("Cream on maroon", "wildcats-profile-icon-cream-on-maroon.png"),
        ("Cream on gradient", "wildcats-profile-icon-cream-on-gradient.png"),
        ("Maroon on cream", "wildcats-profile-icon-maroon-on-cream.png"),
        ("White on black", "wildcats-profile-icon-white-on-black.png"),
        ("96 Wildcats", "wildcats-profile-wildcats-cream-on-maroon.png")]]

    templates = []
    for key, _, _, is_print in T.TEMPLATES:
        d = os.path.join(ROOT, "templates", key)
        ex = os.path.join(d, f"wildcats-{key}-example.png")
        t, tw, th = thumb(ex, os.path.join(SITE, "thumbs", f"template-{key}.jpg"), 720)
        files = [("Example", rel(ex))]
        for label, fn in (("Blank", f"wildcats-{key}-blank.png"), ("Example PDF", f"wildcats-{key}-example.pdf"),
                          ("Blank PDF", f"wildcats-{key}-blank.pdf")):
            if os.path.exists(os.path.join(d, fn)):
                files.append((label, rel(os.path.join(d, fn))))
        name, size = TEMPLATE_INFO[key]
        templates.append(dict(id=key, name=name, size=size, thumb=t, tw=tw, th=th,
                              files=[dict(label=a, path=b) for a, b in files]))

    pages = []
    for i, nm in enumerate(G11.NAMES, 1):
        src = os.path.join(ROOT, "guidelines", "pages", f"{i:02d}_{nm}.png")
        t, _, _ = thumb(src, os.path.join(SITE, "thumbs", f"page-{i:02d}.jpg"), 340)
        pages.append(dict(n=i, title=PAGE_TITLES[i - 1], thumb=t, full=rel(src)))

    data = dict(
        version="1.1",
        repo="https://github.com/gbyo/wildcatsbrand",
        zip="https://github.com/gbyo/wildcatsbrand/archive/refs/heads/main.zip",
        guidelines="guidelines/Wildcats_Brand_Guidelines_v1.1.pdf",
        colors=[dict(id=k, name=k.title(), hex=v) for k, v in K.COLORS.items()],
        gradient=dict(top=K.GRAD_TOP, bottom=K.GRAD_BOTTOM),
        marks=marks, teams=teams, profiles=profiles, templates=templates, pages=pages)
    with open(os.path.join(SITE, "data.js"), "w") as f:
        f.write("// Generated by source/site.py. Do not edit by hand.\n")
        f.write("window.BRAND = " + json.dumps(data, indent=1) + ";\n")
    og_image(os.path.join(SITE, "og.png"))
    print("site data:", len(marks), "marks,", len(teams), "teams,", len(templates), "templates,",
          len(pages), "pages")


if __name__ == "__main__":
    build()
