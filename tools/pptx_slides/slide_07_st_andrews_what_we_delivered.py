"""Slide 07 -- St Andrews: What We Delivered. Figma node 65944:137.

Note: two stale duplicate "Slide 07" frames also exist in the Figma file at x=0,y=0 --
ignored; 65944:137 is the canonical one (sequential y-position between slides 06/08).

Three full-bleed photo cards (each with a subtle baked-in gradient tint) -- flattened
images, no text inside them. Title + intro copy are real text.
"""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Client Story", "07/33")

    add_text(
        slide, 48, 115, 1300, 90,
        [[("Three solutions. One iconic venue.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )
    add_text(
        slide, 1394, 119, 483, 80,
        [[("Outdoor refill stations. Premium restaurant water. Reusable bottles.", FONT_MEDIUM, 30, "#71717a", 1.2)]],
    )

    add_picture(slide, f"{assets_dir}/slide_07/card_1.png", 48, 287, 586, 745, radius_px=32)
    add_picture(slide, f"{assets_dir}/slide_07/card_2.png", 666, 287, 586, 745, radius_px=32)
    add_picture(slide, f"{assets_dir}/slide_07/card_3.png", 1284, 287, 586, 745, radius_px=32)

    return slide
