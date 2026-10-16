---
title: "Taking the Whys Seriously: Limitations of Counterfactual Explanations in Justification and Recourse"
authors: Cerrato, Mattia; Sahlgren, Otto; Heilmann, Xenia
year: 2026
url: https://arxiv.org/abs/2608.30956
doi: 10.48550/arXiv.2608.30956
source_type: paper
publication_status: preprint
retrieved: 2026-10-16
human_reviewed: false
drive_file_id: 1auhHQV0WH1Iv1TsOQjONiEz1nBuWZWiI
file_hash: e496dbd576b13339fa2bf5b0233c1eb1dcbaf98d8b0627abde006e7128f30d79
---

# Taking the Whys Seriously: Limitations of Counterfactual Explanations in Justification and Recourse

**Citation.** Cerrato, M., Sahlgren, O. & Heilmann, X. (2026). *Taking the Whys Seriously: Limitations of Counterfactual Explanations in Justification and Recourse.* arXiv:2608.30956.

**Summary.** This preprint argues that counterfactual explanations (CEs) used to justify algorithmic decisions or offer recourse can obscure contestable organizational choices made earlier in the machine-learning pipeline. Across four experiments, it finds that upstream choices about measurement, business rules, model selection, and validation can change generated CEs as much as or more than a counterfactual generator's validity threshold, so CEs alone are insufficient for accountability-oriented explanation or recourse.

## Key claims
- Counterfactual explanations are model-dependent artifacts, so they cannot by themselves justify a decision or provide adequate recourse when upstream feature, label, business-rule, validation, and performance-metric choices are contestable.
- Using American Community Survey microdata in a simulated screening setting, the authors find that upstream interventions often perturb generated counterfactuals more than changing the generator's validity threshold across DiCE-kdtree and NICE retrieval-based methods.
- Changing the model-success metric produced the largest sensitivity effects; changing from accuracy to recall, ROC-AUC, NDCG@100, or F1 exceeded the threshold baseline, whereas changing cross-validation folds had effects comparable to that baseline.
- Across three of four interventions, DiCE-kdtree's mean categorical-value agreement fell from 0.39 across threshold changes to 0.18–0.26 under upstream interventions; NICE showed the same direction, falling from 1.00 to 0.61–0.87.

## Evidence & limitations
- The experiments use seven ACS demographic, occupational, and educational variables, approximate latent applicant fit with earnings, and evaluate intervention effects over ten seeds; this is a simulated screening context rather than evidence from an operating hiring system.
- The analysis focuses on two retrieval-based CE methods and one set-level agreement/sensitivity framework, so its empirical magnitude estimates may not generalize to other explanation methods or recourse metrics such as actionability and diversity.
- This is an arXiv v1 preprint, not a peer-reviewed publication; the Drive PDF exactly matches the public arXiv PDF by SHA-256, and the extracted text contained no model-directed prompt-injection language.

## Feeds
- [[algorithmic-assessment]]
- [[responsible-ai-deployment]]
- [[human-ai-agent-interaction-design]]
