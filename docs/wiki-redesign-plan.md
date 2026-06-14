# Wiki Redesign — Build Plan (markdown-in-git, Karpathy-aligned)

Status: **approved plan, ready to build.** Created 2026-06-14.
This supersedes the Notion-database approach in `docs/sciaiwiki-roadmap.md` (kept for history).
Read `OPERATING_MODEL.md` first for the operating context.

## Why (decision record)

Decided 2026-06-14 after a requirements review anchored on Karpathy's LLM-wiki pattern
(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Owner's answers:

- **Purpose:** (1) feeds his own writing/thinking, (2) a queryable knowledge base, (3) feedstock
  for work analysis via DC. **Not** a public resource for others.
- **Scale:** small now, unsure later → Karpathy regime (full-context reading, no RAG/vector DB).
- **Synthesis is the product:** heavy cross-source synthesis in his own framings, especially for
  writing; what he reaches for is *synthesized topic views + connections/contradictions*.
- **Flagged as over-engineered:** the 5-database Notion split and the governance stack.
- **Capture:** PDFs into Google Drive `_inbox` (unchanged).
- **DC/work handoff:** wants a synthesized brief; mechanism not yet established.

**Verdict:** migrate the wiki from the Notion 5-database stack to plain cross-linked markdown in
this repo; **Obsidian** as the human visualization/editing layer (wikilinks, backlinks, graph,
mobile); retire Notion once migrated; **minimal governance.**

## Target architecture

The lean data model:

| Unit | Role |
|---|---|
| **topics/** | THE core — cross-linked synthesis pages; surface connections & contradictions in prose |
| **sources/** | evidence under syntheses: one file per paper (citation + summary + key claims) |
| **overview.md** | one living orientation page: topics that exist, open questions, thin areas |
| **schema.md** (or `CLAUDE.md`) | conventions + the 3 workflows + the one hard rule |

```
wiki/
  overview.md
  schema.md
  topics/        # cross-linked synthesis (the compounding core)
  sources/       # per-paper evidence records
```

- Raw PDFs stay in Google Drive `_inbox` (immutable capture front door).
- **Obsidian** vault = the `wiki/` dir (or repo root); gives wikilinks/backlinks/graph/search/mobile.
- **NJ maintains the repo** — it's already cloned at `/root/work/llm-research-wiki`, bind-mounted, and
  auto-synced on the VPS, so the maintenance loop already exists; the `wiki/` dir rides along.
- **One source of truth:** git holds machinery **and** content. This collapses the build-time/run-time
  two-plane model in `OPERATING_MODEL.md` — update that doc as part of the build.

## What gets cut (the over-engineering removed)

- **Reviews database** → a review is on-demand synthesis across topic pages when a project needs one.
- **Log database** → git history is the log.
- **Inbox database** → capture is Drive `_inbox`; the agent writes pages directly.
- **Index / public front door** → not building for others.
- **Research Map machinery** (8 lenses, frontier map, evidence map, deep-dive queue) → lean `overview.md`.
- **Governance fields** (confidence/contested/boundary-flags, candidate-update bundles, layered role rules).

## Governance (minimal — locked)

One hard rule: **public-only sources.** Owner approves before a synthesis becomes canonical.
Contradictions are **surfaced in prose, never auto-resolved** (Karpathy: disagreement carries meaning).

## Operations (the few that matter)

- **Ingest:** Drive `_inbox` PDF → a `sources/` record → integrate its claims into the relevant
  `topics/` pages (update, strengthen links, flag contradictions).
- **Query:** answer from topic/source pages; file durable answers back as/into pages (don't let
  good synthesis evaporate into chat).
- **Lint:** periodic health check — orphan pages, stale claims, broken wikilinks, claims with no source.

## Build sequence (for the new session)

1. **Inventory** the existing Notion content: export/count the current Sources + Concepts (the real
   material to migrate). Keep Notion untouched until the markdown version is verified.
2. **Define conventions** in `wiki/schema.md` (CLAUDE.md-style): topic-page and source-page templates,
   minimal frontmatter, the `[[wikilink]]` convention, the public-only rule, the 3 workflows.
3. **Scaffold** `wiki/` (overview, topics/, sources/, schema).
4. **Migrate** Notion Sources/Concepts → markdown pages (agent-assisted, one pass), cross-linking as it goes.
5. **Replace the skills/scripts**: the current 5 skills + `graph_lint.py` are Notion-API based; rewrite
   them to operate on the markdown wiki (ingest, query, lint), or retire what's no longer needed.
6. **Set up Obsidian** over the repo; confirm wikilinks/backlinks/graph render; decide vault scope + device sync.
7. **Verify end-to-end** with a couple of real sources (ingest → topic update → query → lint).
8. **Retire Notion** once the markdown wiki is confirmed good; archive or delete the workspace.
9. **Update `OPERATING_MODEL.md`** to the collapsed single-substrate model (git = machinery + content).

## Open decisions to resolve early

- **DC reading GitHub from the Uber work env — UNRESOLVED.** Determines the work-handoff path. If the
  work environment can read a public repo, the handoff is trivial; if not, design an alternative
  (carry a synthesized brief manually, or a sanctioned mirror). Resolve before relying on it.
- Obsidian vault scope (wiki/ vs repo root) and how it syncs to his devices.
- Fate of the Notion workspace after migration (archive vs delete).

## Don't break

- The **public-only boundary** (the one governance rule).
- The **VPS sync infra** (bind mounts + `research-wiki-sync.timer`) — the `wiki/` dir is in the same
  repo, so NJ's existing sync already covers it. (See `Hermes/FLEET_STATUS.md`.)
- The clean **build/run separation discipline** until `OPERATING_MODEL.md` is formally updated in step 9.
