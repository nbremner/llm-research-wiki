---
title: "It’s How You Ask: Gender-Associated Linguistic Bias in LLMs"
authors: Van Koevering, Katherine; Field, Anjalie
year: 2026
url: https://arxiv.org/abs/2608.13328
doi: 10.48550/arXiv.2608.13328
source_type: paper
publication_status: peer-reviewed
retrieved: 2026-09-22
human_reviewed: false
drive_file_id: 1yceO_cTsSb_v81z5MhbHLyl8g4zelWhm
file_hash: d23aeabf6216c4986f5dc080ae97e13696a46ef478bcd1a0f54c242e0e94ca1b
---

# It’s How You Ask: Gender-Associated Linguistic Bias in LLMs

**Citation.** Van Koevering, K., & Field, A. (2026). *It’s How You Ask: Gender-Associated Linguistic Bias in LLMs.* COLM 2026. https://arxiv.org/abs/2608.13328

**Summary.** This conference paper tests whether gender-associated linguistic features in professional-writing prompts affect outputs from four LLMs. In controlled paired prompt manipulations, prompts with hedges, tag questions, collective reference, and expressive adjectives associated with women elicited less sophisticated, less formal, and generally more readable responses than matched prompts using men-associated features. The authors argue that implicit linguistic register is more behaviorally consequential than sign-off names and that mitigations focused only on explicit demographic markers will miss this source of disparate impact.

## Key claims
- Across emails, job applications, and resignation letters, women-associated linguistic-feature (WALF) prompts elicited responses with lower lexical sophistication, lower grade level, and less formality than men-associated-feature (MALF) prompts; effects were strongest for emails and job applications.
- The formality difference was significant across all three document categories (email and job application p < 0.001; resignation letter p = 0.033), while politeness density and clout did not differ significantly by prompt condition.
- Prompt-level complexity and style explained limited response-level variance (maximum reported R² = 0.341), and feature carry-over only partially mediated a small subset of outcomes, so simple style mirroring did not account for the observed differences.
- In a sign-off experiment, gender-associated names had virtually no significant effect on output metrics, whereas linguistic-register effects replicated; Llama-3.2-3B-Instruct encoded linguistic-feature condition strongly by layer 5 (peak probe accuracy 0.988) and name gender more weakly (0.717).

## Evidence & limitations
- The study rewrote 427 WildChat workplace prompts into paired WALF and MALF variants, evaluated four models, and used paired tests, regression/mediation analyses, human validation of task preservation and realism, and mechanistic analyses on Llama-3.2-3B-Instruct.
- The operationalization draws on binary gender-associated English-language patterns and does not capture the full range of gender expression or linguistic variation; the authors also note that artificial prompt modifications may retain residual artifacts and that mechanistic results from one model may not generalize.
- The Drive PDF is arXiv version 1, publicly verified against the arXiv record; the paper identifies itself as a COLM 2026 conference paper, but no publisher DOI was found in the source or exact-title Crossref lookup.

## Feeds
- [[responsible-ai-deployment]]
- *Proposed new topic:* linguistic-equity-in-ai-mediated-work — LLMs can produce systematically different workplace communication quality from socially patterned linguistic register, a distinct user-facing fairness mechanism not naturally covered by the current map.
