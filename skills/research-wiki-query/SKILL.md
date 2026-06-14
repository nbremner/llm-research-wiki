---
name: research-wiki-query
description: Use when answering a question against the markdown research wiki, and deciding whether the answer should become durable synthesis — an updated topic page, a new source, an open question in overview.md, an on-demand cross-topic review, or no logged artifact at all.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, query, durable-synthesis, markdown, knowledge-graph]
    related_skills: [research-wiki-ingest, research-wiki-graph-lint]
---

# Research Wiki Query Workflow

## Overview

Answer questions against the markdown research wiki (`wiki/`, plain markdown in git), and stop useful
synthesis from evaporating into chat — while preventing casual answers from bloating the wiki. There
is no Notion: the wiki is topic and source pages read in full context (Karpathy regime), with
`wiki/overview.md` as orientation and `wiki/schema.md` as the contract.

Default posture: **answer from existing wiki material first**, then decide whether the answer deserves
durable capture. Topic synthesis becomes canonical only with owner approval (the one governance gate).

## Locations

- Repo (VPS): `/root/work/llm-research-wiki`; vault is `wiki/`.
- `wiki/overview.md` — what topics exist, open questions, thin areas (read first for durable queries).
- `wiki/schema.md` — conventions + the one hard rule (public-only sources).
- `wiki/topics/` — synthesis pages. `wiki/sources/` — per-source evidence records.

## When to use

Use when the owner asks a substantive question about the wiki's domain (AI workforce transformation +
I-O psychology), what the wiki says about a topic/source/gap, or for a synthesis that may become
durable. Don't use for trivial lookups or operational status checks.

## Query workflow

1. **Orient.** For durable queries, read `overview.md` and the relevant `topics/` pages.
2. **Retrieve from the wiki first.** Search `topics/` and `sources/` (`grep -ri`, read pages) before
   reaching for external search.
3. **Separate evidence from synthesis.** Mark each claim as source-backed (`[[source]]`),
   topic-backed (existing synthesis), or new agent synthesis.
4. **Answer directly.** Don't bury the answer in process notes.
5. **Decide durability** (rubric below) and **route** rather than silently mutate.
6. **File durable work back into pages**, owner-approved; commit. Git history is the log.

## Durability decision rubric

### No artifact
Simple lookup, already covered cleanly by an existing topic, or too thin/speculative to keep. Answer
only; commit nothing.

### Update / add a topic page
The answer is durable synthesis that belongs in a topic. Edit the relevant `topics/*.md` (or create
one), cite sources with `[[source-slug]]`, and **surface contradictions in prose**. Owner approves the
diff before commit (synthesis becomes canonical). Add new topics to `overview.md`.

### Add a source (missing-source task)
The query reveals a public source the wiki should hold. Route to `research-wiki-ingest` (drop the PDF
in the Drive `_inbox`, or note the candidate with its public provenance). Don't fabricate a record.

### Open question in overview
The query clarifies a frontier/gap question but isn't yet answerable. Add a concise line to
`overview.md`'s open-questions or thin-areas section. Keep it short.

### On-demand review (deeper cross-topic synthesis)
When a project needs a deeper pass across several topics/sources, produce a structured review. This
replaces the old standalone Reviews database — a review is now on-demand synthesis written into the
wiki (an enriched topic page, or a one-off synthesis doc), owner-approved. Pick the framing that fits:

- **Literature review** — "What do we know about X?": state of evidence, major claims, mechanisms,
  practical implications, points of disagreement.
- **Gap map** — "Where is evidence strong / thin / mixed / contested?": evidence status by
  sub-question, gaps, unresolved contradictions, candidate sources.
- **Construct bridge** — "How does an I-O construct illuminate an AI-work question?": construct
  definition, nomological net, measurement implications, AI-work mechanism, boundary conditions.
- **Implementation review** — "What does the evidence imply for practice?": design / adoption /
  measurement / governance implications, and what evidence would change the recommendation.
- **Summary review** — narratively connect a small set of sources; lighter, descriptive.

A review's durable output is topic-page synthesis (and possibly new open questions), not a separate
artifact class. Surface contradictions; never auto-resolve them.

## Output shape for durable query answers

```markdown
## Answer
[Direct answer in plain language.]

## Evidence basis
- From sources: [[...]]
- From existing topics: [[...]]
- New agent synthesis: [clearly labelled]

## Durability decision
- Route: none | update topic | add source | open question | on-demand review
- Why:
- Owner approval needed before commit: yes | no
```

For casual answers, skip the structure and answer directly.

## Governance rules

- Public-only boundary stays active; if an answer leans on weak or non-public material, say so.
- Query answers do not make topic synthesis canonical without owner approval.
- Evidence gaps become source-discovery (ingest) tasks or open questions, not confident prose.
- Keep `overview.md` lean — don't append every query to it.
- If confidence is low, say so visibly.

## Verification checklist

- [ ] `overview.md` + relevant topics read for durable queries.
- [ ] Wiki searched before external search.
- [ ] Source-backed claims separated from agent synthesis.
- [ ] Durability route explicit for substantive answers.
- [ ] No topic synthesis committed as canonical without owner approval.
- [ ] Casual answers not over-committed.
