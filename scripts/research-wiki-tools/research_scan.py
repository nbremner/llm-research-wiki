#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx",
#   "feedparser",
#   "pymupdf",
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "google-auth-httplib2",
# ]
# ///
"""
research_scan.py -- the deterministic research-scan harness (Phase 1).

Discovery (API/feed-first) -> dedup vs the coverage ledger -> acquisition ladder
(OA-resolve -> direct PDF -> Jina reader) -> pre-rank -> write a ranked manifest +
acquired files to the Drive _triage store, updating the ledger. No LLM: this is
the deterministic half. The judgment half (disposition {wiki|read-once|discard})
is the separate research-scan-triage skill run by NicholasJunior.

Safe by default: runs local-only (no Drive writes). Add --drive to sync the
ledger from / to Drive and upload acquired files + the manifest.

Examples:
  uv run research_scan.py --queries 3 --acquire 5 --no-acquire   # discovery smoke
  uv run research_scan.py --queries 3 --acquire 5                 # local acquire smoke
  uv run research_scan.py --drive                                 # full run to Drive

See docs/research-scrape-plan.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402


# ---------------------------------------------------------------------------
# Discovery channels -- each returns a list[ScanRecord] (metadata only)
# ---------------------------------------------------------------------------

def _record_from_parts(*, source: str, query: str, url: str | None, pdf_url: str | None,
                       doi: str | None, arxiv_id: str | None, title: str,
                       authors: list[str], year: str | None, venue: str | None,
                       api_type: str | None, abstract: str,
                       cited_by: int | None) -> c.ScanRecord | None:
    cid = c.candidate_id(doi=doi, arxiv_id=arxiv_id, url=url)
    if not cid:
        return None
    source_type = c.source_type_for(url, api_type, cfg.HOST_SOURCE_TYPE)
    if arxiv_id and source_type == "other":
        source_type = "preprint"
    return c.ScanRecord(
        id=cid, source=source, query=query, url=url, pdf_url=pdf_url,
        doi=c.normalize_doi(doi), arxiv_id=c.arxiv_id_from(arxiv_id) or c.arxiv_id_from(url),
        title=(title or "").strip(), authors=authors or [], year=str(year) if year else None,
        venue=venue, source_type=source_type, abstract=(abstract or "").strip()[:4000],
        cited_by_count=cited_by, acq_state="abstract-only" if abstract else "link-only",
    )


def _openalex_abstract(work: dict[str, Any]) -> str:
    inv = work.get("abstract_inverted_index")
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)[:4000]


def discover_openalex(query: str, per_query: int) -> list[c.ScanRecord]:
    data = c.http_get_json(
        "https://api.openalex.org/works",
        params={"search": query, "per-page": min(per_query, 50),
                "sort": "relevance_score:desc", "mailto": cfg.CONTACT_MAILTO},
    )
    out: list[c.ScanRecord] = []
    for w in data.get("results", []):
        loc = w.get("primary_location") or {}
        src = loc.get("source") or {}
        rec = _record_from_parts(
            source="openalex", query=query,
            url=loc.get("landing_page_url") or w.get("id"),
            pdf_url=c.openalex_pdf_url(w),
            doi=w.get("doi"), arxiv_id=None,
            title=w.get("display_name") or "",
            authors=[(a.get("author") or {}).get("display_name", "")
                     for a in (w.get("authorships") or [])][:12],
            year=w.get("publication_year"),
            venue=src.get("display_name"),
            api_type=w.get("type"),
            abstract=_openalex_abstract(w),
            cited_by=w.get("cited_by_count"),
        )
        if rec:
            out.append(rec)
    return out


def discover_arxiv(query: str, per_query: int) -> list[c.ScanRecord]:
    import feedparser
    resp = c.http_get(
        "http://export.arxiv.org/api/query",
        params={"search_query": f"all:{query}", "max_results": min(per_query, 40),
                "sortBy": "submittedDate", "sortOrder": "descending"},
    )
    feed = feedparser.parse(resp.text)
    out: list[c.ScanRecord] = []
    for e in feed.entries:
        aid = c.arxiv_id_from(getattr(e, "id", "") or "")
        pdf = None
        for link in getattr(e, "links", []):
            if link.get("type") == "application/pdf":
                pdf = link.get("href")
        if not pdf and aid:
            pdf = f"https://arxiv.org/pdf/{aid}"
        rec = _record_from_parts(
            source="arxiv", query=query,
            url=getattr(e, "id", None), pdf_url=pdf,
            doi=getattr(e, "arxiv_doi", None), arxiv_id=aid,
            title=getattr(e, "title", ""),
            authors=[a.get("name", "") for a in getattr(e, "authors", [])][:12],
            year=(getattr(e, "published", "") or "")[:4] or None,
            venue="arXiv", api_type="preprint",
            abstract=getattr(e, "summary", ""), cited_by=None,
        )
        if rec:
            out.append(rec)
    return out


def discover_crossref(query: str, per_query: int) -> list[c.ScanRecord]:
    data = c.http_get_json(
        "https://api.crossref.org/works",
        params={"query": query, "rows": min(per_query, 40),
                "mailto": cfg.CONTACT_MAILTO,
                "select": "DOI,title,author,issued,container-title,type,URL,abstract"},
    )
    out: list[c.ScanRecord] = []
    for it in (data.get("message", {}) or {}).get("items", []):
        title_list = it.get("title") or []
        authors = []
        for a in it.get("author", []) or []:
            nm = " ".join(x for x in [a.get("given"), a.get("family")] if x)
            if nm:
                authors.append(nm)
        issued = (it.get("issued", {}) or {}).get("date-parts", [[None]])
        year = issued[0][0] if issued and issued[0] else None
        cont = it.get("container-title") or []
        rec = _record_from_parts(
            source="crossref", query=query,
            url=it.get("URL"), pdf_url=None,
            doi=it.get("DOI"), arxiv_id=None,
            title=title_list[0] if title_list else "",
            authors=authors[:12], year=year,
            venue=cont[0] if cont else None, api_type=it.get("type"),
            abstract=(it.get("abstract") or "").replace("<jats:p>", " ").replace("</jats:p>", " "),
            cited_by=it.get("is-referenced-by-count"),
        )
        if rec:
            out.append(rec)
    return out


DISCOVERY = {
    "openalex": discover_openalex,
    "arxiv": discover_arxiv,
    "crossref": discover_crossref,
}


# ---------------------------------------------------------------------------
# Acquisition ladder
# ---------------------------------------------------------------------------

def unpaywall_pdf(doi: str) -> str | None:
    data = c.http_get_json(
        f"https://api.unpaywall.org/v2/{doi}",
        params={"email": cfg.CONTACT_MAILTO}, timeout=25.0,
    )
    return c.unpaywall_pdf_url(data)


def _artifact_name(rec: c.ScanRecord, ext: str) -> str:
    year = rec.year or "nd"
    author = c.slugify((rec.authors[0].split()[-1] if rec.authors else "source"), 24)
    title = c.slugify(rec.title or "untitled", 60)
    return f"{year}-{author}-{title}.{ext}"


def acquire(rec: c.ScanRecord, ledger: c.Ledger, *, files_dir: Path,
            drive=None, files_folder: str | None = None) -> None:
    """Walk the ladder, mutating rec in place. Rung 4 records a failure."""
    def store_bytes(data: bytes, name: str, mime: str) -> None:
        if drive and files_folder:
            rec.artifact_drive_id = c.drive_upload_bytes(drive, files_folder, name, data, mime)
        else:
            files_dir.mkdir(parents=True, exist_ok=True)
            p = files_dir / name
            p.write_bytes(data)
            rec.artifact_path = str(p)

    # Rung 1: resolve an OA pdf url (from discovery, else Unpaywall by DOI).
    pdf_url = rec.pdf_url
    if not pdf_url and rec.doi:
        try:
            pdf_url = unpaywall_pdf(rec.doi)
        except Exception as e:  # noqa: BLE001
            ledger.record_failure(rec.id, f"unpaywall:{rec.doi}", f"unpaywall:{type(e).__name__}")

    # Rung 2: direct PDF download + text-layer check.
    if pdf_url:
        try:
            data = c.http_get_bytes(pdf_url, timeout=60.0)
            if c.looks_like_pdf(data):
                has_text, _pages, _chars = c.pdf_text_layer_ok(data)
                rec.acq_state = "full-pdf"
                rec.needs_ocr = not has_text
                rec.flags = sorted(set(rec.flags) | (set() if has_text else {"scanned-pdf-no-text"}))
                store_bytes(data, _artifact_name(rec, "pdf"), "application/pdf")
                return
            else:
                ledger.record_failure(rec.id, pdf_url, "pdf-url-returned-non-pdf",
                                      workaround="try-jina-reader")
        except Exception as e:  # noqa: BLE001
            ledger.record_failure(rec.id, pdf_url, f"pdf-download:{type(e).__name__}",
                                  workaround="try-jina-reader")

    # Rung 3: Jina reader on the landing url (JS-capable, server-side).
    if rec.url:
        try:
            text = c.jina_read(rec.url)
            if text and len(text) > 800:
                rec.acq_state = "full-text"
                store_bytes(text.encode("utf-8"), _artifact_name(rec, "md"), "text/markdown")
                return
        except Exception as e:  # noqa: BLE001
            ledger.record_failure(rec.id, rec.url, f"jina:{type(e).__name__}",
                                  workaround="rung4-browser")

    # Rung 4: no artifact -- keep as abstract/link record for the browser tail.
    rec.acq_state = "abstract-only" if rec.abstract else "link-only"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def rank(rec: c.ScanRecord) -> None:
    concept, topics = c.concept_match(f"{rec.title}\n{rec.abstract}", cfg.WIKI_CONCEPTS)
    recency = c.recency_score(rec.year, cfg.RECENCY_HALFLIFE_DAYS)
    authority = c.authority_score(rec.source_type, cfg.SOURCE_AUTHORITY)
    citation = float(rec.provenance.get("citation_proximity", 0.0))
    score, comps = c.rank_record(recency, authority, concept, citation, cfg.RANK_WEIGHTS)
    rec.rank_score = score
    rec.rank_components = comps
    rec.matched_topics = topics
    rec.flags = sorted(set(rec.flags) | set(c.boundary_flags(f"{rec.title}\n{rec.abstract}")))


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deterministic research-scan harness")
    p.add_argument("--queries", type=int, default=None, help="Limit number of seed queries")
    p.add_argument("--per-query", type=int, default=cfg.MAX_DISCOVERY_PER_QUERY)
    p.add_argument("--acquire", type=int, default=cfg.MAX_ACQUIRE_PER_RUN)
    p.add_argument("--surface", type=int, default=cfg.MAX_SURFACED_PER_RUN)
    p.add_argument("--sources", default="openalex,arxiv,crossref")
    p.add_argument("--no-acquire", action="store_true", help="Discovery + rank + manifest only")
    p.add_argument("--drive", action="store_true", help="Sync ledger + upload files/manifest to Drive")
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--work-dir", default=None, help="Local working dir (ledger, files, manifest)")
    p.add_argument("--wiki-sources", default=None, help="wiki/sources dir to warm-start seen-index")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    work_dir = Path(args.work_dir or (Path(cfg.DEFAULT_OUT_ROOT) / f"scan-{c.utc_now_stamp()}"))
    ledger_dir = work_dir / "ledger"
    files_dir = work_dir / "files"
    work_dir.mkdir(parents=True, exist_ok=True)

    drive = None
    if args.drive:
        drive = c.build_drive_service(args.token_path)
        # Pull the NEWEST dated ledger snapshot from Drive so dedup persists across
        # runs (snapshots are 'seen_index-<UTCSTAMP>.json'; legacy undated names are
        # a read-only fallback from before the 2026-07-04 migration).
        ledger_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("seen_index.json", "failure_catalog.json"):
            stem = fname[:-5]
            names = c.drive_list_names(drive, cfg.TRIAGE_LEDGER_FOLDER_ID, stem)
            latest = c.pick_latest_dated(names, stem) or (fname if fname in names else None)
            if latest:
                (ledger_dir / fname).write_text(
                    c.drive_download_text(drive, names[latest]), encoding="utf-8")

    ledger = c.Ledger(ledger_dir).load()
    if args.wiki_sources:
        n = ledger.warm_start(c.load_wiki_source_ids(args.wiki_sources), note="wiki-source")
        t = 0
        for slug, title in c.load_wiki_source_titles(args.wiki_sources):
            cid = f"wikisrc:{slug}"
            if not ledger.is_seen(cid):
                ledger.mark_seen(cid, {"title": title, "origin": "wiki-source-title"})
                t += 1
        print(f"warm-started seen-index with {n} wiki source ids + {t} titles", flush=True)

    queries = cfg.SEED_QUERIES[: args.queries] if args.queries else cfg.SEED_QUERIES
    sources = [s.strip() for s in args.sources.split(",") if s.strip() in DISCOVERY]

    # --- Discovery + dedup ---------------------------------------------------
    fresh: dict[str, c.ScanRecord] = {}
    seen_titles: set[str] = set()  # run-local near-duplicate guard (same title, different id)
    for q in queries:
        for src in sources:
            try:
                found = DISCOVERY[src](q, args.per_query)
            except Exception as e:  # noqa: BLE001
                print(f"WARN discovery {src} '{q[:40]}': {type(e).__name__}: {e}", file=sys.stderr)
                ledger.log_search(q, src, 0, 0)
                continue
            new = 0
            for rec in found:
                if ledger.is_seen(rec.id) or rec.id in fresh:
                    continue
                if not c.is_on_mission(f"{rec.title}\n{rec.abstract}", cfg.AI_TERMS, cfg.WORK_TERMS):
                    continue
                nt = c.normalize_title(rec.title)
                if ledger.is_title_seen(nt) or (len(nt) >= 20 and nt in seen_titles):
                    continue
                if len(nt) >= 20:
                    seen_titles.add(nt)
                fresh[rec.id] = rec
                new += 1
            ledger.log_search(q, src, len(found), new)
            print(f"  {src:9s} '{q[:44]}' -> {len(found):3d} found, {new:3d} new", flush=True)

    records = list(fresh.values())
    for rec in records:
        rank(rec)
    records.sort(key=lambda r: r.rank_score, reverse=True)
    print(f"\nDiscovered {len(records)} new on-mission candidates.", flush=True)

    # --- Acquisition (top-ranked, capped) -----------------------------------
    to_acquire = records[: args.acquire]
    if not args.no_acquire:
        for i, rec in enumerate(to_acquire, 1):
            try:
                acquire(rec, ledger, files_dir=files_dir, drive=drive,
                        files_folder=cfg.TRIAGE_FILES_FOLDER_ID if args.drive else None)
            except Exception as e:  # noqa: BLE001
                ledger.record_failure(rec.id, rec.url or rec.id, f"acquire:{type(e).__name__}")
                rec.acq_state = "link-only"
            print(f"  [{i}/{len(to_acquire)}] {rec.acq_state:13s} {rec.title[:60]}", flush=True)

    # Every candidate we surface is marked seen so it never re-surfaces.
    surfaced = records[: args.surface]
    for rec in surfaced:
        ledger.mark_seen(rec.id, {"title": rec.title, "source": rec.source,
                                  "acq_state": rec.acq_state, "rank": rec.rank_score})

    # --- Manifest + ledger ---------------------------------------------------
    manifest = {
        "schema_version": cfg.SCHEMA_VERSION,
        "produced_by": cfg.PRODUCED_BY,
        "generated": c.utc_now_iso(),
        "queries": len(queries), "sources": sources,
        "discovered": len(records), "surfaced": len(surfaced),
        "acquired": sum(1 for r in to_acquire if r.acq_state in ("full-pdf", "full-text")),
        "records": [r.to_dict() for r in surfaced],
    }
    stamp = c.utc_now_stamp()
    manifest_name = f"manifest-{stamp}.json"
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False)
    (work_dir / manifest_name).write_text(manifest_text, encoding="utf-8")
    ledger.save()

    if args.drive:
        c.drive_upload_text(drive, cfg.TRIAGE_FOLDER_ID, manifest_name, manifest_text)
        # Dated snapshots, stamp-matched to the manifest — chronological in Drive,
        # and the next run loads the newest one (no same-name duplicates).
        for fname in ("seen_index.json", "failure_catalog.json"):
            c.drive_upload_text(drive, cfg.TRIAGE_LEDGER_FOLDER_ID,
                                f"{fname[:-5]}-{stamp}.json",
                                (ledger_dir / fname).read_text(encoding="utf-8"))

    print(f"\nWrote {work_dir / manifest_name}")
    print(f"Surfaced {len(surfaced)} (cap {args.surface}); "
          f"acquired {manifest['acquired']} full artifacts; "
          f"ledger now tracks {len(ledger.seen)} seen ids, "
          f"{len(ledger.failures)} failure entries.")
    if args.drive:
        print("Uploaded manifest + ledger + files to Drive _triage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
