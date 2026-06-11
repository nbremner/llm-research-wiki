# SciAI Wiki Alignment Roadmap

Created: 2026-05-29
Status: active roadmap
Scope: public research-wiki architecture, `llm-research-wiki` workflow spine, Notion operating layer, and future markdown/wiki graph layer.

## Purpose

This roadmap captures the architecture improvements identified from reviewing *Beyond Retrieval: Compounding Scientific Extelligence with Artificial Intelligence Wikis* against Nicholas Bremner's current public research-wiki system.

The central conclusion is:

> Keep the current Notion + Google Drive governance model, but add the SciAI-style markdown/graph discipline: a living overview, review workflow, graph linting, dense cross-links, researcher-intent ingestion, and durable query outputs.

The current system is stronger than the paper's minimal implementation on public-boundary control, provenance, role separation, and operational safety. It is weaker on the compounding wiki-graph experience the paper advocates.

## Current architecture baseline

### Current public research-wiki operating layer

- **Notion** is the live operating layer:
  - Schema
  - Agent Operating Guide
  - Sources database
  - Concepts database
  - Inbox database
  - Log database
  - Index placeholder
- **Google Drive** stores public raw source artifacts:
  - `public-literature-wiki/`
  - `_inbox/` staging folder
- **Hermes / NicholasJunior** normally writes only:
  - Inbox
  - Log
- **LC / DC / Hermes role boundaries** preserve public-only scope and reduce epistemic contamination.
- **`llm-research-wiki` GitHub repo** stores the portable workflow spine only:
  - skills
  - scripts
  - docs
  - tests
  - non-secret config examples

### SciAI Wiki reference architecture

The SciAI Wiki model emphasizes:

- immutable raw sources;
- an LLM-maintained interlinked markdown wiki;
- schema/protocol/skill files governing agent behavior;
- four core operations:
  - ingestion;
  - query;
  - lint / maintenance;
  - review;
- compounding scientific memory through durable cross-links, provenance, contradiction tracking, and review synthesis.

## Design principle

Do **not** copy SciAI's broad autonomy wholesale.

For a private local research wiki, “AI owns wiki” is acceptable. For this public research-wiki, with work-adjacent topics and strict public/private boundaries, the safer pattern is:

1. preserve staged governance;
2. create better approved pathways for compounding synthesis;
3. make uncertainty, provenance, and promotion status explicit;
4. mirror/export to markdown so the system remains portable and agent-readable.

## Roadmap themes

### Theme 1 — Add a living Research Map / Overview layer

**Problem**

The current system has Schema and Agent Guide, but lacks a first-class living intellectual map equivalent to SciAI's `overview.md`.

**Goal**

Create a durable artifact that tracks:

- purpose of the public research wiki;
- current research questions;
- frontier questions;
- conceptual map;
- active themes;
- known gaps;
- what would make the wiki more useful next.

**Candidate Notion location**

```text
research-wiki
└── Research Map / Overview
```

**Candidate GitHub artifact**

```text
docs/research-map-template.md
```

**Acceptance criteria**

- A Notion page exists for the live Research Map / Overview.
- A portable markdown template exists in GitHub.
- Agent Operating Guide references when to update it.
- Updates are restricted to public-source-backed synthesis or owner-approved research-direction notes.

---

### Theme 2 — Create a dedicated research-wiki Review workflow

**Problem**

The current workflow supports PDF summaries and backlog triage, but not a mature review-generation operation.

**Goal**

Create a `research-wiki-review` skill that can synthesize durable literature reviews from Sources and Concepts.

**Review workflow outline**

1. Read Schema and Agent Operating Guide.
2. Identify topic scope and public-boundary constraints.
3. Retrieve relevant Sources and Concepts.
4. Separate source-backed claims from synthesis.
5. Identify foundational work, current state, disagreements, methods, limitations, gaps, and implications.
6. Draft a review artifact with explicit provenance.
7. Propose candidate Concept updates rather than directly mutating Concepts unless approved.
8. Log high-signal review runs.

**Candidate output structure**

```markdown
# Literature Review: [Topic]

## Scope
## Core argument
## Foundational sources
## Current state
## Major constructs / mechanisms
## Points of disagreement
## Methodological limitations
## Gaps
## Implications for workforce transformation / job design / AI adoption
## Candidate Concept updates
## Source coverage table
```

