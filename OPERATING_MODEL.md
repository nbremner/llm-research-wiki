# Operating Model — llm-research-wiki

Status: canonical **architecture** for the research wiki. Read this to change the system.
Last updated: 2026-06-14.

This document is the build-time architecture: the two-plane model, the role model
rationale, the operating loop, the cron design, and the Notion setup reference. It is
**not** the live enforced contract. The contract agents read at action time is the
**Notion Schema** (`36accc4a-237c-81a9-8de2-c667d2a95796`). Where this document and the
Schema both touch roles or write-permissions, the **Schema is canonical** and this file
points to it rather than restating it.

## First principle: two planes, by time-of-use

The system has two sources of truth, separated by *when you read them*, not by
machinery-vs-content:

- **Git repo (`llm-research-wiki`) — build-time.** *How the system is built and evolved.*
  Architecture (this doc), skills, scripts, tests, roadmap, setup references, the Notion
  address map. Read it to **change the system**.
- **Notion + Google Drive — run-time.** *What agents enforce and read to act now.*
  The Schema and Agent Operating Guide (the live operating contract), the Research Map,
  and the content databases (Sources, Concepts, Reviews, Inbox, Log) + raw public PDFs.
  Read it to **take action**.

Notion **legitimately holds agent instructions** — the Schema and Agent Operating Guide
are the runtime contract and belong there, because that is where NicholasJunior reads
them to act. The Git repo holds the *architecture and machinery* for building/evolving
the system. Neither plane holds the other's canonical facts.

## Sources of truth: two canonical stores, two mirrors

| Plane | Canonical store | Mirrors (never independent sources) |
|---|---|---|
| Build-time | **GitHub origin** (`llm-research-wiki`) | LC local clone, NicholasJunior clone — kept in sync by `git pull`/`push` |
| Run-time | **Notion** (`research-wiki`) | none — accessed live (LC via MCP, NJ via API / prompt URLs) |

The local clone and NJ's clone are working copies of origin, not separate truths.
Google Drive is the immutable raw-source store under the run-time plane.

### Single-source-per-fact discipline

Each fact lives in exactly **one** plane. The other plane **links** to it; it never
restates it. This is the rule that prevents drift (the DC role inconsistency happened
because role text was restated in both Schema and this doc).

- Enforced roles, write-permissions, taxonomy, promotion rules → **Notion Schema** (canonical).
- Live run steps + current Notion IDs → **Notion Agent Operating Guide** (canonical).
- Architecture, cron design, parsimony rules → **this doc** (canonical).
- Roadmap → **`docs/sciaiwiki-roadmap.md`** (canonical); the Notion roadmap page is a pointer.
- Skills/scripts/tests → **Git** (canonical); NJ runs them from its synced clone.
- Research Map / Overview → **Notion** (canonical, content).

## Roles (orientation only — canonical text in Schema)

One sentence each; the **enforced** definitions live in the Notion Schema and Agent
Operating Guide. Do not treat the lines below as the contract.

- **LC** (Claude Code, human-directed): architect and overseer. Owns the Git spine,
  approves promotions into canon, runs/reads lint, keeps the model small.
- **NicholasJunior** (Hermes, GPT-5.5, VPS, scheduled): operator. Runs bounded cron
  loops and answers research queries, writing only to low-trust zones; routes durable
  synthesis to LC.
- **DC** (work AI, Uber environment): quarantined outbound analyst. Consumes public
  artifacts passed into the confidential work environment; **no write path back** into
  the public wiki; out of the wiki build/maintain loop.

The trust model behind the write-permissions (canonical matrix in Schema) is three
tiers: agents auto-write **low-trust** zones (Inbox, Log, Review/Summary drafts);
**canon** (Sources, Concepts, Schema, Research Map, Index) is approval-gated through LC;
**DC** has no write path. Concept graduation is always approval-gated.

## The loop — four operations only

Everything maps to one of these or is frozen:

1. **Ingest** — PDFs from Drive `_inbox` → Inbox + Review/Summary drafts.
2. **Lint** — graph-coherence audit → report surfaced to LC (read-only; no auto-fix).
3. **Review** — staged synthesis (literature reviews, gap maps) → Review drafts +
   candidate Concept/Research-Map updates (proposed, not applied).
4. **Query** — answer from existing material; route durable synthesis to LC.

Supporting skills in the repo: `manual-research-pdf-summary`,
`research-wiki-pdf-backlog-triage`, `research-wiki-graph-lint`,
`research-wiki-review`, `research-wiki-query`.

## Cron schedule (start small)

NicholasJunior runs conservative scheduled jobs. Hermes already auto-alerts job failures
to Discord. Every loop must be volume-capped, deduped, and logged.

