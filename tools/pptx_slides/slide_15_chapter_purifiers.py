"""Slide 15 -- Chapter: Purifiers. Figma node 63148:404.

Section divider: a large title over three bleeding product-close-up photos
(Cleone, Spirit, Pro) that sit mostly on white, so simple back-to-front
compositing (matching the original z-order) reproduces the design.
"""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Purifiers", "15/33")

    add_picture(slide, f"{assets_dir}/slide_15/cleone_photo.png", 0, 0, 1561, 1080)
    add_picture(slide, f"{assets_dir}/slide_15/pro_photo.png", 782, 115, 1139, 965)
    add_picture(slide, f"{assets_dir}/slide_15/spirit_photo.png", 0, 145, 1920, 935)

    add_text(
        slide, 48, 175, 1200, 150,
        [[("Our purifiers.", FONT_SEMIBOLD, 120, "#18181b", 1.0)]],
    )

    return slide
