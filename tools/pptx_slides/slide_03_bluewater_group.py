"""Slide 03 -- Bluewater Group. Figma node 63929:137.

Bento grid of 6 cards: top row = brand logo + description, bottom row = stat number.
Descriptions and stat numbers are bottom-anchored within their card (matches Figma's
`justify-end` flex layout) via MSO_ANCHOR.BOTTOM on an oversized text box.
"""

from pptx.enum.text import MSO_ANCHOR

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rounded_rect, FONT_MEDIUM, FONT_SEMIBOLD

CARD_W = 586
CARD_H_TOP = 360
CARD_H_BOTTOM = 354
GAP = 32
COL_X = [48, 48 + CARD_W + GAP, 48 + 2 * (CARD_W + GAP)]
ROW_TOP_Y = 283
ROW_BOTTOM_Y = 675


def _logo_card(slide, x, logo_path, logo_w, logo_h, description_runs):
    add_rounded_rect(slide, x, ROW_TOP_Y, CARD_W, CARD_H_TOP, "#f4f4f5", 32)
    add_picture(slide, logo_path, x + 48, ROW_TOP_Y + 48, logo_w, logo_h)
    add_text(
        slide, x + 48, ROW_TOP_Y + 232, 490, 80,
        [{"runs": description_runs}],
        anchor=MSO_ANCHOR.BOTTOM,
    )


def _stat_card(slide, x, label, number):
    add_rounded_rect(slide, x, ROW_BOTTOM_Y, CARD_W, CARD_H_BOTTOM, "#f4f4f5", 32)
    add_text(
        slide, x + 48, ROW_BOTTOM_Y + 48, 490, 40,
        [[(label, FONT_MEDIUM, 20, "#71717a", 1.34)]],
    )
    add_text(
        slide, x + 48, ROW_BOTTOM_Y + 206, 490, 100,
        [[(number, FONT_SEMIBOLD, 80, "#27272a", 1.1)]],
        anchor=MSO_ANCHOR.BOTTOM,
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater", "03/33")

    add_text(
        slide, 48, 115, 1824, 80,
        [[("Bluewater Group.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )

    _logo_card(
        slide, COL_X[0], f"{assets_dir}/slide_03/logo_bluewater.png", 251, 48,
        [("Turns any water source into the world's most healthy and sustainable beverage.", FONT_MEDIUM, 24, "#71717a", 1.34)],
    )
    _logo_card(
        slide, COL_X[1], f"{assets_dir}/slide_03/logo_tappwater.png", 254, 64,
        [("Cleaner water for your home in seconds — with filters that don't need installation.", FONT_MEDIUM, 24, "#71717a", 1.34)],
    )
    _logo_card(
        slide, COL_X[2], f"{assets_dir}/slide_03/logo_flowater.png", 254, 56,
        [("Upgrade your business's tap water — with great taste and zero plastic waste.", FONT_MEDIUM, 24, "#71717a", 1.34)],
    )

    _stat_card(slide, COL_X[0], "Available in", "28 countries")
    _stat_card(slide, COL_X[1], "Locations", "7 offices")
    _stat_card(slide, COL_X[2], "Employees", "+200 people")

    return slide
