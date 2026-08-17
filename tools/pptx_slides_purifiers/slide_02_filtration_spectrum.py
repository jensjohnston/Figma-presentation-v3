"""Slide 02 -- Filtration Spectrum. Figma node 61219:17971 (canvas "All purifiers").

Near-identical to the main deck's slide_09_filtration_spectrum.py (same column
copy, same divider geometry) -- just a different background photo and a
renumbered meta (Figma's own page label read "2/14", a stale artifact of a
larger unbuilt sequence; renumbered to 02/08 to match this standalone deck).

A stray text node (id 61219:17973, generic hydration marketing copy) sits at
x=2886, entirely off the 1920px-wide frame -- excluded as invisible/orphaned.
"""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rect, add_label_with_mark, FONT_MEDIUM, FONT_SEMIBOLD

_GRAY_800 = "#27272a"
_GRAY_500 = "#71717a"
_BLUE_600 = "#2563eb"

_COLUMNS = [
    (48, "Particle filtration", ">1000-1.0 µm", 438, _GRAY_500),
    (359, "Microfiltration", ">1.0-0.1 µm", 436, _GRAY_500),
    (687, "Ultrafiltration", ">0.1-0.01 µm", 436, _GRAY_500),
    (1002.5, "Nanofiltration", ">0.01-0.001 µm", 436, _GRAY_500),
    (1319, "Reverse osmosis", ">0.001-0.0001 µm", 436, _GRAY_500),
]

_DIVIDERS = [
    (64, 541, 487),
    (305, 483.94, 546.059),
    (618, 481.98, 549.016),
    (946, 482, 550.001),
    (1623, 484, 545),
    (1262, 486, 542),
]


def build(prs, assets_dir):
    slide = new_slide(prs)

    add_picture(slide, f"{assets_dir}/slide_02/background.png", 0, 0, 1920, 1080)

    for x, y, h in _DIVIDERS:
        add_rect(slide, x - 1, y, 2, h, "#e4e4e7")

    add_meta(slide, "Bluewater Purifiers · 2026", "02/09")

    add_text(
        slide, 48, 115, 1164, 90,
        [[("Every filter has a limit.", FONT_SEMIBOLD, 80, "#18181b", 1.0)]],
    )

    add_text(
        slide, 1463, 119, 414, 72,
        [[
            ("Bluewater SuperiorOsmosis", FONT_MEDIUM, 30, _GRAY_500, 1.2),
            ("™", FONT_MEDIUM, 30, _GRAY_500, 1.2),
            (" technology removes them all.", FONT_MEDIUM, 30, _GRAY_500, 1.2),
        ]],
    )

    for x, label, spec, spec_top, spec_color in _COLUMNS:
        add_text(
            slide, x, 399, 280, 40,
            [[(label, FONT_SEMIBOLD, 24, _GRAY_800, 1.34)]],
        )
        add_text(
            slide, x, spec_top, 280, 30,
            [[(spec, FONT_MEDIUM, 24, spec_color, 1.34)]],
        )

    add_label_with_mark(
        slide, 1642, 399, "SuperiorOsmosis", FONT_SEMIBOLD, 24, _BLUE_600,
        "™", FONT_MEDIUM, 15, w=280, h=40, line_spacing=1.34,
    )
    add_text(
        slide, 1642, 438, 280, 30,
        [[(">0.0001 µm", FONT_MEDIUM, 24, _GRAY_800, 1.34)]],
    )

    return slide
