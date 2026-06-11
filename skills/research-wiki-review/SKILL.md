---
name: research-wiki-review
description: Use when creating structured review artifacts for Nicholas's public AI workforce transformation + I-O psychology research wiki, including literature reviews, gap maps, construct bridges, implementation reviews, and summary reviews.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, review, literature-review, gap-map, io-psychology, ai-workforce-transformation]
    related_skills: [llm-wiki, manual-research-pdf-summary, research-wiki-pdf-backlog-triage]
---

# Research Wiki Review Workflow

## Overview

Use this skill to create durable review artifacts for Nicholas's public research wiki at the intersection of **AI workforce transformation** and **industrial-organizational psychology**.

A review artifact is staged synthesis. Its job is to connect existing Sources, Concepts, Research Map questions, and candidate future work. It should be useful enough to revisit, cite internally, and turn into Concept updates, but it does **not** directly mutate canonical Concepts unless Nicholas explicitly approves that application step.

The default artifact is:

> structured literature review + gap map + candidate Concept updates + candidate Research Map updates.

## Canonical Notion locations

Read these before every review run:

- Schema: `36accc4a-237c-81a9-8de2-c667d2a95796`
- Agent Operating Guide: `36bccc4a-237c-813c-b884-c89702815b03`
- Research Map / Overview: `37cccc4a-237c-81cc-b455-ff673f15e97c`
- Reviews database: DB `09776168-d11e-4868-ab34-6ebe3b900cee` / data source `eb454605-2dea-4b8b-a173-407be60184ed`
- Sources database: DB `0569f238-61a3-4705-9ae4-945a45acf7b1` / data source `2491c01c-8c1d-42b7-9272-ab235ea64586`
- Concepts database: DB `b5239ba5-7ecc-44f4-a300-4ec4b0f08cc3` / data source `f578eaf9-81bb-4668-8bdc-191fdea8e5f1`
- Inbox database: DB `cb35f9c7-0fd7-41b8-b32a-17784da9160c` / data source `56bea68b-7a43-4494-bf80-23f15202ef1c`
- Log database: DB `aff36f8c-2ce0-4d65-b9cb-fc392a3bf341` / data source `d1169e63-cf4d-4a9b-b8a8-139c78faab5c`
- Drive `_inbox`: `1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1`
- Drive raw public source folder: `17vtadKJwx81gjsS85kwaogyQvZweZ_n_`

## When to Use

Use when Nicholas asks to:

- review a topic from the Research Map deep-dive queue;
- synthesize a set of papers already in Sources or Drive `_inbox`;
- create a literature review, gap map, construct bridge, implementation review, or summary review;
- compare evidence across I-O psychology and AI workforce transformation;
- produce candidate Concept updates from an evidence set;
- identify concise Research Map updates from a deeper synthesis.

Do **not** use for casual questions that do not need durable synthesis. Answer those directly and log only if the answer surfaces durable gaps, contradictions, or follow-up work.

## Review Types

### 1. Literature review

Use for: “What do we know about X?”

Core output: current state of evidence, major claims, construct/theory map, mechanisms, practical implications, points of disagreement, candidate Concept updates.

### 2. Gap map

Use for: “Where is the evidence strong, thin, mixed, or contested?”

Core output: evidence status by sub-question, literature gaps, unresolved contradictions, suggested source/concept candidates, and next review questions.

### 3. Construct bridge

Use for: “How does an I-O construct illuminate an AI-work question?”

Core output: construct definition, nomological network, measurement implications, AI-work mechanism, boundary conditions, related Concepts, and candidate Concept updates.

### 4. Implementation review

Use for: “What does the evidence imply for practice?”

Core output: design implications, adoption/change implications, measurement implications, governance risks, implementation constraints, and what evidence would change the recommendation.

### 5. Summary review

Use for: “Summarize and narratively connect this small set of papers.”

Core output: source-by-source synthesis, associative links across Concepts, key claims, and light candidate updates. This can use fewer sources when the task is descriptive rather than evaluative.

## Evidence Thresholds

Evidence thresholds are guidelines, not rigid rules.

- **Summary review:** coherent small set is acceptable when the goal is narrative description.
- **Literature review:** usually aim for 5+ relevant Sources, mixing foundational and current evidence where possible.
- **Gap map:** use broader evidence when making claims about what the literature lacks or where evidence is thin.
- **Quantitative relationship comparison:** requires substantially broader source coverage and explicit attention to measurement, populations, study designs, effect sizes where available, and boundary conditions.
- **Construct bridge:** can begin with fewer sources if the I-O construct is well established, but must separate mature I-O theory from early AI-work evidence.

