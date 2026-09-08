# Reviewing a weekly synthesis pull request

The owner's checklist for the one approval gate in the automated pipeline. Every Monday at ~09:00 PT
NicholasJunior turns the queue in `wiki/sources/unreviewed/` into one pull request on a
`synthesis/YYYY-MM-DD` branch and posts the link to #research-digest. **Merging the PR is the
approval.** Nothing in it is canon until you merge; nothing needs approving anywhere else.
(Design: `docs/wiki-redesign-plan.md` §4 and §7; mechanics: `skills/research-wiki-ingest/SKILL.md`
§ Weekly synthesis batch.)

## Before you start (1 minute)

1. Open the PR link from the digest. Read the PR body: per topic it lists sources integrated, claims
   added, contradictions surfaced, deferrals, the lint status and the bot's own "my read". Treat it
   as the *intent*; the diff is the truth. Review the diff, never only the summary.
2. Open the **Files changed** tab. The only file classes that belong in a batch are:
   - `wiki/topics/*.md` (the synthesis);
   - at most one edit each to `wiki/topic-map.md`, `wiki/watchlist.md`, `wiki/open-questions.md`,
     `wiki/research-gaps.md`;
   - source records **renamed** from `wiki/sources/unreviewed/` to `wiki/sources/` with
     `human_reviewed: false → true` and their `## Feeds` adjusted.
   Anything else (skills, scripts, docs, a deleted topic, an unpromoted edit to a source record) means
   the batch violated its rules: do not merge; tell the local Claude.

## Reviewing each topic page (2–3 minutes per page)

For every changed `wiki/topics/*.md`, work hunk by hunk:

- **Cited and specific.** New prose names the source as `[[slug]]` and says what the evidence shows
  (design, sample, effect, limits), not that a paper "relates to" the topic.
- **Your framing.** It reads as the wiki's synthesis, not the paper's abstract restated.
- **Nothing lost.** Red lines are the ones to scrutinize: a deleted or rewritten claim is acceptable
  only as a Connections-bullet merge, a fix, or a contradiction being surfaced. Silent removal of an
  existing claim is a reject.
- **Contradictions surfaced, never resolved.** If the new evidence disagrees with what the page
  already said, the disagreement belongs under "Contradictions & open questions" as prose.
- **Right page?** Would this have been better as a new topic, a split of a bloated page, or a
  `watchlist.md` deferral? The accretion lint flags pages that keep absorbing sources.
- **Frontmatter.** `updated:` equals the batch date on every synthesized page and only those.
- **Spot-check against the record.** Click the promoted source record in the same PR and confirm the
  claim used matches its "Key claims".

## Reviewing the deferrals (1 minute)

The PR body and digest list sources the batch chose not to integrate, with reasons. Those records
stay in `unreviewed/` and are re-judged next week. If you think one should have been integrated, or
should be dropped from the wiki altogether, say so (see "What your feedback does" below).

## Deciding

- **Everything acceptable →** click *Merge pull request* (a merge commit or squash are both fine;
  the VPS syncs either), confirm, and delete the branch if offered (the bot prunes it anyway).
- **Acceptable with small wording changes →** edit the file directly on GitHub (pencil icon on the
  file in *Files changed*, commit to the branch), then merge. The branch is yours to edit; the bot
  never rebases or rewrites it. Your edits *are* the review.
- **Substantive problems →** do not merge. Leave comments on the hunks and tell the local Claude in
  chat what to decline or change. The bot does not read PR comments; the loop closes through the
  local Claude (below). The stale PR is closed and regenerated from current `main` by the next
  Monday run (or on request), with your rulings applied.
- **Never** resolve a merge conflict by hand or use *Update branch* to pull `main` into the branch.
  Conflicts should not occur (the daily drain only adds files under `unreviewed/`); if GitHub shows
  one, tell the local Claude and the batch is regenerated.

## What your feedback does

Every decline or substantive correction is written by the local Claude into
`skills/research-wiki-ingest/references/declined-synthesis-log.md` (source, proposed move, your
ruling) so the batch never re-proposes it, and — when the ruling generalizes — into a
`references/*-topic-assessment.md`, the library the batch consults when grouping. "Integrate X into
Y", "split Y", "drop X from the wiki" and "this belongs on the watchlist" are all rulings the next
batch must honour. Dropping a source runs the rejection path: record deleted, artifact moved to Drive
`_triage/discarded`, triage manifest amended.

## Rejecting a paper outright

Any time, from Discord: reply in #research-digest (or message NicholasJunior) with
`reject <source slug or Drive file id> — <reason>`. NicholasJunior deletes the unreviewed record,
moves the artifact to Drive `_triage/discarded`, amends the scan manifest so triage never re-proposes
it, logs your reason in the declined-synthesis log, closes an open synthesis PR that contained it (the
batch regenerates next Monday), and replies with what it did. A paper that is already human-reviewed
is not deleted this way — removing it means editing the topic pages that cite it, which comes back to
you as a small PR.

## After you merge

Nothing to do. The next daily drain (09:30 PT) pulls `main`, lints it, and moves the promoted
artifacts from Drive `_sources/_unreviewed` to `_sources`; the public site rebuilds within six hours
and the pages leave the "unreviewed" folder. If no PR is merged or commented within seven days, next
Monday's run closes it and opens a fresh one — so feedback on an unmerged PR must reach the local
Claude within the week.

## The trial (plan §7)

Batches 1–4 are reviewed in full, hunk by hunk. The local Claude records per batch: sources, pages
touched, your edits and rejections. After four consecutive batches with no substantive corrections,
only the two mechanical edit classes — `watchlist.md` deferral entries and Connections-bullet merges —
may start landing on `main` without a PR, listed for information in the digest. Prose synthesis stays
PR-gated indefinitely.
