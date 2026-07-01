---
title: "The Shift to Agentic AI: Evidence from Codex"
authors: Johnston, Holtz, Richmond, Ong, Tambe, Chatterji
year: 2026
url: https://cdn.openai.com/pdf/5d1e1489-21c0-43e4-9d42-f87efdbf0082/the-shift-to-agentic-ai-evidence-from-codex.pdf
doi: null
source_type: paper
publication_status: working-paper
retrieved: 2026-07-01
drive_file_id: 1O4J9EYdy9LsKA8moC-RH_e31tnkOHq2h
file_hash: 3dd8fafc88fe6f08ef9f9910251fc012f25e024237921d133480828fb2bd4ca2
---

# The Shift to Agentic AI: Evidence from Codex

**Citation.** Johnston, D., Holtz, D., Richmond, A. M., Ong, C., Tambe, P., & Chatterji, A. (2026). *The shift to agentic AI: Evidence from Codex*. OpenAI working paper. https://cdn.openai.com/pdf/5d1e1489-21c0-43e4-9d42-f87efdbf0082/the-shift-to-agentic-ai-evidence-from-codex.pdf

**Summary.** Johnston and colleagues analyze aggregated, privacy-protecting usage data from OpenAI Codex across individual users, organizational users, and OpenAI workers to describe the transition from conversational AI assistance to agentic AI delegation. They find rapid but uneven diffusion, with usage deepest inside OpenAI and broader organizational adoption still concentrated around technical work. The paper's core contribution is measurement of agentic work organization: task complexity, runtime, concurrency, reusable skills/plugins, and output volume show users beginning to manage delegated AI work rather than only exchange messages with a chatbot.

## Key claims
- Codex weekly active users increased more than fivefold between January 1 and June 1, 2026, with especially rapid growth outside the initial software-developer audience.
- As of June 11, 2026, Codex accounted for 99.8% of output tokens generated across Codex and ChatGPT among OpenAI workers, 63.3% among organizational users, and 16.5% among individual users, even though fewer than 1% of active individual users had used Codex in the preceding 28 days.
- Organizational adoption remained uneven: 17.3% of organizational users used Codex in the preceding 28 days, and among organizational users with job-title data, engineers averaged 26.8% of output tokens on Codex while legal roles averaged 1.9%.
- Codex use is best interpreted as delegated production rather than consultation because users ask it to debug, refactor, validate changes, configure applications, draft documents, analyze data, and produce or modify artifacts.
- Among sampled individual users, the share with at least one prompt estimated to require more than eight hours of experienced-human work rose from 2.1% to 25.6%, and the first turn of a thread was more than twice as likely as the fourth turn to exceed one hour of estimated human work.
- Parallel delegation was much more common inside OpenAI: only 10.7% of OpenAI users used a sole workflow at any one time in the week before June 11, 2026, and 28.6% managed five or more concurrent agents at some point, while most individual and organizational users did not use concurrent turns.
- Skill and plugin use grew from 5.4% of active Codex users on March 1, 2026 to 26.6% on June 11, 2026; in the June 11 window, 25.7% of active individual users, 30.4% of active organizational users, and 96.2% of active OpenAI users invoked at least one skill.
- The median OpenAI employee had Codex turns running for 2.5 hours on June 11, 2026, while the 99th percentile had about 71 hours of cumulative agent-turn runtime in an average day because overlapping turns are summed.
- Between November 1, 2025 and June 11, 2026, median OpenAI output tokens rose at least tenfold in every job function, including a 13-fold increase for legal roles and more than a 50-fold increase for researchers.

## Evidence & limitations
- Evidence comes from platform usage logs, automated classifiers, token measures, runtime/concurrency traces, and job-title/function metadata; the paper deliberately avoids researchers reading underlying user messages.
- OpenAI worker evidence is a frontier case with low adoption frictions, high model familiarity, strong organizational support, and workflows close to the product, so it should not be treated as representative of typical organizations.
- Task complexity is estimated by a model-based classifier on a 0.1% sample of opted-in individual accounts, so the complexity figures are useful directional evidence but not direct observation of counterfactual human work time.
- Output-token growth measures AI-mediated production volume, not validated productivity, quality, business value, or worker well-being.
- The public OpenAI-hosted PDF has the same extracted text, metadata, page count, and title/author content as the Drive PDF, but its binary SHA-256 differs from the Drive file; the Drive hash is recorded in frontmatter.
- The PDF text extracted cleanly during ingest; no model-directed prompt-injection language was found.

## Feeds
- [[agentic-delegation]]
- [[task-level-ai-adoption]]
- [[work-redesign]]
- [[ai-workforce-impact-measurement]]
