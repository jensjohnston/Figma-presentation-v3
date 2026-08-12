"""Slide 13 -- The Bluewater Extract Range. Figma node 63239:136."""

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect,
    FONT_MEDIUM, FONT_SEMIBOLD,
)

CARD_Y = 287
CARD_W = 432
CARD_H = 745
CARD_XS = [48, 512, 976, 1440]


def _card_text(slide, x, heading_runs, body_paragraphs):
    add_text(
        slide, x + 48, CARD_Y + 48, CARD_W - 96, 300,
        [
            {"runs": heading_runs, "space_after_px": 16},
            *body_paragraphs,
        ],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Technology", "13/33")

    add_text(
        slide, 48, 115, 884, 90,
        [[("Our extract range.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )
    add_text(
        slide, 1298, 115, 574, 90,
        [[("Developed in Stockholm. From minerals and coffee optimization to wellness and flavor.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    # Card 1 -- Liquid Rock (light gray card, photo fills bottom portion)
    x = CARD_XS[0]
    add_rounded_rect(slide, x, CARD_Y, CARD_W, CARD_H, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_13/liquid_rock.png", x, CARD_Y + 189, CARD_W, 556, radius_px=32)
    _card_text(
        slide, x,
        [("Liquid Rock", FONT_SEMIBOLD, 36, "#27272a", 1.15), (" ®", FONT_SEMIBOLD, 18, "#27272a", 1.15)],
        [{"runs": [("Swedish electrolytes in a 2:1 calcium-to magnesium ratio, restoring essential minerals.", FONT_MEDIUM, 24, "#3f3f46", 1.34)]}],
    )

    # Card 2 -- Coffee Rock (full-bleed dark photo, white text)
    x = CARD_XS[1]
    add_rounded_rect(slide, x, CARD_Y, CARD_W, CARD_H, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_13/coffee_rock.png", x, CARD_Y, CARD_W, CARD_H, radius_px=32)
    _card_text(
        slide, x,
        [("Coffee Rock", FONT_SEMIBOLD, 36, "#ffffff", 1.15)],
        [{"runs": [("Built for specialty coffee. Calcium and magnesium in a 6:1 ratio. Chloride free.", FONT_MEDIUM, 24, "#ffffff", 1.34)]}],
    )

    # Card 3 -- Functional Extracts (full-bleed dark glow photo, white text)
    x = CARD_XS[2]
    add_rounded_rect(slide, x, CARD_Y, CARD_W, CARD_H, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_13/functional_extracts.png", x, CARD_Y, CARD_W, CARD_H, radius_px=32)
    add_text(
        slide, x + 48, CARD_Y + 48, CARD_W - 96, 300,
        [
            {"runs": [("Functional Extracts", FONT_SEMIBOLD, 36, "#ffffff", 1.15)], "space_after_px": 16},
            {"runs": [("Hydrate, Energy, Zen and more. Choose your favourite.", FONT_MEDIUM, 24, "#ffffff", 1.34)]},
            {"runs": [("— Coming Soon", FONT_MEDIUM, 24, "#ffffff", 1.34)]},
        ],
    )

    # Card 4 -- Flavor Extracts (pink card, full-bleed photo, dark text)
    x = CARD_XS[3]
    add_rounded_rect(slide, x, CARD_Y, CARD_W, CARD_H, "#ffe4e6", 32)
    add_picture(slide, f"{assets_dir}/slide_13/flavor_extracts.png", x, CARD_Y, CARD_W, CARD_H, radius_px=32)
    add_text(
        slide, x + 48, CARD_Y + 48, CARD_W - 96, 300,
        [
            {"runs": [("Flavor Extracts", FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [("Natural fruits and berries for customized drinks.", FONT_MEDIUM, 24, "#3f3f46", 1.34)]},
            {"runs": [("— Coming Soon", FONT_MEDIUM, 24, "#3f3f46", 1.34)]},
        ],
    )

    return slide
