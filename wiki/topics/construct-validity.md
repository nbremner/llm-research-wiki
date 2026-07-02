---
title: Construct validity
status: active
updated: 2026-06-22
---

# Construct validity

Construct validity is the discipline of making sure a named thing in the wiki is actually a thing: conceptually bounded, measured coherently, and located in a defensible nomological network.

[[2014-briner-employee-engagement-evidence-based]] is a useful negative case. Briner argues that employee engagement became practically salient despite weak agreement about what it meant, measures that overlapped heavily with job satisfaction and organizational commitment, and claims that often borrowed evidence from adjacent constructs. The failure mode is construct sprawl: a label becomes useful rhetorically while becoming less useful scientifically.

For AI-mediated work, construct validity is not academic housekeeping. It determines whether measures like “AI adoption,” “AI readiness,” “human-AI collaboration,” or “trust in AI” can support decisions about work redesign, intervention, and evaluation.

The same discipline applies to [[algorithmic-assessment]]. [[2016-chamorro-premuzic-new-talent-signals]] warns that new data sources and technology-mediated talent signals often move faster than theory and validation, especially when vendors emphasize novelty, speed, or proprietary prediction. [[2023-landers-machine-learning-psychometric-assessment]] shows why method choice and measurement design have to be separated: machine learning does not automatically improve prediction from validated scale composites, and the more interesting item-level or novel-signal uses are exactly where construct interpretation becomes harder. [[2023-nyc-automated-employment-decision-tools-faq]] adds a regulatory vocabulary for AEDTs and bias audits, but those categories do not replace the I-O question of what construct is being inferred and whether it is job-relevant.

[[2026-tomei-what-jobs-can-ai-learn]] is a useful positive case of construct sharpening. Instead of treating "AI exposure" as generic overlap between occupational task descriptions and current LLM capabilities, the paper defines a narrower construct: feasibility of improving task performance through RL-based post-training. The distinction matters because occupations can rank high on LLM exposure but low on RL feasibility, or the reverse.

[[2022-strah-diversity-issues-job-analysis]] moves construct validity upstream into job analysis itself. If the performance domain is built from majority-group norms, biased archival language, unequal SME voice, or averaged ratings that wash out subgroup differences, then later validation work may be anchored to an incomplete construct. The issue is not only whether a predictor measures the intended KSAO; it is whether the job and criterion domain were inclusively specified in the first place.

[[2008-icf-competency-modeling-job-analysis]] adds a label-boundary problem. “Competency” can mean job-level KSAO, observable behavior, personality-like attribute, motive, cultural value, or organization-level capability. That flexibility is part of why competency modeling travels well in HR practice, but it also creates construct-validity risk when competency labels are used for selection, assessment, or performance decisions without enough task evidence, rater reliability, and job-relevance logic.

[[2009-sanchez-levine-competency-modeling-job-analysis]] gives a partial defense of loose competency language: if the goal is strategic signaling and behavior influence, a competency label may be intentionally broader than a clean latent trait. Construct-validity trouble begins when that strategic signal is treated as if it were already a bounded psychological attribute or job-specific KSAO.

[[2023-zhang-human-capital-resources]] gives a more direct measurement case in human capital resources. In their review, only 23.6% of HCR measures focused solely on HCR, while many were partially or fully contaminated by antecedents, HR practices, attitudes, expenses, or outcomes. The important construct-validity lesson is that a measure can become more predictive by absorbing adjacent performance-relevant content while becoming less valid as evidence about the focal construct.

[[1997-goh-benchmarking-learning-capability]] gives a useful positive-but-limited measurement case for a broad organizational capability. The OLS bounds learning capability around five conditions — purpose, leadership, experimentation, knowledge transfer, and teamwork — and reports reliability and preliminary validity evidence, while explicitly not measuring performance or learning outcomes directly. That boundary discipline matters for AI-era constructs such as readiness, adoption quality, and organizational learning from AI experimentation.

[[2026-wang-agent-development-real-world-work]] extends the construct-validity problem to AI-agent benchmarks. A benchmark score can be valid evidence for performance on a sampled task distribution while invalid evidence for "real-world work capability" if the task distribution overrepresents programming-heavy, easily specified, easily verified work and underrepresents management, legal, interpersonal, or long-horizon work.

[[2015-neubert-assessment-21st-century-skills]] gives a positive-but-unfinished construct-validity case. CPS and ColPS are more bounded than loose future-skills labels because they specify active knowledge acquisition, knowledge application, dynamic problem features, and collaborative interaction; the unresolved validation question is whether simulated microworld performance supports the same inferences organizations want to make about real jobs and redesigned work.

