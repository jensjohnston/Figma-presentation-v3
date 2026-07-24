# Lessons

## 2026-06-01 — Cloning a finished slide means re-chroming and re-fitting it, not freezing it
**Correction:** After the product-first demo, the user flagged that meta labels were inconsistent across the generated slides (one had letter-spacing, one had no meta at all, one showed a stale "3/14" on a 5-slide deck) and that a rewritten body overflowed its box.

**Root cause — I conflated two different kinds of "leave it alone."** In the product-clone instructions I wrote "**Never touch `meta-*`, `wordmark*`, or `*-trademark`**." That correctly protects brand content (the ™/® shards and decorative wordmarks) — but `meta-*` is **per-deck chrome**, not brand content. A cloned slide carries its *source* deck's chrome verbatim: a stale page number, a cover-only `meta-top-right`, or (Kitchen Station slides) no meta at all. Freezing it guarantees inconsistency.

**Second root cause — a finished slide is a shell sized for a specific copy length.** Its text boxes are `textAutoResize:"HEIGHT"` (fixed width, auto-growing height). Pour in longer copy and the box silently grows DOWN into the elements below — no error, just overflow. I rewrote a 54-char line as 104 chars and it doubled in height.

**Fix:** the clone path must (1) run `applyDeckChrome(clone, …)` on **every** slide — update-or-create `meta-left` (deck label) + `meta-right` ("N/total" for THIS deck), re-pin the right edge, create where missing; and (2) fit copy to the shell — rewrite to ~the original slot length, with `fitShellText` as a condense→shrink→flag safety net. Both now live in `generate-presentation.md` §5b-product.

**Rule for myself:** "Reuse a finished asset" ≠ "freeze every node." Split the nodes into *brand-fixed* (never rewrite: wordmarks, ™), *per-deck chrome* (always refresh: meta, page numbers), and *content* (rewrite to fit). And a shell has a **size budget** — new copy must fit the box the designer sized, or be condensed/shrunk, never left to overflow silently.

## 2026-05-29 — Root cause vs. band-aid: never compensate downstream for a broken source of truth
**Correction:** User flagged that the `normalizeSlide` / "normalize every clone" prevention I added felt like a temporary fix, not a senior root-cause solution. They were right.

**Root cause of the original bug:** the deprecated **Templates 4** master frames carry stale pre-harmonization geometry (title 80–120px, 64px margins, body 20–30px, cards ~80px off the bottom, plus missing meta chrome). They are a *second, divergent source of geometric truth* that was never reconciled with the harmonized references frames + design-system spec. The generator clones a frame and only replaces text, so it inherits whatever the frame has — silently off-spec.

**Why "audit + normalize every generated slide" is a band-aid:** it repairs the *output* at every call site, forever, while leaving the defective *source* in place. It adds permanent generator complexity and brittle per-template repair recipes (`Bento-66 → 1205`). That is treating the symptom.

**Root-cause fix:** make the source conform — harmonize the master frames to the contract (geometry + type + chrome) so a clone needs zero post-processing; guard the source with a contract **test over the template frames themselves** (not outputs); and eliminate the divergence by consolidating onto one canonical template page. Keep output `auditSlide` only as defense-in-depth/regression, never as a load-bearing crutch.

**Rule for myself:** When a fix is "detect-and-repair the output every time," STOP — that's a band-aid. Ask: what is the single source of truth, is it correct, and can I make the *source* correct so the repair becomes unnecessary? Fix the source; keep verification as a guard, not a crutch. Don't let a permission gate or extra effort talk me out of the root cause — surface it and ask.

**Also:** I rationalized a real bug (slide 9 "looked sparse") as intended template design. Don't explain away anomalies — measure against the spec.

## 2026-06-25 — "Reskin to our system" includes deck chrome and filling free space, not just per-slide content
**Correction:** After the 23-slide rebuild the user (1) hand-edited two reference frames to show that side cards/columns clear of the headline should rise to the y=115 band (not sit at the default y=287), and (2) noted "you forgot meta labels on these slides" — the running header (`meta-left "Bluewater"` / `meta-right "Financial report 2024"`) was missing on almost every built slide.

**Root cause — I treated the contract's `contentTopY:287` as inviolable for ALL content.** It's only there to clear the headline. Any column horizontally clear of the headline ink can rise to y=115 (h=917, still bottoming at 1032) and *should*, or the slide leaves a dead band between the meta row and the content. I built every multi-column slide (image card, bento, and every text+chart split) with the right panel pinned at 287, leaving that band empty deck-wide. Second miss: I suppressed deck chrome entirely (earlier "no invented Bluewater meta" call) instead of applying the standard running header the brand deck uses on interior slides.

