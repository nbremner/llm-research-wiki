# llm-research-wiki

Portable workflow spine for Nicholas Bremner's LLM-assisted research wiki.

This repository is intentionally **not** a mirror of the research corpus. It stores the reusable machinery needed to operate or migrate the workflow to another agent/runtime: skills, workflow scripts, operating notes, validation guardrails, and configuration examples.

## What belongs here

- Hermes skill markdown files for the research-wiki workflows
- Durable Python scripts used to triage or prepare research-wiki inputs
- Operating-layer documentation that another agent needs in order to respect boundaries
- Non-secret configuration examples and setup notes
- Lightweight tests/validators for the workflow spine

## What does not belong here

- Research PDFs or document corpora
- Notion database exports, wiki records, or research ops logs
- Google Drive inventories, generated backlog CSVs, JSONL run outputs, downloads, or caches
- Hermes sessions, memories, state databases, auth files, logs, or credentials
- API tokens, OAuth refresh tokens, `.env` files, or private runtime state

The canonical research artifacts live in Notion and Google Drive. This repo tracks the machinery, not the corpus.

## Current contents

```text
skills/
  manual-research-pdf-summary/
  research-wiki-pdf-backlog-triage/

scripts/
  research-wiki-tools/
    pdf_backlog_triage.py
    numbers_review_extract.py

docs/
  research-wiki-operating-layer.md
  sciaiwiki-roadmap.md

config/
  example.env

tests/
  test_spine_guardrails.py
```

## Basic usage

The scripts are designed to run from a configured agent machine with Google Drive OAuth already available. They do not contain credentials.

```bash
uv run scripts/research-wiki-tools/pdf_backlog_triage.py --max-files 10
uv run scripts/research-wiki-tools/pdf_backlog_triage.py --no-download
uv run scripts/research-wiki-tools/numbers_review_extract.py /path/to/review.numbers --out /path/to/review.csv
```

## Agent migration notes

To move this spine to another agent:

1. Clone this repo.
2. Install/import the skills under `skills/` into that agent's skill mechanism.
3. Configure credentials locally using `config/example.env` as a guide. Do not commit real credentials.
4. Read `AGENTS.md` and `docs/research-wiki-operating-layer.md` before running workflows.
5. Run the guardrail test before committing any changes.

```bash
python -m pytest tests/ -q
```

## Boundary

This repo should remain boring. If a file is an artifact of a specific research scan, a PDF processing run, or a Notion/Drive state snapshot, it does not belong here.
