# Reviews Database Setup Notes — 2026-06

Session-specific implementation detail for Nicholas's public research wiki review artifacts.

## Purpose

The Reviews database was created as the staged synthesis layer between raw/public Sources, canonical Concepts, and the Research Map / Overview. It is not a generic notes database. It is where durable research questions become review artifacts that can later propose Concept and Research Map updates.

## Notion IDs

- Reviews database: `09776168-d11e-4868-ab34-6ebe3b900cee`
- Reviews data source: `eb454605-2dea-4b8b-a173-407be60184ed`

## Property shape

Core properties established for the first version:

- Review type: `literature-review`, `gap-map`, `construct-bridge`, `implementation-review`, `summary-review`
- Status
- Canonical status
- Evidence status
- Confidence
- Review question
- Researcher intent
- Scope
- Evidence guideline
- Source coverage summary
- Key claims
- Candidate Concept updates
- Candidate Research Map updates
- Practical implications
- Suggested sources/concepts
- Reviewed Sources relation
- Related Concepts relation
- Started
- Last reviewed
- Needs source search

## Design decisions to preserve

- Every review should capture researcher intent, not just agent synthesis.
- Reviews should use existing Sources and Concepts before searching outward.
- Reviews can include Drive `_inbox` PDFs as candidate evidence, but those remain non-canonical until ingested through the Sources workflow.
- Web/arXiv search can identify candidate missing sources, but those sources need ingestion before being treated as canonical public-wiki evidence.
- Every substantive review should explicitly address:
  - I-O constructs
  - AI workforce mechanisms
  - level of analysis
  - measurement implications
  - practical implications
  - evidence gaps / weakly supported claims
- Evidence thresholds are guidelines, not rigid rule sets. Match the evidence standard to the question: narrative orientation can tolerate fewer sources; quantitative relationship claims, comparative claims, and method recommendations require broader and stronger evidence.
- Reviews propose Concept updates and Research Map updates; they do not directly mutate canonical Concepts unless Nicholas explicitly approves that follow-on step.

## Verification pattern used at setup

The database setup was verified by creating an archived validation row and querying it back. Future structural changes should use the same low-risk pattern: create a clearly marked validation Review, query it through the Reviews data source, then archive or leave it archived.
