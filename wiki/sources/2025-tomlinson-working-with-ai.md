---
title: "Working with AI: Measuring the Applicability of Generative AI to Occupations"
authors: Tomlinson, Jaffe, Wang, Counts, Suri
year: 2025
url: https://arxiv.org/abs/2507.07935
doi: 10.48550/arXiv.2507.07935
source_type: paper
publication_status: preprint
retrieved: 2026-06-24
drive_file_id: 1ZjI1uoqueiDRrkKrnFfB2FviNo0-h8Sc
file_hash: 41050083ba4450baa1800df0912e0f77c63b49db0f786d095daca4e04c6f2673
---

# Working with AI: Measuring the Applicability of Generative AI to Occupations

**Citation.** Tomlinson, K., Jaffe, S., Wang, W., Counts, S., & Suri, S. (2025). *Working with AI: Measuring the applicability of generative AI to occupations*. arXiv. https://arxiv.org/abs/2507.07935

**Summary.** Tomlinson et al. analyze 200,000 anonymized Microsoft Bing Copilot conversations and map both user goals and AI actions to O*NET intermediate work activities. They distinguish AI assisting a worker's goal from AI performing an action inside the conversation, then combine observed use, completion, feedback, and scope into occupation-level AI applicability scores. The source is useful because it moves beyond exposure forecasts toward observed conversational use while still warning that applicability does not equal productivity gain, wage change, or labor substitution.

## Key claims
- The most common and successful Copilot work activities are information-work activities: learning, communicating, teaching/explaining, writing, and related creation, processing, and communication of information.
- User goals and AI actions are often different work activities: the paper reports that the two sets of intermediate work activities are disjoint in 40% of conversations, and in 96% of conversations there are more activities unique to one side than shared.
- Copilot performs an average of two work activities in service of each work activity matched to a user goal, which means a single AI-assisted episode can contain a different AI-side task structure than the human-side goal.
- The authors compute AI applicability by aggregating activity-level measures through O*NET to occupations, using activity frequency, task completion, user feedback, and a six-point scope rating of how much of the work activity the AI appears able to assist or perform.
- High-scoring occupational groups are dominated by information work: media and communication workers score 0.38, sales representatives in services score 0.35, information and record clerks score 0.33, mathematical science occupations score 0.32, and tour and travel guides score 0.32.
- The authors explicitly caution against reading high AI-action applicability as job automation or high user-goal applicability as wage-raising augmentation, because employment and wage effects depend on business decisions, task recomposition, and downstream organizational design.
- The paper argues that current AI applicability is broad because most occupations contain some information-work component, but it is still limited by modality mismatch, data analysis performance gaps, platform coverage, O*NET's U.S.-centric and sometimes stale occupational taxonomy, and the missing connective tissue between listed tasks.

## Evidence & limitations
- Evidence comes from 200,000 anonymized Bing Copilot conversations, O*NET 29.0 work-activity mappings, LLM-based classifiers, explicit user feedback, and task-completion validation; the study was approved by Microsoft IRB #11028 and releases results at https://github.com/microsoft/working-with-ai.
- The dataset observes one mainstream LLM product and one slice of the AI market, not all generative AI systems, organization-specific copilots, embedded workflow automations, or occupation-specific tools.
- The authors do not observe each user's actual occupation, so they infer occupational relevance by mapping observed work activities to O*NET rather than directly measuring job-level AI use in workplaces.
- Completion and scope measure AI utility toward an intermediate work activity, not realized productivity, quality, learning, accountability, wages, or labor demand for people doing that work.
- O*NET decomposition is useful for cross-occupation aggregation but may miss how tasks are actually connected inside jobs, how work has already changed, and how non-U.S. or unpaid work should be represented.

## Feeds
- [[ai-workforce-impact-measurement]]
- [[task-level-ai-adoption]]
- [[human-ai-task-taxonomy]]
- [[automation-and-substitution]]
- [[job-analysis]]
