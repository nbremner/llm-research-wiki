---
name: research-wiki-graph-lint
description: Use when auditing the markdown research wiki for graph coherence — broken wikilinks, orphan pages, claims without a source, sources that feed no topic, provenance gaps, and stale topics — or when running the monthly semantic lint (contradiction check over the --pairs shortlist + evidence-staleness review). Report-only; fixes route through the normal write paths.
version: 2.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, lint, markdown, knowledge-graph, provenance]
    related_skills: [research-wiki-ingest, research-wiki-query]
---

# Research Wiki Graph Lint

## Overview

Keep the markdown wiki from quietly accumulating disconnected pages, dead links, or synthesis with no
evidence under it. This is a **read-only audit** over `wiki/` (plain markdown in git) — it reports;
it does not edit. The old version linted the Notion layer; the wiki is now files, so linting is a
filesystem walk, not API queries.

## What it checks

The engine is `scripts/research-wiki-tools/graph_lint.py`. It parses frontmatter + `[[wikilinks]]`
across `wiki/` and reports, by severity:

- **High — Broken wikilink:** a `[[target]]` that resolves to no page.
- **High — Source missing public url/doi:** a `sources/` record with no canonical public link
  (the one hard rule: public provenance).
- **Medium — Orphan source / Orphan topic:** a page nothing links to.
- **Medium — Source feeds no topic:** evidence sitting unused — no resolvable `[[topic]]` link.
- **Medium — Topic cites no source:** an active topic making claims with no `[[source]]` behind them.
- **Medium — Topic evidence-stale:** ≥2 linked sources with `retrieved` dates *after* the topic's
  `updated` — the synthesis is behind the evidence. (Depends on the `updated:`-discipline rule in
  `wiki/schema.md`: mechanical passes must not bump `updated`, or this check goes blind.)
- **Low — Topic stale:** `updated` older than the threshold (default 180 days) — calendar fallback;
  evidence-stale is the sharper signal.
- **Low — Source missing file_hash:** provenance hash absent (dedup weaker).

It skips `schema.md` (documentation full of illustrative template links) and `README.md` placeholders,
and ignores links inside code fences — so templates and examples don't produce false positives.
Stubs (`status: stub`) are exempt from the "cites no source" check; they're intentionally thin.

## Run

```bash
cd /root/work/llm-research-wiki
python scripts/research-wiki-tools/graph_lint.py                 # markdown report to stdout
python scripts/research-wiki-tools/graph_lint.py --json          # JSON findings
python scripts/research-wiki-tools/graph_lint.py --fail-on High  # non-zero exit if any High+ (for CI/hooks)
```

No arguments needed in-repo; `--wiki-dir` defaults to the repo's `wiki/`.

## Semantic lint (monthly cron)

The structural checks above are deterministic; the **contradiction check is judgment work** and runs
monthly. The script selects *what to read*; you judge *whether it contradicts*.

1. Get the shortlist: `python scripts/research-wiki-tools/graph_lint.py --pairs` (first ever run:
   `--pairs --bootstrap --max-pairs 35`). Pairs share ≥2 cited sources or link directly; normal runs
   are change-gated to recently edited pairs, ranked by shared-source count, plus a month-keyed
   rotating tail of cold pairs. The JSON reports `eligible_total` vs `selected` (normal runs also
   carry `gated_total`) — quote the counts in your report so coverage limits are never silent.
2. For each pair, read both topic pages in full. Flag only **wiki-voice contradictions**: topic A
   asserting as settled what topic B contradicts, one page citing a finding the other treats as
   refuted, or the same shared source summarized with incompatible claims. **Documented disagreement
   between studies is content, not a defect** — topic pages have a "Contradictions & open questions"
   section precisely for that; never flag it.
3. Also run the structural lint (`--json`) and pull any **Topic evidence-stale** findings into your
   report — they are the "synthesis behind the evidence" queue.
4. Deliver one digest: contradictions found (quote the two conflicting passages, name the shared
   sources), evidence-stale topics, pairs-checked/eligible counts. **Report-only** — fixes are
   synthesis edits and go through the owner-approved path; never edit topic pages from this skill.

## When to use

- After an ingest, to confirm no broken links / orphans / unsupported claims were introduced.
- Periodically, as a wiki health check.
- Before relying on the wiki for a synthesis or query run.
- Monthly semantic lint (cron): the contradiction-pair procedure above.

## How findings get fixed (not by this skill)

The lint run itself is **report-only** — it never edits the wiki (this matches the lint row in
`OPERATING_MODEL.md`). Fixes are separate actions under the normal write rules: mechanical repairs
(a broken slug, a missing link) go through whoever owns the affected page class and must not bump
`updated:` (schema.md); anything touching topic claims goes through owner-approved synthesis.

- **Structural issues** (broken link, orphan, source feeds no topic) → name the concrete fix in the
  report; an unused source is integrated via `research-wiki-ingest` step 9.
- **Provenance gaps** (missing url/doi) → find the canonical public landing page, or flag the source
  for review; do not invent a citation.
- **Topic cites no source** → propose adding the evidence link or marking the page `status: stub`
  until it has one. Don't let agent synthesis stand as canon with no source under it.
- **Stale topics** → revisit when newer sources exist; staleness is a watchlist signal, not an error.

Canonical edits (topic synthesis) still follow the governance rule: owner approves before synthesis
becomes canonical. Lint proposes; it does not rewrite topics on its own.

## Verification checklist

- [ ] Lint run against the current `wiki/` (note pages checked).
- [ ] Findings grouped by severity.
- [ ] Each finding carries a proposed route (mechanical fix via the owning workflow / flag / synthesis queue).
- [ ] No wiki edits made by the lint run itself.
