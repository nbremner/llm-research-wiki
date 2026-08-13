---
title: "Large Language Models Develop Novel Social Biases Through Adaptive Exploration"
authors: Wu, Liu, Bai, Griffiths
year: 2026
url: https://icml.cc/Conferences/2026
doi: null
source_type: paper
publication_status: peer-reviewed
retrieved: 2026-08-13
drive_file_id: 1T-iRwTWi51HfCfJpo6Znudv870zoVUYH
file_hash: f0563ccb6057b6b3309558844731102bb251cd6366319214df6e347ccc28ca7c
---

# Large Language Models Develop Novel Social Biases Through Adaptive Exploration

**Citation.** Wu, A. J., Liu, R., Bai, X., & Griffiths, T. L. (2026). *Large Language Models Develop Novel Social Biases Through Adaptive Exploration.* Proceedings of the 43rd International Conference on Machine Learning, PMLR 306.

**Summary.** Wu and colleagues adapt a sequential hiring paradigm in which fictional demographic groups have identical success probabilities to test whether LLMs develop allocative stereotypes from their own feedback histories. Across 40-round, 30-run experiments, frontier models stratified groups into different job classes more strongly than human participants, despite the absence of group differences in the task. The paper argues that performance on static bias benchmarks does not establish fairness in stateful, long-horizon agentic settings and evaluates interventions that change prompting, task structure, and objectives.

## Key claims
- In the equal-probability hiring paradigm, human participants showed stratification (SI = .84, 95% CI [.79, .89]; BGD = .56) above fair random assignment (SI = .25, 95% CI [.22, .29]; BGD = .29), while frontier LLMs averaged SI = 1.39 and BGD = .69.
- Across the tested Claude, GPT, Gemini, Llama, and Qwen model families, newer or larger models showed statistically significantly greater stratification than predecessors on SI and BGD, even though higher-performing models scored better on the single-prompt BBQ bias benchmark.
- High between-run group-assignment stochasticity (mean GASI = .52 for models versus .47 for humans) and ablations reported in the paper support the authors' interpretation that the group-role associations emerged from stochastic success feedback within runs rather than fixed associations with the fictional group names.
- Chain-of-thought prompting, higher temperature, and context compression did not robustly remove stratification; changing task environments and removing gamified rewards also left strong effects.
- Explicitly incorporating diversity into the decision objective was the most robust prompt-level mitigation tested, but the paper cautions that prescriptive diversity steering may trade off with success when real group-level success probabilities are unequal or unknown.

## Evidence & limitations
- Controlled multi-turn simulation adapted from a psychology hiring experiment: 40 sequential allocation rounds, four artificial demographic groups, four job classes, and 30 runs per model/prompt condition; it is evidence about modeled agent behavior, not observed workplace deployment or discrimination outcomes.
- The groups, jobs, reward structure, and equal underlying success probabilities are deliberately stylized; the authors test variants, but external validity for real hiring or other high-stakes allocation systems remains unresolved.
- The PDF identifies itself as an ICML 2026 proceedings paper (PMLR 306), but as retrieved the expected PMLR volume path and exact-title Crossref search did not yield a live, matching public source record or DOI. The public ICML 2026 conference page is recorded as venue-level provenance; exact paper-level public provenance still needs verification.
- The PDF was extracted successfully with pypdf (41 pages; 227,253 characters). The scan found scholarly discussion and examples of system prompts, not instructions directed at this ingesting agent; no prompt-injection risk was identified.

## Feeds
- [[responsible-ai-deployment]]
