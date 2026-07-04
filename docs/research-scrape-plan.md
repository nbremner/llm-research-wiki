# Research Scrape Harness — Build Plan (comprehensive scan → triage → wiki)

Status: **approved plan, ready to build.** Created 2026-07-03.
Read `OPERATING_MODEL.md` first for the operating context, and `docs/wiki-redesign-plan.md` for the
wiki this feeds. This plan builds the *front end* that fills the pipeline; the synthesis engine
(`skills/research-wiki-ingest`, `research-wiki-batch-ingest`, the `sources/`→`topics/` split) is
unchanged.

## Why (decision record)

Decided 2026-07-03 after reviewing the existing "Daily research scans" workflow (Claude Co-Work, ~31
intermittent scans Apr–Jul 2026, filed in Notion under "Workforce Transformation & IO Psych").

The prior workflow's **discovery and relevance judgment were strong** — each scan tiered articles
(high/moderate/low) with per-item rationale mapped to research questions. What failed was purely
**acquisition**: Co-Work tried to pull the primary PDFs/HTML directly and was blocked — in April by a
total egress proxy (0 of 21 downloads succeeded), and later by JavaScript-rendered pages, scanned PDFs
with no text layer, and WebFetch provenance limits. The "comprehensive scan" quietly degraded into a
digest of abstracts and secondary summaries.

The generated-summary PDFs Co-Work produced are low quality and are **disregarded**. The historical
scans are kept for exactly two uses: (1) a **failure-mode lessons** catalogue to engineer against, and
(2) an **optional seed list** of already-relevance-judged candidate URLs — none of which were ever
actually acquired, so they remain legitimate targets for the new ladder.

**Verdict:** rebuild the front end as a *split pipeline* running on NicholasJunior (Hermes VPS), anchored
on the wiki's own mission rather than the (now-wrapped-up) applied research questions.

## Core principle — split the pipeline by determinism and trust

The prior job mushed four jobs an LLM handles unevenly. We split them:

- **Deterministic (Python, no LLM):** discovery via APIs/feeds, dedup, acquisition, pre-rank. These
  want durable state and reproducibility — not model judgment. An LLM asked to "remember what it
  searched" or "fetch a URL" is where the prior quality problems lived.
- **Judgment (NicholasJunior / GPT-5.5):** relevance classification, disposition routing, synthesis —
  operating only on clean, already-acquired text against an explicit, **config-driven** rubric.

This mirrors the wiki's existing trust split (evidence auto-commits; synthesis is approval-gated),
extended upstream into discovery.

## Architecture

```
DISCOVERY  (deterministic, API/feed-first — no LLM)
  OpenAlex · arXiv · Semantic Scholar · Crossref · NBER/SSRN · think-tank & gov feeds · newsletters→Gmail
  seeded by: wiki thin-areas + open-questions + citation-chase of existing sources/
      │ candidate {id, meta, url}
      ▼
DEDUP vs LEDGER ── seen? ──► drop (logged)
      │ new
      ▼
ACQUISITION LADDER  → record {id, meta, acq_state, artifact_ptr?, provenance}   (rung 4 → failure-catalog)
      │
      ▼
PRE-RANK  (deterministic): recency × source-authority × concept-match × citation-proximity
      │ top-N / day  ← the throttle: comprehensive capture in, daily trickle out
      ▼
TRIAGE  (NicholasJunior / GPT-5.5 — classify clean text vs the wiki rubric) ── hybrid autonomy:
   ├─ wiki-candidate → promote file to wiki Drive _inbox → existing INGEST (owner-approval-gated)
   ├─ read-once      → daily digest (summarized); record stays in the triage store
   └─ discard        → logged in ledger (reversible)
```

Everything above TRIAGE is deterministic Python; the parts GPT-5.5 is weak at run before it is ever
invoked.

### Stores and where each lives (respecting the AGENTS.md hard boundary)

| Layer | Holds | Lives in |
|---|---|---|
| **Git repo** | harness scripts, the triage skill, the rubric + seed-query config, wiki content | git (origin ↔ LC ↔ NJ, already synced) |
| **Triage store** (general inbox) | acquired **files** + **link/abstract records** + the manifest | Google Drive `_triage/` |
| **Coverage ledger** | seen-index · search-log · failure-catalog | Google Drive (state-of-record, JSON) |
| **Wiki `_inbox`** | wiki-bound PDFs only | Google Drive `_inbox` (unchanged) |
| **Discord** | the daily digest — a *view*, not the record | Discord via `hermes send` |

Generated artifacts (candidate lists, the ledger, acquired PDFs) never enter git — they are corpus/state
per AGENTS.md and `.gitignore`. Only machinery and the curated rubric/seed config are versioned.

## Acquisition ladder (verified on the VPS 2026-07-03)

Every candidate resolves to the best rung it can reach; each record carries its **acquisition-state** so
nothing silently degrades to a secondary source the way the prior job did.

| Rung | Method | Deterministic? | Verified |
|---|---|---|---|
| 1 · Metadata + OA URL | OpenAlex / Crossref / Unpaywall / arXiv / S2 APIs (Python) | ✅ | Crossref ✅, Unpaywall ✅ returned JSON |
| 2 · Direct PDF → disk | `curl`/httpx → local → Drive | ✅ | arXiv PDF ✅ 998 KB, valid, text layer |
| 3 · JS / bot-blocked HTML → text | **Jina reader** (`r.jina.ai`) | ✅ | ✅ extracted a JS page that failed twice in Co-Work |
| 4 · Stubborn tail (login walls, hard bot-blocks) | NJ built-in **`browser`** toolset, invoked only when the harness flags "browser-needed" | ✗ (in-Hermes agent step) | ✅ NJ browser extracted the same JS page via DOM |
| 5 · Scanned/image PDF (no text layer) | `pdftotext` → empty ⇒ flag for later OCR (vision) | deferred | vision works but is not a turnkey PDF-OCR pipeline |

