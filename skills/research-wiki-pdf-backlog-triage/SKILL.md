---
name: research-wiki-pdf-backlog-triage
description: Use for recurring research-wiki PDF backlog indexing from Google Drive _inbox, human review CSV/Numbers handling, domain-cluster triage, and selecting candidates for ingest into the markdown wiki.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, pdf, google-drive, triage, backlog, literature-review]
    related_skills: [research-wiki-ingest, google-workspace, ocr-and-documents]
---

# Research Wiki PDF Backlog Triage

Use this skill when Nicholas wants to continue or rerun the research-wiki PDF backlog workflow for many PDFs in the Drive `_inbox` folder.

## Current durable tooling

Local tool directory:

```text
/root/research-wiki-tools/
```

Key scripts:

```text
/root/research-wiki-tools/pdf_backlog_triage.py
/root/research-wiki-tools/numbers_review_extract.py
```

Run artifacts:

```text
/root/research-wiki-runs/
/root/research-wiki-runs/latest-pdf-triage
```

Drive folders:

- `_inbox`: `1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1`
- raw public source folder `public-literature-wiki`: `17vtadKJwx81gjsS85kwaogyQvZweZ_n_`
- ops/review artifacts folder `research-wiki-ops`: `1YYsH8wb4yGwoDzaeKR1NyizracPHVdL-`

## Boundaries

- Default mode is dry-run indexing only.
- Do not rename, move, or delete Drive PDFs during indexing (that happens during ingest).
- Do not write wiki pages during indexing.
- Use `research-wiki-ops` for generated CSV/Numbers/review artifacts.
- Do not place generated review artifacts in `_inbox` or `public-literature-wiki`.
- Ingesting a selected PDF into the wiki (and refiling its raw PDF) is done by `research-wiki-ingest`,
  with topic synthesis owner-approved before commit.

## Rerun indexing

Full run:

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py
```

Smoke test:

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py --max-files 10
```

Metadata-only:

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py --no-download
```

The script writes:

- `SUMMARY.md`
- `pdf_triage.csv`
- `pdf_triage.jsonl`
- `drive_inventory_raw.json`
- `downloads/`

Update latest pointer when needed:

```bash
ln -sfn /root/research-wiki-runs/<run-id> /root/research-wiki-runs/latest-pdf-triage
```

## Human review workflow

Nicholas may review CSVs in Apple Numbers and upload `.numbers` files to `research-wiki-ops`. Extract them with:

```bash
uv run /root/research-wiki-tools/numbers_review_extract.py \
  /path/to/review.numbers \
  --out /path/to/review_from_numbers.csv
```

This creates a CSV plus `.review_summary.json` with reviewed/commented rows.

Review status semantics:

- `looks-good` = `ok-to-summarize`
- `Exclude` = do not summarize and do not create Inbox candidate
- “Need to expand topic catalog to correctly categorize this” = source is probably acceptable, but Schema topic assignment is weak

## Domain cluster field

`pdf_backlog_triage.py` adds `domain_cluster_candidate` as an ops-layer field. These are not wiki topics (in the markdown wiki, topics are pages, not tags). Use them to spot recurring clusters that may deserve their own `wiki/topics/` page.

Current cluster set:

- `selection-and-assessment`
- `psychometrics-and-measurement`
- `validity-and-utility`
- `teams-and-team-effectiveness`
- `leadership`
- `employee-attitudes-and-commitment`
- `turnover-and-retention`
- `job-design-and-work-motivation`
- `training-and-development`
- `csr-and-sustainability`
- `organizational-culture`
- `organizational-network-analysis`
- `research-methods-and-statistics`
- `competency-modeling`
- `legal-ethical-and-professional-standards`
- `ai-and-algorithmic-assessment`
- `organizational-theory-and-strategy`

## Known latest state from first workflow build

Initial `_inbox` batch had 101 PDFs.

Latest full domain-cluster run:

```text
/root/research-wiki-runs/pdf-triage-20260525-domain-clusters
```

Latest pointer:

```text
/root/research-wiki-runs/latest-pdf-triage
```

Nicholas reviewed about 20 rows in an Apple Numbers file. A merged review CSV with domain clusters was created:

```text
/root/research-wiki-runs/human-review-20260525/pdf_triage_review_with_domain_clusters.csv
```

Uploaded to Drive ops as:

```text
pdf_triage_review_with_domain_clusters_2026-05-25.csv
```

Also uploaded a domain-cluster-only index CSV:

```text
pdf_triage_domain_clusters_2026-05-25.csv
```

## Portable workflow spine repo

When Nicholas asks to version or migrate the research-wiki operating machinery, keep the Git repo narrow: commit skills, scripts, operating docs, config examples, and guardrail tests — not the corpus, Notion exports, Drive inventories, ops logs, run outputs, PDFs, caches, Hermes state, or credentials.

Maintenance rule: when changing mirrored research-wiki skills, `/root/research-wiki-tools/`, or the portable workflow repo's docs/config/tests/guardrails, update the `llm-research-wiki` Git mirror in the same work session, run guardrail tests, commit, push, and verify `origin/main` when credentials permit.

Session-specific detail, a known-good repo layout, and the sync-maintenance checklist live in `references/portable-workflow-spine-repo.md`.

Heuristic-maintenance notes and regression-test patterns from Nicholas's reviewed-row feedback live in `references/heuristic-maintenance-notes.md`.

## Recommended next step

The first reviewed-row heuristic pass has been implemented. Current durable behaviors to preserve with regression tests:

1. Reject PDF metadata/layout garbage during title detection and fall back to filename-derived titles when needed.
2. Add filename-derived author candidates and `author_confidence` when PDF metadata is missing.
3. Filter garbage URLs and prefer DOI-derived `https://doi.org/<doi>` as the canonical URL candidate.
4. Improve source/evidence type categories for policy guide, standards manual, slide deck, practice guide, methods paper, empirical study, review/meta-analysis, and book/book chapter.
5. Select full `research-wiki-ingest` candidates from clean rows: no boundary flags, high extraction confidence, DOI/canonical URL present, non-slide evidence type, and central wiki-relevant domain clusters.
