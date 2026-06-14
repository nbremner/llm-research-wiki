---
name: research-wiki-graph-lint
description: Use when auditing the markdown research wiki for graph coherence — broken wikilinks, orphan pages, claims without a source, sources that feed no topic, provenance gaps, and stale topics. Read-only by default.
version: 2.0.0
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
- **Low — Topic stale:** `updated` older than the threshold (default 180 days).
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

## When to use

- After an ingest, to confirm no broken links / orphans / unsupported claims were introduced.
- Periodically, as a wiki health check.
- Before relying on the wiki for a synthesis or query run.

## How to act on findings

- **Fix structural issues directly** (broken link → fix the slug; orphan → link it or remove it;
  source feeds no topic → integrate it via `research-wiki-ingest` step 9).
- **Provenance gaps** (missing url/doi) → find the canonical public landing page, or flag the source
  for review; do not invent a citation.
- **Topic cites no source** → either add the evidence link or mark the page `status: stub` until it
  has one. Don't let agent synthesis stand as canon with no source under it.
- **Stale topics** → revisit when newer sources exist; staleness is a watchlist signal, not an error.

Canonical edits (topic synthesis) still follow the governance rule: owner approves before synthesis
becomes canonical. Lint proposes; it does not rewrite topics on its own.

## Verification checklist

- [ ] Lint run against the current `wiki/` (note pages checked).
- [ ] Findings grouped by severity.
- [ ] Broken links and provenance gaps triaged (fix / flag).
- [ ] Any fixes committed; lint re-run clean (or remaining findings explained).