| Job | Cadence | Writes | Cap |
|---|---|---|---|
| PDF backlog triage + Inbox→Review drafts | Weekly | Inbox, Review drafts | low per-run cap |
| Candidate-source discovery | Weekly / biweekly | Inbox | low per-run cap |
| Graph-lint report | Monthly | report only (no canon writes) | n/a |

Expand autonomy only after manual runs produce clean artifacts and logs. Concept
graduation stays approval-gated regardless of cadence.

## Parsimony guardrails

- **Frozen for now:** roadmap Themes 5 (markdown mirror), 6 (Concept subtype expansion),
  7 (confidence/contested schema fields). Revisit only when the small loop is stable.
- One Schema is canonical; everything reads it first.
- No loop becomes a backlog sink: caps + dedupe + logs on every scheduled job.
- When in doubt, do less. Complexity is the failure mode this model exists to prevent.

## Notion operating-layer reference

How the run-time plane is structured and built. (Setup machinery; the live rules are in
the Schema, not here.)

### Target structure

Under the `research-wiki` parent page, keep the live operational layer small:

```text
research-wiki
├── Schema                         # live agent contract; read first (canonical)
├── Agent Operating Guide           # runbook for LC/NicholasJunior; current IDs (canonical)
├── Research Map / Overview         # living intellectual map: scope, questions, evidence map
├── Sources                         # canonical public source DB
├── Concepts                        # canonical synthesis DB
├── Reviews                         # staged review artifacts
├── Inbox                           # low-trust capture/staging DB
├── Log                             # append-only audit DB
├── Index                           # future public front door
└── System Docs / Archive           # frozen rationale + completed setup docs + roadmap pointer
```

The Google Drive raw-source folder holds only public source artifacts plus a single
`_inbox` staging subfolder. No agent instructions, private notes, or working synthesis
in the raw-source folder.

### Document roles

- **Schema**: live enforced contract. Agents read it first.
- **Agent Operating Guide**: runbook with current IDs, role-boundary detail, workflows,
  and run sequence. Linked from Schema.
- **Research Map / Overview**: living intellectual map (scope, lenses, active questions,
  frontier areas, evidence status, gaps).
- **Reviews**: staged synthesis; proposes Concept/Research-Map updates, not canon by default.
- **Architecture Master Reference — frozen** / **Setup Checklist — completed**: historical;
  not active operating instructions.
- **System Docs / Archive**: links frozen/completed docs and points to the Git roadmap.

### Build / reorg sequence

1. Read the master reference and setup checklist; the master rules win over checklist detail.
2. Create/verify `Schema`.
3. Create full-page databases: `Sources`, `Concepts`, `Reviews`, `Log`, `Inbox`.
4. Add relations only after target data sources exist.
5. Create `Index` placeholder.
6. Create `Research Map / Overview`.
7. Create `Agent Operating Guide` and link it from Schema.
8. Create `System Docs / Archive`; mark old docs frozen/completed and link them.
9. Create a marked validation Source/Concept/Log row, verify relation/query behavior, then
   archive the test rows after review.
10. Create/verify Drive raw-source folder and `_inbox` child.
11. Log the setup/reorg action.

### Notion API quirks

- With Notion API `2025-09-03`, a full-page database has a **database ID** and one or more
  **data source IDs**. `GET /v1/databases/{database_id}` returns `data_sources[]`;
  schema/query operations use the data source ID.
- Patch schema properties via `PATCH /v1/data_sources/{data_source_id}`.
- Relation properties require `single_property` or `dual_property`; `data_source_id` alone
  fails validation.
- Creating a relation can auto-create reverse relation labels; this is normal.
- Patching a page `parent` may report success without visibly moving the page in the tree.
  Prefer functional archiving: rename (`— frozen`, `— completed`), add status callouts, and
  link from `System Docs / Archive`. If the visible tree must be perfect, drag/drop in the UI.

### Validation checklist

- Query each data source successfully.
- Confirm expected property counts/types.
- Confirm Source ↔ Concept relation works.
- Confirm Reviews can relate to reviewed Sources and related Concepts.
- Confirm Log entries can be created.
- Confirm test rows are archived after review.
- Confirm Drive raw-source folder and `_inbox` exist.
- Confirm Schema links to Agent Operating Guide and System Docs / Archive.
- Confirm Agent Operating Guide links to Research Map / Overview and states when to update it.

## Maintenance rule

When a workflow file mirrored here changes, update this repo in the same session, run
`python -m pytest tests/ -q`, and keep `origin/main` in sync with `HEAD` (see `AGENTS.md`).
If a change alters roles or write-permissions, update the **Notion Schema** (canonical)
and reconcile this doc's pointer. If it alters architecture, cron design, or the two-plane
model, update **this** doc.
