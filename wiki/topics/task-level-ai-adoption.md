---
title: Task-level AI adoption
status: active
updated: 2026-07-01
---

# Task-level AI adoption

Task-level AI adoption asks where workers actually bring AI into the work, before the organization has necessarily redesigned roles, governance, or labor demand around it. The unit is not the occupation and not the tool rollout; it is the task or task cluster where AI use appears.

[[2025-handa-economic-tasks-ai]] gives the first broad observed-use baseline. Mapping more than four million Claude.ai conversations to O*NET tasks showed that usage was concentrated in software development and writing but still spread unevenly across many occupations. The key move was methodological: replacing exposure speculation with conversation-level evidence about which tasks people actually attempted with AI.

[[2025-agarwal-what-work-ai-doing]] adds a task-characteristics explanation for that observed-use map. Using the same scale of Claude interaction data, the authors score O*NET tasks across routine, cognitive, social-intelligence, creativity, domain-knowledge, complexity, and decision-making dimensions. AI use was highest for non-routine, cognitively demanding, creative, and complex tasks, and the top 5% of tasks accounted for 59% of all interactions.

[[2025-tomlinson-working-with-ai]] extends observed-use mapping from task occurrence to AI applicability. Using 200,000 Bing Copilot conversations, the authors map both user goals and AI actions to O*NET intermediate work activities, then weight those activity maps by completion, feedback, and scope. The user-goal / AI-action split matters because it separates the activity the worker is trying to accomplish from the activity the AI performs in service of that goal; in 40% of conversations, the two activity sets were disjoint.

[[2025-shao-future-work-ai-agents]] adds the missing worker-preference side of task-level mapping. Instead of inferring adoption from conversation traces or exposure scores, it audits 844 computer-compatible O*NET tasks across 104 occupations using 1,500 domain workers and 52 AI experts. Workers expressed positive attitudes toward AI-agent automation for 46.1% of tasks, but the important signal is the mismatch map: some tasks are technically feasible and desired, some are feasible but unwanted, some are desired but not yet feasible, and some are low priority on both dimensions.

The useful design implication is that adoption is not simply moving from routine work upward into knowledge work. Current conversational GenAI use appears especially attractive for high-friction cognitive starts: idea generation, information processing, originality, synthesis, and dynamic problem solving. Standardized operational tasks show less conversational use, which may mean they are already automated elsewhere, better suited to API/workflow automation than chat interaction, or less compelling for current LLMs.

[[2026-almog-barriers-ai-adoption]] adds a live-task behavioral counterpoint to large-scale conversation traces. In an AI-assisted image-categorization task, workers used AI less when reliance was visible to an evaluator, despite lower final accuracy. Task-level adoption is therefore not only a function of task characteristics or technical fit; it can be suppressed by whether the use event is socially visible and evaluatively meaningful.

[[2026-johnston-shift-agentic-ai-codex]] shifts the observed-use evidence from conversational traces to agentic task delegation. Codex usage remains anchored in software production — engineering operations, code implementation, code understanding, application management, and validation — but in deeper-adoption contexts it spreads into research, planning, communication, data analysis, product work, recruiting, sales, and other knowledge-work categories. The adoption unit also changes: the relevant event is no longer only a conversation about a task, but a delegated work thread with estimated human-time complexity, runtime, outputs, and possible follow-up review.

## Connections
- Connects to [[ai-adoption]] because task-level usage is an input to the mapping problem: organizations need to know which task patterns actually invite AI use before they can turn experimentation into durable adoption.
- Connects to [[work-redesign]] because observed use identifies pressure points, not finished designs. The redesign question is how those task clusters get reallocated, governed, verified, and recombined.
- Connects to [[automation-and-substitution]] because conversation-level automation-like behavior is not the same as labor substitution. Task use can be high while jobs, accountability, and integration remain human-held.
- Connects to [[ai-workforce-impact-measurement]] because task-level traces become stronger evidence when they are linked to completion, scope, work-activity taxonomies, and explicit limits on what can be inferred.
- Connects to [[human-ai-collaboration]] because the same task can involve learning, iteration, partial delegation, or direct fulfillment depending on how the human scopes and uses the AI output.

## Contradictions & open questions
- [[2025-handa-economic-tasks-ai]] classifies observed conversations into augmentation-like and automation-like uses, while [[2025-agarwal-what-work-ai-doing]] explains adoption with task characteristics. The relationship between interaction form and task demand is still underdeveloped: dynamic problem solving may invite AI use, but that does not say whether the use is good collaboration, automation, or overreliance.
- Observed use is not organizational adoption. Both sources see what people do in Claude conversations, not whether the work system changed around those conversations or whether output quality, accountability, learning, and downstream performance improved.
- [[2025-tomlinson-working-with-ai]] improves the measurement chain by adding completion and scope, but it still does not observe realized productivity, job redesign, wages, or staffing. Applicability is stronger than raw use, but still weaker than organizational impact.
- Worker desire is not realized adoption either. [[2025-shao-future-work-ai-agents]] adds a needed demand-side measure, but preferences from structured interviews do not show whether workers would use agents in live workflow conditions, whether quality improves, or whether organizations redesign work around those preferences.
- Social intelligence is a live boundary condition. [[2025-agarwal-what-work-ai-doing]] finds it statistically decoupled from usage, but that may reflect what users currently ask chat-based tools to do rather than what AI can or should do in relational work.
- Visibility changes the adoption map. [[2026-almog-barriers-ai-adoption]] suggests the same AI-assisted task can show different use rates depending on whether reliance is private or attached to evaluation, so observed-use data may understate latent usefulness where workers expect reputational penalties.
- [[2026-johnston-shift-agentic-ai-codex]] improves task-level measurement for agentic tools, but its strongest adoption evidence comes from a product and company context with unusually low frictions. The gap between OpenAI-internal usage and external organizational usage is itself part of the finding: task fit does not automatically become broad organizational adoption.