**Acceptance criteria**

- New skill exists in GitHub and Hermes skill store.
- Skill preserves public-only and role-boundary rules.
- Skill defaults to proposed updates, not direct canonical mutation.
- Review artifacts have a defined Notion destination or staging rule.

---

### Theme 3 — Add researcher-intent capture to ingestion

**Problem**

The manual PDF summary workflow is operationally strong, but it does not consistently capture Nicholas's tacit interpretation before promotion.

**Goal**

Add a researcher-interpretation step to important PDF ingests.

**Prompt block to add to dry-run summaries**

```markdown
## Researcher interpretation prompts
- Why does this source matter for the wiki?
- What should the agent pay attention to?
- Does this source confirm, sharpen, or contradict an existing Concept?
- Is this a foundational source, supporting source, edge case, or weak signal?
- Should this source update any frontier question?
```

**Acceptance criteria**

- `manual-research-pdf-summary` includes this section.
- Routine backlog processing can mark the step optional.
- High-value or promotion-bound sources should collect researcher intent before canonical Source/Concept updates.

---

### Theme 4 — Build graph-semantic linting

**Problem**

Current checks are strong on provenance, Drive/Notion state, extraction, and workflow safety. They are weaker on graph health and knowledge quality.

**Goal**

Create an LC-style lint workflow for knowledge graph coherence.

**Initial lint checks**

- Concepts with no Sources.
- Sources linked to no Concepts.
- Concepts with only one weak Source and no confidence flag.
- Candidate duplicate Concepts.
- Stale Concepts not updated after newer relevant Sources.
- Contradictory claims across Concepts.
- Unpromoted Inbox items older than a threshold.
- Repeated `domain_cluster_candidate` values suggesting Schema pressure.
- Review artifacts not traceable to Sources.

**Acceptance criteria**

- Lint workflow exists as a skill and/or script.
- Lint reports distinguish structural, provenance, semantic, and governance issues.
- Lint can run read-only by default.
- Meaningful lint runs are logged.

---

### Theme 5 — Create a markdown mirror/export path

**Problem**

Notion is useful as an operating UI, but markdown is more portable, inspectable, git-friendly, and agent-readable.

**Goal**

Generate a markdown mirror/export of the public research-wiki operating layer.

**Candidate export shape**

```text
research-wiki-export/
├── schema.md
├── agent-guide.md
├── index.md
├── overview.md
├── sources/
├── concepts/
├── reviews/
└── log.md
```

**Design constraint**

The export should not become a second source of truth until explicitly designed. Default posture: Notion remains canonical; markdown is a compiled substrate for agent inspection, git review, and portability.

**Acceptance criteria**

- Export script can read Notion Sources/Concepts/Schema/Guide and emit markdown.
- Export excludes secrets, private notes, and generated runtime artifacts.
- Export can be linted for broken wikilinks and frontmatter validity.
- Export location and git policy are defined before committing any generated outputs.

---

### Theme 6 — Enrich canonical page/entity semantics without exploding databases

**Problem**

The current Sources/Concepts split may become too coarse as the wiki matures.

**Goal**

Add richer semantic typing while avoiding premature Notion schema sprawl.

**Candidate Concept subtypes**

- construct
- method
- framework
- empirical finding
- intervention
- metric
- risk
- author/org
- case pattern
- review/synthesis
- open question

**Acceptance criteria**

- Schema proposes approved subtype vocabulary.
- LC reviews whether these should be Concept subtypes, Source fields, or separate databases.
- Existing Concepts can be classified without disruptive migration.

---

### Theme 7 — Add confidence, contested, and contradiction conventions

**Problem**

Persistent memory can compound errors. The system needs visible uncertainty, not just clean prose.

**Goal**

Make evidence strength and disagreement explicit.

**Candidate fields / conventions**

- `confidence`: high / medium / low
- `contested`: yes / no
- `contradicts`: relation to Concept or Source
- `evidence_strength`
- `last_evidence_update`
- `needs_review`
- `open_questions`

**Acceptance criteria**

- Schema proposal drafted.
- LC lint surfaces low-confidence and contested items.
- Review workflow uses these fields when synthesizing literature.

---

### Theme 8 — Turn high-signal queries into durable synthesis

**Problem**

User-facing answers can remain ephemeral, even when they create useful synthesis.

**Goal**