When evidence is insufficient, mark `Evidence status` as `thin`, `mixed`, or `contested`, set appropriate confidence, and propose source/concept candidates instead of overstating the review.

## Required Human Researcher Intent Capture

Every review starts by capturing Nicholas's intent. Ask or infer only when explicitly available:

1. What is the review question?
2. Why does this matter for the wiki?
3. What angle should the review take?
4. Is this descriptive, evaluative, comparative, or practice-oriented?
5. Any must-include or must-exclude sources?
6. What would make the review useful when revisited later?
7. Should the review emphasize I-O theory, AI transformation practice, measurement, governance, or practical implications?

Do not skip this for high-value reviews. The intent layer is what keeps the wiki from becoming generic synthesis.

## Source Selection Rules

1. Orient first: read Schema, Agent Operating Guide, and Research Map / Overview.
2. Use existing Sources and Concepts first.
3. Search Reviews to avoid duplicate artifacts.
4. Use Drive `_inbox` PDFs as candidate material when relevant, but remember: `_inbox` files are not canonical Sources until ingestion/promotion.
5. Web or arXiv search may be used during review to identify candidate missing sources, but those sources must go through ingestion before becoming canonical wiki material.
6. If the review needs a source-expansion pass, state that clearly and create candidate source recommendations rather than silently mixing unvetted web findings into canonical synthesis.

## Required Review Content

Every review should include, scaled to the review type:

- review question;
- researcher intent;
- scope and boundaries;
- review type and evidence guideline;
- short answer / synthesis;
- source coverage table;
- key claims with claim-level provenance for major assertions;
- relevant I-O constructs;
- AI workforce-transformation mechanisms;
- level of analysis: individual, team, job, organization, labor market, or multi-level;
- measurement implications;
- general practical implications;
- points of disagreement or contested claims;
- literature gaps or weak evidence areas;
- suggested sources/concepts;
- candidate Concept updates;
- candidate Concept Update Bundle when the review proposes canonical Concept changes;
- candidate Research Map updates;
- confidence / evidence status;
- next review questions.

Use links aggressively and usefully: link Reviewed Sources, Related Concepts, Research Map areas, and candidate follow-up items. The associative linkage is the point.

## Default Review Page Template

Use this structure in the body of the Notion Reviews row:

```markdown
# Review: [Topic]

## Review question

## Researcher intent

## Scope and boundaries

## Review type and evidence guideline

## Short answer

## Source coverage

| Source | Type | Role in review | Key contribution | Limitations |
|---|---|---|---|---|

## Key claims and provenance

| Claim | Provenance | Confidence | Notes |
|---|---|---|---|

## I-O constructs involved

## AI workforce transformation mechanisms

## Level of analysis

## Measurement implications

## General practical implications

## Points of disagreement / contested claims

## Literature gaps and weak evidence areas

## Suggested sources or concepts

## Candidate Concept updates

Summarize proposed Concept changes. If the review proposes canonical Concept mutation, also prepare a Candidate Concept Update Bundle using `templates/candidate-concept-update-bundle.md`.

## Candidate Research Map updates

## Next review questions
```

Replace empty sections with `Not assessed in this review` only when genuinely out of scope. Do not pad.

## Notion Review Row Defaults

Set these properties when creating a Reviews row:

- `Review type`: one of `literature-review`, `gap-map`, `construct-bridge`, `implementation-review`, `summary-review`
- `Status`: `draft` until Nicholas reviews it, then `ready-for-review` if complete
- `Canonical status`: `staged` or `proposed`
- `Evidence status`: `strong`, `mixed`, `thin`, `contested`, or `narrative-summary`
- `Confidence`: `high`, `medium`, or `low`
- `Review question`: concise question
- `Researcher intent`: short note from Nicholas's intent capture
- `Scope`: what is included/excluded
- `Evidence guideline`: why the source volume is appropriate for the review type
- `Source coverage summary`: concise source count/type/coverage statement
- `Candidate Concept updates`: summary of proposed changes
- `Candidate Research Map updates`: concise high-level update proposals only
- `Practical implications`: general implications, not only organizational design
- `Suggested sources/concepts`: source/concept candidates for later approval/ingestion
- `Reviewed Sources`: relation links where canonical Sources exist
- `Related Concepts`: relation links where Concepts exist
- `Needs source search`: true when the review identifies source candidates that need ingestion/search

