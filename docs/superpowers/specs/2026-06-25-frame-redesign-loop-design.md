# Frame Redesign Loop — Design

**Date:** 2026-06-25
**Status:** Approved (design questions answered), pending spec review

## Goal

Reproduce all 23 source frames (Page 01–23, under node `65202:5083` "Page 82" in
Figma file `GkUiwJTK5Xi65AKw4MOjTL`) on a new Bluewater page — preserving each
slide's **layout silhouette, information structure, and verbatim placeholder
copy** — but rendered entirely in the Bluewater design system (Suisse Int'l,
typescale, card tiers, color tokens, grid).

The source is a generic grayscale "Financial report Template" investor deck
(title, safe-harbor legal text, gray bento highlight cards, stat cards, an area
chart, lorem ipsum / "Company X" placeholder). The output is a **reusable
on-brand template deck** — placeholder copy is kept, not replaced.

### Fidelity definition ("as close as possible to the original")

Match the original's **composition**, not its grayscale skin. Same number of
elements, same reading order, same relative emphasis and grid position — but
Bluewater typography, card tiers, color tokens, and spacing. A reskin, not a
reinterpretation.

## Non-goals

- Replacing placeholder copy with real Bluewater financial content (this is a template).
- Re-composing layouts beyond what the design system requires.
- Editing the original source frames (read-only).
- Touching the source Figma page or any existing Bluewater page.

## The playbook (what "on-brand" means)

Existing canon, used unchanged:

- `templates/design-system.md` — typescale (Minor Third), card size tiers
  (xs/sm/lg/hero), grid, color system (Gray/Blue/Rose/Green), creative guide,
  `auditSlide`/`auditFrame` geometry contract, `applyChrome`.
- `templates/registry.json` — 69 templates + `slideContract` (margins 48,
  title 64@y115/110, body 28, content y287→1032, cardHeight 745).
- `core/brand-tokens.json` — canonical color scales.

Plus one task-specific file:

- `tasks/redesign-playbook.md` — reskin-only rules: preserve silhouette, map
  source archetype → nearest template, keep copy verbatim, never invent/drop
  content, prefer Gray tokens (source is monochrome) with restrained Blue accent
  only where the original uses emphasis.

## The rubric

`tasks/redesign-rubric.md`. The evaluator scores each generated slide against
its original screenshot:

**Hard gates (fail ⇒ slide is broken regardless of looks):**
1. **Geometry** — `auditSlide(kind)` returns no issues.
2. **Content fidelity** — every original text string present verbatim; none
   added or dropped; same reading order.

**Scored dimensions (0–5 each):**
3. **Layout fidelity** — silhouette, element count, grid position, relative emphasis.
4. **Design-system compliance** — correct card tiers, spacing, line-heights, grid rhythm.
5. **Typography** — Suisse Int'l, correct weight/size per tier and slide level.
6. **Color/token usage** — Gray/Blue/Rose/Green tokens; dark-slide pattern where original is dark.

**Done condition (per slide):** both gates pass AND mean(3–6) ≥ 4.5;
OR scores plateau (no net improvement) across 2 consecutive iterations;
hard cap 3 iterations/slide. Any slide that hits the cap below threshold is
logged in `tasks/redesign-log.md` with its residual issues — never silently
accepted as done.

## The three roles

### Planner (read-only, parallel across slides)
Input: a source frame. Output: one entry in `tasks/redesign-plan.json`:
`{ page, sourceNodeId, archetype, targetTemplate, slotMapping, verbatimText[], notes }`.
Extracts all text verbatim, classifies the archetype (title / legal-multipara /
bento-highlights / stat-cards / area-chart / …), and picks the nearest of the 69
templates with a slot→text mapping. Read-only: safe to run all 23 in parallel.

### Generator (serial per slide)
Input: one plan entry + (on repair iterations) the evaluator's fix-list.
Action: clone the chosen template onto the output page via `use_figma`, fill
slots with the verbatim text, apply tiers/tokens, run `auditSlide`. **Serial**
— concurrent `use_figma` writes to one file collide.

### Evaluator (per slide)
Input: generated node id + source node id. Action: screenshot both, score
against the rubric, return `{ scores, gatesPass, fixList[] }`. The fix-list is
specific and actionable ("body card uses 28px, tier sm requires 24px";
"dropped the '— TechCrunch' attribution").

## Orchestration

Driven from the main session (not a Workflow), per user choice:

1. **Plan phase** — dispatch planner subagents in parallel for all 23 frames →
   assemble `redesign-plan.json`. (Read-only, parallel-safe.)
2. **Create output page** — new page "Redesign — Financial Report (Bluewater)"
   in the same file.
3. **Pilot loop (serial)** — Page 01 (title), 02 (legal text), 04 (bento
   highlights), 05 (area chart) — the distinct archetypes. Per slide:
   generate → evaluate → repair until done condition.
4. **Checkpoint** — present the 4 pilot slides + scores to the user; tune the
   rubric/playbook if needed.
5. **Rollout loop (serial)** — remaining 19 slides through the same loop.
6. **Final report** — `tasks/redesign-log.md`: per-slide final scores,
   iteration counts, any capped slides + residual issues.

## Output

New page in `GkUiwJTK5Xi65AKw4MOjTL`, 23 frames in a strip mirroring source
order. Source frames untouched.

## Risks & mitigations

- **Figma write collisions** → generation strictly serial.
- **Chart slides** (Page 05) — area chart isn't a clone-and-fill template;
  data-viz needs an escape-hatch build. Flagged per design-system.md §Data viz.
  If no clean template fits, build to the grid + tokens by hand under the same
  rubric.
- **Evaluator over-scoring** — gates are pass/fail and content fidelity is
  verbatim-checked, anchoring the soft scores.
- **Plateau without quality** — capped + logged, surfaced to user, never hidden.
