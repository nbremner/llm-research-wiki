# Research-wiki Notion + Drive operating layer pattern

Use this reference when setting up or reorganizing a public research wiki that uses Notion as the operating layer and Google Drive as immutable raw-source storage.

## Target structure

Under a parent Notion page such as `research-wiki`, keep the live operational layer small:

```text
research-wiki
├── Schema                         # live agent contract; read first
├── Agent Operating Guide           # practical runbook for LC/DC/Hermes
├── Research Map / Overview         # living intellectual map: scope, questions, frontier/evidence map
├── Sources                         # canonical public source DB
├── Concepts                        # canonical synthesis DB
├── Inbox                           # low-trust capture/staging DB
├── Log                             # append-only audit DB
├── Index                           # future public front door
└── System Docs / Archive           # architecture rationale + completed setup docs
```

The raw-source Google Drive folder should contain only public source artifacts and a single `_inbox` staging subfolder. Do **not** store agent instructions, private notes, setup docs, or working synthesis in the raw-source folder.

## Document roles

- **Schema**: live operating contract. Agents read this first and follow it.
- **Agent Operating Guide**: practical runbook with IDs, role boundaries, workflows, and run sequence. Link it from Schema.
- **Research Map / Overview**: living intellectual map for scope, core lenses, active research questions, frontier areas, evidence status, and known gaps.
- **Architecture Master Reference — frozen**: preserved design rationale; not active operating instructions.
- **Setup Checklist — completed**: historical build artifact; not active operating instructions.
- **System Docs / Archive**: admin page linking frozen/completed docs.

## Agent role boundaries

- **Hermes / NicholasJunior**: normally writes only Inbox + Log; reads Schema and selected Sources/Concepts for dedupe/classification/routing. Do not write Sources, Concepts, Schema, or Index except during explicit owner-approved setup/maintenance.
- **LC**: linting, provenance, dedupe, promotion recommendations, boundary flags, schema proposals.
- **DC**: retrieval, user-facing answers, and public-source-backed synthesis. Never write work-derived/confidential synthesis into the public wiki.

## Recommended build sequence

1. Read the master reference and setup checklist; treat the master/reference rules as authoritative over checklist details.
2. Create/verify `Schema`.
3. Create full-page databases: `Sources`, `Concepts`, `Log`, `Inbox`.
4. Add relations only after target data sources exist.
5. Create `Index` placeholder.
6. Create `Research Map / Overview` as the living intellectual map for scope, core lenses, active research questions, frontier areas, evidence status, and known gaps.
7. Create `Agent Operating Guide — LC / DC / Hermes` and link it from Schema.
8. Create `System Docs / Archive`; rename old docs to frozen/completed and link them from the archive.
9. Create a clearly marked validation Source/Concept/Log row, verify relation/query behavior, then archive the test rows after user review.
10. Create/verify Drive raw-source folder and `_inbox` child.
11. Log the setup/reorg action in the Log database.

## Notion API quirks encountered

- With Notion API `2025-09-03`, a full-page database has a **database ID** and one or more **data source IDs**. `GET /v1/databases/{database_id}` returns `data_sources[]`; schema/query operations use the data source ID.
- Patch schema properties via `PATCH /v1/data_sources/{data_source_id}`.
- Relation properties require `single_property` or `dual_property`; `data_source_id` alone fails validation.
- Creating a relation can auto-create reverse relation labels such as `Related to Sources (...)`; this is normal Notion behavior.
- Patching a page `parent` may return success without visibly moving the child page in the Notion page tree. For archival organization, prefer functional archiving: rename pages (`— frozen`, `— completed`), add archival status callouts, and link them from `System Docs / Archive`. If the visible tree must be perfect, the user may need to drag/drop manually in the Notion UI.

## Validation checklist

- Query each data source successfully.
- Confirm expected property counts/types.
- Confirm Source ↔ Concept relation works.
- Confirm Log entries can be created.
- Confirm test rows are archived after user review.
- Confirm Drive raw-source folder and `_inbox` exist.
- Confirm Schema links to Agent Operating Guide and System Docs / Archive.
- Confirm Agent Operating Guide links to Research Map / Overview and states when to update it.