Reader-API decision: NJ's **`web`** toolset does **not** execute JavaScript (confirmed by NJ), so it is
not a reader replacement. **Jina** keeps acquisition deterministic and *out of the LLM turn*; NJ's
**`browser`** is the free in-Hermes last resort. Firecrawl is not needed.

### Failure modes observed → how the ladder addresses each

| Prior failure (from the historical scans) | Root cause | Addressed by |
|---|---|---|
| "all blocked by egress proxy" (0/21) | Co-Work environment egress proxy | VPS has open outbound — the proxy does not exist here |
| "PDF contained no machine-readable text" | scanned/image PDF | OA-resolution prefers arXiv/publisher text PDF; else flag for OCR |
| "navigation HTML only (client-rendered)" | JS-rendered page | Jina reader (rung 3) / NJ browser (rung 4) |
| "WebFetch provenance restriction" | Claude WebFetch guard | direct HTTP / Jina on the VPS — WebFetch not used |
| "URL returned empty response" | transient / soft bot-block | retry + Jina fallback |

## Scope & routing

The **wiki mission is the anchor** (broad AI-workforce × I-O psychology, per `wiki/overview.md`), not the
wrapped-up applied "U4B/B2B-sales" research questions. The relevance rubric and seed queries live as
**config data in git**, so a future applied project is a config add, not a rebuild.

Dispositions (hybrid autonomy — auto-discard obvious noise, auto-queue obvious wiki-candidates into the
approval gate, surface the ambiguous middle + read-once for the owner):

- **wiki-candidate** ≈ primary research with real evidence on a wiki gap → Drive `_inbox` → existing
  ingest (owner-approval-gated for synthesis; unchanged).
- **read-once** ≈ on-topic but secondary/practitioner/context → daily digest, record kept, not ingested.
- **discard** ≈ off-topic/noise → logged in the ledger (reversible), never silently dropped.

## Build phases

- **Phase 0 — Grounding (LC).** Mine the 31 scans → failure-mode note + optional seed list; create Drive
  `_triage/`; finalize the JSON ledger format. No system yet.
- **Phase 1 — Deterministic harness (LC; Python on the VM).** Discovery (API-first, seeded by wiki gaps +
  citation-chase) → dedup vs fresh seen-index → acquisition ladder rungs 1–3 → pre-rank → write candidates
  + acquired files to Drive `_triage/` + ledger. Set up the venv + free API keys. Guardrail tests.
- **Phase 2 — Triage skill (NJ/GPT-5.5).** Build `research-scan-triage`; **retire
  `research-wiki-pdf-backlog-triage`** (no proliferation). Reads pre-ranked candidates, hybrid-routes,
  invokes `browser` for rung-4 stragglers, drafts the digest. Retire carefully: rewrite the fail-closed
  gateway mount drop-in's required list *before* unmounting the old skill; update `skills.allowlist` +
  `AGENTS.md` + NJ's live store in the same session.
- **Phase 3 — Schedule + delivery (NJ).** **systemd timer runs the harness** (deterministic, zero tokens);
  **`hermes cron` runs the triage/digest turn** (the LLM step) — the clean split. Daily digest to Discord +
  Drive `_triage/` as record; volume caps + failure alerts to #logs, matching the existing cron discipline.
- **Phase 4 — Proof + calibration (LC + owner).** Re-acquire the high-relevance items Co-Work left blocked
  (the "it works now" demo); calibrate a few daily batches before widening autonomy.

## Deployment & operations

- **Code lives on the VM via the existing loop:** harness → `scripts/research-wiki-tools/` (symlinked to
  `/root/research-wiki-tools`); triage skill → `skills/` (bind-mounted). Push to `origin/main` → the daily
  `research-wiki-sync.timer` pulls it to `/root/work/llm-research-wiki`. The only new cloud object is the
  cron schedule.
- **Python env:** the VPS has Python 3.12 but **no `uv`** — add a venv + `requirements.txt` (or install uv).
- **Secrets:** free API keys (OpenAlex, Semantic Scholar) + a `mailto` polite-pool contact live in NJ's
  config/secrets, **never git**. OpenAlex/S2 rate-limit anonymous access; Crossref/Unpaywall are fine with
  `mailto`.
- **Caps + dedupe + logs on every scheduled job** (OPERATING_MODEL cron discipline). Topic synthesis stays
  owner-approval-gated regardless of cadence. Cadence: daily trickle.

## Open / deferred

- **Delivery mechanism** finalized last (Discord digest + Drive store is the working shape).
- **Scanned-PDF OCR** (rung 5) deferred — flag, don't OCR, in v1.
- **Seed-list bootstrap** — whether to prime the first runs from the historical scan URLs (optional).
- **Future applied lens** — a second rubric/seed profile if a project like the old U4B work recurs.

## Don't break

- The **public-only boundary** (the one wiki governance rule) — all scan inputs are public web.
- The **fail-closed gateway mounts** — retiring a mirrored skill stops the gateway unless the drop-in's
  required-mount list is rewritten first (the 2.5-min-outage lesson, 2026-06-14).
- The **VPS sync loop** (`research-wiki-sync.timer`, bind mounts) — the harness rides the same rails.
- The clean **deterministic/judgment split** — acquisition must stay out of the LLM turn (rungs 1–3), with
  `browser` (rung 4) the only judgment-side acquisition, used sparingly.
