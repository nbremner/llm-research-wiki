---
title: "Agentic coding and persistent returns to expertise"
authors: Hitzig, Massenkoff, Lyubich, Heller, McCrory
year: 2026
url: https://www.anthropic.com/research/claude-code-expertise
doi: null
source_type: report
publication_status: other
retrieved: 2026-07-03
drive_file_id: 1IUWzGxgxhfEJOvWI7C6CxQ5tqCmM0qPw
file_hash: 644d0e3fe30c350d10217f4db0051f4e36bc4cceaa3e5d27cd3efdcee2e444f0
---

# Agentic coding and persistent returns to expertise

**Citation.** Hitzig, Z., Massenkoff, M., Lyubich, E., Heller, R., & McCrory, P. (2026). *Agentic coding and persistent returns to expertise.* Anthropic.

**Summary.** Anthropic analyzes roughly 400,000 Claude Code sessions from about 235,000 users between October 2025 and April 2026 to describe what interactive agentic coding looks like in practice. The report finds a stable division of labor in which users make most planning decisions while Claude makes most execution decisions, and it argues that domain expertise—not formal coding occupation alone—predicts more effective use. It also shows that Claude Code work shifted away from debugging toward operating software, data analysis, and writing, while estimated task value rose over the observation window.

## Key claims
- In a typical Claude Code session, the user makes about 70% of planning decisions while Claude makes about 80% of execution decisions, suggesting that agentic coding often allocates goal-setting and acceptance criteria to the human while delegating implementation choices to the agent.
- About 56% of sessions involve writing, fixing, testing, or orchestrating code; operating software accounts for 17%, planning or exploring for 14%, and analysis or prose for 13%, with 48% of sessions primarily modifying existing code and 17% exploring codebases.
- More expert users elicit substantially more agent work per prompt: novice sessions average about 5 Claude actions and 600 words of output per prompt, while expert sessions average about 12 actions and 3,200 words of output, with positive expertise effects persisting after controls for work mode, task value, month, occupation, and model family.
- Between October 2025 and April 2026, the share of sessions fixing broken code fell from 33% to 19%, operating software grew from 14% to 21%, writing and data analysis roughly doubled from about 10% to 20%, and estimated average session value rose by 27%.
- Verified success rises with task-specific expertise: novice-rated sessions reach verified success 15% of the time and at least partial success 77% of the time, while intermediate-or-higher sessions reach verified success 28–33% of the time and at least partial success 91–92% of the time.
- Among sessions that produce code, software-related occupations reach verified success about 34% of the time and other professions about 29% of the time; the report interprets the small occupation gap as evidence that coding agents reduce the importance of formal coding background while preserving returns to domain understanding.

## Evidence & limitations
- Evidence comes from privacy-preserving analysis of Claude Code transcripts and telemetry from October 2025 through April 2026, with classifiers used to label work mode, decision attribution, task-specific expertise, occupation, success, and failure signals.
- The report does not observe downstream real-world outcomes such as whether produced code was adopted, maintained, or economically valuable; verified success is transcript- and telemetry-based, using signals such as tests, commits, pull requests, and user affirmation.
- Occupation and expertise are inferred from session content, so findings depend on classifier validity and on what users reveal in the transcript; the authors report checks against telemetry and public datasets but the measures remain model-mediated.
- The Drive PDF exactly matches the public Anthropic PDF at `https://cdn.sanity.io/files/4zrzovbb/website/433472e34b60db1a52ebf0b8c6600f057b6908c5.pdf` by SHA-256; the public landing page also links to a separate appendix PDF that does not match the ingested report file.

## Feeds
- [[domain-expertise-in-agentic-work]]
- [[agentic-delegation]]
- [[human-ai-task-allocation]]
- [[ai-workforce-impact-measurement]]
- [[work-redesign]]
