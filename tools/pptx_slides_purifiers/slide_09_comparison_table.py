"""Slide 09 -- Purifier Comparison Table. Figma node 61219:17872.

Pure text table, no images -- header + 8 spec rows, each row a 20px cell for
the label (Semi Bold, #27272a) and three data cells (Regular, #3f3f46),
separated by 1px #e4e4e7 divider rules. Row/divider y-offsets are read
directly off Figma's own auto-layout geometry for this frame (gap-20
between elements, 67px row height, table origin at x=48,y=112) rather than
recomputed, to avoid compounding rounding error across 8 rows.
"""

from tools.pptx_core import new_slide, add_meta, add_text, add_rect, FONT_REGULAR, FONT_SEMIBOLD

_TABLE_X = 48
_COL_XS = [0, 464, 928, 1392]  # relative to _TABLE_X; C0 has no left padding, C1-3 have +8px
_LABEL_COLOR = "#27272a"
_DATA_COLOR = "#3f3f46"

_HEADER_Y = 112
_DIVIDER_YS = [192, 300, 408, 516, 624, 732, 840, 948]
_ROW_YS = [213, 321, 429, 537, 645, 753, 861, 969]

_HEADER = ["", "Cleone", "Spirit", "Pro"]

_ROWS = [
    ("Installation (W×D×H)", "235×400×436 mm", "170x385x482 mm", "245x480x486 mm"),
    ("Water purification rate", "99%", "99.7%", "99.7%"),
    ("Recovery rate", "50%", "70%", "80%"),
    ("Flow per day", "Up to 610 L/day", "Up to 3,800 L/day", "Up to 7,600 L/day"),
    ("Purification technology", "Reverse osmosis", ("SuperiorOsmosis", "™"), ("SuperiorOsmosis", "™")),
    ("Best for", "1–2 people", "Family home", "Large household"),
    ("Included", "Purifier, 12 L tank", "Purifier, no tank needed", "Purifier, no tank needed"),
    ("Certifications", "WQA - NSF/ANSI/CAN 372", "NSF/ANSI/CAN 372", "NSF/ANSI/CAN 372"),
]


def _cell(slide, col, row_top, value, font, color):
    x = _TABLE_X + _COL_XS[col] + (8 if col > 0 else 0)
    w = 424 if col == 0 else 416
    if isinstance(value, tuple):
        base, mark = value
        runs = [(base, font, 20, color, 1.34), (mark, font, 12.9, color, 1.34)]
    else:
        runs = [(value, font, 20, color, 1.34)]
    add_text(slide, x, row_top + 20, w, 30, [runs])


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Purifiers · 2026", "09/09")

    for col, label in enumerate(_HEADER):
        if label:
            _cell(slide, col, _HEADER_Y, label, FONT_SEMIBOLD, _LABEL_COLOR)

    for row_y, (label, c1, c2, c3) in zip(_ROW_YS, _ROWS):
        _cell(slide, 0, row_y, label, FONT_SEMIBOLD, _LABEL_COLOR)
        _cell(slide, 1, row_y, c1, FONT_REGULAR, _DATA_COLOR)
        _cell(slide, 2, row_y, c2, FONT_REGULAR, _DATA_COLOR)
        _cell(slide, 3, row_y, c3, FONT_REGULAR, _DATA_COLOR)

    for div_y in _DIVIDER_YS:
        add_rect(slide, _TABLE_X, div_y, 1824, 1, "#e4e4e7")

    return slide
