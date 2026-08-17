"""Slide 03 -- SuperiorOsmosis Technology. Figma node 61219:18156.

Same card geometry as the main deck's slide_10_superiorosmosis_technology.py
(identical card position/size, identical hero-card copy) -- only the left
card's heading ("Technology" vs. "Purification technology") and intro line
are reworded, and one mini-stat's body copy is trimmed slightly. Renumbered
meta (Figma read "3/14", a stale artifact of a larger unbuilt sequence).
"""

from pptx.enum.text import PP_ALIGN

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rect, add_rounded_rect, add_label_with_mark,
    FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD,
)

_CARD_FILL = "#09090b"
_BODY_GRAY = "#b4b4b6"

_MINI_CARDS = [
    (588, "0.0001 μm", 423, 187,
     "Filtration level — 5,000× finer than standard carbon filters."),
    (747, "Up to 80%", 271, 339,
     "Water recovery — vs. ~25% for conventional RO. 82% less waste."),
    (906, "4–6 yrs", 213, 397,
     "Membrane life through continuous self-cleaning (vs. 1–2 years standard RO)."),
]


def build(prs, assets_dir):
    slide = new_slide(prs)

    add_rect(slide, 0, 0, 1920, 1080, "#18181b")
    add_meta(slide, "Bluewater Purifiers · 2026", "03/09")

    # -- Right hero card: "Engineered for Purity / 99.7%" ------------------------
    add_rounded_rect(slide, 666.857, 112, 1205.143, 920, _CARD_FILL, 32)
    add_picture(slide, f"{assets_dir}/slide_03/circle_badge.png", 1872 - 887, 112, 887, 920)

    add_text(
        slide, 714.857, 755, 460, 30,
        [[("Engineered for Purity", FONT_SEMIBOLD, 24, "#ffffff", 0.9167)]],
    )
    add_text(
        slide, 714.857, 793, 460, 96,
        [[("99.7%", FONT_SEMIBOLD, 80, "#ffffff", 1.1)]],
    )
    add_text(
        slide, 714.857, 897, 460, 96,
        [[(
            "contaminants removed — including PFAS, microplastics, lead, bacteria, "
            "viruses, arsenic, chlorine and more.",
            FONT_MEDIUM, 24, "#ffffff", 1.2083,
        )]],
    )

    # -- Left top card: "Technology" ---------------------------------
    add_rounded_rect(slide, 48, 112, 586.286, 444, _CARD_FILL, 32)

    add_text(
        slide, 96, 160, 490, 30,
        [[("Technology", FONT_SEMIBOLD, 24, "#ffffff", 0.9167)]],
    )
    add_label_with_mark(
        slide, 96, 280, "SuperiorOsmosis", FONT_SEMIBOLD, 48, "#2563eb",
        "™", FONT_REGULAR, 16, w=490, h=65, line_spacing=1.1,
    )
    add_text(
        slide, 96, 349, 490, 165,
        [[("The world's most efficient compact water purification.", FONT_MEDIUM, 48, "#d4d4d8", 1.1)]],
    )

    # -- Mini stats column ----------------------------------------------------------
    for card_y, heading, body_x, body_w, body in _MINI_CARDS:
        add_rounded_rect(slide, 48, card_y, 586, 126, _CARD_FILL, 32)
        add_text(
            slide, 72, card_y + 42.5, 200, 45,
            [[(heading, FONT_SEMIBOLD, 36, "#ffffff", 1.15)]],
        )
        add_text(
            slide, body_x, card_y + 44, body_w, 40,
            [[(body, FONT_REGULAR, 14, _BODY_GRAY, 1.34)]],
            align=PP_ALIGN.RIGHT,
        )

    return slide
