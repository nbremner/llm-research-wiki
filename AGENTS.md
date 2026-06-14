# Agent instructions for llm-research-wiki

This repository contains the portable operating spine for the LLM-assisted research wiki.

## Hard boundary

Do not commit corpus artifacts or runtime state. Specifically, do not commit:

- PDFs, Word documents, slide decks, spreadsheets, or extracted document caches
- generated research-scan outputs, backlog CSVs, JSONL outputs, or Drive inventory dumps
- Notion exports, research ops logs, or activity ledgers
- Hermes `state.db`, sessions, memories, logs, caches, auth files, cron outputs, or `.env` files
- API keys, OAuth tokens, cookies, private keys, or credential helper files

The repo tracks workflow machinery only: skills, scripts, templates, schemas, tests, and non-secret setup docs.

## Sync-maintenance rule

When changing any workflow file mirrored here, update this repo in the same work session. This includes self-improvement edits to research-wiki-related Hermes skills, especially:

- `skills/research-wiki-ingest/`
- `skills/research-wiki-pdf-backlog-triage/`
- local source copies under `/root/.hermes/skills/research/...`
- local workflow tooling under `/root/research-wiki-tools/`
- repo docs, config examples, tests, and guardrails

After changing mirrored files: copy the updated version into this repo, run tests, commit, push, and verify `origin/main` matches local `HEAD`.

When renaming or retiring a mirrored skill, update `skills.allowlist`, this file, and
NicholasJunior's live Hermes skill store in the same session so the mirror stays consistent.

## Before committing

Run:

```bash
python -m pytest tests/ -q
git status --short
```

If pytest is unavailable, at minimum inspect staged files with:

```bash
git diff --cached --name-only
```

and verify no forbidden artifact class is staged.
