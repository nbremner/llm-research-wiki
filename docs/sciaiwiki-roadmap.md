# SciAI Wiki Alignment Roadmap

Created: 2026-05-29
Status: active roadmap
Canonical home: **this file** (Git), and the only copy. The former Notion "SciAI Wiki Alignment Roadmap" pointer page was deleted 2026-06-14.
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

- [x] Lint workflow exists as a skill and/or script.
- [x] Lint reports distinguish structural, provenance, semantic, and governance issues.
- [x] Lint can run read-only by default.
- Meaningful lint runs are logged.

**Current implementation**

- Skill: `skills/research-wiki-graph-lint/SKILL.md`
- Script: `scripts/research-wiki-tools/graph_lint.py`
- Test coverage: `tests/test_graph_lint.py`
- Output: local `REPORT.md` and `graph_lint.json` under `/root/research-wiki-runs/graph-lint-*`

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

**Current implementation**

- Skill: `skills/research-wiki-query/SKILL.md`
- Artifact routing: none, Log-only, Inbox/source task, Review artifact, Candidate Concept Update Bundle, or Research Map update proposal.
- Governance: query answers do not directly mutate canonical Concepts; Concept-changing results route through approval bundles.

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

---

### Theme 11 — Add agentic ingestion and review loops

**Problem**

The current workflow is intentionally staged, but it still depends too much on one-off manual prompting. That keeps governance safe, but it also means the wiki only compounds when Nicholas explicitly asks for a run.

**Goal**

Add bounded agentic loops that increase throughput while preserving the key governance boundary: agents may create Inbox and Review/Summary artifacts, but they do **not** directly graduate material into canonical Concepts without approval.

**Loop A: Inbox-to-Review artifact loop**

Regularly process papers already in Drive `_inbox` / Notion Inbox:

1. detect new or unprocessed candidate papers;
2. extract citation metadata, abstract, and full text where possible;
3. summarize the paper against the public research-wiki scope;
4. create a Notion Review or Summary artifact directly, without the older dry-run approval step;
5. link the artifact back to the Inbox item / Drive file;
6. propose candidate Concepts, Concept updates, Research Map updates, and follow-up source searches;
7. mark the artifact as needing approval before any canonical Concept mutation.

**Governance boundary**

- The artifact itself may be created automatically.
- Canonical Concepts are not updated automatically.
- Graduation from Review/Summary into Concepts remains an explicit approval workflow.
- Agent runs must log what was created and which source files were used.
- Failed extraction, weak evidence, or ambiguous scope should produce a low-confidence artifact or triage note, not silent discard.

**Loop B: Candidate-source discovery loop**

Regularly search public web/scholarly sources for candidate papers relevant to the Research Map:

1. read active Research Map questions and known gaps;
2. query arXiv, Semantic Scholar / OpenAlex / Crossref, Google Scholar-adjacent sources where available, and targeted web searches;
3. deduplicate against existing Sources, Inbox, and Drive filenames/DOIs;
4. add promising candidates to Inbox with metadata and rationale;
5. download or attach public PDFs only when licensing and access make that appropriate;
6. tag why the source matters: foundational, recent empirical evidence, methods, construct bridge, contradiction, or weak signal;
7. log the discovery pass and surface high-priority candidates.

**Scheduling model**

Start as explicit/manual runs, then move to scheduled Hermes jobs once the dry path is stable:

- weekly candidate-source discovery;
- weekly or twice-weekly Inbox-to-Review processing;
- optional monthly gap-map refresh for Research Map questions.

**Acceptance criteria**

- Agent Operating Guide defines write permissions for automated Inbox and Review/Summary creation.
- Review database supports status values for agent-created artifacts awaiting approval.
- Inbox items can record discovery source, rationale, dedupe key, and processing status.
- A dry-read validation script can report what would be created before automation is enabled.
- First scheduled jobs run with conservative limits and clear logs.
- Concept graduation remains approval-gated.

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
- [x] Create durable-query workflow notes or skill section.
- [x] Define where review artifacts live in Notion.

### Phase 4 — Tighten ingestion and promotion

- [x] Patch `manual-research-pdf-summary` with researcher-interpretation prompts.
- [x] Add candidate Concept update bundle format.
- [x] Define high-value source criteria.

### Phase 5 — Build graph linting

- [x] Draft LC graph-lint checklist.
- [x] Implement read-only lint script or Notion query workflow.
- [ ] Add confidence/contested/contradiction checks.

### Phase 6 — Markdown mirror/export

- [ ] Design export schema.
- [ ] Prototype Notion-to-markdown export.
- [ ] Decide whether generated exports are committed, ignored, or stored outside repo.
- [ ] Add tests/guardrails to prevent corpus/runtime leakage.

### Phase 7 — Agentic ingestion and review loops

- [ ] Define automated Review/Summary artifact statuses and approval gates.
- [ ] Add Inbox metadata needed for source-discovery provenance, dedupe, and processing state.
- [ ] Build a conservative Inbox-to-Review runner that creates Notion Review/Summary artifacts from `_inbox` papers.
- [ ] Build a candidate-source discovery runner that searches public scholarly/web sources and stages promising papers in Inbox.
- [ ] Add read-only/dry-report modes for both loops before scheduling.
- [ ] Schedule low-volume Hermes jobs only after manual runs produce clean artifacts and logs.
- [ ] Keep Concept graduation approval-gated.

## Open decisions

1. Should the Research Map live as a top-level Notion page, inside System Docs, or both? Current implementation: top-level Notion page with repo template.
2. How should durable-query workflow differ from full Reviews?
3. Should markdown exports be committed to GitHub, generated locally, or stored in a separate private/public repo?
4. Which Concept subtype vocabulary should become Schema-approved first?
5. What threshold makes an Inbox item stale enough to appear in LC lint?
6. What human approval threshold is required before batch promotion or automated promotion?
7. Should automatically created paper summaries live in the Reviews database as `summary-review` rows, or should there be a separate lightweight Summaries database later?
8. Which discovery sources should be allowed in the candidate-source loop: arXiv only at first, or arXiv plus OpenAlex/Crossref/Semantic Scholar/web search?
9. What weekly volume cap should scheduled loops use so the Inbox and Reviews database do not become a new backlog sink?

## Non-goals

- Do not store PDFs, generated corpus exports, Notion snapshots, secrets, or runtime state in `llm-research-wiki`.
- Do not loosen public-only boundaries.
- Do not let agent-generated synthesis enter canonical Concepts without the approved workflow.
- Do not let scheduled discovery or review loops create unbounded backlog; they need caps, dedupe, and logs.
- Do not create a second source of truth accidentally through markdown exports.

## Bottom line

The next architectural move is not more ingestion volume by itself. It is making the wiki more capable of compounding: a living research map, review synthesis, semantic linting, durable query outputs, bounded agentic ingestion/review loops, and a markdown-readable graph substrate — while keeping the current governance guardrails intact.
