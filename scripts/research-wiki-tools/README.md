# Research Wiki PDF Backlog Workflow

This directory contains durable local tooling for the public research-wiki PDF backlog.

## Current tool

`pdf_backlog_triage.py` indexes PDFs in the Google Drive `public-literature-wiki/_inbox` folder.

Default behavior is dry-run only:

- reads Drive metadata;
- downloads PDFs to a local run directory;
- computes SHA-256 hashes;
- extracts first-page/sample text and PDF metadata with PyMuPDF;
- detects DOI/URL/title/year/source-type/Schema-topic candidates;
- adds `domain_cluster_candidate` as an ops-layer classification signal for possible future Schema topic expansion;
- flags duplicates, provenance gaps, OCR needs, prompt-injection risk, and public-boundary risk;
- writes local CSV/JSONL/Markdown artifacts;
- performs no Drive or Notion mutations.

## Run

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py
```

Smoke test:

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py --max-files 10
```

Metadata-only inventory:

```bash
uv run /root/research-wiki-tools/pdf_backlog_triage.py --no-download
```

Outputs are written under:

```text
/root/research-wiki-runs/pdf-triage-YYYYMMDDTHHMMSSZ/
```

Key artifacts:

- `SUMMARY.md` — human-readable batch summary.
- `pdf_triage.csv` — spreadsheet-friendly review table.
- `pdf_triage.jsonl` — machine-readable rows for later automation.
- `drive_inventory_raw.json` — raw Drive metadata.
- `downloads/` — local PDF cache for that run.

## Human review in Apple Numbers

If Nicholas reviews the CSV in Apple Numbers and uploads a `.numbers` file, extract it back to CSV with:

```bash
uv run /root/research-wiki-tools/numbers_review_extract.py \
  /path/to/pdf_triage_review_2026-05-25.numbers \
  --out /path/to/pdf_triage_review_from_numbers.csv
```

This also writes a `.review_summary.json` file with rows where `human_review_status` or `human_review_notes` is populated.

## Human review interpretation

- Treat `looks-good` as `ok-to-summarize`.
- Treat `Exclude` as do-not-summarize and do-not-create-Inbox-candidate.
- Treat “Need to expand topic catalog to correctly categorize this” as “source looks acceptable, but Schema-topic assignment is weak.” Use `domain_cluster_candidate` to collect possible future taxonomy improvements.

## Operating boundary

These tools are intentionally not apply-mode tools. They do not rename/move Drive files or create Notion rows. Promotion into Notion Inbox, Drive canonical filing, and Source/Concept updates should be separate explicit workflows with approval gates.
