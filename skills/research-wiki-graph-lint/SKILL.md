---
name: research-wiki-graph-lint
description: Use when auditing Nicholas's public research wiki for graph coherence, provenance gaps, weak evidence, stale or orphaned artifacts, duplicate Concepts, and governance risks before promotion or automation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, lint, knowledge-graph, provenance, notion, governance]
    related_skills: [llm-wiki, research-wiki-review, manual-research-pdf-summary]
---

# Research Wiki Graph Lint

## Overview

Use this skill to run or design LC-style graph-semantic linting for Nicholas's public research wiki. The purpose is not just structural cleanup. It is to keep the wiki from quietly accumulating disconnected summaries, weak Concepts, stale evidence, duplicate constructs, or agent-generated synthesis that hardens into canon without review.

Default posture: **read-only audit first**. Lint reports may propose fixes, Candidate Concept Update Bundles, Review artifacts, or Research Map updates, but they do not mutate canonical Sources, Concepts, Reviews, Schema, or Research Map without explicit approval.

## Canonical Notion locations

Read Schema and Agent Operating Guide before every lint run.

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

Use when Nicholas asks to:

- lint, audit, health-check, or clean up the research wiki;
- prepare for automated ingestion/review loops;
- identify orphan Sources, orphan Concepts, or unlinked Reviews;
- find weak, stale, contested, duplicate, or unsupported Concepts;
- check whether Reviews actually produce traceable candidate Concept updates;
- assess whether the wiki is compounding or merely accumulating artifacts.

## Operating Rules

1. Read Schema, Agent Operating Guide, and Research Map first.
2. Prefer read-only queries and reports unless Nicholas explicitly asks to apply fixes.
3. Separate **structural issues** from **semantic/evidence issues** and **governance issues**.
4. Do not use linting as a backdoor to mutate canonical Concepts.
5. Do not mark a Concept wrong just because evidence is thin; mark what evidence is missing.
6. Treat agent-generated Reviews and summaries as staged synthesis unless promoted.
7. Log meaningful lint runs, especially if they produce an action queue.

## LC Graph-Lint Checklist

### A. Structural graph integrity

Check for:

- Concepts with no linked Sources.
- Sources linked to no Concepts.
- Reviews with no Reviewed Sources.
- Reviews with no Related Concepts when they make Concept claims.
- Inbox items with no processing status or stale triage status.
- Duplicate or near-duplicate Source records by DOI, title, canonical URL, Drive file ID, or hash.
- Duplicate or near-duplicate Concepts by title, synonym, construct label, domain cluster, or overlapping definition.
- Broken Notion relations where relation counts or linked pages do not match expectations.
- Research Map questions that have no related Concepts, Reviews, or candidate Sources.

### B. Provenance and evidence quality

Check for:

- Concepts with only one weak Source and no confidence/evidence flag.
- Concepts whose major claims have unclear provenance.
- Reviews whose key claims are not traceable to Sources, Inbox items, or explicit agent synthesis.
- Candidate Concept updates with no evidence basis table or no confidence rating.
- Sources with missing DOI/canonical URL/public provenance where promotion depends on stable provenance.
- Drive `_inbox` files referenced in Reviews without being marked non-canonical.
- Web/arXiv findings used as if canonical Sources before ingestion.

### C. Confidence, contested, and contradiction signals

Check for:

- Concepts lacking confidence/evidence status when evidence is thin, mixed, single-source, or fast-moving.
- Concepts that should be marked contested because linked Sources disagree.
- Reviews that report mixed evidence but do not propagate a contested/low-confidence signal into candidate Concept updates.
- Claims that appear contradicted by newer Sources or Reviews.
- Candidate contradictions that need a Review artifact rather than an immediate Concept rewrite.

### D. Staleness and drift

Check for:

- Concepts not updated after newer relevant Sources or Reviews were added.
- Research Map questions whose evidence map no longer reflects current Sources/Reviews.
- Inbox items older than the agreed stale threshold.
- Reviews whose `Needs source search` flag remains unresolved after source candidates were added.
- Repeated source-discovery candidates that suggest the same gap but never become a Review or Concept update.

### E. Schema pressure and taxonomy health

Check for:

- Repeated `domain_cluster_candidate`, topic, or tag suggestions that imply Schema pressure.
- Concepts that are doing too many jobs and should be split into construct / method / empirical finding / intervention / metric / risk / open question.
- Source types or evidence types being used inconsistently.
- New terms introduced in Reviews that should become approved Concept subtypes or taxonomy candidates.

### F. Review and promotion workflow health

Check for:

- Reviews with proposed Concept updates but no Candidate Concept Update Bundle.
- Candidate Concept Update Bundles with no approval status.
- Approved bundles that were not applied or logged.
- Applied Concept updates with no link back to the Review or evidence basis.
- Review artifacts that are high quality but remain isolated from Research Map or Concepts.
- Summary reviews that should be promoted into a fuller literature review or gap map.

### G. Automation readiness

Before enabling or expanding scheduled agentic loops, check:

- Inbox discovery items have dedupe keys and rationale.
- Review/Summary artifacts have processing status and approval gate fields.
- Scheduled runs have volume caps and logs.
- No automated loop is creating repeated low-value candidates.
- Failed extraction or ambiguous scope produces blocked/needs-review notes rather than silent drops.

## Severity Levels

Use these levels in reports:

- **Critical:** public/private boundary risk, canonical mutation without approval, broken provenance for promoted claims, duplicate canonical records likely to mislead.
- **High:** orphan canonical Concepts/Sources, untraceable major claims, missing approval packets for proposed Concept mutation, stale Research Map areas on active questions.
- **Medium:** weak evidence signals missing, duplicate candidates, stale Inbox items, Reviews disconnected from Concepts, inconsistent source/evidence types.
- **Low:** formatting, naming, minor relation gaps, optional cross-links, housekeeping.

## Recommended Report Shape

```markdown
# Research Wiki Graph-Lint Report

## Run metadata
- Run date:
- Mode: read-only | dry-report | apply-approved-fixes
- Scope:
- Databases checked:
- Schema / Agent Guide versions read:

## Executive summary
- Critical:
- High:
- Medium:
- Low:

## Critical issues

## High-priority issues

## Medium-priority issues

## Low-priority housekeeping

## Candidate Concept Update Bundle queue

## Suggested Review / Gap Map queue

## Suggested Schema / Research Map pressure

## Automation readiness notes

## Recommended next actions
```

## Scripted read-only workflow

Preferred script in the portable workflow spine:

```bash
python scripts/research-wiki-tools/graph_lint.py --max-pages 100
```

Full run on a configured Hermes machine:

```bash
python /root/work/llm-research-wiki/scripts/research-wiki-tools/graph_lint.py
```

The script:

- retrieves Schema, Agent Operating Guide, and Research Map page metadata/block samples first;
- queries Sources, Concepts, Reviews, and Inbox data sources read-only;
- writes `REPORT.md` and `graph_lint.json` under `/root/research-wiki-runs/graph-lint-*`;
- checks current structural orphans, missing provenance, duplicate Source/Concept keys, stale Inbox items, Review traceability, and weak-evidence confidence signals;
- performs no Notion mutations.

Implementation notes and false-positive pitfalls are captured in `references/read-only-notion-graph-lint.md`.

Use the report as an LC review queue. Do not apply canonical fixes directly from the script output; route Concept-changing work through Candidate Concept Update Bundles.

## Output Rules

- Be specific: include page titles, IDs/URLs when available, relation names, and why the issue matters.
- Do not generate vague cleanup lists.
- Distinguish `fix now`, `needs Nicholas approval`, `needs LC review`, and `watchlist`.
- If a finding would mutate canonical Concepts, route it through a Candidate Concept Update Bundle.
- If a finding reveals weak or missing evidence, prefer a Review/Gap Map or source-discovery task over a confident rewrite.

## Verification Checklist

- [ ] Schema, Agent Operating Guide, and Research Map were read.
- [ ] Scope and mode were explicit.
- [ ] Structural graph checks were run or clearly marked not run.
- [ ] Provenance/evidence checks were run or clearly marked not run.
- [ ] Confidence/contested/contradiction checks were run or clearly marked not run.
- [ ] Staleness and Inbox checks were run or clearly marked not run.
- [ ] Review/promotion workflow checks were run or clearly marked not run.
- [ ] Automation readiness checks were run when relevant.
- [ ] Findings were grouped by severity.
- [ ] Canonical mutation recommendations were routed through Candidate Concept Update Bundles.
- [ ] Meaningful run was logged.