## Candidate Concept Update Bundles

Use a Candidate Concept Update Bundle when a Review or Summary artifact produces concrete proposed changes to canonical Concepts. The bundle is the promotion packet between staged synthesis and canonical mutation.

Template: [`templates/candidate-concept-update-bundle.md`](templates/candidate-concept-update-bundle.md)

A good bundle includes:

- Review artifact / source artifact links;
- affected existing Concepts or proposed new Concepts;
- proposed update type: new Concept, revise definition, add source support, add contested note, add measurement implication, add practical implication, add method/evidence note, add Concept relation, update Research Map question, or no canonical update recommended;
- exact proposed canonical language, not just a vague recommendation;
- evidence basis table with source provenance, evidence role, confidence, and limitations;
- I-O construct, AI workforce mechanism, level-of-analysis, measurement, and practical-implication mapping;
- boundary conditions / caveats;
- concise Research Map update proposal when needed;
- no-change/watchlist items where the evidence is interesting but not promotion-ready;
- Nicholas approval decision before canonical Concept mutation.

Bundle rules:

1. Separate source-backed claims from agent synthesis.
2. Do not bury weak evidence in confident prose; mark thin/mixed/contested evidence explicitly.
3. Prefer small exact patches to broad Concept rewrites.
4. If proposing a new Concept, check existing Concepts for overlap first.
5. If the Review only produced a light summary, create a light bundle or explicitly record `no canonical update recommended`.
6. A bundle can be created automatically or agentically, but applying it to canonical Concepts requires approval.

## Governance Rules

- Reviews are staged synthesis artifacts.
- Reviews may propose Concept updates and Research Map updates.
- Reviews must not directly mutate canonical Concepts unless Nicholas explicitly approves that step.
- Candidate Concept Update Bundles are the default approval packet for moving Review/Summary insights into canonical Concepts.
- Research Map update proposals should stay concise and high-level; do not bloat the overview.
- Drive `_inbox` PDFs can inform candidate selection but are not canonical Sources until ingested.
- Web/arXiv findings are candidate sources until ingestion/promotion.
- Preserve the public-only boundary. No confidential, work-derived, or private synthesis enters Reviews.

## Logging

Log meaningful review runs in the Log database when a review artifact is created, materially updated, blocked, or promoted.

A good Log summary includes:

- review title and URL;
- review type;
- number/type of sources reviewed;
- evidence status;
- whether Concept updates were proposed;
- whether Research Map updates were proposed;
- next action.

## Common Pitfalls

1. **Skipping researcher intent.** This produces generic synthesis. Always capture the angle before doing the review.
2. **Treating evidence thresholds as rigid.** The threshold depends on the review type and claim strength.
3. **Calling missing literature “missing sources.”** Say `literature gaps`, `weak evidence areas`, or `suggested source/concept candidates` unless a specific source is known.
4. **Over-updating the Research Map.** Only propose concise changes when high-level understanding shifts.
5. **Collapsing I-O theory and AI practice.** Separate mature construct knowledge from early AI-work evidence.
6. **Weak provenance.** Major claims need source links or claim-level provenance.
7. **Creating unlinked essays.** A review without Source/Concept links is just prose. The associative graph is the point.
8. **Promoting agent synthesis directly.** Reviews propose; canonical Concept mutation needs approval.

## Verification Checklist

- [ ] Schema, Agent Operating Guide, and Research Map were read.
- [ ] Researcher intent was captured.
- [ ] Existing Sources/Concepts were checked first.
- [ ] Duplicate Reviews were checked.
- [ ] Review row created in Reviews DB.
- [ ] Reviewed Sources and Related Concepts relations populated where possible.
- [ ] Source coverage table included.
- [ ] Major claims have provenance.
- [ ] I-O constructs, AI mechanisms, level of analysis, measurement implications, and practical implications included.
- [ ] Literature gaps / weak evidence areas are distinguished from specific suggested sources/concepts.
- [ ] Candidate Concept Update Bundle prepared when the review proposes canonical Concept changes.
- [ ] Candidate Concept updates and concise Research Map updates proposed, not applied.
- [ ] Log row created for meaningful review artifact.
