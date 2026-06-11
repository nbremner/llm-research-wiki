---
name: research-wiki-query
description: Use when answering questions against Nicholas's public research wiki and deciding whether the answer should become durable synthesis, a Review artifact, a Candidate Concept Update Bundle, a Research Map update proposal, a missing-source task, or no logged artifact.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, query, durable-synthesis, knowledge-graph, governance]
    related_skills: [llm-wiki, research-wiki-review, research-wiki-graph-lint]
---

# Research Wiki Query Workflow

## Overview

Use this skill for **question answering against Nicholas's public research wiki** when the answer may produce durable synthesis. The goal is to stop useful query work from evaporating while also preventing casual answers from bloating Notion, Log, Reviews, or Concepts.

Default posture: answer from existing public wiki material first, then decide whether the answer deserves durable capture. Do not mutate canonical Concepts from a query response unless Nicholas explicitly approves that follow-on step.

## Canonical Notion locations

Read Schema, Agent Operating Guide, and Research Map before durable query work.

- Schema: `36accc4a-237c-81a9-8de2-c667d2a95796`
- Agent Operating Guide: `36bccc4a-237c-813c-b884-c89702815b03`
- Research Map / Overview: `37cccc4a-237c-81cc-b455-ff673f15e97c`
- Sources database: DB `0569f238-61a3-4705-9ae4-945a45acf7b1` / data source `2491c01c-8c1d-42b7-9272-ab235ea64586`
- Concepts database: DB `b5239ba5-7ecc-44f4-a300-4ec4b0f08cc3` / data source `f578eaf9-81bb-4668-8bdc-191fdea8e5f1`
- Reviews database: DB `09776168-d11e-4868-ab34-6ebe3b900cee` / data source `eb454605-2dea-4b8b-a173-407be60184ed`
- Inbox database: DB `cb35f9c7-0fd7-41b8-b32a-17784da9160c` / data source `56bea68b-7a43-4494-bf80-23f15202ef1c`
- Log database: DB `aff36f8c-2ce0-4d65-b9cb-fc392a3bf341` / data source `d1169e63-cf4d-4a9b-b8a8-139c78faab5c`

If live Notion Schema or Agent Guide conflicts with this skill, live Notion wins.

## When to Use

Use when Nicholas asks:

- a substantive question about the research wiki's domain;
- what the wiki says about a topic, construct, mechanism, source, gap, or Research Map question;
- for a synthesis that may become a Review, Concept update, gap map, or source-discovery task;
- whether a query result should be saved, logged, or turned into durable wiki material.

Do not use for trivial lookups, operational status checks, or questions unrelated to the public research wiki.

## Query workflow

1. **Orient.** Read Schema, Agent Operating Guide, and Research Map / Overview for durable queries.
2. **Retrieve existing material first.** Search/read Sources, Concepts, Reviews, and relevant Inbox candidates before external search.
3. **Separate evidence from synthesis.** Mark whether each claim is source-backed, existing Concept-backed, Review-backed, Inbox-candidate-backed, or agent synthesis.
4. **Answer the question directly.** Do not bury the answer inside process notes.
5. **Classify durability.** Decide whether the answer should become one of the durable artifact classes below.
6. **Route rather than mutate.** Proposed Concept or Research Map changes should become candidate updates unless Nicholas explicitly approves application.
7. **Log only meaningful durable work.** Casual read-only answers should not create Log noise.

## Durability decision rubric

### No durable artifact

Use when the answer is:

- a simple lookup;
- already covered cleanly by existing Concepts/Reviews;
- not likely to be reused;
- too speculative or thin to preserve.

Action: answer only. No Log entry needed.

### Log entry only

Use when the query matters operationally but produces no reusable synthesis.

Action: create a concise Log row or note only if the run changed workflow state, revealed a blocker, or documents a meaningful decision.

### Candidate Source / Inbox task

Use when the query reveals a missing source, promising candidate, or evidence gap.

Action: propose or create an Inbox candidate only within current permissions. Include provenance, rationale, dedupe key, and Research Map relevance.

### Review artifact

Use when the answer synthesizes multiple sources/concepts, identifies disagreements, bridges I-O constructs with AI workforce mechanisms, or would be painful to re-derive.

Action: route to `research-wiki-review`. Create or propose a Review row with source coverage and provenance.

### Candidate Concept Update Bundle

Use when the query produces concrete proposed changes to canonical Concepts.

Action: prepare a Candidate Concept Update Bundle. Do not directly edit Concepts without explicit approval.

### Research Map update proposal

Use when the query clarifies a frontier question, active theme, gap, deep-dive queue item, or evidence map.

Action: propose concise Research Map language. Apply only if Nicholas approves or the current task explicitly asks for Research Map maintenance.

## Output shape for durable query answers

When a query is substantive, structure the answer as:

```markdown
## Answer
[Direct answer in plain language.]

## Evidence basis
- Existing Sources:
- Existing Concepts:
- Existing Reviews:
- Inbox candidates / non-canonical material:
- Agent synthesis:

## Durability decision
- Artifact class: none | log-only | Inbox candidate | Review | Candidate Concept Update Bundle | Research Map update proposal
- Why:
- Approval needed before canonical mutation: yes | no

## Proposed follow-up
[Only if useful.]
```

For casual answers, skip the full structure and answer directly.

## Governance rules

- Public-source boundary remains active.
- Query answers do not directly promote material into canonical Concepts.
- Evidence gaps should become source-discovery or Review tasks, not confident prose.
- Research Map updates should stay concise; do not bloat the overview with every query.
- If the query uses non-canonical Inbox material, label it as non-canonical.
- If confidence is low, say so visibly.

## Verification checklist

- [ ] Schema, Agent Guide, and Research Map were read when the query was durable.
- [ ] Existing Sources/Concepts/Reviews were checked before external search.
- [ ] Evidence-backed claims were separated from agent synthesis.
- [ ] Durability decision was explicit for substantive answers.
- [ ] No canonical Concepts were mutated without approval.
- [ ] Candidate Concept changes were routed through a bundle.
- [ ] Research Map changes were proposed concisely.
- [ ] Casual read-only answers were not over-logged.
