"""Slide 23 -- Beverage Station. Figma node 63132:547."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_REGULAR, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater Stations", "23/33")

    # Countertop surface (behind), then product composition (device + tablet) on top,
    # matching Figma's z-order. Both screenshots are already clipped to the slide's
    # visible canvas bounds by the Figma renderer.
    add_picture(slide, f"{assets_dir}/slide_23/counter_bg.png", 0, 902, 1920, 178)
    add_picture(slide, f"{assets_dir}/slide_23/product.png", 450.5, 234, 1019, 846)

    add_text(
        slide, 48, 115, 400, 45,
        [
            [
                ("Beverage Station 1", FONT_MEDIUM, 32, "#f43f5e", 1.1),
                ("™", FONT_REGULAR, 16, "#f43f5e", 1.1),
            ]
        ],
    )

    add_text(
        slide, 48, 162, 841, 90,
        [[("Customized beverages.", FONT_SEMIBOLD, 64, "#18181b", 1.1)]],
    )

    add_text(
        slide, 1406, 115, 466, 100,
        [[("Create custom beverages with pure water infused with our functional extracts and natural flavors.", FONT_MEDIUM, 28, "#71717a", 1.34)]],
    )

    return slide
