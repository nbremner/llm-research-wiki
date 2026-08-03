---
name: research-scan-triage
description: "Use when triaging surfaced candidates from the daily research scan into visible Drive state folders — wiki, read-once, or discarded — while preserving manifest/ledger audit state."
version: 1.2.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research-wiki, triage, scan, google-drive, digest, literature-review]
    related_skills: [research-wiki-ingest, research-wiki-query, research-wiki-graph-lint]
---

# Research Scan Triage

## Overview

The research pipeline is split by determinism (see `docs/research-scrape-plan.md`): a deterministic
harness (`research_scan.py`, run on a schedule) discovers candidates via APIs, acquires what it can
(OA PDF → direct download → Jina reader), pre-ranks against the wiki's concept vocabulary, and writes
a **manifest** of surfaced records plus acquired artifacts to the Drive `_triage` store. **This skill
is the judgment half**: read the manifest, assign each record a disposition, let the deterministic
applier (`scan_triage_apply.py`) do every mechanical action, and deliver the owner digest.

Trust model: this skill routes *candidates*. Nothing becomes wiki canon here — wiki-bound artifacts go
to Drive `_triage/wiki`, where `research-wiki-ingest` processes them **one at a time** with
owner-approved synthesis.

## Locations

| Thing | Where |
|---|---|
| Harness + applier | `/root/research-wiki-tools/research_scan.py`, `scan_triage_apply.py` |
| Local run dirs (manifests) | `/root/research-wiki-runs/scan-*/manifest-*.json` |
| Drive `_triage` store | folder `1tXLfXs2z8LkbAurlrw8G7IYfQu1mCXh8` (under `public-literature-wiki`) |
| `_triage/pending` (unresolved artifacts) | `1_9TRp4H1Qqm0M4QI8hGiMkWNs9hc_GXg` |
| `_triage/wiki` (approved; awaiting ingest) | `1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1` |
| `_triage/read-once` (reviewed; not canonical) | `1RQdnNN1d_iWegTWSqr4jZ7lYV86vtL8o` |
| `_triage/discarded` (reviewed; rejected) | `1fNRrNYxwxB87lQeXtfiZ7Fc6S5FMcwNx` |
| `_triage/ledger` (seen-index, failures, search log) | `1Fw7J30oerCSCYSLcEB5k0mbbdfOGwyx1` |
| Rubric config (edit to retune the scan) | `/root/research-wiki-tools/scan_config.py` |

## The disposition rubric (owner-calibrated 2026-07-04, batch 1)

The wiki's mission: **AI workforce transformation × I-O psychology** — how AI changes work, workers,
jobs, organizations, and measurement (`wiki/topic-map.md` is the live topic list).

- **wiki** — contributes evidence *or* a framework to an AI×work topic the wiki tracks. **Inclusive**:
  empirical studies and RCTs, evidence syntheses / meta-analyses, theory papers, benchmark/measurement
  proposals, AND practitioner frameworks or position papers that organize a tracked topic. The owner
  keeps frameworks (e.g. ORCHESTRA) and position papers (e.g. a time-saved benchmark) as wiki material.
- **read-once** — AI×work-*adjacent* but centered in a domain the wiki does not track: automation of a
  different profession's work product (e.g. financial audit / accounting IS), a different industrial
  context (e.g. manufacturing / Industry 5.0 human-machine collaboration), **student-sample
  learning/cognition studies with no genuine work or labor setting** (owner ruling 2026-07-04:
  construct overlap with tracked topics like [[ai-mediated-learning]] or cognitive offloading does
  NOT overcome a missing work context), or on-topic news/commentary with no durable evidence. Worth a
  summary line in the digest, not wiki-durable.
- **discard** — duplicates (same normalized title under a different DOI/URL) and off-mission items
  (no genuine work/labor angle — e.g. a pure computer-vision or LLM-methods paper). This bucket is
  small; when in doubt it is not a discard.

**Ambiguity rule: never guess.** `confidence: clear` only when the rubric decides cleanly; anything
else is `ambiguous`, which the applier surfaces as "needs your call" with your proposed disposition.
Auto-actions happen only on `clear`.

### Worked examples (owner labels, batch 1)

| Paper | Disposition | Why |
|---|---|---|
| Human vs AI-agent workflows across 5 skill domains | wiki | comparative evidence, human-ai-collaboration |
| Auditing fairness interventions in algorithmic hiring (AAAI) | wiki | algorithmic-assessment evidence |
| GenAI narrows education-based productivity gaps (RCT) | wiki | strong causal evidence |
| GenAI productivity systematic review (269k) | wiki | evidence synthesis |
| Deskilling pressure in human-AI task allocation (simulation) | wiki | ai-induced-skill-erosion, simulation OK |
| Algorithm aversion as rational optimization (experiment) | wiki | ai-receptivity/task-allocation evidence |
| Time-Saved Benchmark position paper | wiki | benchmark-validity framework counts |
| Context engineering principal-agent theory | wiki | theory on a tracked topic counts |
| ORCHESTRA human-agent leadership framework | wiki | practitioner framework counts |
| Automated audit tools & audit quality (accounting IS) | read-once | other profession's domain |
| Industry 5.0 human-machine collaboration review | read-once | manufacturing context |
| University-student cognitive-offloading study, no work setting | read-once | student sample; construct match alone insufficient (owner-ratified 2026-07-04) |
| Same paper under a second SSRN DOI | discard | duplicate |

