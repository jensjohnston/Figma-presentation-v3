"""Slide 32 -- Customise Your Bottle. Figma node 63222:212."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rounded_rect, FONT_MEDIUM, FONT_SEMIBOLD


def _bento_cell_text(slide, x, y, label, heading, body):
    add_text(
        slide, x, y, 792, 190,
        [
            {"runs": [(label, FONT_MEDIUM, 24, "#52525b", 1.34)], "space_after_px": 16},
            {"runs": [(heading, FONT_SEMIBOLD, 36, "#27272a", 1.15)], "space_after_px": 16},
            {"runs": [(body, FONT_MEDIUM, 24, "#52525b", 1.34)]},
        ],
    )


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Bottles", "32/33")

    add_text(
        slide, 48, 115, 1400, 90,
        [[("Make it yours. Customize your bottle.", FONT_SEMIBOLD, 64, "#212126", 1.0)]],
    )

    add_rounded_rect(slide, 48, 287, 888, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_32/left_photo.png", 48, 550, 888, 482, radius_px=32)
    add_picture(slide, f"{assets_dir}/slide_32/swatches_left.png", 96, 488, 330, 24)
    _bento_cell_text(slide, 96, 335, "Silicone loop", "Carry your bottle with ease", "Durable silicone loop. Available in 10 colors.")

    add_rounded_rect(slide, 984, 287, 888, 745, "#f4f4f5", 32)
    add_picture(slide, f"{assets_dir}/slide_32/right_photo.png", 984, 550, 888, 482, radius_px=32)
    add_picture(slide, f"{assets_dir}/slide_32/swatches_right.png", 1032, 488, 126, 24)
    _bento_cell_text(slide, 1032, 335, "Sports cap", "Lid designed for active people", "Smart sports-cap. Available in 4 colors.")

    return slide
