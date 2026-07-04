# Research Wiki Tools

Durable local tooling for the markdown research-wiki operating layer. The wiki is plain markdown in
git (`wiki/`); these scripts support the daily research scan, its triage, and the graph lint. There
is no Notion.

## graph_lint.py — markdown graph lint

Read-only lint over `wiki/`. Parses frontmatter + `[[wikilinks]]` and reports broken links, orphan
pages, sources that feed no topic, active topics citing no source, provenance gaps (missing
url/doi/hash), and stale topics. Skips `schema.md` (template docs), `README.md`, and code fences, so
examples don't produce false positives. Performs no edits.

```bash
python scripts/research-wiki-tools/graph_lint.py                 # markdown report to stdout
python scripts/research-wiki-tools/graph_lint.py --json          # JSON findings
python scripts/research-wiki-tools/graph_lint.py --fail-on High  # non-zero exit on any High+ finding
```

`--wiki-dir` defaults to the repo's `wiki/`. See `skills/research-wiki-graph-lint/`.

## research_scan.py — deterministic scan harness

Discovery (OpenAlex / arXiv / Crossref, seeded from `scan_config.py`) → dedup vs the coverage ledger →
acquisition ladder (OA-resolve → direct PDF → Jina reader) → pre-rank → ranked manifest + acquired
files to the Drive `_triage` store. No LLM anywhere in this path. Runs daily on the VPS via
`research-scan.timer` (08:00 America/Los_Angeles, failure alert to #logs).

```bash
uv run scripts/research-wiki-tools/research_scan.py --queries 3 --no-acquire  # local discovery smoke
uv run scripts/research-wiki-tools/research_scan.py --drive                   # full run to Drive
```

## scan_triage_apply.py — triage disposition applier

Deterministic applier for the `research-scan-triage` skill's judgments: validates the dispositions
JSON (fails loud on unknown/already-disposed ids), enforces caps, moves auto-queued artifacts
`_triage/files` → `_inbox`, stamps the manifest (local + Drive), and renders the owner digest.
Dry-run by default; `--execute` performs the Drive changes.

```bash
uv run scripts/research-wiki-tools/scan_triage_apply.py --latest --dispositions d.json            # dry run
uv run scripts/research-wiki-tools/scan_triage_apply.py --manifest m.json --dispositions d.json --execute
```

`scan_common.py` holds the shared machinery (id/dedup, ranking, OA-URL selection, ledger, Drive
helpers); `scan_config.py` is the editable rubric (seed queries, concept vocabulary, authority/rank
weights, caps). Edit `scan_config.py` to retune the scan — no code change needed.

## Operating boundary

`graph_lint.py` is read-only. `research_scan.py` writes only to the Drive `_triage` store and its
ledger. `scan_triage_apply.py` moves files into the wiki `_inbox` only when executing clear
dispositions, within caps, and never deletes. Writing the wiki itself (`sources/`, `topics/`,
commits, Drive refiling) is done solely by the `research-wiki-ingest` skill, one source at a time,
with topic synthesis owner-approved before commit.
