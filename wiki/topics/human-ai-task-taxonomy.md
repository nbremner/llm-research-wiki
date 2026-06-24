---
title: Human-AI task taxonomy
status: active
updated: 2026-06-24
---

# Human-AI task taxonomy

Human-AI task taxonomy is the work of naming the dimensions that make one AI-enabled task meaningfully different from another. It sits between broad exposure/adoption claims and actual work redesign: before deciding whether AI augments, automates, or collaborates, the task has to be described at the right grain.

[[2026-doshi-human-ai-task-tensor]] gives the wiki its first explicit taxonomy for this. The Human–AI Task Tensor organizes tasks across eight dimensions: task definition, AI contribution, interaction modality, audit requirement, output definition, decision-making authority, AI structure, and human persona. That matters because it prevents “AI use” from being treated as a unitary condition; the same tool can occupy different positions depending on whether the output is defined, who holds authority, whether process/output audit is required, how customized the system is, and what kind of human user is involved.

The chapter’s derived frameworks make the taxonomy more usable. The AI Function Matrix separates production, idea generation, assistance, editing, explanation, and open-ended interaction by crossing AI contribution with output definition. The Task Augmentation/Automation Scale makes authority granular rather than binary. The Task Audit Matrix separates process and output audit requirements, which is a clean bridge to the wiki’s recurring concern that formal human authority is not enough if the work system does not preserve review, verification, and accountability.

The useful move for this wiki is not to adopt the tensor as final truth. It is to use it as a diagnostic checklist when evaluating AI-work evidence: what task is being studied, what output is being judged, where authority sits, what kind of audit is possible, and whether the human role is defined by expertise, preference, vulnerability, or some other relevant persona.

[[2026-zhu-choose-your-agent]] gives an empirical reason to keep authority and interaction modality separate. Advisor, Coach, and Delegate all used the same underlying model capability, but changed whether humans received recommendations, received feedback after proposing an action, or ceded execution authority. Those distinctions produced different adoption, preference, and welfare patterns, so they should not be collapsed into a single "AI assistance" condition.

[[2026-zhang-fatigue-aware-learning-defer]] adds a temporal and human-state dimension to the taxonomy problem. In learning-to-defer under fatigue, the relevant task description includes not only task difficulty and AI confidence, but also where the task occurs in a sequence and how prior allocations have changed the human expert's workload state.

[[2026-wang-agent-development-real-world-work]] pushes the taxonomy problem upstream into benchmark design. Its O*NET-based mapping shows that agent benchmarks can appear broad at the generic skill level while remaining narrow in occupational domain coverage, so a useful human-AI task taxonomy has to preserve both cross-occupational work activities and domain-specific context before benchmark performance is interpreted as work capability.

[[2025-tomlinson-working-with-ai]] adds an observed-use reason to distinguish the human-side task from the AI-side task. In Copilot conversations, the user goal and the AI action can map to different O*NET work activities, and the paper reports disjoint user-goal and AI-action activity sets in 40% of conversations. That means a taxonomy that only labels the user's requested task can miss what the AI actually did, while a taxonomy that only labels the AI output can miss the worker's underlying goal.

## Connections
- Connects to [[work-redesign]] because task taxonomy is the upstream language for deciding which workflow nodes can be delegated, constrained, audited, or protected.
- Connects to [[human-ai-collaboration]] because collaboration quality depends on authority, auditability, output definition, and the human persona in the task, not just whether a human and AI are both present.
- Connects to [[automation-and-substitution]] because augmentation/substitution claims need task-level dimensional detail before they can imply labor substitution or protected human judgment.
- Connects to [[task-level-ai-adoption]] because observed-use maps describe where AI is used, while task taxonomy describes what kind of use that is.
- Connects to [[ai-workforce-impact-measurement]] because the validity of an applicability or exposure measure depends on whether the task labels preserve human goals, AI actions, scope, authority, and audit requirements.
- Connects to [[job-analysis]] because AI-era task taxonomy is adjacent to classic work analysis: both define the work before redesign, assessment, or governance is built on top.
- Connects to [[human-ai-task-allocation]] because a taxonomy becomes operational when it informs routing rules for which actor should handle a specific task instance under current human and system conditions.
- Connects to [[ai-agent-benchmark-validity]] because benchmark scores only become interpretable when the benchmark task is located in a defensible task taxonomy.

## Contradictions & open questions
- [[2026-doshi-human-ai-task-tensor]] is a conceptual framework and book chapter, not validation evidence. The wiki still needs empirical work testing whether tensor-based task classification predicts adoption, performance, trust, motivation, skill erosion, or governance quality.
- The tensor is broad enough to be useful, but broad taxonomies can become naming systems rather than measurement systems. The construct-validity question is whether the dimensions are bounded, reliably coded, and linked to outcomes that matter.
- The human persona dimension is promising but underdeveloped for I-O use. It could connect to expertise, skill level, motivation, identity, vulnerability, or worker-desired agency; those are not interchangeable constructs.
- [[2026-zhang-fatigue-aware-learning-defer]] highlights that persona and state should not be collapsed. A worker's expertise level, current fatigue, cumulative workload, motivation, and accountability position may all affect allocation differently.
- [[2026-wang-agent-development-real-world-work]] suggests that task taxonomies used for agent evaluation inherit the limits of benchmark task descriptions. If a task prompt omits context, purpose, stakeholders, or verification conditions, taxonomy labels can become cleaner than the work they claim to represent.
- [[2025-tomlinson-working-with-ai]] shows the value of O*NET intermediate work activities for cross-occupation measurement, but also repeats the taxonomy risk: work activities are not the whole job, and the connective tissue between activities may carry much of the value that AI impact measures miss.
