# Wiki Plan — Ingest Automation (current) + Redesign Record (archived)

Status: **ACTIVE build plan — ingest automation, owner-approved 2026-09-07.** Phases 0–3 shipped
2026-09-07/08 (see §11 Build log); Phase 4 (attended trial) in progress.
The original 2026-06 markdown-in-git redesign this file used to describe is **built and archived**
in the appendix at the bottom; everything above the appendix is the current plan.

Read first: `OPERATING_MODEL.md` (architecture, roles, cron), `wiki/schema.md` (the live contract),
`AGENTS.md` (hard boundary + sync-maintenance rule), `docs/research-scrape-plan.md` (the scan front
end this plan sits downstream of), `skills/research-wiki-ingest/SKILL.md` (the only path that
writes wiki pages).

## 1. Problem and decision record (2026-09-07)

**Problem.** The scan pipeline promotes up to 10 papers/day into Drive `_triage/wiki`, but nothing
consumes that folder — it drains only via manual, attended, one-at-a-time ingest. An unbounded
producer/consumer mismatch, in tension with `OPERATING_MODEL.md`'s "no loop becomes a backlog sink."

**Decision.** Automate along the trust split that already exists (source records auto-commit;
topic synthesis is owner-gated):

1. **Daily scheduled source drain** — NJ auto-ingests source records only (new files; conflict-free).
2. **Weekly consolidated synthesis batch** — one approval unit, grouped by target topic page, each
   page touched once, **at most one batch open at a time**. Approval surface: a GitHub PR of real
   diffs; the owner merging is the approval.

**Alternatives rejected, with evidence** (full review in the 2026-09-07 session):

- *Queue of per-source topic diffs*: measured against this repo's own history (103 synthesize
  commits), independent queued diffs collide on the same topic file 46% of the time at queue depth
  3 and 92% at depth 5; `wiki/watchlist.md` alone is touched in 47% of recent syntheses. Batching
  per page makes collisions impossible instead of managed.
- *Full auto-ingest with periodic AI review*: the lint evidence-staleness check only produces
  signal because a human gate creates lag between `retrieved:` and `updated:` — automate synthesis
  and it reads zero forever; the monthly contradiction-pair check floods its 15-pair cap; nothing
  automated checks topic fixation/padding — the exact failure the gate protects against (the 21
  `references/*-topic-assessment.md` files are crystallized owner corrections). Rejection base
  rate to date ~3% (3 of ~107 sources), but the rejects were judgment calls.
- Prior art inside the repo: the retired batch-ingest skill
  (`git show 69051f6^:skills/research-wiki-batch-ingest/SKILL.md`) already validated
  cluster-by-target-topic, "pay the human gate once per cluster," and "partial batch is the
  designed resting state." It was retired for parsimony after the backlog cleared, not because it
  failed. This plan resurrects that design at the synthesis stage only.
- External patterns adopted: living-systematic-review batching + materiality triggers (Cochrane),
  regenerate-don't-rebase bot proposals (Renovate/conda-forge), review-real-diffs-not-summaries
  (Wikipedia AI-agent policy), trial-batch authorization before widening autonomy (Wikidata bots),
  statement-level sampled fidelity audits (FutureHouse WikiCrow rubric).

**Design principles** (carry through every phase):

- The LLM writes *judgments*; deterministic code owns state, caps, and side effects (the
  scan/triage split, extended downstream).
- No new skill, no new database. Both new behaviors are modes of `research-wiki-ingest`
  (no allowlist/mount/drop-in churn). The pending-synthesis queue is *computed* (orphan-source
  lint findings + the Drive `_triage/wiki` folder), never stored. Proposals live on an ephemeral
  git branch. This is what keeps the plan on the right side of the June-2026 "no inbox database /
  no candidate-update bundles" cut (see appendix).
- Approved *intent* is durable (PR body); diffs are disposable and regenerated on staleness.
- Every scheduled loop capped, deduped, logged. Topic synthesis stays owner-gated regardless of
  cadence.

