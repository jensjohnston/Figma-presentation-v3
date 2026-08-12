"""Slide 29 -- Chapter: Bluewater Bottles. Figma node 63222:179."""

from pptx.enum.text import PP_ALIGN

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Bottles", "29/33")

    # Background photo (two hands passing a bottle) -- the node overflows past the slide's
    # bottom edge in Figma and is clipped there; the exported screenshot is already the
    # clipped 1921x864 visible portion, placed at the node's original top-left.
    add_picture(slide, f"{assets_dir}/slide_29/bottles_photo.png", 0, 216, 1921, 864)

    add_text(
        slide, 48, 115, 1824, 120,
        [[("Bluewater Bottles.", FONT_SEMIBOLD, 120, "#18181b", 1.0)]],
        align=PP_ALIGN.CENTER,
    )

    return slide
