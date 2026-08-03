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
- `skills/research-scan-triage/`
- `skills/research-wiki-graph-lint/`
- `skills/research-wiki-query/`
- local source copies under `/root/.hermes/skills/research/...`
- local workflow tooling under `/root/research-wiki-tools/`
- repo docs, config examples, tests, and guardrails

After changing mirrored files: get the change into this repo, run tests, commit, push, and verify
`origin/main` matches local `HEAD`. On the VPS, `/root/research-wiki-tools` and the skill mounts are
symlinks/bind mounts into the repo clone — edits there already sit in the clone's working tree, so
commit from the clone rather than copying; copy only for any genuinely separate local file.

When renaming or retiring a mirrored skill, update `skills.allowlist`, this file,
`OPERATING_MODEL.md`, NicholasJunior's live Hermes skill store, **and** the per-skill mount units +
the gateway drop-in's required-mount list — rewrite that list *before* unmounting, or the running
gateway stops (see `OPERATING_MODEL.md` § Deployment).

## Wiki frontmatter discipline

`updated:` on wiki pages means last **synthesis** edit. Set it to the synthesis date whenever a
page's claims, evidence, or connections change; mechanical passes (style, link fixes, typo sweeps)
must not bump it — the graph lint's evidence-staleness check depends on this. Rule adopted
2026-08-03, prospective. Full rule in `wiki/schema.md` § Formatting.

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