[[2025-teyssier-roberge-21st-century-skills-overlap]] turns the broader 21st-century-skills field into a direct construct-validity caution. Across 40 identified skills, 446 definitions, and 457 assessment measures, the authors find enough semantic and psychometric overlap to make label proliferation itself the measurement problem: different skill names can create an appearance of precision while the definitions and instruments are still tapping shared higher-order competencies.

## Connections

- Relates to [[employee-engagement]] as a cautionary case of loose construct boundaries.
- Relates to [[evidence-based-management]] because poor construct validity weakens the evidence chain between an intervention, a measured mediator, and an organizational outcome.
- Relates to [[ai-adoption]] because adoption should not become a catch-all label for attitudes, usage, capability, managerial search, and workflow redesign at once.
- Relates to [[automation-and-substitution]] because exposure indices only guide decisions if the measured construct matches the mechanism of automation being claimed.
- Relates to [[algorithmic-assessment]] because algorithmic hiring tools are only defensible when their signals, model outputs, and employment decisions are tied back to coherent job-relevant constructs.
- Relates to [[job-analysis]] because construct validity begins before measurement: the construct has to be defined from work as actually performed and experienced, including perspectives that are easy to miss.
- Relates to [[competency-modeling]] because competency labels need boundaries before they can support assessment, training, succession, or strategic HR decisions, and 21st-century-skills labels show how competency language can proliferate faster than discriminant-validity evidence when organizations want evergreen skills for future work.
- Relates to [[human-capital-resource-measurement]] because HCR shows how collective capability measures can be deficient, contaminated, or predictively useful for the wrong construct.
- Relates to [[complex-collaborative-problem-solving]] because CPS and ColPS show how a broad capability label can become more construct-valid when problem features, process data, and assessment tasks are explicitly modeled.
- Relates to [[ai-agent-benchmark-validity]] because benchmark validity is construct validity applied to agent evaluation: what exactly is being measured, and what claims does that measure license?
- Relates to [[organizational-learning-capability]] because learning capability must be separated from adjacent constructs such as satisfaction, culture, formalization, innovation, and performance before it can support AI transformation claims.


## Contradictions & open questions

- Practical constructs often become useful before they become clean. The question is when pragmatic usefulness justifies action, and when loose measurement starts producing false certainty.
- The wiki needs positive examples of strong construct validation in AI workforce transformation, not only cautionary cases from older I-O constructs.
- [[2026-tomei-what-jobs-can-ai-learn]] improves the exposure construct but still relies on LLM-based annotations. The next validation question is whether RL feasibility predicts observed deployment and labor-market change better than existing exposure measures.
- [[2022-strah-diversity-issues-job-analysis]] complicates the usual “job-relatedness” safeguard: a procedure can be tied to a documented job analysis and still be unfairly narrow if the job analysis failed to capture diverse ways of performing the work.
- [[2008-icf-competency-modeling-job-analysis]] shows that competency modeling can improve strategic fit while weakening construct precision if broad organizational competencies are treated as if they were job-specific KSAOs.
- [[2009-sanchez-levine-competency-modeling-job-analysis]] suggests a two-standard problem: the construct can be rhetorically useful for strategy communication while still inadequate for measurement-heavy HR decisions unless translated into observable, job-family-specific behavioral indicators.
- [[2023-zhang-human-capital-resources]] adds a prediction-versus-explanation problem: contaminated HCR measures can correlate more strongly with performance, but that strength may come from mixing HCR with other constructs rather than from cleaner measurement of human capital resources.
- [[2026-wang-agent-development-real-world-work]] sharpens the validation target but still relies on benchmark-task descriptions and LLM-assisted taxonomy mapping. The next question is whether benchmark coverage and autonomy metrics predict real deployment outcomes better than raw agent scores.
- [[2015-neubert-assessment-21st-century-skills]] improves on generic 21st-century-skills rhetoric by narrowing the construct, but it raises the familiar simulation-validity question: when does performance in a controlled microworld become valid evidence about workplace problem solving rather than only evidence about the microworld?
- [[2025-teyssier-roberge-21st-century-skills-overlap]] strengthens the jangle-fallacy concern but leaves the positive taxonomy problem unfinished: if many skills are overlapping manifestations of broader competencies, the field still needs evidence about where to draw the higher-order boundaries and which behavior-based assessments support selection, training, or workforce-planning inferences.
- [[1997-goh-benchmarking-learning-capability]] shows the value and limit of bounding a broad organizational construct: the OLS may diagnose learning-enabling conditions, but the next validation question is whether those scores predict actual knowledge transfer, behavior change, and AI-related work redesign over time.
