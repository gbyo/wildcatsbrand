# Ninety Six Wildcats Identity: Audits

- [v1.2: Social templates and profile pictures](#v12-social-templates-and-profile-pictures)
- [v1.0 audit, with the changes made in v1.1](#v10-audit-with-the-changes-made-in-v11)

## v1.2: Social templates and profile pictures

A review of the social media templates and profile pictures, rendered from the build and viewed at real phone sizes. The logo geometry did not change. Boards are in `audit/social/`.

### What failed in v1.1

- **Profile pictures** (`02`, `03`). Team pictures were the square team logo at 70% of the canvas. At 32–48 px, the size of comments and feed headers, the 96 was 2–3.5 px tall and read as a blank chip, and team names had a 4–6 px cap height.
- **Social templates** (`01`). They were three separate examples, not a family. Photos sat in a dark box (44% of the post, 27% of the story), nothing adjusted to longer text, the footer logo competed with the headline, and nearly every canvas was solid maroon. Instagram's profile grid crops posts to 3:4, which cut the 1:1 post's left-aligned text.

### Profile pictures

Six layouts were tested in circles at 180, 96, 64, 48 and 32 px (`04`) and in context (`05`). In comments and feed headers the username sits next to the picture, so the picture mainly has to read as 96. In the story tray, usernames are cut to about ten characters, so a team needs a word of its own there.

| Account | Layout |
|---|---|
| Main account | The 96 alone, as large as the circle allows |
| Sports and groups with a one-word name | The 96 box, fixed size and position, with the name under it: FOOTBALL, BAND, NHS |
| Established short forms | The same, using the form the team already uses: XC for Cross Country, TRACK, BAND. No invented abbreviations |
| Clubs without a one-word name | The full name under a smaller 96: Academic Team, Student Council |

The rules are in `AVATAR_LABELS` and `AVATAR` in `source/kit.py`. Final set: `10_v1.2_profile_pictures.jpg`.

### Social templates

Three directions were tested with the same awkward content (`06`–`08`): a two-word headline, a nine-word headline, an academic notice, portrait and landscape photos, no photo, a long opponent, an eight-event schedule, and a three-digit double-overtime score. `09` shows them as Instagram grid tiles and in the feed.

- **Number Box** (chosen). The date or score sits in a slant panel proportioned like the 96 box. Scores read even as grid tiles.
- **Type & Field.** Cream and typographic. Strong for announcements, but less distinctive.
- **Full Bleed.** Photo-led. Fails without a photo.

v1.2 has five post layouts (announcement, photo, game or event, result, schedule) at 1080 x 1350 and a story at 1080 x 1920, built by `source/social.py`. Headlines size themselves to fit. Announcements are maroon for spirit and athletics and cream for academic and family news. Photos fill their space instead of sitting in a frame.

### Editable files

The templates are also written as PowerPoint files (`templates/social/*.pptx`). They have real text boxes, slant panels as shapes, and photos that can be replaced. They open in PowerPoint, Keynote and Google Slides, and Canva can import them. A layered PSD was considered and rejected. The Python tools can only write PSDs with flattened pixel layers, so the text would not be editable.

## v1.0 audit, with the changes made in v1.1

This is a review of the v1.0 logo kit and guidelines before any v1.1 changes. All measurements are taken from the artwork files. The team-name rules are tested in `audit/team_system_test.png`. **C** is the cap height of WILDCATS; **H** is the height of the 96 box.

### Keep unchanged

These parts are working well and stay as they are:

- **WILDCATS**: Saira Condensed Black with a single slant. It's bold, readable and athletic without falling back on varsity clichés.
- **The 96 box.** It's the most distinctive piece of the identity, and the same shape works as an icon, inside the horizontal logo, and for team names.
- **Color**: maroon and cream as the core pair, with black and white for one-color printing. All four logos work in a single color.
- **The marks themselves**: primary, horizontal, stacked, wordmark and icon. No new marks are needed.
- **The stacked logo.** Its NINETY SIX uses a different font from the primary. I tested switching it to Saira ExtraBold for consistency, and the result was weaker (`audit/stacked_study.png`). It stays as it is, and the difference is now documented as deliberate.
- **The team-name idea**: the 96 box with the team name in place of WILDCATS.

### Inconsistencies found

| # | Issue | Impact |
|---|---|---|
| 1 | Primary rails were 0.060C thick, while NINETY SIX strokes are 0.073C. | The rails looked lighter than the letters next to them. |
| 2 | The gap between the rails and NINETY SIX (0.13C) was about the same as the gaps between its letters (0.08–0.12C). | The rails read like part of the word ("—NINETY SIX—"). |
| 3 | The rails ended at the outer edge of the whole word. The S bulges 0.04C past its top corner, so the right rail overhung. NINETY SIX was centered on the bounding box, not the rail span. | The rails were unequal (a 0.02C difference). |
| 4 | Two-line team logos used a different box (numerals 60% of the box height, 13% padding) from the icon (64%, 17%). The square layout used 66%. | Three slightly different 96 boxes existed. |
| 5 | The guide said the slant was "7 degrees". The artwork uses a shear of 0.12, which is 6.84°. | Anyone rebuilding the logo from the guide would get it slightly wrong. |
| 6 | The guide said NINETY SIX is Saira ExtraBold. The stacked logo uses Saira Condensed Black. | The exception wasn't documented. |
| 7 | Team names didn't use WILDCATS' spacing adjustments. | Matching letter pairs were spaced differently in team logos. |

### Things that relied on eyeballing

None of these had documented values: the slant, tracking, kerning, the custom A, the size of NINETY SIX, all vertical and horizontal spacing, rail weight and length, the box proportions and padding, the box-to-name gap, and line spacing for two-line names. v1.1 defines every one of them as a ratio of C or H (see `brand.py` and the Construction pages of the guide).

### Reproduction risks

The thinnest features in the artwork are what limit how small each logo can go:

| Feature | Width | Where |
|---|---|---|
| Gap between C and A in WILDCATS | **0.034C** (v1.0) | every mark with WILDCATS |
| Gaps inside the E in NINETY SIX | 0.038C | primary only |
| Gap between 9 and 6 | 0.055H | icon, horizontal, team logos |
| Counter of the 9 and 6 | 0.070H | icon, horizontal, team logos |
| NINETY SIX stroke, rails | 0.073C | primary only |

- The C–A gap was the single weakest point. It closes up in small print, screen printing, vinyl and embroidery.
- NINETY SIX in the primary is about a quarter the height of WILDCATS, so the primary can't go as small as the other marks on apparel. v1.0 gave one minimum size for screen use only.

### Edge cases not covered in v1.0

- Long names (National Honor Society), names of three or more words, ampersands, abbreviations, clubs as opposed to teams, and JV/varsity labels.
- Formal and academic use, where the athletic WILDCATS treatment isn't appropriate.
- Production minimums for embroidery, screen printing and vinyl.
- Which color combinations are not allowed (maroon on the TV gradient is as low as 1.4:1; maroon on black is 1.64:1).
- File naming, PDF versions, and any guidance for layouts and type beyond the logo itself.

### Changes made in v1.1

Only four changes to the artwork are justified. Each has a before/after comparison:

1. **Primary rails** (`audit/change1_primary_rails.png`). Rails now match the NINETY SIX stroke weight (0.073C). The rail gap is 0.19C, the same as the gap between NINETY SIX and WILDCATS. The rails end at the top corners of W and S and are exactly equal in length. Fixes 1–3.
2. **C–A spacing** (`audit/change2_ca_spacing.png`). The C–A pair is tightened 10/1000 em instead of 25/1000 em, which widens the gap from 0.034C to 0.054C. That matches the 9–6 gap, so the system has one consistent minimum gap. The difference is barely visible at large sizes.
3. **One 96 box everywhere** (`audit/change3_team_box.png`). The numerals are 64% of the box height, with 17% padding, in every layout. Fixes 4.
4. **Team names use WILDCATS' spacing adjustments.** Fixes 7.

The remaining issues are documentation fixes (5, 6) or new guidance (edge cases), not design changes.
