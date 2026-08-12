"""Slide 28 -- Emergency Station. Figma node 63132:436."""

from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from tools.pptx_core import (
    new_slide, add_meta, add_text, add_picture, add_rounded_rect, add_rect, add_label_with_mark,
    FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD,
)


def _stat_card(slide, y, number, caption, caption_w):
    add_rounded_rect(slide, 48, y, 586, 126, "#000000", 32)
    add_text(
        slide, 72, y, 250, 126,
        [[(number, FONT_SEMIBOLD, 36, "#ffffff", 1.15)]],
        anchor=MSO_ANCHOR.MIDDLE,
    )
    add_text(
        slide, 610 - caption_w, y, caption_w, 126,
        [[(caption, FONT_REGULAR, 14, "#ffffff", 1.34)]],
        align=PP_ALIGN.RIGHT,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def build(prs, assets_dir):
    slide = new_slide(prs)

    # Full dark background (this slide's bg is near-black, not white like the rest of the deck).
    add_rect(slide, 0, 0, 1920, 1080, "#18181b")

    add_meta(slide, "Bluewater Stations", "28/33")

    # Left card: label + heading + subhead (real editable text over a black rounded card).
    add_rounded_rect(slide, 48, 112, 586, 444, "#000000", 32)
    add_label_with_mark(
        slide, 96, 160, "Emergency Station 1", FONT_MEDIUM, 24, "#ffffff",
        "™", FONT_REGULAR, 12, w=490, h=22, line_spacing=1.1,
    )
    add_text(
        slide, 96, 280, 490, 106,
        [[("Clean drinking-water. Anywhere, anytime.", FONT_SEMIBOLD, 48, "#ffffff", 1.1)]],
    )
    add_text(
        slide, 96, 402, 490, 106,
        [[("Safe hydration for up to 10,000 people daily.", FONT_MEDIUM, 48, "#71717a", 1.1)]],
    )

    # Right: photo card. Black rounded background + flattened photo (exact node screenshot).
    add_rounded_rect(slide, 666, 112, 1206, 920, "#000000", 32)
    add_picture(slide, f"{assets_dir}/slide_28/photo.png", 706, 435, 1126, 597)

    # Mini stat cards (number + caption, real text over black rounded cards).
    _stat_card(slide, 588, "1,000 L/h", "Purification capacity", 187)
    _stat_card(slide, 747, "15 min", "One-person setup, start to finish", 414)
    _stat_card(slide, 906, "99.7%", "Contaminants removed.", 412)

    return slide
