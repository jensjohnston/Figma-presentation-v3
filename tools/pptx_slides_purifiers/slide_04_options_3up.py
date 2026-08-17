"""Slide 04 -- Purifiers: Three Options. Figma node 61219:18130.

Pixel-for-pixel the same content, card geometry and object-cover crop math as
the main deck's slide_16_purifiers_three_options.py (verified: the object-fit
percentages on each card resolve to identical place_y/place_w/place_h values),
so the already-cropped product PNGs from that slide's asset pass are reused
directly rather than re-downloading and re-cropping the same photos.
"""

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect,
    FONT_MEDIUM, FONT_SEMIBOLD,
)

CARD_Y = 287
CARD_W = 586.6666870117188
CARD_H = 745
CARD_XS = [48, 48 + 618.6666870117188, 48 + 1237.3333740234375]


def _card(slide, x, product_img, place_y, place_w, place_h, heading, body):
    add_rounded_rect(slide, x, CARD_Y, CARD_W, CARD_H, "#f4f4f5", 32)
    add_picture(slide, product_img, x, CARD_Y + place_y, place_w, place_h)
    add_text(
        slide, x + 48, CARD_Y + 48, CARD_W - 96, 220,
        [
            {"runs": [(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [(body, FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Purifiers · 2026", "04/09")

    add_text(
        slide, 48, 115, 1205, 90,
        [[("Three purifier series.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )

    a = f"{assets_dir}/slide_04"
    _card(
        slide, CARD_XS[0], f"{a}/cleone_product.png", 104.0, CARD_W, 641.0,
        "Cleone", "Tank-based RO purification for apartments and small households. Up to 610 L/day.",
    )
    _card(
        slide, CARD_XS[1], f"{a}/spirit_product.png", 129.03, CARD_W, 615.97,
        "Spirit", "Compact purification with direct flow. Cafés, restaurants or offices. Up to 3,800 L/day.",
    )
    _card(
        slide, CARD_XS[2], f"{a}/pro_product.png", 138.42, CARD_W, 606.58,
        "Pro", "Maximum output with direct flow. Entire venues or commercial use. Up to 7,600 L/day.",
    )

    return slide
