---
title: Automation complacency
status: active
updated: 2026-06-22
---

# Automation complacency

Automation complacency is the failure mode where better machine advice reduces human attention, effort, or learning enough that the combined human-AI system underperforms what the model's standalone accuracy would imply. It is not simply algorithm aversion's opposite. The problem is not that workers distrust the tool; it is that they trust or defer to it in a way that changes the work they still do.

[[2022-dellacqua-falling-asleep-at-wheel]] makes this mechanism concrete in HR screening. In a field experiment with professional recruiters, AI assistance improved accuracy overall, but recruiters followed advice more often as stated AI quality rose and lower-quality AI induced more time and effort. The useful design lesson is uncomfortable: maximizing model accuracy is not the same as maximizing system performance when human effort is endogenous.

[[2025-lee-generative-ai-critical-thinking]] gives the GenAI knowledge-work analogue. Higher confidence in GenAI was associated with less critical thinking, while higher self-confidence and confidence evaluating AI were associated with more critical thinking. That suggests complacency can arise through confidence calibration, not just through formal delegation.

[[2026-dellacqua-jagged-technological-frontier]] adds the task-boundary version. Fluent AI-supported work can improve performance inside the frontier while harming correctness outside it, especially if users cannot tell which kind of task they are in. Complacency is most dangerous when subjective coherence rises faster than actual correctness.

[[2026-ehsan-future-workers]] extends complacency from a short-run effort problem into a longitudinal expertise problem. Its “intuition rust” finding suggests that faster approval and reduced hands-on practice can look like efficiency before they become visible as skill atrophy or identity loss.

[[2025-yun-generative-ai-knowledge-work]] adds a synthesis-specific complacency pathway. Product managers valued AI summaries, clusters, and Q&A, but they also worried about hallucinations, confirmation bias, and missing business context; one participant warned that an agreeable tool could lead them down the wrong path. In knowledge synthesis, complacency can appear when generated structure makes messy evidence feel settled before the user has checked sources, compared interpretations, or added context outside the model's reach.

[[2025-kosmyna-brain-chatgpt-cognitive-debt]] adds an effort-and-ownership signal from repeated LLM-assisted writing. The LLM condition showed weaker neural connectivity and lower ability to quote recently written essays, while search-engine and brain-only conditions preserved more engagement. This is not the same as workplace automation complacency, but it shows how apparently useful assistance can change the human's contribution to the task before the output itself obviously fails.

[[2026-lepine-precision-proactivity]] complicates the complacency frame by showing the opposite burden can also matter. In AI-assisted financial valuation, AI-generated content use was associated with better quality, but extraneous cognitive load from task switching and information sprawl was strongly harmful. Some AI failures reduce human effort too much; others consume attention in repair work and leave too little capacity for judgment.

## Connections
- Relates to [[human-ai-collaboration]] because collaboration quality depends on preserving competent human review, not merely keeping a human nominally in the loop.
- Relates to [[critical-thinking]] because attention, verification, and stewardship are effortful behaviors that can decay when AI confidence is high.
- Relates to [[algorithmic-assessment]] because hiring tools often frame humans as final decision-makers while simplified recommendations can still reshape discretion.
- Relates to [[work-redesign]] because interface design, feedback, task sequencing, and escalation rules can either preserve or erode human oversight.
- Relates to [[ai-induced-skill-erosion]] because repeated complacency can become capability loss when workers no longer practice the judgment they are expected to retain.
- Relates to [[ai-supported-knowledge-synthesis]] because synthesis tools are especially prone to making partial or contextual evidence look clean, ranked, and complete.
- Relates to [[cognitive-load-in-ai-assisted-work]] because overload and complacency are distinct ways AI can weaken human contribution to system performance.

## Contradictions & open questions
- Better AI can still improve average performance, as [[2022-dellacqua-falling-asleep-at-wheel]] shows when pooling AI conditions and in the perfectly predictive benchmark. The claim is not "worse AI is better"; it is that human behavioral response can make the model-quality optimum differ from the system-performance optimum.
- The strongest evidence here is short-run task behavior. The wiki still needs longitudinal evidence on whether complacency becomes skill atrophy, whether feedback restores calibration, and which design interventions preserve attention without wasting human effort.
- There is a design tension between reducing unnecessary cognitive load and preserving enough friction for meaningful review. Removing all friction can be efficient when the model is right and dangerous when the model is wrong.
- There is a parallel learning tension: reducing cognitive load can be the point of assistance, but [[2025-kosmyna-brain-chatgpt-cognitive-debt]] suggests that repeated reduction in effort may also reduce ownership, recall, or practice when the task is supposed to build capability.
- [[2025-yun-generative-ai-knowledge-work]] suggests design countermeasures — citations, audit trails, comparative outputs, and access to raw data — but it does not test which of these actually prevents complacency in live organizational decisions.
- [[2026-lepine-precision-proactivity]] suggests that proactivity should be load-sensitive rather than maximal. The unresolved question is how systems detect when help should become repair, simplification, or silence.
