"""Slide 20 -- Chapter: Bluewater Stations. Figma node 63150:131."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "20/33")

    a = f"{assets_dir}/slide_20"

    add_picture(slide, f"{a}/background.png", 0, 0, 1920, 1080)

    add_text(
        slide, 48, 420, 741, 240,
        [
            [("Bluewater", FONT_SEMIBOLD, 120, "#18181b", 1.0)],
            [("Stations.", FONT_SEMIBOLD, 120, "#18181b", 1.0)],
        ],
    )

    return slide