## 2. Phase 0 — pipeline defect fixes (do first; valuable regardless)

All in `scripts/research-wiki-tools/`, with tests in `tests/`.

**(a) Stranded ambiguous triage records.** `scan_triage_apply.py`'s `--latest` always selects the
newest manifest (a fresh daily scan always has unresolved records), so yesterday's `ambiguous`
items are never re-judged and "Needs your call" resets every morning. Fix: replace latest-manifest
selection with an *open set* — load all manifests within a `--carryover-days` window (default 7)
that contain unresolved records, merge their unresolved entries into one judging set, and let a
dispositions file reference records across manifests (stamp each record back onto its own
manifest). Digest gains a "Carried over (age)" section, and a "stranded" warning when an
unresolved record is about to age out of the window — nothing may disappear silently. Keep the
dup-id fail-loud behavior. (This also resolves the surfaced⇒marked-seen-before-disposition loss
path: seen-marking stays, recovery now comes from the manifest carryover.)

**(b) Ingest→manifest writeback.** When the owner rejects a source at ingest time, the PDF moves
to Drive `discarded` but the manifest still says `disposition: wiki`, and the applier raises on
any attempt to re-dispose. Fix: add an explicit amend verb to `scan_triage_apply.py`
(e.g. `--amend --id <id> --to discarded --reason "..."`) that is allowed to re-dispose a disposed
record, appends the change to that record's `proposal_history`, and moves nothing in Drive by
default (ingest already moved the PDF). Then add one step to the ingest SKILL's rejection path:
run the amend after the unwind.

**(c) `WIKI_CONCEPTS` drift** (renamed `WIKI_CONCEPT_ENRICHMENT` on shipping)**.** `scan_config.py`
has 36 concept keys vs 54 topic files — the 18 newest topics are invisible to pre-ranking (a self-reinforcing fixation loop). Fix: derive the
concept key set from `wiki/topics/*.md` (slug + title) at scan time — the scan already warm-starts
from `wiki/` — and demote the hand-tuned map in `scan_config.py` to keyword *enrichment* only.
Scan output warns when a topic has no enrichment entry. Test: every topic slug is represented in
the derived concept set.

**(d) Topic-accretion lint.** `graph_lint.py` gains a check making the ingest skill's Split
decision a signal instead of a vibe: Medium "Topic accretion" at ≥35 cited sources or ≥3,500
words; Low at ≥25 / ≥2,500 (constants at top of file). Report-only, like everything in lint.
(`work-redesign.md` at 41 sources / ~4,100 words should trip it on day one — that is correct.)

Acceptance: `python -m pytest tests/ -q` green with new tests covering carryover selection, amend,
concept coverage, and the accretion thresholds; one manual `--execute` triage run on the VPS shows
a carried-over item resolving.

## 3. Phase 1 — daily source drain (unattended source-record ingest)

Add a **"Scheduled source drain" mode** to `skills/research-wiki-ingest/SKILL.md`:

- Runs the existing ingest steps 1–8 only (contract read → locate in `_triage/wiki` → preflight
  dedup/boundary → download/extract/hash + prompt-injection scan → naming → Drive refile → source
  record → auto-commit), for up to **5 sources per run, oldest first**. **No step 9**: no topic
  edits, no map-page edits, no `updated:` bumps anywhere.
- The source record's `## Feeds` section is written as the drafter's **proposed** target topics
  (best judgment from the topic map). This is deliberate: it is the grouping input for the weekly
  batch, which may revise it. A source page whose Feeds targets don't link back yet is the normal
  pending state.
- Lint gate: `graph_lint.py --fail-on High` (source-only state). **Orphan-source Medium findings
  are the pending-synthesis queue** — expected state, not defects.
- Push to `origin/main`; post one summary line per drained source to #research-digest.
- Deployment: one new hermes cron job on NJ's main profile, daily **09:30 PT** (after the 08:30
  triage), delivering to #research-digest, skill `research-wiki-ingest` (keeps its per-skill model
  override). Standard cron failure alerting applies. No mount/allowlist changes.

