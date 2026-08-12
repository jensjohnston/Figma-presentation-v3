"""Slide 30 -- Glass Bottles. Figma node 63222:184."""

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect, FONT_MEDIUM, FONT_SEMIBOLD,
)

CARD_W = 587
CARD_TOP = 287
CARD_H = 745
GAP = 618.667 - CARD_W  # figma bento gutter (~31.7px), applied between the 3 card left-edges


def _cell_heading(slide, x, label_runs, heading, body_runs):
    """label_runs / body_runs: either a plain string or a list of (text, size_px) tuples
    for runs that mix the 24px body copy with a smaller trademark glyph."""
    y = CARD_TOP + 48
    if isinstance(label_runs, str):
        label_runs = [(label_runs, 24)]
    runs = [(t, FONT_MEDIUM, s, "#52525b", 1.34) for t, s in label_runs]
    add_text(slide, x, y, 491, 32, [runs])

    add_text(
        slide, x, y + 48, 491, 41,
        [[(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)]],
    )

    if isinstance(body_runs, str):
        body_runs = [(body_runs, 24)]
    runs2 = [(t, FONT_MEDIUM, s, "#52525b", 1.34) for t, s in body_runs]
    add_text(slide, x, y + 105, 491, 64, [runs2])


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Bottles", "30/33")

    add_text(
        slide, 48, 115, 900, 90,
        [[("Reusable glass bottles.", FONT_SEMIBOLD, 64, "#212126", 1.0)]],
    )

    x1 = 48
    x2 = 48 + 618.667
    x3 = 48 + 1237.333

    # Card backgrounds.
    add_rounded_rect(slide, x1, CARD_TOP, CARD_W, CARD_H, "#f4f4f5", 32)
    add_rounded_rect(slide, x2, CARD_TOP, CARD_W, CARD_H, "#f4f4f5", 32)
    add_rounded_rect(slide, x3, CARD_TOP, CARD_W, CARD_H, "#f4f4f5", 32)

    # Card 1 -- Glass Bottle 1: Hydrate on the go.
    _cell_heading(
        slide, x1 + 48,
        [("Glass Bottle 1", 24), ("™", 15.48)],
        "Hydrate on the go",
        "Borosilicate glass. Matching silicone sleeve. Temperatures up to 100°C. 500 mL",
    )
    add_picture(slide, f"{assets_dir}/slide_30/swatches.png", x1 + 48, 515, 92, 24)
    add_picture(slide, f"{assets_dir}/slide_30/bottle_card1.png", x1, 484, 587, 548)

    # Card 2 -- Restaurant Bottle 1: Elegant table dining.
    _cell_heading(
        slide, x2 + 48,
        [("Restaurant Bottle 1", 24), ("™", 15.48)],
        "Elegant table dining",
        [("Crafted from premium Duragrade", 24), ("™", 15.48), (" Borosilicate glass. 500 mL · 1000 mL", 24)],
    )
    add_picture(slide, f"{assets_dir}/slide_30/bottle_card2.png", 755, 317, 411, 724)

    # Card 3 -- Retail Bottle 1: Durable and reusable.
    _cell_heading(
        slide, x3 + 48,
        [("Retail Bottle 1", 24), ("™", 15.48)],
        "Durable and reusable",
        "Designed for hotel rooms and retail settings. Soda Lime glass. 330 mL · 500 mL",
    )
    add_picture(slide, f"{assets_dir}/slide_30/bottle_card3.png", x3 + 83, 299, 420, 733)

    return slide
