---
title: "AI Contextual Measurement for Recovering Individual and Group-Level Effects: Validation Against Survey Measures and an Occupational Application"
authors: Jiang, Wang, Wu
year: 2026
url: https://arxiv.org/abs/2609.02821
doi: 10.48550/arXiv.2609.02821
source_type: paper
publication_status: preprint
retrieved: 2026-10-21
human_reviewed: false
drive_file_id: 1D-ljWkTV9lxioL_3apRlnYa9Ak2LK_DD
file_hash: 6fc8b4bc4f7b54d576f7bc0a747649e90d37a4706db07645ff354263ba5d168b
---

# AI Contextual Measurement for Recovering Individual and Group-Level Effects: Validation Against Survey Measures and an Occupational Application

**Citation.** Jiang, W., Wang, X., & Wu, Y. (2026). *AI Contextual Measurement for Recovering Individual and Group-Level Effects: Validation Against Survey Measures and an Occupational Application.* arXiv. https://arxiv.org/abs/2609.02821

**Summary.** Jiang, Wang, and Wu introduce AICOME, a framework for evaluating whether respondent-level AI-derived measures can recover both within-group and between-group associations in contextual models rather than merely predict survey responses. Using 2022 China Family Panel Studies data, they compare AI-derived and observed measures of computer use, foreign-language use, weekly hours, and management responsibilities. The results support limited use of rich existing data to recover selected unmeasured constructs, while showing deterioration when information is sparse or several related constructs are simultaneously missing.

## Key claims
- A respondent-level AI measure can be decomposed into an occupation mean and an individual deviation, enabling contextual models to estimate both between-occupation and within-occupation associations that occupation-level AI scores cannot identify.
- For weekly hours, the observed CFPS individual effect on job satisfaction was -0.135; rich-prompt and survey-prompt AI measures estimated -0.136 and -0.129, respectively, with negative contextual contrasts in all three specifications.
- Under simultaneous missingness of four related job dimensions, the contextual-model R² gain was 0.0269 for observed CFPS measures versus 0.0142 for rich-prompt AI and 0.0167 for survey-prompt AI, with no contextual effect significant in the joint model.

## Evidence & limitations
- The preprint evaluates two prompting strategies against observed 2022 CFPS occupational and respondent-level measures, using job satisfaction as the outcome and occupations as the grouping structure.
- Direct validation is limited to four observed dimensions; the later autonomy, people-things, creative-routine, and technology applications lack direct CFPS benchmarks and are not proof that the AI-derived latent measures recover true constructs.
- The authors caution that AI-derived measures are not substitutes for direct survey measurement, depend on rich available features, and require human diagnosis because prompts can over-weight misleading proxy information.

## Feeds
- [[ai-workforce-impact-measurement]]
- [[construct-validity]]
