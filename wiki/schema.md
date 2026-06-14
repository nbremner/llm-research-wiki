# Wiki conventions (schema)

The contract for this wiki. Read first. Lean by design — see `docs/wiki-redesign-plan.md` for the why.

This is plain cross-linked markdown in git, visualized/edited in **Obsidian** (wikilinks, backlinks,
graph). The vault is the `wiki/` directory. There is no database, no RAG, no vector store — the wiki is
small enough to read in full context (Karpathy regime).

## The one hard rule

**Public-only sources.** Nothing confidential, work-derived, or client-internal enters the wiki —
not as a source, not as framing, not as an example. If a claim can't be traced to a public source,
it doesn't become canonical.

## The shape

```
wiki/
  overview.md      # the single living orientation page
  schema.md        # this file
  topics/          # cross-linked synthesis — the compounding core
  sources/         # one record per public source (paper, report, article)
```

- **topics/** is the product. Each topic page is synthesis *in the owner's own framing*, surfacing
  connections and contradictions across sources in prose.
- **sources/** is the evidence layer beneath the syntheses: one file per source.
- **overview.md** is the orientation layer: what topics exist, open questions, thin areas.

## Linking

- Link with Obsidian wikilinks: `[[topic-slug]]`, `[[source-slug]]`. Obsidian resolves by filename
  (minus `.md`), so the link target is the filename.
- Filenames are kebab-case slugs: `human-ai-collaboration.md`, `2026-noy-zhang-chatgpt-productivity.md`.
- Link liberally. A `[[link]]` to a page that doesn't exist yet is fine — it marks a page worth writing.
- Source filename convention: `YYYY-firstauthor-shorttitle` (year first, so sources sort chronologically).

## Topic page template

```markdown
---
title: Human–AI collaboration
status: stub            # stub | active
updated: 2026-06-14
---

# Human–AI collaboration

[Synthesis in prose. State what the evidence says, in your own framing. Cite sources inline
with wikilinks: "[[2026-noy-zhang-chatgpt-productivity]] found a 40% time reduction…".]

## Connections
- Relates to [[work-redesign]] via task reallocation.

## Contradictions & open questions
- [[source-a]] and [[source-b]] disagree on whether augmentation raises or lowers skill demand —
  surfaced, not resolved. Disagreement carries meaning.
```

## Source page template

```markdown
---
title: ChatGPT and the productivity of professional writers
authors: Noy, Zhang
year: 2023
url: https://www.science.org/doi/10.1126/science.adh2586
source_type: paper      # paper | report | article | book | dataset | policy | other
retrieved: 2026-06-14
---

# ChatGPT and the productivity of professional writers

**Citation.** Noy, S. & Zhang, W. (2023). *Science.*

**Summary.** [2–4 sentences, neutral, public.]

## Key claims
- [Claim 1 — each should be defensible from the source.]
- [Claim 2]

## Feeds
- [[human-ai-collaboration]]
- [[productivity-measurement]]
```

Frontmatter is minimal on purpose. No confidence/contested/boundary fields — contradictions live in
topic prose, not in metadata.

## The three workflows

1. **Ingest.** A public source → write a `sources/` record → integrate its claims into the relevant
   `topics/` pages (update prose, strengthen links, flag contradictions in prose).
2. **Query.** Answer from topic/source pages. File durable answers *back into* pages — don't let good
   synthesis evaporate into chat.
3. **Lint.** Periodic health check: orphan pages, broken wikilinks, claims with no source, stale topics.

## Governance

Minimal. The owner approves before a synthesis becomes canonical. Contradictions are **surfaced in
prose, never auto-resolved.** Git history is the log; there is no separate log/review/inbox database.
