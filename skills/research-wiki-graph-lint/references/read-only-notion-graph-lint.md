# Read-only Notion graph-lint implementation notes

Session-derived pattern for turning the graph-lint checklist into durable instrumentation.

## Durable pattern

Build the lint workflow as a read-only script that:

1. Reads canonical governance pages first: Schema, Agent Operating Guide, Research Map / Overview.
2. Queries live Notion data sources read-only: Sources, Concepts, Reviews, Inbox.
3. Emits both human and machine artifacts:
   - `REPORT.md` for LC review;
   - `graph_lint.json` for later automation or regression checks.
4. Writes artifacts under a runtime directory such as `/root/research-wiki-runs/graph-lint-YYYYMMDDTHHMMSSZ/`, not into the portable repo.
5. Treats findings as a review queue, not apply-mode instructions.

## Checks implemented in the first script pass

- Concepts with no linked Sources.
- Sources with no linked Concepts.
- Sources lacking DOI / canonical URL / provenance signal.
- Duplicate Sources by DOI, canonical URL, or title.
- Duplicate Concepts by title.
- Reviews with no Reviewed Sources.
- Concept-bearing Reviews with no Related Concepts.
- Reviews proposing Concept work without Candidate Concept Update Bundle signal.
- Stale open Inbox items.
- Weak-evidence Concepts lacking obvious confidence / contested signals.

## Important pitfall

Ignore archived / closed records when generating active lint work. In the first smoke run, an archived setup row looked like a High issue because it had no Reviewed Sources. That is a false positive. Add an `is_closed_or_archived` helper that checks Notion `archived` / `in_trash`, status/state fields, and title/status terms such as `archived`, `completed`, `done`, `exclude`, `processed`, or `promoted`.

## Test pattern

Use synthetic Notion-like page dictionaries in unit tests. Cover both positive findings and false-positive suppression:

- orphan Concept and orphan Source produce High findings;
- connected Source with DOI/provenance produces no finding;
- duplicate DOI/title produces Medium duplicate findings;
- Reviews without sources and stale open Inbox items are flagged;
- archived Reviews are ignored.

## Governance rule

Do not let lint output directly mutate canonical Concepts. Any Concept-changing recommendation should become a Candidate Concept Update Bundle or an LC review queue item first.