Create an explicit query workflow for deciding whether an answer should become durable wiki material.

**Workflow**

1. Answer from existing Sources/Concepts.
2. Identify whether the answer produced durable synthesis.
3. If yes, propose one of:
   - new Concept;
   - Concept update;
   - Review artifact;
   - Research Map update;
   - missing Source search;
   - Log entry only.
4. Keep casual read-only answers out of the Log.

**Acceptance criteria**

- DC query rules are updated.
- Durable query outputs have a staging destination.
- The workflow distinguishes source-backed claims from interpretation.

---

### Theme 9 — Build gap-map outputs

**Problem**

The wiki should support planning, not just retrieval.

**Goal**

For major topics, generate gap maps that identify where the wiki is strong, thin, conflicted, or missing sources.

**Gap map structure**

```markdown
# Gap Map: [Topic]

## Well-supported areas
## Thinly supported areas
## Conflicting evidence
## Missing canonical sources
## Concepts needing promotion or revision
## Suggested next sources
## Implications for Research Map / frontier questions
```

**Acceptance criteria**

- Gap maps can be produced by the Review or Query workflow.
- Gap maps cite relevant Sources/Concepts.
- Gap maps suggest concrete next ingestion or search actions.

---

### Theme 10 — Preserve governance while improving throughput

**Problem**

The current governance model is correct but can slow compounding if every improvement requires ad hoc decisions.

**Goal**

Create approved pathways for safe acceleration.

**Candidate pathways**

- candidate Concept update bundle;
- candidate Review artifact;
- Research Map update proposal;
- LC promotion bundle;
- human-approved batch promotion;
- read-only lint/report mode;
- apply mode with verified Notion/Drive mutations.

**Acceptance criteria**

- Agent Operating Guide describes these pathways.
- Each pathway has clear write permissions and verification steps.
- High-trust automation is introduced only after repeated successful manual runs.

## Suggested implementation sequence

### Phase 1 — Capture the architecture intent

- [x] Create this roadmap in GitHub.
- [x] Create a Notion version of this roadmap.
- [x] Add this roadmap to the repo README or docs index.
- [ ] Optionally link the Notion page from System Docs / Archive.

### Phase 2 — Add the living research map

- [x] Create `docs/research-map-template.md`.
- [x] Create Notion Research Map / Overview page.
- [x] Update Agent Operating Guide with when to update Research Map.

### Phase 3 — Add review and durable-query workflows

- [x] Create `research-wiki-review` skill.
- [ ] Create durable-query workflow notes or skill section.
- [x] Define where review artifacts live in Notion.

### Phase 4 — Tighten ingestion and promotion

- [ ] Patch `manual-research-pdf-summary` with researcher-interpretation prompts.
- [ ] Add candidate Concept update bundle format.
- [ ] Define high-value source criteria.

### Phase 5 — Build graph linting

- [ ] Draft LC graph-lint checklist.
- [ ] Implement read-only lint script or Notion query workflow.
- [ ] Add confidence/contested/contradiction checks.

### Phase 6 — Markdown mirror/export

- [ ] Design export schema.
- [ ] Prototype Notion-to-markdown export.
- [ ] Decide whether generated exports are committed, ignored, or stored outside repo.
- [ ] Add tests/guardrails to prevent corpus/runtime leakage.

## Open decisions

1. Should the Research Map live as a top-level Notion page, inside System Docs, or both? Current implementation: top-level Notion page with repo template.
2. How should durable-query workflow differ from full Reviews?
3. Should markdown exports be committed to GitHub, generated locally, or stored in a separate private/public repo?
4. Which Concept subtype vocabulary should become Schema-approved first?
5. What threshold makes an Inbox item stale enough to appear in LC lint?
6. What human approval threshold is required before batch promotion or automated promotion?

## Non-goals

- Do not store PDFs, generated corpus exports, Notion snapshots, secrets, or runtime state in `llm-research-wiki`.
- Do not loosen public-only boundaries.
- Do not let agent-generated synthesis enter canonical Concepts without the approved workflow.
- Do not create a second source of truth accidentally through markdown exports.

## Bottom line

The next architectural move is not more ingestion volume. It is making the wiki more capable of compounding: a living research map, review synthesis, semantic linting, durable query outputs, and a markdown-readable graph substrate — while keeping the current governance guardrails intact.
