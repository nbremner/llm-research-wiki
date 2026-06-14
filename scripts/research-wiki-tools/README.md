# Research Wiki Tools

Durable local tooling for the markdown research-wiki operating layer. The wiki is plain markdown in
git (`wiki/`); these scripts support ingest, lint, and Drive backlog triage. There is no Notion.

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

## pdf_backlog_triage.py — Drive `_inbox` backlog indexer

Indexes PDFs in the Google Drive `public-literature-wiki/_inbox` folder to pick candidates for full
ingest (`research-wiki-ingest`). Dry-run only — it reads Drive metadata, downloads PDFs to a local run
dir, computes SHA-256 hashes, extracts sample text + metadata with PyMuPDF, detects
DOI/URL/title/year/source-type, adds a `domain_cluster_candidate` ops signal, and flags
duplicates/provenance gaps/OCR needs/prompt-injection/boundary risk. It does **not** rename, move, or
delete Drive files and does not write wiki pages.

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py                # full run
uv run /root/research-wiki-tools/pdf_backlog_triage.py --max-files 10 # smoke test
uv run /root/research-wiki-tools/pdf_backlog_triage.py --no-download  # metadata-only inventory
```

Outputs under `/root/research-wiki-runs/pdf-triage-YYYYMMDDTHHMMSSZ/`: `SUMMARY.md`, `pdf_triage.csv`,
`pdf_triage.jsonl`, `drive_inventory_raw.json`, `downloads/`.

`domain_cluster_candidate` is an ops-layer classification signal (not a wiki taxonomy — topics are
pages, not tags). Use it to spot recurring clusters worth a dedicated topic page.

## numbers_review_extract.py — Apple Numbers review extractor

If the owner reviews the triage CSV in Apple Numbers and uploads a `.numbers` file, extract it back to
CSV plus a `.review_summary.json` of reviewed/commented rows:

```bash
uv run /root/research-wiki-tools/numbers_review_extract.py /path/to/review.numbers --out /path/to/out.csv
```

Review status semantics: `looks-good` = ok-to-ingest; `Exclude` = do not ingest; "need to expand
topic catalog…" = source looks acceptable but a topic page may be missing.

## Operating boundary

These scripts are read-only with respect to the wiki and Drive. Ingest (writing `sources/`, editing
`topics/`, committing, and refiling the Drive PDF) is done by the `research-wiki-ingest` skill, with
topic synthesis owner-approved before commit.
