---
title: Critical thinking in AI-assisted work
status: active
updated: 2026-07-02
---

# Critical thinking in AI-assisted work

This page is not a general construct page for critical thinking. It tracks how GenAI changes where, when, and whether critical thinking is exercised in knowledge work: verification, stewardship, integration, source checking, judgment under cognitive load, and skill-preserving use.

Critical thinking matters for the wiki because GenAI changes not only what knowledge workers produce, but where judgment is exercised in the work process.

[[2025-lee-generative-ai-critical-thinking]] studies this directly. In a CHI 2025 survey of 319 knowledge workers using GenAI at least weekly, participants supplied 936 workplace examples. They reported enacting some critical thinking in about 60% of examples, usually to improve work quality, avoid negative outcomes, or develop skill. The strongest warning is confidence-shaped: higher confidence in GenAI doing the task was associated with less critical thinking, while higher self-confidence and confidence evaluating AI responses were associated with more critical thinking.

The useful framing is not simply “AI reduces thinking.” The paper suggests that GenAI shifts critical thinking: from information gathering to information verification, from problem-solving to response integration, and from task execution to task stewardship. That makes critical thinking a design problem inside [[human-ai-collaboration]], not just an individual trait or training module.

[[2022-dellacqua-falling-asleep-at-wheel]] adds causal behavioral evidence for the effort channel. In an HR-recruiter field experiment, higher-quality AI advice increased reliance, while lower-quality AI induced more time and effort. This supports the concern that confidence in AI can suppress scrutiny, but it also keeps the claim precise: the issue is not less thinking in general, but less task-relevant verification when the system appears competent.

[[2025-shukla-ai-assisted-design-ironies]] gives the design-practice version of the same shift. UX practitioners saw AI as useful for drafts, user flows, research scripts, and ideation, but they also emphasized the need to check hallucinations, detect bias, preserve design rationale, and defend choices. The paper's sharper warning is about cognitive offloading: if AI bypasses sketching, problem framing, incubation, and exploratory iteration, critical thinking may be displaced from creative formation into after-the-fact supervision.

[[2026-ehsan-future-workers]] adds a longitudinal expert-work version: if AI-supported workflows reduce the need to exercise intuition and manual judgment, critical thinking may not just shift location but atrophy through non-use.

[[2025-yun-generative-ai-knowledge-work]] sharpens the verification side of critical thinking in AI-supported synthesis. Product managers in the Yodeai study wanted AI to cluster, summarize, and prioritize unstructured evidence, but they also returned to raw interviews, reviews, citations, company context, and stakeholder judgment because they did not treat AI output as decision authority. Critical thinking here is not an abstract disposition; it is designed into source visibility, cross-verification, audit trails, and the ability to compare AI outputs against the underlying data.

[[2025-kosmyna-brain-chatgpt-cognitive-debt]] gives a more physiological and behavioral warning from essay writing: LLM users appeared to engage less deeply with the writing task, produced more homogeneous language, reported lower ownership, and recalled less of their own text. For this page, the useful point is not “ChatGPT makes people stupid.” It is that critical thinking can be displaced from generating, selecting, and remembering ideas into accepting or lightly editing machine output, which changes both the task process and what the user practices.

[[2026-lepine-precision-proactivity]] adds the overload side of the same problem. In complex AI-assisted valuation work, extraneous load from conversational misalignment was strongly negative for quality, even while AI-generated content helped. Critical thinking requires capacity; when the interaction itself creates task switching, information sprawl, or repair work, stewardship may fail because the user is overloaded rather than because they are complacent.

[[2026-shen-ai-impacts-skill-formation]] adds that critical thinking can be a learning mechanism, not only an output-control mechanism. Participants who asked conceptual questions, requested explanations, or checked their understanding after code generation preserved more skill formation than participants who delegated code writing or debugging to AI. The implication for AI-supported work is concrete: verification routines should be designed to build comprehension and transfer, not merely catch defects in the current artifact.

[[2025-randazzo-genai-power-persuader]] adds a sharper boundary around verification: critical thinking can be attempted and still be captured by the AI interaction if the user validates the model by debating with the model itself. In the consultants' GPT-4 logs, validation episodes were followed by more persuasive responses, so the relevant design problem is not only whether workers think critically, but whether the verification channel gives them independent leverage against model-generated ethos, logos, and pathos.

