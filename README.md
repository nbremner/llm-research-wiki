# llm-research-wiki

The research wiki for Nicholas Bremner's LLM-assisted research — plain cross-linked markdown in git,
plus the machinery that operates it.

This repo holds **both** the wiki content (`wiki/`: synthesis topics, source records, the contract)
**and** the machinery (skills, scripts, tests, operating docs). It is the single source of truth. The
only thing kept outside git is the raw-PDF corpus in Google Drive. See `OPERATING_MODEL.md`.

## What belongs here

- The wiki itself under `wiki/` (`schema.md`, `overview.md`, `topics/`, `sources/`)
- Hermes skill markdown files for the research-wiki workflows
- Durable Python scripts used to triage or prepare research-wiki inputs
- Operating-layer documentation and the architecture model
- Non-secret configuration examples and lightweight guardrail tests

## What does not belong here

- Research PDFs or document corpora (those live in Google Drive)
- Google Drive inventories, generated backlog CSVs, JSONL run outputs, downloads, or caches
- Hermes sessions, memories, state databases, auth files, logs, or credentials
- API tokens, OAuth refresh tokens, `.env` files, or private runtime state

The raw-PDF corpus lives in Google Drive; everything else — content and machinery — lives here.

## Current contents

```text
wiki/                       # the wiki: schema.md (contract), overview.md, topics/, sources/
OPERATING_MODEL.md          # canonical architecture — substrate, roles, loop, deployment, cron
AGENTS.md                   # repo contribution rules + hard boundary

skills/
  research-wiki-ingest/
  research-wiki-graph-lint/
  research-wiki-pdf-backlog-triage/
  research-wiki-query/

scripts/
  research-wiki-tools/
    graph_lint.py
    pdf_backlog_triage.py
    numbers_review_extract.py

docs/
  wiki-redesign-plan.md        # the build plan for the markdown-in-git wiki

config/
  example.env

tests/
  test_graph_lint.py
  test_pdf_backlog_triage.py
  test_spine_guardrails.py
```

## Basic usage

The scripts run from a configured agent machine with Google Drive OAuth already available. They do not contain credentials.

```bash
python scripts/research-wiki-tools/graph_lint.py                       # lint the wiki graph
uv run scripts/research-wiki-tools/pdf_backlog_triage.py --max-files 10
uv run scripts/research-wiki-tools/pdf_backlog_triage.py --no-download
uv run scripts/research-wiki-tools/numbers_review_extract.py /path/to/review.numbers --out /path/to/review.csv
```

## Agent migration notes

To move this spine to another agent:

1. Clone this repo.
2. Install/import the skills under `skills/` into that agent's skill mechanism.
3. Configure credentials locally using `config/example.env` as a guide. Do not commit real credentials.
4. Read `OPERATING_MODEL.md` and `AGENTS.md` before running workflows. The live contract agents read at action time is `wiki/schema.md`.
5. Run the guardrail tests before committing any changes.

```bash
python -m pytest tests/ -q
```

## Boundary

This repo holds the wiki content and its machinery. If a file is an artifact of a specific research scan, a PDF processing run, or a Drive state snapshot, it does not belong here.
