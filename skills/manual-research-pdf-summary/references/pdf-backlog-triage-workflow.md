# PDF backlog triage workflow

Session-derived pattern for moving from one-off manual PDF summaries to repeatable backlog indexing for the public research-wiki Drive `_inbox`.

## When to use

Use before running full Manual Research PDF Summary on a large backlog of PDFs, especially when filenames are inconsistent, incomplete, or wrong. The goal is to turn a pile of PDFs into a reviewable queue without mutating Drive or Notion.

## Core principle

Do not trust filenames as source truth. Use filenames only as clues. Prefer extracted PDF metadata, first-page/title signals, DOI, canonical URL, hashes, and text extraction confidence.

## Recommended dry-run index fields

For each PDF, capture:

- Drive file ID, original filename, MIME type, size, created/modified times, parent folders, Drive link
- local download path for the run cache
- SHA-256 hash and Drive MD5 where available
- page count
- PDF metadata title/author
- detected title and normalized title
- DOI and URL candidates
- publication year/date candidate
- extraction confidence and OCR need
- suggested Schema-approved topics only
- suggested source type and evidence type
- proposed canonical filename
- boundary/workflow flags
- duplicate keys when found

## Flags

Use the same public-boundary vocabulary as the main skill:

- `none`
- `provenance-missing`
- `public-verification-needed`
- `possible-duplicate`
- `extraction-low-confidence`
- `prompt-injection-risk`
- `private-boundary-risk`

## Dedupe strategy

Check duplicates by:

1. SHA-256 hash
2. Drive MD5
3. DOI
4. normalized detected title, but avoid generic journal-title false positives such as `industrial and organizational psychology`, `journal of applied psychology`, or `personnel psychology`

## Heuristic pitfalls found

- Avoid naive substring matching for private-boundary terms. A pattern like `nda` matches ordinary words such as `standardized`. Use word-boundary regexes for sensitive terms.
- Avoid treating publisher boilerplate such as broad copyright or distribution language as automatic `private-boundary-risk`; flag only clear public-boundary concerns like confidential/internal/non-public/proprietary-and-confidential language.
- Extraction can produce bad titles from PDF internals (`PII`, journal names, TeX filenames, production IDs). Keep detected title as a candidate, not canonical truth.
- Batch indexes are not Source/Concept promotion evidence by themselves. They route attention.

## Artifact pattern

Write a timestamped local run directory such as:

```text
/root/research-wiki-runs/pdf-triage-YYYYMMDDTHHMMSSZ/
```

Recommended artifacts:

- `SUMMARY.md` — human-readable run summary
- `pdf_triage.csv` — spreadsheet/review surface
- `pdf_triage.jsonl` — machine-readable rows for later automation
- `drive_inventory_raw.json` — raw Drive metadata
- `downloads/` — local cache for that run

Maintain a convenience symlink if useful:

```text
/root/research-wiki-runs/latest-pdf-triage
```

## Current local script pattern

A reusable script was created at:

```text
/root/research-wiki-tools/pdf_backlog_triage.py
```

Run with:

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

The script is intentionally dry-run only: it does not rename/move Drive files and does not create Notion rows.

## Next workflow stage

After triage, filter `pdf_triage.csv` by boundary/provenance/extraction flags and topic. Then run full Manual Research PDF Summary only on selected high/medium-priority candidates. Keep Notion writes conservative: Inbox and Log only, never canonical Sources/Concepts without explicit owner approval.
