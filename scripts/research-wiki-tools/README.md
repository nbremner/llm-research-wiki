# Research Wiki Tools

Durable local tooling for the markdown research-wiki operating layer. The wiki is plain markdown in
git (`wiki/`); these scripts support the daily research scan, its triage, and the graph lint. There
is no Notion.

## graph_lint.py — markdown graph lint

Read-only lint over `wiki/`. Parses frontmatter + `[[wikilinks]]` and reports broken links, orphan
pages, sources that feed no topic, active topics citing no source, provenance gaps (missing
url/doi/hash), evidence-stale topics (≥2 sources `retrieved` after the topic's `updated` — depends
on the `updated:`-discipline rule in `wiki/schema.md`), and calendar-stale topics. Skips `schema.md`
(template docs), `README.md`, and code fences, so examples don't produce false positives. Performs
no edits.

```bash
python scripts/research-wiki-tools/graph_lint.py                 # markdown report to stdout
python scripts/research-wiki-tools/graph_lint.py --json          # JSON findings
python scripts/research-wiki-tools/graph_lint.py --fail-on High  # non-zero exit on any High+ finding
python scripts/research-wiki-tools/graph_lint.py --pairs         # contradiction-pair shortlist (JSON)
```

`--pairs` selects candidate topic pairs for the monthly semantic contradiction lint: ≥2 shared cited
sources or a direct topic↔topic link, change-gated to recently edited pairs (`--window-days`, 35),
ranked by shared-source count, capped (`--max-pairs`, 15) with rotating tail slots for cold pairs.
`--bootstrap` skips the gate for the first full sweep. The LLM skill judges the shortlist; selection
is deterministic. `--wiki-dir` defaults to the repo's `wiki/`. See `skills/research-wiki-graph-lint/`.

## research_scan.py — deterministic scan harness

Discovery (OpenAlex / arXiv / Crossref, seeded from `scan_config.py`) → dedup vs the coverage ledger →
pre-rank → acquisition ladder for surfaced records only (OA-resolve → direct PDF → Jina reader) →
ranked manifest + acquired files to Drive `_triage/pending`. No LLM anywhere in this path. Runs daily on the VPS via
`research-scan.timer` (08:00 America/Los_Angeles, failure alert to #logs).

```bash
uv run scripts/research-wiki-tools/research_scan.py --queries 3 --no-acquire  # local discovery smoke
uv run scripts/research-wiki-tools/research_scan.py --drive                   # full run to Drive
```

## scan_triage_apply.py — triage disposition applier

Deterministic applier for the `research-scan-triage` skill's judgments: validates the dispositions
JSON (fails loud on unknown/already-disposed ids, while allowing clear resolution of ambiguous calls),
enforces caps, moves artifacts from `_triage/pending` into `wiki`, `read-once`, or `discarded`, stamps
the manifest (local + Drive), and renders the owner digest.
Dry-run by default; `--execute` performs the Drive changes. `--friction` appends the rubric-friction
report — ambiguous proposals recorded in local manifests over the last 14 days (`--friction-days`) —
which the triage skill reads to decide whether to propose a rubric amendment (≤1 per digest;
ratification is owner-side, via git).

```bash
uv run scripts/research-wiki-tools/scan_triage_apply.py --latest --dispositions d.json            # dry run
uv run scripts/research-wiki-tools/scan_triage_apply.py --manifest m.json --dispositions d.json --execute --friction
uv run scripts/research-wiki-tools/scan_triage_apply.py --friction                                # report only
```

`scan_common.py` holds the shared machinery (id/dedup, ranking, OA-URL selection, ledger, Drive
helpers); `scan_config.py` is the editable rubric (seed queries, concept vocabulary, authority/rank
weights, caps). Edit `scan_config.py` to retune the scan — no code change needed.

## Operating boundary

`graph_lint.py` is read-only. `research_scan.py` writes only to Drive `_triage/pending` and its
ledger. `scan_triage_apply.py` moves files among visible `_triage` state folders only when executing
clear dispositions, within caps, and never deletes. Writing the wiki itself (`sources/`, `topics/`,
commits, Drive refiling) is done solely by the `research-wiki-ingest` skill, one source at a time,
with topic synthesis owner-approved before commit.
