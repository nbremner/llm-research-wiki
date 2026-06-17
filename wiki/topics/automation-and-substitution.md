---
title: Automation and substitution
status: active
updated: 2026-06-16
---

# Automation and substitution

Whether AI substitutes for inputs (labor, capital) or augments them — and what scales, what shrinks.

- [[2026-kim-mapping-ai-into-production]]: treated firms grew output (tasks, customers, revenue) while
  **labor demand stayed flat and capital demand fell ~39.5%** — a "do more with less" pattern where
  AI substituted for *external capital* rather than for headcount, at least in young firms over a
  short window. Founders described AI as doing the "analyst or intern version" of tasks.
- [[2026-ermakov-designing-post-role-enterprise]]: automation is framed as a design-boundary problem,
  not simple task replacement. Some workflow nodes can be handed to agents, but others are
  "Human-Critical Nodes" where ethical judgment, relational trust, irreversible consequences, or
  visible accountability require human presence. The design problem is which workflow parts can be
  delegated to digital labor, which require human authority, and how accountability is assigned before
  failure.
- [[2023-dellacqua-jagged-technological-frontier]]: task substitution is jagged, not linear. In a BCG
  consultant experiment, GPT-4 assistance improved productivity and quality for tasks inside the
  frontier but reduced correctness on a task outside it. The substitution question is therefore not
  "can AI do consulting work?" but which task components are currently inside the model's capability
  frontier and how that frontier is detected.
- [[2025-brynjolfsson-generative-ai-at-work]]: GenAI augmented customer-support agents rather than
  replacing them in the observed rollout. Productivity rose 15% on average, especially for lower-skill
  and less experienced workers, but the paper cannot observe wages, overall labor demand, or hiring
  composition. It is evidence for within-job task augmentation, not direct labor substitution.
- [[2026-tomei-what-jobs-can-ai-learn]] reframes exposure around what AI systems may be able to learn,
  not only what current LLMs can already do. Its RL Feasibility Index finds that some monitoring and
  control occupations score higher on future automation feasibility than text-centered exposure indices
  suggest, because the relevant tasks have verifiable outcomes and simulable environments.
- [[2023-nyc-automated-employment-decision-tools-faq]] brings the substitution question into employment
  decisions. Covered AEDTs are defined around tools that substantially assist or replace discretionary
  decision-making, and screening counts as an employment decision. [[algorithmic-assessment]] can
  therefore substitute for parts of human judgment before the final hiring or promotion decision is
  made.
- [[2023-landers-machine-learning-psychometric-assessment]] implies that algorithmic substitution should
  be evaluated at the level of assessment-design components: combining scale composites, scoring item
  responses, dropping predictors, or handling novel data formats. Replacing OLS with machine learning is
  not the same thing as improving the selection system.
- [[2025-mazeika-remote-labor-index]] adds a direct end-to-end automation benchmark for remote
  freelance work. Across 240 real commissioned projects, current agents completed at most 2.5% of tasks
  at a reasonable-client acceptance standard, despite the same models often looking strong on narrower
  knowledge, coding, or computer-use evaluations. This is evidence against treating benchmark progress
  as realized labor substitution without checking whether the whole deliverable can actually be
  completed.
- [[2025-shukla-ai-assisted-design-ironies]] brings in the substitution myth from human-automation
  research. The paper argues that assigning UX tasks to AI based on a simple “machines are better at”
  logic misses how automation changes the human role: designers may do less direct drafting but more
  monitoring, validation, troubleshooting, and accountability work.
- [[2025-handa-economic-tasks-ai]] estimates that 43% of observed Claude.ai usage looked automation-like
  and 57% looked augmentation-like. That makes automation and augmentation empirical usage patterns
  rather than mutually exclusive futures: both appear in current task-level AI use, often before there is
  evidence about employment, wages, or durable substitution.

## Contradictions & open questions

- **Replacement vs. protected human judgment.** Automation can reduce dependence on some human task
  execution while increasing the importance of human accountability at specific nodes. The wiki needs
  empirical sources on whether organizations can actually identify and govern these nodes reliably.
- The labor-demand question is still thin. Disagreement on labor substitution should be surfaced here,
  not averaged away.
- [[2023-dellacqua-jagged-technological-frontier]] is task-performance evidence, not labor-demand
  evidence. It supports selective task delegation, but not claims about headcount substitution.
- **Short-run augmentation vs. equilibrium substitution.** [[2025-brynjolfsson-generative-ai-at-work]]
  shows higher output per hour inside an existing job, but explicitly cannot answer whether firms later
  hire fewer agents, hire different agents, change wages, or automate the role more fully.
- **Exposure vs. realized substitution.** [[2026-tomei-what-jobs-can-ai-learn]] is a forward-looking
  exposure index, not evidence that listed occupations have already been automated. Its job-posting
  analysis is suggestive; the stronger contribution is measurement of task learnability.
- **Support vs. substitution in hiring.** Employers may describe algorithmic assessment as decision
  support, while regulatory language treats some uses of simplified outputs, rankings, or classifications
  as substantial assistance or replacement of discretion. The boundary is practical, not merely semantic.
- **Task exposure vs. end-to-end deliverables.** [[2025-mazeika-remote-labor-index]] cuts against simple
  exposure narratives: a task can be computer-based, remote, and economically valuable while still
  resisting autonomous completion because quality, file integrity, multimodal artifacts, and project
  integration fail at the deliverable level.
- **Substitution vs. transformed responsibility.** [[2025-shukla-ai-assisted-design-ironies]] suggests
  that even when AI substitutes for visible task execution, the human may inherit harder-to-see
  responsibilities for interpretation, correction, rationale, and consequences.
- **Conversation automation vs. labor substitution.** [[2025-handa-economic-tasks-ai]] can classify some
  AI conversations as automation-like, but that does not establish job-level substitution. The human may
  still be selecting the task, evaluating the output, integrating it into a larger workflow, and bearing
  accountability.