The owner's control point over *what enters* is unchanged: the triage rubric + daily digest
upstream, and the existing rejection path (now with the Phase-0 amend) downstream.

## 4. Phase 2 — weekly synthesis batch (the approval unit)

Add a **"Weekly synthesis batch" mode** to `skills/research-wiki-ingest/SKILL.md`:

1. **Precondition — one open batch at a time.** Check for an existing `synthesis/*` branch on
   origin / open PR. Open and <7 days old → skip this week's run, say so in the digest. Open and
   ≥7 days → **regenerate**: close the PR, delete the branch, redraft from current HEAD including
   newly accumulated orphans. Never rebase or merge a stale draft — the human never resolves a
   bot conflict.
2. **Collect** orphan sources (from `graph_lint.py --json`), cap **12 oldest per batch**; the
   rest roll over. Read the contract + all map pages fresh (the existing re-read rule).
3. **Group by target topic page** using the proposed `## Feeds` plus the topic-openness
   assessment (Create / Update / Split / Defer per source-topic pair), consulting
   `references/*-topic-assessment.md` **and the declined-synthesis log (§6)**. Apply the
   living-review materiality test per pair: if a source wouldn't change the page's claims,
   prefer a Connections bullet or a `watchlist.md` deferral over prose.
4. **Draft once per file**: each affected topic page edited exactly once for the whole batch;
   each map page (`topic-map.md`, `watchlist.md`, `open-questions.md`, `research-gaps.md`)
   edited at most once; `updated:` bumped only on genuinely synthesized pages.
5. Lint the working tree: `graph_lint.py --fail-on Medium`, with `--allow-check` for the
   expected-state checks (orphan sources rolling over to the next batch, topic accretion,
   evidence-stale) — otherwise any backlog fails every batch (found in Phase 0; see §11).
6. **Branch + PR**: branch `synthesis/YYYY-MM-DD`, commit *topic synthesis only* (source records
   are already on main; the branch is file-disjoint from the daily drain, so it essentially
   cannot conflict with main while open), message
   `wiki: synthesize batch YYYY-MM-DD (N sources, M topics)`. Push; open a PR whose body carries
   the durable intent: per topic — sources integrated, claims added, contradictions surfaced,
   defers/watchlist entries — plus lint status and a short "my read" on commit-readiness.
   (New topic pages appear natively in the PR diff — this retires the `git diff` untracked-file
   gotcha in the Discord flow.)
7. **Announce** in #research-digest: PR link + one line per topic.
8. **Approval = owner merges the PR** (merge or squash; ff-only sync handles both). Owner
   comments / requests changes → NJ regenerates (step 1 semantics). Post-merge, the next
   scheduled run pulls, verifies lint clean on main, and deletes the branch.

**Owner setup step (required before PR mode):** provision `gh` (or a GitHub API token) on the VPS
for NJ — a fine-grained PAT scoped to `nbremner/llm-research-wiki` with contents:write +
pull-requests:write, stored per Hermes secrets convention, **never in this repo**.

**Fallback until then (and permanent attended path):** the existing Discord flow, batched — leave
the consolidated working-tree diff uncommitted, post per-file fenced diffs (new topic pages via
`git diff --no-index -- /dev/null <path>`), owner replies "Approve," NJ commits to main. Known
fragility (an uncommitted draft dies with the session — already observed once) is why PR mode is
primary. The attended single-source ingest mode stays intact and canonical for owner-initiated
one-offs.

Deployment: one new hermes cron job, weekly **Monday 09:00 PT**, #research-digest, skill
`research-wiki-ingest`.

Expected load at current velocity: ~8–12 sources across ~10–15 pages per batch ≈ one 20–30 minute
owner review session.

## 5. Phase 3 — quality-loop upgrades