## Hybrid autonomy — what acts alone vs. surfaces

| Judgment | Action (by the applier, not by you) |
|---|---|
| `wiki` + clear + artifact in `_triage/pending` | auto-move → `_triage/wiki` (cap: `MAX_AUTO_WIKI_PER_RUN` = 10/run; overflow surfaces) |
| `wiki` + clear + no artifact | bounded rung-4 acquisition attempt (below); else "needs manual acquisition" in digest |
| `read-once` + clear | move artifact → `_triage/read-once`; include a 1–2 sentence digest summary |
| `discard` + clear | move artifact → `_triage/discarded`; log and count it in the digest |
| anything `ambiguous` | keep in `_triage/pending` and surface as "needs your call"; a later clear judgment may resolve it |

## Rung-4 acquisition (bounded)

For at most `MAX_RUNG4_BROWSER_PER_RUN` (3) clear wiki-candidates with `acq_state: abstract-only|link-only`:
use the **browser** toolset to open the landing page and locate the real PDF link (SSRN "Download This
Paper", journal OA button), then download it with `curl` in terminal to the manifest's run `files/` dir.
Verify it is a real PDF (`file` says PDF, has text). If it works, put the local path in the entry's
`acquired_path` — the applier uploads it to `_triage/wiki`. If it fails, just record the disposition; the
applier lists it under "needs manual acquisition". Do not fight hard paywalls or CAPTCHAs; do not log in
anywhere; never buy access.

OSF preprints often do not require browser probing: for DOI paths like `10.31234/osf.io/8hbp9_v1` or
`10.31235/osf.io/e9qw5_v1`, try `https://osf.io/<id>/download` directly with `curl -L --fail -A
'Mozilla/5.0' -o <run-dir>/files/osf-<id>.pdf ...`. Verify with `file`; if `pdftotext` is unavailable,
use Python `pypdf.PdfReader` to confirm page count and extract a small text sample. Keep these direct
OSF attempts within the rung-4 cap.

For SSRN DOI candidates (`10.2139/ssrn.<id>`), use a single bounded public probe for an obvious download
link. If SSRN returns 403, bot-check/CAPTCHA, login wall, or no obvious public download, stop immediately:
leave `acquired_path` unset and let the applier surface manual acquisition. Do not retry with access
workarounds or login flows.

If the landing page presents a bot check, CAPTCHA, login wall, or purchase flow, stop that acquisition
attempt immediately. Keep the disposition judgment, omit `acquired_path`, and let the applier surface it
as manual acquisition. The useful lesson is the bounded stop rule, not repeated browser probing.

See `references/osf-rung4-direct-download.md` for the compact OSF direct-download pattern and verification checks.
See `references/ssrn-rung4-bounded.md` for the compact SSRN stop pattern.
See `references/drive-artifact-inspection.md` for the Drive artifact sanity-check pattern when abstracts are thin or acquired "full-text" may be a bot-check page.
See `references/2026-07-22-triage-edge-cases.md` for concrete examples of OSF DOI download normalization, landing-page artifacts that should surface as ambiguous, and disposition boundary cases.

## Workflow

### Upstream service health first

If the user reports `research-scan.service` or `research-scan.timer` failed, debug the deterministic
harness before doing triage. The triage job can honestly say "no new scan" while the upstream scanner is
broken. Use `systemctl status research-scan --no-pager -l` and `journalctl -u research-scan --no-pager -n
160 -o short-iso` as the tight loop. A common root cause is revoked Google Drive OAuth (`invalid_grant:
Token has been expired or revoked`) at the first Drive ledger call; repair Drive auth with the
`google-workspace` Drive-only headless OAuth flow, then restart and verify the service. See
`references/upstream-service-troubleshooting.md`.

After exchanging a refreshed Drive-only OAuth callback, verify the token with both `$GSETUP --check` and
a targeted Drive read/search. `AUTHENTICATED (partial)` is expected for Drive-only scope; do not treat
missing Gmail/Calendar/Docs/Sheets scopes as a blocker for the scanner. Then run
`systemctl reset-failed research-scan.service || true; systemctl start research-scan.service` and wait for
the oneshot to finish. If the terminal command is interrupted while `systemctl start` is blocking, do not
report failure: immediately check `systemctl status research-scan --no-pager -l`, `systemctl is-active`,
and the recent journal. A running scan will show `Active: activating (start)` and continue under systemd;
wait/poll until it becomes `inactive (dead)` with `status=0/SUCCESS` or `failed`. Non-fatal source warnings
such as arXiv HTTP 429s can appear during discovery; judge success by final manifest write plus
`Uploaded manifest + ledger + files to Drive _triage`.

1. **Find the manifest**: newest local `manifest-*.json` with unresolved records (`disposition: null` or legacy `disposition_confidence: ambiguous`). The intended helper is
   `uv run /root/research-wiki-tools/scan_triage_apply.py --latest --dispositions <valid-json-file>`, but
   if you only need discovery, it is safe to glob `/root/research-wiki-runs/*/manifest-*.json` and choose
   the newest manifest where any record is null or ambiguous. `--dispositions` is optional as of
   the 2026-08-03 applier, but omitting it skips triage entirely (`--friction`-only mode) — it is
   not a manifest-discovery mode, so glob for discovery.
2. **Judge every unresolved record** against the rubric. Read title + abstract +
   matched_topics; check the acquired artifact if the abstract is thin. One line of `reason` each,
   citing the rubric category. When a record has `artifact_drive_id` but little/no abstract, inspect the
   Drive artifact before judging: acquired "full-text" can be a Jina Markdown landing page, paywall, or
   bot-check page rather than usable paper text. If the artifact is only a bot/CAPTCHA/security page and
   the title alone is not enough for a clear rubric call, mark the proposed disposition `confidence:
   ambiguous` so it surfaces.
3. **Rung-4 attempts** for up to 3 clear wiki-candidates lacking artifacts (optional, skip freely). For
   DOI landing pages with obvious public article pages, a fast pattern is: open the DOI in the browser,
   extract anchors whose text looks like "Download PDF" with `browser_console`, download that href with
   `curl -L --fail -A 'Mozilla/5.0'`, then verify with `file` plus a small text-layer/page-count check.
   Stop immediately on bot verification, CAPTCHA, login, or purchase pages; record the judgment without
   `acquired_path`.
4. **Write the dispositions JSON** (schema in the applier's docstring) to the run dir.
5. **Dry-run the applier**, review its plan, then run with `--execute --friction`:
   `uv run /root/research-wiki-tools/scan_triage_apply.py --manifest <path> --dispositions <path> --execute --friction`
6. **Rubric-friction check**: `--friction` prints every ambiguous proposal from the last 14 days
   after the digest (from records' `proposal_history`; entries marked `[later resolved: …]` show what
   an owner follow-up or re-judgment settled on). Read it and decide whether the recent ambiguity
   clusters: **if 3 or more items share the same underlying cause** — the same rubric boundary being
   hit, not merely the same topic — append exactly one `## Rubric proposal` block to your digest
   response:
   - the observed pattern, citing the item titles and dates as evidence;
   - proposed rubric wording (a bullet edit or addition, in the rubric's own style);
   - a proposed worked-example row for the table;
   - which of the cited items the change would have made `clear` instead of ambiguous.
   Resolved entries are your ground truth: if the owner's resolutions contradict your proposed
   wording, follow the resolutions. Hard cap: **one proposal per digest**, and only when the
   ≥3-shared-cause threshold trips. If the pattern matches a **Declined proposals** entry below,
   do not re-propose it.
7. **Deliver only the digest** (the applier prints it) as your response — the cron job's delivery target
   posts it to Discord. If execution logs print mechanical lines such as `moved -> _triage/wiki:` before the
   digest, omit those from the final response. Do not editorialize beyond the digest; append at most 2
   lines of run notes. The single `## Rubric proposal` block from step 6, when warranted, is the one
   exception to that 2-line limit — the friction *report itself* is working data and stays out of the
   digest.

## Rubric governance

Rubric changes are **proposal-only** from this skill. The owner ratifies or declines in the digest
thread; ratified changes are encoded into this file by the local Claude via git (prospective from the
next run, never retroactive). **Never edit this SKILL.md yourself**, even though the clone is writable
— an unratified rubric edit would silently change future dispositions.

### Declined proposals

*(none yet — entries are added here by the local Claude when the owner declines, so the same pattern
is not re-proposed)*

## Boundaries

- **Never write wiki pages** — ingest skills own that, with owner-approved synthesis.
- **Never edit this skill's rubric** — rubric proposals go in the digest (workflow step 6); encoding
  happens owner-side.
- **Never delete Drive files**; clear dispositions move artifacts out of `_triage/pending` into the matching visible state folder.
- When renaming a state folder in place, update only its name. Do not remove its current `_triage` parent without re-adding it; Drive can relocate an unparented folder to the shared-drive root. Verify `parents` after every folder update.
- **Public-only sources** — the one hard rule (`wiki/schema.md`). Anything smelling non-public
  (confidential, internal-use, NDA) gets flagged in the digest, never queued.
- Respect the caps; when a cap binds, surface rather than act.
- The applier fails loudly on ids it does not recognize — fix the dispositions file, do not force.
