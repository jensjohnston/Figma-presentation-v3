"""Slide 02 -- Who We Are. Figma node 63145:136."""

from tools.pptx_core import new_slide, add_meta, add_text, add_picture, FONT_MEDIUM, FONT_SEMIBOLD


def build(prs, assets_dir):
    slide = new_slide(prs)
    add_meta(slide, "Bluewater", "02/33")

    add_text(
        slide, 48, 115, 896, 140,
        [
            [("Meet Bengt Rittri. ", FONT_SEMIBOLD, 64, "#18181b", 1.1)],
            [("Founder of Bluewater.", FONT_SEMIBOLD, 64, "#18181b", 1.1)],
        ],
    )

    body_runs_1 = [
        ("Growing up on the beaches of southern Sweden, Bengt Rittri spent his childhood searching for amber. But over the years, ", FONT_MEDIUM, 32, "#71717a", 1.34),
        ("the amber gave way to plastic bottles", FONT_MEDIUM, 32, "#3f3f46", 1.34),
        (" — and ", FONT_MEDIUM, 32, "#71717a", 1.34),
        ("he knew something had to change.", FONT_MEDIUM, 32, "#3f3f46", 1.34),
    ]
    body_runs_2 = [
        ("In 2013, Rittri founded Bluewater.", FONT_MEDIUM, 32, "#3f3f46", 1.34),
        (" At Bluewater, we set out to reimagine what drinking water could be: using ", FONT_MEDIUM, 32, "#71717a", 1.34),
        ("advanced purification and natural ingredients", FONT_MEDIUM, 32, "#3f3f46", 1.34),
        (" to create the healthiest, most sustainable choice ", FONT_MEDIUM, 32, "#71717a", 1.34),
        ("for you and the world around you.", FONT_MEDIUM, 32, "#3f3f46", 1.34),
    ]
    add_text(
        slide, 48, 602, 850, 430,
        [
            {"runs": body_runs_1, "space_after_px": 32},
            {"runs": body_runs_2},
        ],
    )

    add_picture(slide, f"{assets_dir}/slide_02/photo_card.png", 976, 115, 896, 917)
    return slide
