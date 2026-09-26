---
title: "StagedWorkspace: A Versioned Workspace for Knowledge-Work Agents"
authors: Hua, Yining; Na, Hongbin; Zhou, Yifan; Kalose, Akshay; Ayubcha, Cyrus; Lian, Levi
year: 2026
url: https://arxiv.org/abs/2608.18050
doi: 10.48550/arXiv.2608.18050
source_type: paper
publication_status: preprint
retrieved: 2026-09-26
human_reviewed: false
drive_file_id: 1vMZzo04Na8rhZwhHJaQyWMQBDjJXKKNi
file_hash: a12e4ba283291696905a87472933430cc44b4c796b6ad5960fa9a604da9a65b2
---

# StagedWorkspace: A Versioned Workspace for Knowledge-Work Agents

**Citation.** Hua, Y., Na, H., Zhou, Y., Kalose, A., Ayubcha, C., & Lian, L. (2026). *StagedWorkspace: A Versioned Workspace for Knowledge-Work Agents*. arXiv:2608.18050.

**Summary.** This preprint presents StagedWorkspace, an agent workspace that binds parsed search records, native artifact operations, review diffs, and submitted deliverables to explicit file-version state. In fixed-harness studies on OFFICEQA PRO and APEX-AGENTS, the authors report that synchronized parsed and native views improve benchmark performance relative to the more limiting single-view condition, while visible diffs improve scores on a small file-editing slice. The results concern the evaluated agent harnesses and task settings, not a general causal estimate for all knowledge-work systems.

## Key claims
- The proposed workspace-state contract uses content hashes to tie parsed records and review diffs to the native files that an agent edits and submits, marking parsed records stale when a source file changes until re-parsing completes.
- Across three tested models on OFFICEQA PRO, dual parsed/native access improved Pass@1 by 8.3–12.1 points over artifact-only access in paired ablations; on APEX-AGENTS, it improved mean rubric score by 4.7–9.2 points over parsed-only access.
- In a paired review-axis ablation on 57 APEX file-editing tasks, the paper reports higher observed scores when agents could inspect tracked diffs before submission.

## Evidence & limitations
- The paper evaluates a ReAct-style SW-AGENT under a fixed 250-tool-call budget on OFFICEQA PRO and APEX-AGENTS, using paired ablations that hold the model, parser, retriever, grader, tracker, and tool budget fixed within the stated comparisons.
- Published benchmark comparisons are contextual rather than one-to-one because harnesses, corpora, attempt budgets, retrieval backends, and parser choices differ; trajectory coding is illustrative rather than exhaustive, and benchmark graders score final outputs rather than intermediate state transitions.
- The Drive PDF exactly matches the public arXiv PDF by SHA-256; this is a preprint, not peer-reviewed evidence.

## Feeds
- [[human-ai-agent-interaction-design]]
