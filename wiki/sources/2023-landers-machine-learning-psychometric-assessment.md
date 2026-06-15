---
title: "A simulation of the impacts of machine learning to combine psychometric employee selection system predictors on performance prediction, adverse impact, and number of dropped predictors"
authors: Landers, Auer, Dunk, Langer, Tran
year: 2023
url: https://doi.org/10.1111/peps.12587
doi: 10.1111/peps.12587
source_type: paper
retrieved: 2026-06-15
drive_file_id: 1qwgJZCauB8EJuMYigS2eYvbx8GMZS3OA
file_hash: 7e85a41d4fba48142b877242715b7b6da8a63b6e02e0bc3f52042dc40d422034
---

# A simulation of the impacts of machine learning to combine psychometric employee selection system predictors on performance prediction, adverse impact, and number of dropped predictors

**Citation.** Landers, R. N., Auer, E. M., Dunk, L., Langer, M., & Tran, K. N. (2023). *Personnel Psychology.* https://doi.org/10.1111/peps.12587

**Summary.** Landers and colleagues simulate how modern machine learning methods compare with ordinary least squares regression when combining psychometrically validated employee-selection predictors. The paper is a useful corrective to broad claims that machine learning automatically improves selection: in conventional scale-composite batteries, the clearest advantage was often the ability to drop predictors rather than large gains in prediction. The authors argue that machine learning's stronger promise is likely in less conventional assessment designs, such as item-level inference or novel data formats, rather than simply replacing regression in established psychometric systems.

## Key claims
- The simulation compared modern machine learning with OLS regression on out-of-sample operational validity, adverse impact, and dropped predictor counts in employee-selection systems.
- The study simulated scores from 1.2 billion validation-study participants and evaluated 31,752 combinations of selection-system design and scoring decisions; the broader simulated dataset described outcomes for 38,063,368 selection systems.
- For psychometric scale composites, machine learning improved performance prediction over OLS mainly when the sample-size-to-scale-count ratio was less than approximately 3; algorithm choice, predictor count, and selection ratio also mattered.
- The most consistent practical gain from machine learning was dropping predictors without sacrificing much predictive accuracy, not uniformly improving criterion prediction.
- In item-level scoring scenarios, several machine-learning algorithms, especially elastic net and random forest, showed more consistent predictive advantages over traditional regression.
- The authors suggest future selection research should focus on design contexts where machine learning is structurally useful: individual items making multiple trait inferences, text, image, audio, video, and behavioral-trace data.

## Evidence & limitations
- Evidence comes from simulation rather than observed hiring deployments; it is strong for testing design/scoring contingencies but does not directly estimate real-world organizational adoption, applicant reactions, legal risk, or implementation quality.
- The simulation is explicitly anchored in psychometrically validated employee-selection systems, so it should not be generalized to all algorithmic hiring tools or all people-analytics prediction tasks.
- Adverse impact is modeled inside the simulation design; fairness conclusions still depend on assumptions about predictor distributions, subgroup differences, selection ratios, and operational definitions.
- The paper is especially valuable for separating algorithm choice from measurement design: better algorithms do not rescue weak constructs or poorly chosen signals.

## Feeds
- [[algorithmic-assessment]]
- [[construct-validity]]
- [[evidence-based-management]]
- [[automation-and-substitution]]
