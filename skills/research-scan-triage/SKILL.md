---
name: research-scan-triage
description: "Use when triaging surfaced candidates from the daily research scan (the _triage store manifest) into dispositions — wiki-candidate, read-once, or discard — with hybrid autonomy: auto-queue clear wiki candidates into the Drive _inbox, auto-discard duplicates and off-mission noise, and surface the ambiguous middle plus a read-once digest to Nicholas."
version: 1.0.1
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

Trust model: this skill routes *candidates*. Nothing becomes wiki canon here — wiki-bound PDFs go to
the Drive `_inbox`, where `research-wiki-ingest` processes them **one at a time** with owner-approved
synthesis, unchanged.

## Locations

| Thing | Where |
|---|---|
| Harness + applier | `/root/research-wiki-tools/research_scan.py`, `scan_triage_apply.py` |
| Local run dirs (manifests) | `/root/research-wiki-runs/scan-*/manifest-*.json` |
| Drive `_triage` store | folder `1tXLfXs2z8LkbAurlrw8G7IYfQu1mCXh8` (under `public-literature-wiki`) |
| `_triage/files` (acquired artifacts) | `1_9TRp4H1Qqm0M4QI8hGiMkWNs9hc_GXg` |
| `_triage/ledger` (seen-index, failures, search log) | `1Fw7J30oerCSCYSLcEB5k0mbbdfOGwyx1` |
| Wiki `_inbox` (promotion target) | `1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1` |
| Rubric config (edit to retune the scan) | `/root/research-wiki-tools/scan_config.py` |

## The disposition rubric (owner-calibrated 2026-07-04, batch 1)

The wiki's mission: **AI workforce transformation × I-O psychology** — how AI changes work, workers,
jobs, organizations, and measurement (`wiki/overview.md` is the live topic list).

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
| `wiki` + clear + artifact in `_triage/files` | auto-move → `_inbox` (cap: `MAX_AUTO_WIKI_PER_RUN` = 10/run; overflow surfaces) |
| `wiki` + clear + no artifact | bounded rung-4 acquisition attempt (below); else "needs manual acquisition" in digest |
| `read-once` + clear | digest summary only (1–2 sentences, yours) |
| `discard` + clear | logged + counted in digest; file (if any) stays in `_triage/files` — never deleted |
| anything `ambiguous` | surfaced as "needs your call" with your proposed disposition |

## Rung-4 acquisition (bounded)

For at most `MAX_RUNG4_BROWSER_PER_RUN` (3) clear wiki-candidates with `acq_state: abstract-only|link-only`:
use the **browser** toolset to open the landing page and locate the real PDF link (SSRN "Download This
Paper", journal OA button), then download it with `curl` in terminal to the manifest's run `files/` dir.
Verify it is a real PDF (`file` says PDF, has text). If it works, put the local path in the entry's
`acquired_path` — the applier uploads it to `_inbox`. If it fails, just record the disposition; the
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

1. **Find the manifest**: newest local `manifest-*.json` with un-triaged records. The intended helper is
   `uv run /root/research-wiki-tools/scan_triage_apply.py --latest --dispositions <valid-json-file>`, but
   if you only need discovery, it is safe to glob `/root/research-wiki-runs/*/manifest-*.json` and choose
   the newest manifest where any record has `disposition: null`. Do not rely on `/dev/null` as the
   dispositions file unless the applier has been changed to tolerate empty JSON; older/current versions
   parse it and fail before printing the manifest.
2. **Judge every record** with `disposition: null` against the rubric. Read title + abstract +
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
5. **Dry-run the applier**, review its plan, then run with `--execute`:
   `uv run /root/research-wiki-tools/scan_triage_apply.py --manifest <path> --dispositions <path> --execute`
6. **Deliver only the digest** (the applier prints it) as your response — the cron job's delivery target
   posts it to Discord. If execution logs print mechanical lines such as `moved -> _inbox:` before the
   digest, omit those from the final response. Do not editorialize beyond the digest; append at most 2
   lines of run notes.

## Boundaries

- **Never write wiki pages** — ingest skills own that, with owner-approved synthesis.
- **Never delete Drive files**; discards keep their artifacts in `_triage/files`.
- **Public-only sources** — the one hard rule (`wiki/schema.md`). Anything smelling non-public
  (confidential, internal-use, NDA) gets flagged in the digest, never queued.
- Respect the caps; when a cap binds, surface rather than act.
- The applier fails loudly on ids it does not recognize — fix the dispositions file, do not force.
