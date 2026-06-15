---
title: "What Jobs Can AI Learn? Measuring Exposure by Reinforcement Learning"
authors: Philip Moreira Tomei, Bouke Klein Teeselink
year: 2026
url: https://arxiv.org/abs/2605.02598
doi: 10.48550/arXiv.2605.02598
source_type: paper
retrieved: 2026-06-15
drive_file_id: 116GQGEBZzdxf-2hpxgcwXDjewM_KJ-lA
file_hash: 3a533933473b1a8f1630d05e3dc8db62247b0363bf60223743ee646aff8026cb
---

# What Jobs Can AI Learn? Measuring Exposure by Reinforcement Learning

**Citation.** Tomei, P. M., & Klein Teeselink, B. (2026). *What Jobs Can AI Learn? Measuring Exposure by Reinforcement Learning.* arXiv:2605.02598. https://doi.org/10.48550/arXiv.2605.02598

**Summary.** This preprint proposes an occupational AI-exposure measure focused on whether tasks are feasible to improve through reinforcement-learning post-training, rather than whether current LLM capabilities overlap with task descriptions. The authors score all 17,951 O*NET occupation-task pairs using LLM annotators guided by a rubric developed with RL experts and validated against confirmed deployment cases. Their RL Feasibility Index diverges from existing LLM-exposure measures in policy-relevant ways, especially for monitoring and control occupations that are not text-heavy but have verifiable outcomes and simulable environments.

## Key claims
- Existing AI exposure indices can misclassify occupations when the gap between current capability and learnability is large.
- The RL Feasibility Index first applies a physical-feasibility gate, then scores tasks across eight dimensions: verification method, environment simulability, observability, instance variation / expertise breadth, sequential depth, feedback density / decomposability, tool and interface accessibility, and output tangibility.
- The index is computed for **17,951 O*NET occupation-task pairs** and aggregated to occupations using O*NET task-importance weights.
- The index correlates with Eloundou et al.'s LLM-exposure measure but diverges sharply for specific occupations: power plant operators, railroad conductors, aircraft cargo handling supervisors, gas plant operators, and chemical plant operators score high on RL feasibility but lower on general LLM exposure.
- Creative and interpersonal roles such as musicians, physicians, CEOs, microbiologists, and natural sciences managers can rank high on LLM exposure but lower on RL feasibility because their outputs are more subjective or their environments are harder to simulate.
- A difference-in-differences analysis of U.S. job postings provides suggestive evidence that occupations with higher RL exposure are beginning to experience relative declines in openings compared with less exposed occupations.

## Evidence & limitations
- **Design:** task-level measurement study using O*NET occupations/tasks, an expert-informed RL-feasibility rubric, LLM-based annotation, robustness checks across models, comparison to existing AI-exposure measures, and suggestive labor-market validation using job postings.
- **Evidence strength:** useful forward-looking diagnostic for task learnability under RL-style post-training; explicitly distinguishes digital/software RL feasibility from physical robotics or generic present-day LLM exposure.
- **Limitations:** preprint; relies heavily on LLM-generated task annotations; covers U.S. occupational structure only; validation against human expert annotations, observed automation adoption, and non-U.S. labor markets remains incomplete; the job-posting evidence is suggestive rather than definitive causal proof of automation pressure.

## Feeds
- [[automation-and-substitution]]
- [[work-redesign]]
- [[construct-validity]]
- [[evidence-based-management]]
