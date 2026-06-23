---
title: Human-AI task allocation
status: stub
updated: 2026-06-23
---

# Human-AI task allocation

Human-AI task allocation is the design problem of deciding, at the level of a specific task instance or workflow turn, whether the human, the AI system, or some hybrid arrangement should act. It is narrower than broad [[human-ai-collaboration]] and more operational than [[automation-and-substitution]]: the question is not only whether AI can do a class of work, but when the system should route this case to the model, preserve human judgment, or change routing because the human's state, workload, expertise, or accountability conditions have changed.

[[2026-zhang-fatigue-aware-learning-defer]] gives the topic its first direct algorithmic source. In fatigue-aware learning to defer, each deferral to a human expert changes cumulative workload and therefore future human performance. The allocation policy should therefore be stateful: a difficult case may belong with a fresh expert, while a later difficult case may belong with AI if accumulated fatigue makes human error more likely.

The important I-O bridge is that allocation quality depends on a human-state model, not only a model-capability estimate. Zhang et al. optimize accuracy under a human-AI cooperation budget, but the same architecture points toward richer work-design questions: what human states matter, how they are measured, when worker agency overrides algorithmic routing, and how organizations prevent allocation systems from treating fatigue as merely a resource constraint to optimize around.

## Connections
- Relates to [[human-ai-task-taxonomy]] because allocation policies need task dimensions such as decision authority, audit requirement, output definition, AI contribution, and human persona before routing decisions can be interpreted.
- Relates to [[cognitive-load-in-ai-assisted-work]] because workload and fatigue change the value of human involvement across a sequence, not just within a single static task.
- Relates to [[work-redesign]] because dynamic allocation changes where human judgment enters the workflow and which nodes require escalation, rest, verification, or protection.
- Relates to [[automation-and-substitution]] because task-level routing can substitute for human action at some turns while preserving human involvement at others.
- Relates to [[automation-complacency]] because allocation systems may reduce human burden appropriately or quietly remove the practice and attention needed for competent oversight.

## Contradictions & open questions
- [[2026-zhang-fatigue-aware-learning-defer]] shows performance benefits in simulated benchmark settings, but it does not yet show whether workers accept dynamic routing, whether fatigue measurement is valid in live work, or whether organizations govern such routing fairly.
- Optimizing allocation for accuracy and coverage can conflict with preserving worker agency, learning, task significance, and accountability. A system that routes around fatigue may improve immediate performance while leaving harder questions about staffing, recovery, and work design untouched.
- The wiki needs field evidence on allocation policies that use real human-state signals — fatigue, skill, confidence, workload, motivation, or accountability — rather than assuming those states can be cleanly simulated or inferred.
