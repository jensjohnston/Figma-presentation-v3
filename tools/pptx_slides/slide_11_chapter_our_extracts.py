"""Slide 11 -- Chapter: Our Extracts. Figma node 65364:138."""

from pptx.enum.text import MSO_ANCHOR

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, add_rect, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)

    # Base dark fill (matches the frame's own #18181b paint sitting behind the photo).
    add_rect(slide, 0, 0, 1920, 1080, "#18181b")

    # The background photo is applied as an image FILL directly on the root frame in
    # Figma (no isolable child node), so there's nothing to screenshot in isolation.
    # Reproduced instead via the exact CSS object-fit:cover math from the design
    # context (h-[104.85%] w-[105.68%] left-[-5.68%] top-[-2.38%] of the 1920x1080
    # frame) applied to the raw source asset, whose native aspect ratio (4096x2286)
    # matches the computed box aspect almost exactly, so there is no distortion.
    add_picture(
        slide, f"{assets_dir}/slide_11/background_raw.png",
        1920 * -0.0568, 1080 * -0.0238, 1920 * 1.0568, 1080 * 1.0485,
    )

    add_meta(slide, "Bluewater Technology", "11/33")

    add_text(
        slide, 48, 0, 1824, 1080,
        [[("Our Extracts.", FONT_SEMIBOLD, 120, "#ffffff", 1.0)]],
        anchor=MSO_ANCHOR.MIDDLE,
    )

    return slide