[[2026-shaw-thinking-fast-slow-artificial]] gives the wiki direct behavioral evidence for [[cognitive-surrender]]: people often consult an AI assistant on reasoning problems and then adopt its answer even when it is confidently wrong. In Study 1, AI access improved accuracy when the AI was accurate but pushed accuracy below the Brain-Only baseline when the AI was faulty, while also increasing confidence. That makes critical thinking partly a routing problem: does the person use AI as input to judgment, or does the AI output become the judgment?

This page differs from [[complex-collaborative-problem-solving]] in topic type. CPS and ColPS are transversal skills and assessment targets; this page tracks how GenAI changes the exercise of judgment inside work. Critical thinking may be one process inside complex problem solving, but the focal question here is not how to assess CPS/ColPS generally. It is how AI shifts critical thinking from generation to verification, from solving to stewardship, and from independent cognition to human-AI coordination.

## Connections

- Relates to [[ai-adoption]] because adoption quality depends on whether users retain enough judgment to evaluate, adapt, and steward AI outputs rather than merely use the tool more often.
- Relates to [[automation-complacency]] because reduced critical thinking can be a system-induced response to apparently reliable AI advice, not simply an individual deficit.
- Relates to [[ai-induced-skill-erosion]] because judgment exercised less often may become judgment held less securely.
- Relates to [[evidence-based-management]] because self-reported reductions in cognitive effort should not be treated as direct evidence of long-term skill atrophy without stronger longitudinal or behavioral measures.
- Relates to [[construct-validity]] because “critical thinking” is itself hard to observe; output diversity, self-report, and task performance capture different parts of the construct.
- Relates to [[ai-supported-knowledge-synthesis]] because synthesis tools can either scaffold verification and comparison or make generated structure feel more authoritative than the evidence warrants.
- Relates to [[responsible-ai-deployment]] because critical-thinking safeguards should be built into the system and work process rather than assigned solely to users facing a persuasive model.
- Relates to [[cognitive-load-in-ai-assisted-work]] because verification and stewardship depend on whether the AI interface preserves enough cognitive bandwidth for judgment.
- Relates to [[complex-collaborative-problem-solving]] because AI may change which parts of complex and collaborative problem solving require human critical thinking, especially problem framing, verification, coordination, and adaptive control.
- Relates to [[cognitive-surrender]] because some AI-assisted failures occur when critical thinking is bypassed entirely rather than merely shifted into verification or stewardship.

## Contradictions & open questions

- [[2025-lee-generative-ai-critical-thinking]] is cross-sectional and self-reported. It shows perceived shifts in effort and judgment, not causal evidence that GenAI degrades critical thinking over time.
- Less effort is ambiguous. It may indicate productive cognitive offloading, underinvestment in judgment, or both depending on task stakes and user expertise. [[2022-dellacqua-falling-asleep-at-wheel]] sharpens that ambiguity: less effort can improve performance when AI is truly perfect, but harm learning or oversight when AI is merely good.
- [[2025-shukla-ai-assisted-design-ironies]] is not longitudinal evidence of skill loss. It identifies a plausible de-skilling mechanism from practitioner discourse and automation theory, but the causal claim still needs behavioral and longitudinal evidence.
- [[2025-yun-generative-ai-knowledge-work]] makes verification needs vivid, but it does not measure whether audit trails, citations, or multiple visualizations actually increase critical-thinking behavior or merely make users feel safer.
- [[2025-kosmyna-brain-chatgpt-cognitive-debt]] is stronger than self-report on engagement because it includes EEG and recall measures, but it is still a preprint in an educational essay-writing context; workplace critical-thinking claims need designs closer to real decisions, expertise, and consequences.
- [[2026-lepine-precision-proactivity]] uses transcript-derived cognitive-load proxies rather than direct measures of critical thinking, so its contribution is a plausible capacity mechanism rather than direct evidence about judgment quality.
- [[2026-shen-ai-impacts-skill-formation]] implies that explanation and checking can preserve learning, but it also shows why current-artifact correctness is too narrow as a verification target; users can get a working answer while losing the comprehension needed for future critical thinking.
- [[2025-randazzo-genai-power-persuader]] shows a different failure mode from complacency: professionals may scrutinize the output, but the conversational validation process itself can become persuasive. The unresolved question is which verification designs give users independent traction rather than simply more fluent model self-defense.
- [[2026-shaw-thinking-fast-slow-artificial]] is strong causal evidence for surrender on CRT-style reasoning tasks, but it leaves open whether workplace experts surrender in the same way when tasks carry accountability, domain context, and opportunities for external verification.
