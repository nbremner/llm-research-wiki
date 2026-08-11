---
title: "Three-Phase Evaluation of AI-Assisted Software Development Life Cycle"
authors: Strubel, Russell, Crockett, Ferraro, Londhe, Syed, Viehe
year: 2026
url: https://arxiv.org/abs/2607.05125
doi: 10.48550/arXiv.2607.05125
source_type: paper
publication_status: preprint
retrieved: 2026-08-11
drive_file_id: 1Y3eZsQ7J_l-uKM_sLPs0pmxhfmqJIOiX
file_hash: 4187af1486d4f3a2b6dd9fe93a469f12f0abbcbd0ec8861201ed5216ca619ebe
---

# Three-Phase Evaluation of AI-Assisted Software Development Life Cycle

**Citation.** Strubel, J., Russell, C., Crockett, C., Ferraro, J., Londhe, N., Syed, U., & Viehe, J. (2026). *Three-phase evaluation of AI-assisted software development life cycle.* arXiv. https://doi.org/10.48550/arXiv.2607.05125

**Summary.** This exploratory arXiv preprint compares three sequential reimplementations of the same small full-stack application by four senior computer-science students: partial AI-assisted development with GitHub Copilot, AI-exclusive Copilot, and AI-exclusive AWS Kiro. Across phases, logged development hours, requirement-traceability scores, prompt success, and NASA-TLX workload measures moved in an apparently favorable direction, while frustration rose modestly. The design cannot separate AI-autonomy or platform effects from accumulated familiarity with the application, requirements, prompting, and agentic workflows.

## Key claims
- Logged development hours declined from 36.0 in partial-agentic Copilot (Phase 1) to 9.4 in AI-exclusive Copilot (Phase 2) and 5.9 in AI-exclusive AWS Kiro (Phase 3), an 84% reduction from Phase 1 to Phase 3; the paper also reports an inconsistent 87% figure in its conclusion.
- Requirement-to-Implementation Traceability Matrix (RITM) scores rose from 18/22 to 19/22 to 20/22 across the three phases, but RITM assesses requirement traceability rather than security, maintainability, technical debt, or comprehensive software quality.
- Mean NASA-TLX effort, mental demand, and temporal demand decreased across phases, while mean frustration increased from 6.25 to 6.75 to 7.5; performance self-ratings stayed high but fell from 17.5 to 16.25.
- At nominally equivalent AI-exclusive autonomy, AWS Kiro had lower logged development hours, a higher RITM score, and higher prompt success than Copilot, but its specification-driven workflow used more prompts per feature (2.42 versus 1.92).
- The authors interpret the pattern as a role shift from manual implementation toward requirement interpretation, prompt design, orchestration, and validation rather than evidence that human oversight is unnecessary.

## Evidence & limitations
- This is a July 2026 arXiv preprint (cs.SE; cs.AI), not peer-reviewed. The Drive PDF exactly matches the public arXiv PDF by SHA-256.
- The study is descriptive only: a single four-student team sequentially reimplemented one small greenfield application, phases were neither randomized nor counterbalanced, and there was no statistical inference.
- Developer familiarity with the application, requirements, prompting strategies, and agentic workflows accumulated across phases; neither autonomy nor platform effects can therefore be causally isolated.
- Time tracking was self-reported, prompt success had no standardized rubric, NASA-TLX was measured with four phase-level responses, and the external evaluator knew the phase identity. Exact model versions, runtime configurations, permissions, and session parameters were not systematically archived.
- The source contains no model-directed instructions. Its ordinary methodological use of “large language model” was treated as source text, not a prompt-injection signal.

## Feeds
- [[agentic-delegation]]
- [[cognitive-load-in-ai-assisted-work]]
- [[ai-mediated-work-experience]]
- [[work-redesign]]
