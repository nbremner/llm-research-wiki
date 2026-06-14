# Notion content inventory — for the markdown-wiki migration

Step 1 of `docs/wiki-redesign-plan.md`. Captured 2026-06-14. **Notion untouched** (read-only pass).

## Headline finding (changes the plan's premise)

The plan assumed the migration material is the **Sources** and **Concepts** databases. It isn't:

- **Sources DB** (`collection://2491c01c-…`) — **empty.** Three scoped semantic searches returned zero rows.
- **Concepts DB** (`collection://f578eaf9-…`) — **empty.** Scoped search returned zero rows.

Both are well-designed but **unpopulated scaffolding**. The real accumulated research lives elsewhere,
in two places — and only one of them is in Notion at all.

## Where the actual content is

### A. The `research-wiki` operating tree (root `368ccc4a-…`)

This is the structured "spine" the existing skills target. Almost all of it is **machinery/orientation,
not migratable evidence**:

| Page | ID | Status |
|---|---|---|
| Schema (canonical contract) | `36accc4a-…-81a9-…` | operating doc → becomes `wiki/schema.md` |
| Agent Operating Guide (LC/DC/Hermes) | `36bccc4a-…-813c-…` | operating doc → folds into schema/CLAUDE.md |
| **Research Map / Overview** | `37cccc4a-…-81cc-…` | **rich, real synthesis → becomes `wiki/overview.md`** (near 1:1) |
| Index (public front door placeholder) | `36accc4a-…-81b2-…` | being cut per plan |
| System Docs / Archive | `36bccc4a-…-812f-…` | history |
| Architecture Master Reference (frozen) | `369ccc4a-…-80a7-…` | history |
| Setup Checklist (completed) | `36accc4a-…-8136-…` | history |
| Sources / Concepts / Reviews / Inbox / Log DBs | (see address map) | **all empty / being cut** |

The single most valuable artifact here is the **Research Map / Overview** — it already is the
"living orientation page" the plan calls for (scope, 8 lenses, concept map, active questions,
deep-dive queue, evidence map with strong/thin/contested areas). It transfers almost verbatim.

### B. The personal "Workforce Transformation & IO Psych" tree (root `338ccc4a-…-81f0-…`)

**This is where the substance is — and it is a separate tree from `research-wiki`, not under it.**
It mixes genuinely public research with personal and work-derived material:

- **Daily research scans** (`33fccc4a-…-8057-…`) — **~22 dated digest pages**, 2026-04-09 → 2026-06-12.
  Each lists 1–6 articles with author/org, source type, relevance tier, and a "why it matters" note.
  **These are the closest thing to a Sources corpus that exists** — ~50–80 article records total.
- Synthesis / framework pages: `AI Study Notes`, `Org Design Framework`,
  `Socialization & Change Frameworks`, `Ideas & Strategic Directions`, `EBMgmt and GenAI`,
  `[GenAI] Sales AI Research Brief`, `Strategic workforce planning at NASA`,
  `Forward Deployed IO Psychologist (FDIO) Article`.
- `Psychology and Work Index` (a separate database, `collection://df8ccc4a-…`).
- Clearly personal/private: `Rolodex — People & Initiatives`, `Key Conversations`, `Notes on ACP`,
  `HBR Submission Guidelines`, `Director, Workforce Innovation — Sample JD`, advice notes.

## Two problems this inventory surfaces

### 1. The public-only boundary is entangled (this is the one hard governance rule)

The scan workflow is **Uber work**: the "Transfer research scan" task page spells out the context —
researcher at Uber studying AI in **Uber for Business (U4B) sales teams**, six research questions
**RQ1–RQ6**, digests emailed to **nbremner@uber.com**. The daily scans tag each article against those
RQs. So the daily-scan corpus is *public articles* framed through a *confidential work lens*.

Migrating it wholesale would carry work-derived framing into the public wiki. A migration here needs a
**public/private split**: keep the public article records + their public summaries; drop the U4B/RQ
framing and anything work-specific. This is a judgment call that should be yours, not the agent's.

### 2. The richest evidence isn't in Notion — it's on a work machine

The scans only hold *digests*. The actual structured summaries live as
`~/Documents/AI literature/Research/Completed/*.md` with PDFs in `Archive - Reviewed/` and a
`scan-log.json` dedup index — on whatever machine runs the scan (the Uber work env, per the email).
**Confirmed not present on this machine** (`find ~/Documents` — no match). So from here we can migrate
the Notion digest layer, but not the full per-paper `.md` summaries unless that folder is brought over.

## What cleanly maps to the target model

| Target (`wiki/`) | Best source |
|---|---|
| `overview.md` | Research Map / Overview (`37cccc4a-…-81cc-…`) — near-verbatim |
| `schema.md` | existing Schema + Agent Operating Guide, trimmed to the lean conventions |
| `topics/` | synthesis pages in tree B (Org Design, Socialization & Change, AI Study Notes, …) |
| `sources/` | the ~22 daily-scan digests → one record per article (public ones only) |

## Decision (owner, 2026-06-14): start clean, no migration

Owner's call: **archive the entire Notion infrastructure and start the markdown wiki clean.**
No content is migrated from Notion — not the (empty) Sources/Concepts DBs, not the daily-scan
digests, not the synthesis pages. This sidesteps the public/private entanglement entirely: nothing
work-derived crosses over because nothing crosses over. The new `wiki/` fills going forward via the
ingest/query workflows.

Consequences for the build sequence:

- **Step 4 (migrate) is dropped.** The wiki is scaffolded empty and grows fresh.
- `overview.md` is authored new and lean (not copied from the Research Map).
- **Notion archival (step 8) stays last and is gated on owner confirmation** — it is irreversible and
  outward-facing, so it happens only after the clean wiki exists and is confirmed, never up front.
