---
title: "Fatigue-Aware Learning to Defer via Constrained Optimisation"
authors: Zhang, Nguyen, Rosewarne, Wells, Carneiro
year: 2026
url: https://arxiv.org/abs/2604.00904
doi: 10.48550/arXiv.2604.00904
source_type: paper
publication_status: preprint
retrieved: 2026-06-23
drive_file_id: 1XnBANj0Xq0Gp5yx6zM9Iu8EUAbDGzuS2
file_hash: b062cec07b7ff953537a88a8ba0a3f4f23a4bcce9527b1b500cf706d653efd1d
---

# Fatigue-Aware Learning to Defer via Constrained Optimisation

**Citation.** Zhang, Z., Nguyen, C. C., Rosewarne, D., Wells, K., & Carneiro, G. (2026). *Fatigue-Aware Learning to Defer via Constrained Optimisation*. arXiv. https://arxiv.org/abs/2604.00904

**Summary.** Zhang et al. propose FALCON, a fatigue-aware learning-to-defer framework that decides whether an AI system or human expert should handle each task while accounting for cumulative human workload. The paper argues that standard learning-to-defer methods treat human experts as static oracles, which is unrealistic when fatigue changes expert performance across a task sequence. FALCON models deferral as a constrained Markov decision process and uses PPO-Lagrangian training to optimize accuracy while keeping human utilization within a specified cooperation budget.

## Key claims
- Learning-to-defer systems should model human performance as workload-varying rather than static, because each deferral to a human expert changes future cognitive state and therefore future task-allocation quality.
- FALCON combines task features and cumulative human workload in a constrained Markov decision process, allowing the policy to allocate difficult work to humans when they are fresh and avoid over-deferring when fatigue is likely to degrade human performance.
- The FA-L2D benchmark varies fatigue dynamics across Cifar100, Flickr10K, MiceBone, and Chaoyang datasets, creating scenarios from near-static expert performance to rapid fatigue degradation.
- Across the FA-L2D benchmark, FALCON produced the best AUACC values among tested methods: 74.01 on Cifar100, 84.13 on Chaoyang, 64.40 on Flickr10K, and 86.08 on MiceBone, compared with the strongest non-FALCON baselines of 71.01, 83.24, 63.26, and 84.61 respectively.
- On Cifar100 robustness tests, FALCON led in both fine-tuning and zero-shot settings under sustained high performance, normal fatigue, and rapid fatigue; under rapid fatigue, FALCON reported AUACC of 72.36 fine-tuned and 71.68 zero-shot versus the strongest non-FALCON baselines at 67.36 and 67.49.
- The ablation study suggests that temporal memory alone is insufficient: adding S5 memory to a static one-stage learning-to-defer model helped at high coverage but harmed low-coverage performance, while the fatigue-aware CMDP formulation outperformed both baselines across coverage levels.
- The paper maps a real mammographic film-reading fatigue curve, where radiologist recall declined from 78% to 66% over 100 continuous readings, onto the Chaoyang dataset and reports that FALCON remained effective in zero-shot testing under that real-world fatigue profile.

## Evidence & limitations
- Evidence is computational and benchmark-based: the main results come from simulated fatigue dynamics layered over image-classification datasets, not from deployed workplace systems where task allocation, accountability, and worker experience are endogenous.
- Human performance curves are psychologically motivated and partly validated against a clinical fatigue pattern, but most expert behavior in the benchmark is simulated rather than directly observed across work contexts.
- The paper is an arXiv preprint. The Drive PDF matches arXiv version 1 exactly by SHA-256, while the current arXiv record points to version 2; the stable unversioned arXiv URL is used as canonical provenance.
- The framework treats fatigue-aware allocation as an accuracy-and-coverage optimization problem, so it says less about construct validity of workload measures, worker agency, acceptability, trust, or accountability under real organizational governance.

## Feeds
- [[human-ai-task-allocation]]
- [[human-ai-collaboration]]
- [[human-ai-task-taxonomy]]
- [[cognitive-load-in-ai-assisted-work]]
- [[automation-and-substitution]]
