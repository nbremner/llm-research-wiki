# Operating Model — llm-research-wiki

Status: canonical **architecture** for the research wiki. Read this to change the system.
Last updated: 2026-06-14.

This is the architecture doc — the substrate, roles, the operating loop, deployment, and cron
design. The **live contract** agents read at action time is `wiki/schema.md` (conventions, templates,
the one hard rule, the workflows). Where this doc and `wiki/schema.md` both touch a rule, **schema.md
is canonical** and this file points to it rather than restating it.

## One substrate: git holds machinery *and* content

The system has a **single source of truth: the `llm-research-wiki` git repo.** It holds both the
*machinery* (this doc, skills, scripts, tests) and the *content* (the `wiki/` directory). This
collapses the former two-plane build-time/run-time split — **Notion is retired** (archived
2026-06-14), and with it the separation that required reading different stores at build vs run time.

```text
llm-research-wiki/
  wiki/                  # the wiki itself (content + contract)
    schema.md            # the live contract — read first
    overview.md          # orientation: topics, open questions, thin areas
    topics/              # cross-linked synthesis (the compounding core)
    sources/             # one evidence record per public source
  skills/  scripts/  tests/  docs/   # the machinery
  OPERATING_MODEL.md     # this doc
```

| Store | Role | Mirrors |
| --- | --- | --- |
| **GitHub origin/main** (`llm-research-wiki`) | canonical — machinery **and** content | LC local clone, NicholasJunior VPS clone — synced by git, never independent truths |
| **Google Drive** (`public-literature-wiki` + `_inbox`) | the one external store: immutable raw-PDF capture | none — accessed live |

Google Drive holds only raw public source PDFs and the `_inbox` staging subfolder. No agent
instructions, private notes, or synthesis live there. Everything else is in git.

## Single-source-per-fact discipline

Each fact lives in exactly one place; the others **link**, never restate (this is what prevents drift).

- Conventions, templates, the hard rule, the workflows → **`wiki/schema.md`** (canonical contract).
- Orientation (what topics exist, open questions, thin areas) → **`wiki/overview.md`**.
- Synthesis → **`wiki/topics/`**; evidence → **`wiki/sources/`**.
- Architecture, roles, cron, parsimony → **this doc**.
- Skills / scripts / tests → **the repo** (NJ runs them from its synced clone).
- Roadmap / build history → **`docs/wiki-redesign-plan.md`**.

## Roles (orientation; the enforced rule is the one hard rule in schema.md)

- **LC** (Claude Code, human-directed): architect and overseer. Owns the git spine, approves topic
  synthesis into canon, runs/reads lint, keeps the model small.
- **NicholasJunior** (Hermes, VPS, scheduled): operator. Runs ingest / query / lint, **auto-commits
  source records** (evidence, low-judgment), routes **topic synthesis to owner approval**, and refiles
  raw PDFs in Drive.
- **DC** (work AI, Uber environment): quarantined outbound consumer of public artifacts; **no write
  path back** into the wiki; out of the build/maintain loop.

Trust model: source records are low-judgment and auto-committed; **topic synthesis is approval-gated**
(it becomes canon only with owner approval); DC has no write path.

## The loop — three operations

1. **Ingest** — a public PDF from Drive `_inbox` → a `sources/` record (auto-commit) + integrated
   `topics/` synthesis (owner-approved) + refile the raw PDF into `public-literature-wiki`.
2. **Query** — answer from `topics/` + `sources/`; file durable answers back into pages. Deeper
   cross-topic reviews (literature review, gap map, construct bridge, …) are on-demand synthesis here,
   not a separate artifact class.
3. **Lint** — markdown graph audit (broken wikilinks, orphans, claims-without-source, provenance gaps,
   stale topics) → report to owner; read-only, no auto-fix.

**Git history is the log.** There are no Reviews / Log / Inbox / Index databases — those were cut.

Skills in the repo: `research-wiki-ingest` (one paper at a time — the only ingest path),
`research-scan-triage` (dispositions surfaced scan candidates {wiki | read-once | discard} with
hybrid autonomy), `research-wiki-graph-lint`, `research-wiki-query`. Batch/cluster ingest and the
PDF-backlog triage workflow were retired 2026-07-04 (backlog cleared manually by the owner; sources
are ingested one at a time).

Upstream of ingest sits the **research-scan front end** (`docs/research-scrape-plan.md`): the
deterministic harness `research_scan.py` (discovery → dedup → acquisition ladder → pre-rank) fills the
Drive `_triage` store; `research-scan-triage` routes candidates; only wiki-candidates reach `_inbox`.

## Deployment to NicholasJunior

NJ's gateway loads each research skill via a **per-skill systemd bind mount** from its repo clone
(`/root/work/llm-research-wiki/skills/<name>` → `/root/.hermes/skills/research/<name>`), with a
**fail-closed gateway drop-in** (`hermes-gateway.service.d/research-wiki-mounts.conf`) that requires
those mounts present before the gateway starts. The clone syncs bidirectionally with `origin/main` via
`/root/bin/sync-research-wiki.sh` on `research-wiki-sync.timer` (daily). So: edit a skill → push to
origin → NJ pulls → bind mounts reflect it. Renaming/retiring a skill means updating the mount units
**and** the drop-in's required-mount list (rewrite the list before unmounting, or the running gateway
stops).

## Cron schedule (start small)

Conservative scheduled jobs; every loop volume-capped, deduped, and logged (Hermes auto-alerts
failures to Discord #logs).

| Job | Cadence | Writes | Cap |
|---|---|---|---|
| Research scan (deterministic harness, systemd timer) | Daily | Drive `_triage` only | ≤12 surfaced/run |
| Scan triage (`research-scan-triage`, hermes cron) | Daily | `_triage` → `_inbox` moves + digest | ≤10 auto-moves/run; ambiguous → owner |
| Graph-lint report | Periodic | report only | n/a |
| Ingest | On demand / small scheduled | sources/ (auto), topics/ (owner-approved) | low per-run cap |

(Scan-pipeline scheduling deployed 2026-07-04: `research-scan.timer` fires the harness daily at 08:00
America/Los_Angeles with an `OnFailure` alert to #logs; hermes cron job "Daily research scan triage"
runs the triage turn at 08:30 Pacific and delivers the digest to Discord #research-digest.)

Expand autonomy only after manual runs produce clean artifacts. Topic synthesis stays approval-gated
regardless of cadence.

## Governance (minimal)

- **Public-only sources** — the one hard rule (see `wiki/schema.md`).
- **Owner approves** before topic synthesis becomes canonical.
- **Contradictions are surfaced in prose, never auto-resolved** (disagreement carries meaning).

## Parsimony guardrails

- One contract (`wiki/schema.md`); everything reads it first.
- No loop becomes a backlog sink: caps + dedupe + logs on every scheduled job.
- When in doubt, do less. Complexity is the failure mode this model exists to prevent.

## Maintenance rule

When a workflow file changes, update the repo in the same session, run the tests, and keep
`origin/main` in sync with `HEAD` (see `AGENTS.md`). If a change alters conventions, templates, or the
hard rule → update **`wiki/schema.md`**. If it alters architecture, roles, deployment, or cron →
update **this** doc.
