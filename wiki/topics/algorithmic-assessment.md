---
title: Algorithmic assessment
status: active
updated: 2026-06-21
---

# Algorithmic assessment

Algorithmic assessment is not just selection with newer software. It is a measurement chain: a signal is collected, transformed by a model, interpreted as a construct, and used in an employment decision. The useful question is not whether “AI hiring tools” are good or bad in general. It is what construct is being inferred, from what signal, by what model, for what decision, under what evidence and governance standard.

[[2016-chamorro-premuzic-new-talent-signals]] gives the foundational I-O caution: new talent signals may be technologically novel, but they still need theory, construct clarity, validity evidence, and comparison against established methods. [[2023-landers-machine-learning-psychometric-assessment]] sharpens that caution empirically. Machine learning does not automatically improve conventional psychometric selection batteries, and its clearest value may appear when assessment design changes, not when regression is simply swapped out for a more complex algorithm. [[2023-nyc-automated-employment-decision-tools-faq]] adds the governance layer by defining covered AEDTs, bias audits, independent auditors, impact ratios, and notice obligations.

The topic sits at the intersection of [[construct-validity]], [[evidence-based-management]], and [[automation-and-substitution]]. Construct validity asks whether the tool is measuring a coherent job-relevant attribute rather than a convenient proxy. Evidence-based management asks whether the validity, utility, audit, or compliance claim is supported by evidence matched to the decision. Automation and substitution asks whether the tool supports human judgment, substantially assists it, or replaces discretionary decision-making in screening, ranking, or selection.

[[2022-strah-diversity-issues-job-analysis]] adds a deeper foundation problem for algorithmic assessment.
Even before signals are modeled or audited, the job analysis that defines the criterion domain may miss
underrepresented workers' tasks, constraints, voice, or successful performance strategies. That matters
for algorithmic tools because a model can be technically validated against a criterion that already encodes
an incomplete or majority-normed account of the job.

[[2022-dellacqua-falling-asleep-at-wheel]] adds the human-oversight problem inside algorithmic hiring.
In a field experiment with professional recruiters, algorithmic recommendations improved accuracy overall,
but higher-stated AI quality made recruiters more likely to follow recommendations and lower-quality AI
induced more effort and time spent reviewing resumes. For assessment, this means the validity of a
human-AI selection system depends not only on model accuracy, but on how recommendations reshape human
attention, discretion, and willingness to override.

## Connections
- Relates to [[construct-validity]] because algorithmic assessment only matters if the inferred construct is coherent, job-relevant, and defensible in a nomological network.
- Relates to [[evidence-based-management]] because prediction, validity, adverse impact, compliance, and utility are different evidence claims and should not be collapsed into “the tool works.”
- Relates to [[automation-and-substitution]] because AEDTs can support, substantially assist, or replace discretionary judgment, including at the screening stage before any final employment decision.
- Relates lightly to [[human-ai-collaboration]] when algorithmic outputs are used as decision support; the NYC AEDT language is a reminder that some “support” tools cross into substantial assistance or replacement.
- Relates to [[automation-complacency]] because assessment systems can preserve formal human discretion while still making workers inattentive followers of model advice.
- Relates to [[job-analysis]] because algorithmic assessment inherits its target definition from upstream work analysis; bad job analysis can make later model validation look cleaner than it is.

## Contradictions & open questions
- The cluster separates prediction from explanation. [[2016-chamorro-premuzic-new-talent-signals]] argues that understanding constructs matters, while some big-data assessment practices prioritize predictive relationships without enough theory.
- [[2023-landers-machine-learning-psychometric-assessment]] suggests machine learning's value may be limited in conventional scale-composite batteries but stronger in item-level or novel-data settings. That creates a design question: is the organization improving assessment, or merely adding model complexity?
- [[2023-nyc-automated-employment-decision-tools-faq]] makes bias audits and notices central to compliance, but policy compliance does not by itself establish construct validity, job relatedness, or decision utility.
- “Decision support” is not a safe category by default. A simplified score, classification, or ranking can substantially assist or replace discretion even when a human remains nominally accountable for the final decision.
- [[2022-dellacqua-falling-asleep-at-wheel]] complicates the idea that better hiring AI straightforwardly improves human decisions. Higher-quality recommendations can increase reliance and reduce effort, so the assessment unit is the coupled human-AI decision process, not the model alone.
- Bias audits often focus on output disparities, but [[2022-strah-diversity-issues-job-analysis]] suggests another layer: whether the criterion and job requirements being predicted already excluded some groups' real work contributions.
