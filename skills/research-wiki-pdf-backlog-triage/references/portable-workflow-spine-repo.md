# Portable workflow spine repository

Use this note when Nicholas asks to back up, migrate, or version the research-wiki operating machinery.

## Architectural boundary

The Git repository should track the workflow spine, not the research corpus.

Commit:

- Research-wiki Hermes skills and supporting markdown references.
- Durable scripts used to triage or prepare research-wiki inputs.
- Agent operating notes, guardrails, tests, and non-secret config examples.
- Templates or schemas that another agent would need to run the workflows.

Do not commit:

- PDFs or document corpora.
- Notion database exports, wiki records, research ops logs, or activity ledgers.
- Google Drive inventories, generated backlog CSVs, JSONL outputs, downloads, caches, or run directories.
- Hermes sessions, memory/state DBs, auth files, logs, cron outputs, or credentials.
- API keys, OAuth files, `.env`, cookies, or credential helper files.

The purpose is portability: another agent should be able to clone the repo, import the skills, read the operating boundary, configure credentials locally, and run the workflow code without inheriting Nicholas's corpus or runtime state.

## Known repo shape

Repository name used in the workflow: `llm-research-wiki`.

Recommended layout:

```text
README.md
AGENTS.md
.gitignore
skills.allowlist
config/example.env
docs/research-wiki-operating-layer.md
scripts/research-wiki-tools/
skills/manual-research-pdf-summary/
skills/research-wiki-pdf-backlog-triage/
tests/test_spine_guardrails.py
```

Guardrail test should reject corpus/runtime artifacts by suffix/name/path and assert expected skills exist.

## Practical workflow

1. Build/update a local working copy from selected allowlisted skills and durable scripts only.
2. Write or update `README.md`, `AGENTS.md`, `.gitignore`, `config/example.env`, and guardrail tests.
3. Run the guardrail tests before committing.
4. Secret-scan obvious token patterns before staging.
5. Commit locally.
6. Push only after verifying GitHub credentials have write access to the target repo.

If remote push fails with 403, do not treat that as a workflow failure. Keep the local commit and optionally create a git bundle backup; the durable lesson is to distinguish prepared local spine from missing GitHub write permission.

## Sync-maintenance rule

Treat the `llm-research-wiki` repo as the Git mirror for the portable workflow spine, not as an optional archive. If a session changes any mirrored research-wiki skill, `/root/research-wiki-tools/`, or the repo's own docs/config/examples/tests/guardrails, do the repo sync before closing the work:

1. Copy or regenerate the changed workflow-spine files into the repo.
2. Run the guardrail tests.
3. Commit with a short workflow-focused message.
4. Push to `origin/main` when credentials permit.
5. Verify local `HEAD` and `origin/main` match after push.

Do not apply this rule to corpus/run artifacts; those still stay out of Git.
