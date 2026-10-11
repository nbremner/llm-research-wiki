---
title: "Leveraging Expert Consistency to Improve Algorithmic Decision Support"
authors: De-Arteaga, Jeanselme, Dubrawski, Chouldechova
year: 2025
url: https://doi.org/10.1287/mnsc.2022.01576
doi: 10.1287/mnsc.2022.01576
source_type: paper
publication_status: peer-reviewed
retrieved: 2026-10-11
human_reviewed: false
drive_file_id: 1PmsROvVorVDSsY_PrF-bXhLWt4TmzJWJ
file_hash: 40cb67357dd8d7a1b2f1c8ababa2e9786a19a7503c68ec7fa886daf32efc6b48
---

# Leveraging Expert Consistency to Improve Algorithmic Decision Support

**Citation.** De-Arteaga, M., Jeanselme, V., Dubrawski, A., & Chouldechova, A. (2025). Leveraging Expert Consistency to Improve Algorithmic Decision Support. *Management Science, 71*(12), 10465–10485. https://doi.org/10.1287/mnsc.2022.01576

**Summary.** De-Arteaga and colleagues address the construct gap that arises when a high-stakes decision objective is represented only by imperfect outcome proxies and historical expert decisions. They estimate instance-level consistency among experts even when each case was assessed by one expert, then use consistency to combine expert decisions with observed outcomes as training labels. Simulations and child-maltreatment hotline data indicate that this label-amalgamation approach can better approximate the intended construct than models trained on either proxy alone.

## Key claims
- Historical expert decisions should not be treated as uniformly authoritative training labels: agreement across experts is proposed as an instance-level signal for when their decisions may add information beyond an observed outcome proxy.
- The method estimates expert consistency from single-expert-per-case records using prediction confidence and influence functions, including a variant designed for non-random expert-to-case assignment.
- In simulations of imperfect, heterogeneous, and partially shared expert errors, the proposed label-amalgamation model achieved higher AUC for the unobserved construct than the observed-outcome, expert-decision, deferral, noisy-label, ensemble, and weak-supervision baselines reported by the authors.
- In child-welfare hotline data, models trained to predict out-of-home placement can miss other risk-relevant outcomes; the proposed approach improved precision on substantiation and service outcomes while retaining comparable performance on the placement target.
- The approach depends on the substantive assumption that expert consistency signals correctness; deterministic, widely shared bias can therefore be learned rather than corrected.

## Evidence & limitations
- The evaluation combines semi-synthetic emergency-department triage simulations with observational administrative data from Allegheny County child-maltreatment hotline screening; the paper does not provide a randomized deployment evaluation of downstream organizational or welfare effects.
- Expert consistency is an indirect estimate, not observed inter-rater agreement on the same case, and its validity depends on model calibration, available covariates, assignment patterns, and the relationship between agreement and correctness in the domain.
- The 2024 Drive PDF is arXiv v3; Crossref identifies the canonical peer-reviewed 2025 *Management Science* article and DOI, so the record uses the published provenance while preserving the ingested Drive binary hash.

## Feeds
- [[algorithmic-assessment]]
- [[construct-validity]]
- [[expert-authority-in-ai-decisions]]
