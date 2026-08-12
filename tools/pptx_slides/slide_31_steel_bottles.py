"""Slide 31 -- Steel Bottles. Figma node 63222:198."""

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect, add_label_with_mark, FONT_MEDIUM, FONT_SEMIBOLD,
)

CARD_W = 888
CARD_TOP = 287
CARD_H = 745


def _cell_heading(slide, x, label, heading, body):
    y = CARD_TOP + 48
    add_label_with_mark(slide, x, y, label, FONT_MEDIUM, 24, "#52525b", "™", FONT_MEDIUM, 15.48, w=792, h=32, line_spacing=1.34)
    add_text(
        slide, x, y + 48, 792, 41,
        [[(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)]],
    )
    add_text(
        slide, x, y + 105, 792, 32,
        [[(body, FONT_MEDIUM, 24, "#52525b", 1.34)]],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Bottles", "31/33")

    add_text(
        slide, 48, 115, 900, 90,
        [[("Steel bottles made to last.", FONT_SEMIBOLD, 64, "#212126", 1.0)]],
    )

    x1 = 48
    x2 = 48 + 936

    add_rounded_rect(slide, x1, CARD_TOP, CARD_W, CARD_H, "#f4f4f5", 32)
    add_rounded_rect(slide, x2, CARD_TOP, CARD_W, CARD_H, "#f4f4f5", 32)

    # Card 1 -- Steel Bottle 1: Reusable and compact.
    _cell_heading(slide, x1 + 48, "Steel Bottle 1", "Reusable and compact", "Lightweight stainless steel. 400 mL")
    add_picture(slide, f"{assets_dir}/slide_31/bottle_card1.png", 277, 287, 430, 760)

    # Card 2 -- Steel Bottle 2: Made to last for generations.
    _cell_heading(slide, x2 + 48, "Steel Bottle 2", "Made to last for generations", "Double-wall. Built to last. 400 mL")
    add_picture(slide, f"{assets_dir}/slide_31/swatches.png", x2 + 48, 488, 92, 24)
    add_picture(slide, f"{assets_dir}/slide_31/bottle_card2.png", 1197, 248, 462, 816)

    return slide
