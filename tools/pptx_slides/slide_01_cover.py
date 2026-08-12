"""Slide 01 -- Cover. Figma node 63145:131.

No meta-left/meta-right on this slide (title slide) -- confirmed via get_design_context,
so add_meta() is intentionally skipped.

Judgment call: the headline "Water like never before." uses a Figma linear-gradient
text fill (rgb(29,78,216) -> rgb(59,130,246)). pptx run colors are solid only, so this
is approximated with a single mid-blue (#2c68e7, the average of the two gradient stops).
"""

from tools.pptx_core import new_slide, add_text, add_picture, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)

    add_picture(slide, f"{assets_dir}/slide_01/logo.png", 48, 46, 334, 64)
    add_picture(slide, f"{assets_dir}/slide_01/bottle.png", 920, 69, 1001, 1011)

    add_text(
        slide, 48, 403, 953, 280,
        [
            [("Water like", FONT_SEMIBOLD, 152, "#2c68e7", 0.9)],
            [("never before.", FONT_SEMIBOLD, 152, "#2c68e7", 0.9)],
        ],
    )

    return slide
