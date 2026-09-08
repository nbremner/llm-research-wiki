# Declined synthesis log

The batch's rejection memory (`docs/wiki-redesign-plan.md` §6). Every owner rejection or substantive correction of a weekly synthesis batch gets a dated entry here: the source, the move the batch proposed, and the owner's ruling. **The batch must read this before grouping and must never re-propose a declined move.** Where a ruling generalizes beyond one source, the local Claude also distills it into (or updates) a `references/*-topic-assessment.md`; that library is the accumulated output of the approval loop.

Entries are added by the local Claude from the owner's PR review comments, never by the batch itself.

Format:

```
## YYYY-MM-DD — PR #N
- **Source:** [[source-slug]] — **Proposed:** <Create|Update|Split|Defer> → <topic-slug> — **Ruling:** <owner's words, condensed> — **Generalizes to:** <topic-assessment file or "no">
```

## 2026-09-08 — PR #1 (closed and regenerated)
- **Source:** [[2026-gao-making-agent-mediated-contributions-governable]] — **Proposed:** Update → agentic-organization-design, human-ai-agent-interaction-design; new topic proposed: agent-mediated-contribution-governance — **Ruling:** owner dropped the paper from the wiki entirely (by Drive file id; no reason recorded). Record deleted, artifact → `_triage/discarded`, manifest amended. Never re-ingest or re-propose. — **Generalizes to:** no
- **Source:** [[2026-westover-ai-washing-phantom-productivity]] — **Proposed:** Update → automation-and-substitution, responsible-ai-deployment — **Ruling:** owner dropped the paper from the wiki entirely (by Drive file id; no reason recorded). Record deleted, artifact → `_triage/discarded`, manifest amended. Never re-ingest or re-propose. — **Generalizes to:** no
