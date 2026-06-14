# Agentic ingestion and review loops — 2026-06

Session learning from Nicholas's research-wiki roadmap update.

## Pattern

Nicholas wants the public research wiki to become more agentic without losing staged governance.

Two bounded automation loops were added to the roadmap:

1. **Inbox-to-Review artifact loop**
   - Regularly detects papers in Drive `_inbox` / Notion Inbox.
   - Extracts citation metadata, abstract, and full text where possible.
   - Creates an actual Notion Review or `summary-review` artifact directly.
   - Does **not** require the older dry-run approval step before artifact creation.
   - Links the artifact back to the Inbox item / Drive file.
   - Proposes candidate Concepts, Concept updates, Research Map updates, and follow-up source searches.
   - Keeps graduation into canonical Concepts approval-gated.

2. **Candidate-source discovery loop**
   - Reads active Research Map questions and known gaps.
   - Searches public scholarly/web sources for candidate papers.
   - Deduplicates against existing Sources, Inbox, Drive filenames, DOIs, and known titles.
   - Stages promising candidates in Inbox with metadata and rationale.
   - Downloads or attaches PDFs only when access/licensing is appropriate.
   - Tags why each source matters: foundational, recent empirical evidence, methods, construct bridge, contradiction, or weak signal.
   - Logs the discovery pass and surfaces high-priority candidates.

## Governance boundary

The key distinction is **artifact creation vs. canonical graduation**:

- Agent-created Review/Summary artifacts are allowed once the workflow is implemented and bounded.
- Canonical Concept mutation remains approval-gated.
- Research Map and Concept updates should be proposed inside the artifact unless Nicholas explicitly approves applying them.
- Scheduled runs need caps, dedupe, logs, confidence/status flags, and failure handling.
- Weak extraction, ambiguous scope, or thin evidence should produce a low-confidence artifact or triage note, not silent discard.

## Implementation posture

Start manual, then schedule:

1. Define Review/Summary statuses and approval gates.
2. Add Inbox metadata for discovery provenance, dedupe key, processing state, and rationale.
3. Build dry-report/read-only modes for both loops.
4. Run conservative manual passes and inspect artifacts/logs.
5. Only then create low-volume Hermes scheduled jobs.

Candidate cadence from roadmap:

- weekly candidate-source discovery;
- weekly or twice-weekly Inbox-to-Review processing;
- optional monthly gap-map refresh for Research Map questions.

## Pitfall

Do not let “agentic” mean “automated backlog generator.” The point is bounded throughput: queue discipline, dedupe, volume caps, logs, and explicit approval gates.