---
title: "Speak for Me: Giving LLMs the Situational Awareness to Participate in a Meeting"
authors: Khan, Muneeb; Kirstein, Frederic; Ruas, Terry; Gipp, Bela
year: 2026
url: https://arxiv.org/abs/2609.03923
doi: 10.48550/arXiv.2609.03923
source_type: paper
publication_status: preprint
retrieved: 2026-10-25
human_reviewed: false
drive_file_id: 1h_l5iwG91c8AETgJOI40evR9On20wzs4
file_hash: 378de5d0fd3095e922f63aed5bfe8a0debf821d596284362a2ef9ab6b43cf54d
---

# Speak for Me: Giving LLMs the Situational Awareness to Participate in a Meeting

**Citation.** Khan, M., Kirstein, F., Ruas, T., & Gipp, B. (2026). *Speak for Me: Giving LLMs the Situational Awareness to Participate in a Meeting.* arXiv preprint arXiv:2609.03923. https://doi.org/10.48550/arXiv.2609.03923

**Summary.** Khan et al. introduce CAPA, a modular LLM-agent architecture for representing an absent participant in a live multi-party meeting. Rather than generating directly from a transcript, CAPA maintains an explicit state of topic, decisions, open questions, participant stances, prior coverage, and floor control to decide whether and what to say. In causal-replay evaluation on the AMI meeting corpus, the system substantially reduced missed speaking opportunities relative to raw-context and Reflexion-style baselines, while shifting residual failures toward traceable selection errors.

## Key claims
- In multi-party meeting delegation, prompt-only LLM delegates missed 51.4% of the absent participant's valid speaking opportunities; CAPA reduced the reported silence rate to 2.5% on the 137-meeting AMI evaluation.
- CAPA separates floor-taking from utterance realization and uses a perceive-act-recalibrate loop to update a structured meeting state after each observed turn and post-action assessment.
- Against the transcript-only baseline, CAPA raised credited recovery from 26.1% to 52.2% and Decision F1 from 38.1 to 63.0 while reporting a 0.6% hallucination rate.
- The paper's episode-level protocol evaluates whether, when, and what a delegate contributes around participant-owned idea units; its schema-constrained LLM judges reached Cohen's kappa of 0.71 against human annotations.

## Evidence & limitations
- The experiment uses 137 scenario meetings from the AMI Meeting Corpus, with matched 20-meeting subsets for ablations and robustness checks; it evaluates replayed meeting interactions rather than deployed organizational use.
- The authors report that the primary evaluation is limited to the AMI scenario portion, that alternative meeting corpora require protocol adaptation, and that performance depends materially on the underlying language model.
- This is an arXiv preprint; arXiv metadata reports acceptance at EMNLP 2026 Main, but the retrieved artifact is the preprint version.

## Feeds
- [[agentic-delegation]]
- [[human-ai-agent-interaction-design]]
