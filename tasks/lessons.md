# Lessons

## 2026-05-29 — Root cause vs. band-aid: never compensate downstream for a broken source of truth
**Correction:** User flagged that the `normalizeSlide` / "normalize every clone" prevention I added felt like a temporary fix, not a senior root-cause solution. They were right.

**Root cause of the original bug:** the deprecated **Templates 4** master frames carry stale pre-harmonization geometry (title 80–120px, 64px margins, body 20–30px, cards ~80px off the bottom, plus missing meta chrome). They are a *second, divergent source of geometric truth* that was never reconciled with the harmonized references frames + design-system spec. The generator clones a frame and only replaces text, so it inherits whatever the frame has — silently off-spec.

**Why "audit + normalize every generated slide" is a band-aid:** it repairs the *output* at every call site, forever, while leaving the defective *source* in place. It adds permanent generator complexity and brittle per-template repair recipes (`Bento-66 → 1205`). That is treating the symptom.

**Root-cause fix:** make the source conform — harmonize the master frames to the contract (geometry + type + chrome) so a clone needs zero post-processing; guard the source with a contract **test over the template frames themselves** (not outputs); and eliminate the divergence by consolidating onto one canonical template page. Keep output `auditSlide` only as defense-in-depth/regression, never as a load-bearing crutch.

**Rule for myself:** When a fix is "detect-and-repair the output every time," STOP — that's a band-aid. Ask: what is the single source of truth, is it correct, and can I make the *source* correct so the repair becomes unnecessary? Fix the source; keep verification as a guard, not a crutch. Don't let a permission gate or extra effort talk me out of the root cause — surface it and ask.

**Also:** I rationalized a real bug (slide 9 "looked sparse") as intended template design. Don't explain away anomalies — measure against the spec.
