"""Slide 09 -- Filtration Spectrum. Figma node 64346:5608."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rect, FONT_MEDIUM, FONT_SEMIBOLD

_GRAY_800 = "#27272a"
_GRAY_500 = "#71717a"
_BLUE_600 = "#2563eb"

# (x, label, spec_text, spec_top, spec_color)
_COLUMNS = [
    (48, "Particle filtration", ">1000-1.0 µm", 438, _GRAY_500),
    (359, "Microfiltration", ">1.0-0.1 µm", 436, _GRAY_500),
    (687, "Ultrafiltration", ">0.1-0.01 µm", 436, _GRAY_500),
    (1002.5, "Nanofiltration", ">0.01-0.001 µm", 436, _GRAY_500),
    (1319, "Reverse osmosis", ">0.001-0.0001 µm", 436, _GRAY_500),
]

# Thin vertical divider lines between columns: (x_center, y_top, height).
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

    # Full-bleed background: a photo of particulate-laden water fading to clean water,
    # confined to the lower half of an otherwise white frame (screenshot of the
    # isolated background node 64346:5609, which already spans the whole 1920x1080
    # canvas).
    add_picture(slide, f"{assets_dir}/slide_09/background.png", 0, 0, 1920, 1080)

    for x, y, h in _DIVIDERS:
        add_rect(slide, x - 1, y, 2, h, "#e4e4e7")

    add_meta(slide, "Bluewater Technology", "09/33")

    add_text(
        slide, 48, 115, 1164, 90,
        [[("Every filter has a limit.", FONT_SEMIBOLD, 80, "#18181b", 1.0)]],
    )

    add_text(
        slide, 1463, 119, 414, 72,
        [[
            ("Bluewater SuperiorOsmosis", FONT_MEDIUM, 30, _GRAY_500, 1.2),
            ("™", FONT_MEDIUM, 19, _GRAY_500, 1.2),
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

    # SuperiorOsmosis(TM) column -- heading in brand blue, spec in the darker gray800
    # (unlike the other five columns' gray500 spec).
    add_text(
        slide, 1642, 399, 280, 40,
        [[
            ("SuperiorOsmosis", FONT_SEMIBOLD, 24, _BLUE_600, 1.34),
            ("™", FONT_MEDIUM, 15, _BLUE_600, 1.34),
        ]],
    )
    add_text(
        slide, 1642, 438, 280, 30,
        [[(">0.0001 µm", FONT_MEDIUM, 24, _GRAY_800, 1.34)]],
    )

    return slide