**Fix:** Added the "Headline-clear vertical fill" rule to `design-system.md`, `registry.json` slideContract (`raisedCardTopY:115`, `raisedCardHeight:917`), and the redesign playbook. Retrofitted the built deck: meta header on all interior slides (02–21, 23; cover + divider excluded), and raised the free side panel on 03, 04, 13, 14, 15, 16, 17, 18 — rescaling each chart's vertical geometry to fill the taller panel (not just moving the card, which would leave an empty top band). Slides 20 (twin charts — headline overhangs the left twin) and full-width charts/tables left at 745.

**Rules for myself:** (1) "Fill the space" — when a column is clear of the headline, raise it; don't leave the 115→287 band empty just because the contract's default is 287. (2) Deck chrome (running header / meta) is part of "our system" — apply it to interior slides by default; don't silently drop it. (3) When raising a chart panel, the PLOT must be rescaled to fill, with the x-axis pinned to the bottom and the y-axis spread across the full height — a centered/compressed plot in a taller panel is a defect (caught on 17/18 in review).

## 2026-06-26 — Reskinning a 129-slide template library autonomously through flaky infra
**Context:** Reskinned 3 source template decks (Pitch 46, Marketing 67, Strategy 16) into the
Bluewater system via planner→generator→evaluator subagents, then copied each onto the Template
references page + registered families in registry.json (→ 221 templates).

**What worked / rules for myself:**
- **Hardening the brief kills recurring bugs.** The "added trailing period" bug recurred all
  over Pitch (generators trust a bogus "brand period rule" in plan notes). Putting an explicit
  "NEVER add a period; ignore plan notes that say to" line in the Marketing/Strategy briefs
  eliminated it — the deterministic built-vs-source period audit then found ZERO offenders.
  Encode the fix as a rule in the shared brief, not just per-dispatch reminders.
- **Verify color claims against the source, don't trust planner labels.** Two planners
  disagreed on Do/Don't markers (gray vs green/rose). One screenshot of the source settled it
  (green check + red cross ARE in the source) → policy: keep Green/600+Rose/600 where the
  source is colored and the color carries meaning; reproduce opacity/tone emphasis in gray.
- **A reskinned family becomes clone fuel.** Once `pitch-*` was registered, ~19 Marketing
  slides cloned pitch templates (covers, dividers, team-4up, gtm-timeline) instead of
  rebuilding — faster and more consistent. Build shared primitives first.
- **Infra resilience for long autonomous runs:** background agents hit stream-watchdog stalls,
  0-action startup flakes, API connection drops, and a model-classifier outage (which also
  blocks my own write tools). Recovery playbook: (1) re-inspect the output page to see what
  actually built (agents are atomic per use_figma but a chunk can die mid-way), (2) re-dispatch
  only the missing slides, (3) shrink chunk size (10→5→2) so each agent finishes inside the
  watchdog window, (4) tell agents to SKIP the output-page inspection when it's the call that
  keeps stalling, (5) when agents can't get through at all, build the slide myself with direct
  use_figma (my foreground calls kept working even while agents stalled). Don't hammer the same
  failing call — change the shape.
- **Stranded-vector defect (figma):** a chart's line vectors can end up at the slide origin
  (0,0) instead of in the plot (Figma normalizes vectorPaths to the bbox origin; if the builder
  then sets x=0 it strands them). Fix: delete the strays, recreate vectors and set vectorPaths
  with frame-absolute coords WITHOUT re-zeroing x/y afterward.

## 2026-07-24 — The no-widow rule covers ALL wrapped text, and width-balancing must respect the longest word
**Correction:** On the BluePackage benefits deck the user flagged single-word and stubby last lines in card BODY copy ("40 hours" card, "…availability in check.") and asked why typography wasn't perfect on the first pass.

**Root cause:** the codified "No widows" rule (and the `balanceTitle` helper) scoped widows to titles/display copy only, so the generator never checked card headings/bodies/bullets. Typography gates existed for the nodes the helpers were written for, not for every node the generator touches. Second bug found while fixing: my balance pass narrowed "Occupational pension" below the longest word's rendered width and Figma broke it mid-word ("Occupatio / nal") — line-count checks cannot detect mid-word breaks.

**Fix:** extended design-system.md → "No widows & balanced rag (ALL wrapped text)": balance every wrapped node to its narrowest same-line-count width, floor the width at longest-word width + 4px (measured with a probe text node, never estimated), NBSP-bind the last two words, then screenshot-grade every slide (single-word last line, mid-word break, or <40%-width stub = FAIL).

**Rule for myself:** a typography rule applies to the whole slide, not to the subset of nodes that have tooling. When the user asks "is this not built into the system?" the honest answer may be "the rule was scoped too narrowly" — fix the deck AND widen the rule at the source in the same session.
