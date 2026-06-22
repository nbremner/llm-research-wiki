---
title: Cognitive load in AI-assisted work
status: stub
updated: 2026-06-22
---

# Cognitive load in AI-assisted work

Cognitive load in AI-assisted work tracks the mental burden created by the task itself, the AI interface, and the coordination work required to keep human and model aligned. The useful distinction is between intrinsic load, which comes from genuine task difficulty, and extraneous load, which comes from unnecessary interaction friction: task switching, information sprawl, incoherent model initiative, missing context, or outputs that force the user to repair the conversation instead of progressing the work.

[[2026-lepine-precision-proactivity]] gives this topic its first direct work-domain evidence. In a study of 34 financial professionals completing a complex valuation task with GPT-4o, AI-generated content use was positively associated with output quality, but extraneous load had the largest negative association with quality, roughly three times the magnitude of intrinsic load. The important design claim is precise: AI can help with content while still making the work cognitively harder through badly timed or badly structured proactivity.

The paper also makes cognitive load observable in human-AI traces. Lepine et al. estimate load from transcript features grounded in task decomposition, semantic coherence, dependency structure, and knowledge-graph representations. That gives the wiki a measurement bridge between broad claims about AI-mediated effort and concrete interaction diagnostics: when the model initiates task switches, spreads information across too many directions, or truncates needed structure, load becomes a design signal rather than a vague complaint.

## Connections
- Relates to [[human-ai-collaboration]] because collaboration quality depends on whether model initiative reduces burden or creates coordination work the human must absorb.
- Relates to [[automation-complacency]] because low effort and high load are different failure modes: some AI systems suppress scrutiny, while others overwhelm the user with extraneous coordination demands.
- Relates to [[critical-thinking]] because verification and stewardship require enough cognitive capacity to evaluate AI output rather than merely cope with conversational disorder.
- Relates to [[ai-mediated-work-experience]] because cognitive load is one channel through which AI changes workload, competence, control, and felt job quality.
- Relates to [[work-redesign]] because task sequencing, escalation rules, and interface defaults can either suppress extraneous load or push it onto workers.

## Contradictions & open questions
- [[2026-lepine-precision-proactivity]] is observational and domain-specific. Its framework is promising because it uses real transcripts from professionals, but its load measures are computational proxies that still need validation against established cognitive-load assessments.
- AI-generated content can improve quality while extraneous load harms it. That means “AI makes the task easier” is too coarse: assistance can reduce one burden while creating another.
- The open design question is when proactivity should be suppressed, delayed, or transformed into repair. More initiative is not automatically better; proactivity needs to be state-dependent and load-sensitive.
- The framework depends on domain-specific task decompositions and knowledge graphs, so portability to software engineering, healthcare, HR, or strategy work remains an empirical problem rather than an assumption.