- **Monthly claim-fidelity audit** (extends the existing monthly semantic-lint cron prompt, still
  report-only): sample ~10 claims added by the past month's synthesis commits (`git log --since`),
  pull each cited source's text from Drive canonical storage, grade each claim
  **cited+supported / cited+unsupported / uncited / reasoning error** (the WikiCrow rubric), and
  report the counts + trend in the digest. The owner spot-checks at least 2 graded claims per
  audit — LLM reviewers are measurably biased toward LLM-written text, so the human stays in the
  audit sample.
- **Contradiction-gate monitoring**: the semantic lint digest must warn when change-gated pairs
  exceed the 15-pair cap by a wide margin (`dropped_gated` ≫ 0), so coverage degradation is
  visible instead of silent in a JSON field.
- **Staleness signal preserved by design**: the drain never bumps `updated:`; only weekly batches
  do. The deliberate lag keeps the evidence-staleness lint check meaningful. Do not "fix" the lag.

## 6. Rejection memory (new, small)

Create `skills/research-wiki-ingest/references/declined-synthesis-log.md`, mirroring the triage
skill's declined-rubric-proposals pattern: every owner rejection or substantive correction of a
batch gets a dated entry (source, proposed move, owner's ruling). Batch drafting (step 3 above)
must consult it so a declined move is never re-proposed. Where a correction generalizes, also
distill it into (or update) a `*-topic-assessment.md` — that library is the accumulated output of
the approval loop and must keep growing under automation.

## 7. Phase 4 — trial protocol and the autonomy dial

- **Batches 1–4 are attended**: the owner reviews every hunk of the PR (real diffs, no
  summaries-only review). Track per batch: sources, pages touched, owner edits/rejections.
  The owner's step-by-step checklist is `docs/synthesis-pr-review.md`.
- **Loosening criterion**: after 4 consecutive clean batches (no substantive corrections), the
  batch mode may auto-commit the two mechanical edit classes — `watchlist.md` deferral entries and
  Connections-bullet merges — directly to main, listed FYI in the weekly digest. **Prose topic
  synthesis stays PR-gated indefinitely** (`OPERATING_MODEL.md`: "regardless of cadence").
- **Rollback is trivial**: disable the two cron jobs; the skill's attended one-at-a-time mode is
  untouched and everything reverts to today's behavior. No migrations, no state to unwind.

## 8. Contract and doc updates (same sessions as the code they describe)

- `wiki/schema.md`: map pages "maintained on every ingest" → "maintained on every synthesis
  (batch or single)"; add two lines: scheduled drain may commit source records ahead of synthesis,
  and orphan-source lint findings constitute the pending-synthesis queue (expected state).
- `OPERATING_MODEL.md`: split Ingest into drain + weekly batch in the loop description and cron
  table (drain daily 09:30 PT; batch weekly Mon 09:00 PT; fidelity audit inside the monthly
  lint); record the one-open-batch rule and PR-merge-as-approval under governance.
- `AGENTS.md`: one line noting `synthesis/*` branches are the sanctioned exception to
  "`origin/main` matches local `HEAD`" while a batch awaits review.
- `docs/research-scrape-plan.md`: pointer that the consumer side is now specified here.
- Per the sync-maintenance rule: every phase lands in this repo with tests green
  (`python -m pytest tests/ -q`), committed and pushed in the same session; SKILL.md edits reach
  NJ through the existing clone sync + bind mounts.

## 9. Caps (single reference table)

| Loop | Cadence | Cap | Writes |
| --- | --- | --- | --- |
| Source drain | daily 09:30 PT | ≤5 sources/run | `wiki/sources/` on main (auto) |
| Synthesis batch | weekly Mon 09:00 PT | ≤12 sources/batch; **1 open batch**; regenerate at 7 days stale | `synthesis/*` branch → PR → owner merge |
| Triage carryover | daily (in applier) | 7-day window; stranded warning on age-out | manifests + digest |
| Fidelity audit | monthly (in lint cron) | ~10 claims sampled | report only |

## 10. Don't break

- The **public-only boundary** and the owner gate on topic synthesis — this plan changes the
  *shape* of the gate (per-batch PR instead of per-source Discord), never removes it.
- The **`updated:` discipline** and the staleness lag it feeds (see §5).
- The **VPS sync + fail-closed mounts**: no skill renames in this plan, so no mount/drop-in/
  allowlist edits are needed. If that ever changes, follow `AGENTS.md` §renaming to the letter.
- The **guardrail tests**: no `backlog/` paths, no `.jsonl`/`.csv` state in git; queue state stays
  computed (lint) or external (Drive manifests, GitHub PRs).

## 11. Build log

- **2026-09-08 — stranded backfill applied + drain order.** Owner labelled all 67 stranded triage
  records (29 discard, 20 read-once, 18 wiki: 5 auto-moved, 13 to the acquisition ledger with copies
  the owner dropped into `_triage/wiki`), applied deterministically with the new `--max-auto-wiki`
  flag; one 66-day-old record surfaced separately and discarded on the owner's word. Open set now
  empty. `drain_queue.py`: the drain takes **owner-dropped files first** (no scan manifest uploaded
  them), then scan-promoted, oldest first within each — ingest skill 2.8.0.

- **2026-09-08 — needs-acquisition ledger (owner decision: step 1 only, no auto-retry, no
  abstract-only records).** 182 candidates had been judged `wiki` without an obtainable copy and
  each appeared in one digest and never again. `acquisition_queue.py` computes the queue from the
  manifests on every triage run (clear `wiki`, no artifact, not already in the wiki by DOI/URL/title,
  not since re-disposed), renders `_triage/needs-acquisition.md` + a state JSON in Drive, and the
  applier appends the `Acquisition backlog:` count line to every digest. Owner works it by dropping
  copies into `_triage/wiki` or rejecting from Discord.

- **2026-09-08 — cap + venue quality (owner decisions):** contradiction-pair cap 15/4 → **40/10**
  (`graph_lint.py` defaults) after the first Phase-3 coverage warning. **Venue-quality tier** added to
  the scan: `venue_tier` on every surfaced record (`watchlist` = the 55-journal roster; `indexed` = DOAJ
  or OpenAlex/CWTS core; `unlisted`; `unknown`; `n/a` for non-journal sources), signals captured free
  from OpenAlex at discovery and looked up once for surfaced journal articles that lack them; the triage
  digest tags unlisted/unknown venues and rubric 1.5.0 makes `unlisted` ambiguous by default. Prompted
  by three unlisted-venue articles merged in PR #2.

- **2026-09-08 — Phase 3 shipped:** `claim_audit.py` (deterministic sampler/recorder: prose lines
  added by synthesis commits in the last 35 days → month-keyed sample of ~10 → sheet with cited
  records; grades validated against the fixed WikiCrow set, counts + supported rate + trend from
  earlier audits, record stored in Drive `_triage/ledger`); graph-lint skill 2.4.0 adds the audit to
  the monthly cron with **one subagent per claim**, the owner spot-check rule, the `--pairs`
  coverage `warning` (emitted when `dropped_gated ≥ max_pairs`) quoted at the top of the digest, and
  the "staleness is a signal" note. First sample on real history: 177 candidate claims from 34
  commits. **First audit (manual run 2026-09-08, model gpt-6-astra):** 10 claims → 9 supported,
  1 reasoning error (a Connections bullet on `ai-enabled-job-crafting` overreaching Liu 2026),
  supported rate 90%, record `claim_audit-20260908T052536Z.json` in the Drive ledger; parent
  context peaked at 54k with grading delegated. The coverage warning fired for real: 300 of 315
  eligible pairs pass the 35-day change-gate and 289 are dropped beyond the 15-pair cap — the
  monthly contradiction check is a rotating sample; raising the cap is an owner decision (§9).

- **2026-09-08 — Phase 4 trial, batch 1.** First draft (PR #1: 6 sources → 9 topics, 4 deferred)
  drew two owner rejections *of sources* — an agents-engineering paper outside the behavioral-science
  lens and a hypothesis-only practitioner post — encoded as prospective rules (triage rubric 1.4.0,
  `agentic-organization-design-topic-assessment.md`, batch "Proposed rejections"). PR #1 closed,
  batch regenerated from `main`: **PR #2 (8 sources → 8 topics, 0 deferred) reviewed and merged
  clean** — trial tally: 1 clean batch of 4. Post-merge housekeeping ran as designed (prune, sync,
  lint, `drive_review_sync.py` promoted 8 artifacts). Observation: the two drafts judged materiality
  differently — sources deferred in PR #1 were integrated in PR #2 — so "Proposed rejections" and the
  evidence-threshold rule now carry that judgment instead of run-to-run variance.

- **2026-09-08 — Phase 2 shipped:** `research-wiki-ingest` 2.6.0 gains the **Weekly synthesis
  batch** mode: one-open-batch rule enforced by `synthesis_pr.py` (status/open/close/prune over the
  GitHub API; token from the git credential store, never in the repo); ≤12 oldest unreviewed sources,
  grouped by target topic, one subagent per affected page, each page drafted once, records promoted
  out of `unreviewed/` in the same branch, lint gate `--fail-on Medium` with the expected-state
  checks allowed, branch `synthesis/YYYY-MM-DD` → PR whose merge is the approval, digest with the PR
  link. `references/declined-synthesis-log.md` created (§6). *Deviation from §4 as written:* PR mode
  is primary from day one — the classic token already on the VPS can open PRs until it expires
  2026-09-16, and the Discord-diff fallback is unsafe on the VPS because the daily sync auto-commits
  any dirty working tree. Deployed as hermes cron "Weekly research-wiki synthesis batch", Mon 09:00 PT.

- **2026-09-07 — Phase 1b: human-review split + subagent drain + Drive mirror.** Owner asked for
  a user-visible line between human-reviewed and auto-written sources: every source record carries
  `human_reviewed: true|false`; auto-written records live in `wiki/sources/unreviewed/` and are
  promoted by the approving synthesis commit (`graph_lint`: Medium missing flag, High flag/folder
  mismatch, High topic-cites-unreviewed). The public site publishes `/sources/unreviewed/` with a
  "Not yet human-reviewed" callout and fails its build on any contradiction (site repo `34d4bf5`).
  Drive mirrors the split: `public-literature-wiki/_sources` and `_sources/_unreviewed` (owner-created;
  leading underscores deliberate), reconciled by `drive_review_sync.py`. The drain was rewritten
  around `delegate_task` — one isolated subagent per source, parent validates/commits — after the
  first run's transcript showed the single-context design reaching ~145k tokens and stalling on its
  final model call; the cron also gets a hard codex request timeout. Skill 2.5.0.

- **2026-09-07 — Phase 1 shipped:** `research-wiki-ingest` 2.4.0 gains the **Scheduled source
  drain** mode (§ Modes in the skill): ≤5 ingested / ≤10 examined per run, oldest first, steps 1–8
  only, Feeds over existing slugs with new-topic ideas as plain text, exact duplicates →
  `_triage/discarded`, judgment cases skipped and listed under "Needs your call", `--fail-on High`
  gate with orphan sources as the expected queue, push + verify, one digest. Full-text `.md` artifacts
  (60 of 124 queued; 8 of them bot-check stubs) handled explicitly. Deployed as hermes cron
  `2586a6d3525f` "Daily research-wiki source drain", 09:30 PT, model pinned to `gpt-5.6-terra`
  (`openai-codex`), delivering to #research-digest. Owner decisions recorded the same day: keep the
  plan's caps (drain the 124-file queue slowly); **foundational papers without AI content are wiki
  material** (rubric + `wiki/schema.md`); fine-grained PAT deferred (the classic token expires
  2026-09-16 — the drain's push fails after that until it is replaced). First drain run (manual
  trigger, attended): 5 of the 5 oldest queued artifacts ingested and pushed (`0526374..94944c6`),
  lint High-clean with 5 expected orphan-source findings. The agent's actual work took **5.4
  minutes** (30 model calls, 61 tool calls, context ~145k tokens by the end); the 31st model call —
  the final digest turn — was sent at 20:47:43 UTC and never returned, and no watchdog fired in the
  following 50 minutes, so the digest was never produced (LC then killed the process on a separate
  false alarm). Root cause under investigation; mitigations: a hard per-request timeout for the codex
  provider, and per-source subagents so the parent's context stays small (see Phase 1b).
  `hermes cron run` executes the job inside the CLI process and blocks until it finishes; trigger
  manual runs in the background.

- **2026-09-07 — Phase 0 shipped** (a)–(d): open-set carryover in `scan_triage_apply.py`
  (`--latest` = every manifest in a `--carryover-days` window with unresolved records, merged;
  dispositions span manifests and stamp back; `--show-open` prints the judging set; digest gains
  **Carried over (age)** + aging-out and stranded warnings); `--amend` writeback (by record id or
  artifact Drive file id; appends to `proposal_history`; moves nothing in Drive) wired into the ingest
  rejection path; concept vocabulary derived from `wiki/topics/` at scan time
  (`scan_common.derive_wiki_concepts`; `WIKI_CONCEPTS` → `WIKI_CONCEPT_ENRICHMENT`, 19 missing topics
  enriched, scan warns on unenriched topics and stale keys); `Topic accretion` lint (Medium ≥35 sources
  or ≥3,500 words; Low ≥25 / ≥2,500 — trips on `work-redesign` day one, as predicted) plus
  `--allow-check` so a gate can pass named expected-state checks. Suite 59 → 74 tests.
  *Refinements found while implementing:* (1) the live queue had 81 unresolved records across 23
  manifests back to 2026-07-04, far outside the 7-day window — the first carryover run needs an explicit
  owner-approved backfill (`--carryover-days N`; the digest now states N); (2) the Phase-2 batch lint
  gate cannot be a bare `--fail-on Medium` while any orphan sources roll over (§4 step 5 amended);
  (3) a Hermes v0.21.0 regression (restart-safe cron workers need the user D-Bus env) had broken every
  hermes cron job that morning — fixed fleet-side with a `user-bus.conf` gateway drop-in before
  deployment.

---

## Appendix — archived: the 2026-06 markdown-in-git redesign (built)

Decided 2026-06-14, built June 2026, after a requirements review anchored on Karpathy's LLM-wiki
pattern (<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>). Full original plan in
git history (this file, pre-2026-09-07).

- **Verdict executed:** migrated from a 5-database Notion stack to plain cross-linked markdown in
  this repo (`wiki/`: `schema.md`, `overview.md`, `topics/`, `sources/`), Obsidian as the human
  layer, Notion retired 2026-06-14, single substrate (git holds machinery + content), minimal
  governance (public-only sources; owner approves synthesis; contradictions surfaced in prose,
  never auto-resolved).
- **Deliberately cut as over-engineering** (still binding on new designs): Reviews/Log/Inbox
  databases (git history is the log; Drive `_triage` folders are the visible capture state),
  Research-Map machinery incl. the deep-dive queue, and governance fields incl.
  confidence/contested flags and **candidate-update bundles**. §1's design principles record why
  the current plan doesn't reintroduce these.
- **Since superseded by later decisions:** lean `overview.md` split into map pages
  (`topic-map.md`, `open-questions.md`, `research-gaps.md`, `watchlist.md`) 2026-08-01; a public
  Quartz site shipped 2026-07-29 (the original "not for others" scoping changed); the scan front
  end (`docs/research-scrape-plan.md`) deployed 2026-07-04.
- **Still open from the original plan:** the DC/work-environment handoff path (can DC read a
  public repo from the Uber environment?) — unresolved, resolve before relying on it.
