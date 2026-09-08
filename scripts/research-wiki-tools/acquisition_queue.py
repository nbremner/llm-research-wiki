#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "google-auth-httplib2",
# ]
# ///
"""
acquisition_queue.py -- the "wiki-judged but no copy" ledger (owner request 2026-09-08).

Triage can judge a candidate `wiki` without ever obtaining its text (paywall,
bot wall, rate limit). Until now that record appeared once in a daily digest
under "needs manual acquisition" and was never seen again: 182 such records had
accumulated silently by 2026-09-08. This module computes that queue from the
manifests -- every clear `wiki` record with no artifact, minus anything already
in the wiki (DOI/URL/title match) and anything since re-disposed -- and renders
it as a markdown ledger the owner can work from. It is regenerated on every
triage run (scan_triage_apply.py appends its one-line summary to the digest)
and uploaded to Drive `_triage/needs-acquisition.md`; nothing is stored in git.
A copy the owner drops into `_triage/wiki` flows through the drain and the
record leaves the ledger by itself once its DOI matches a wiki source.

No automatic retries and no abstract-only records (owner decision 2026-09-08).

  uv run acquisition_queue.py                # print the ledger (dry run)
  uv run acquisition_queue.py --execute      # also upload ledger + state JSON to Drive _triage/
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402

LEDGER_NAME = "needs-acquisition.md"
STATE_NAME = "needs-acquisition.json"


# ---------------------------------------------------------------------------
# Pure core
# ---------------------------------------------------------------------------

def build_queue(manifests: list[dict[str, Any]], wiki_ids: set[str], wiki_titles: set[str],
                today: dt.date) -> list[dict[str, Any]]:
    """Clear `wiki` records with no artifact that are not already in the wiki.
    Oldest first (by triage date). `wiki_ids` are candidate ids (doi:/arxiv:/url:)
    derived from wiki/sources frontmatter; `wiki_titles` normalized titles."""
    out: dict[str, dict[str, Any]] = {}
    for m in manifests:
        for r in m.get("records", []):
            rid = r.get("id")
            if not rid or r.get("disposition") != "wiki" or r.get("disposition_confidence") == "ambiguous":
                continue
            if r.get("artifact_drive_id"):
                continue
            if rid in wiki_ids or (r.get("doi") and f"doi:{c.normalize_doi(r['doi'])}" in wiki_ids):
                continue
            nt = c.normalize_title(r.get("title"))
            if len(nt) >= 20 and nt in wiki_titles:
                continue
            tri = (r.get("triaged_at") or r.get("first_seen") or "")[:10]
            try:
                waiting = (today - dt.date.fromisoformat(tri)).days
            except ValueError:
                waiting = None
            out[rid] = {"id": rid, "title": c.clean_title(r.get("title")), "year": r.get("year"),
                        "venue": r.get("venue") or "", "source_type": r.get("source_type") or "",
                        "venue_tier": r.get("venue_tier") or "", "url": r.get("url") or "",
                        "doi": r.get("doi") or "", "acq_state": r.get("acq_state") or "",
                        "triaged": tri, "days_waiting": waiting}
    return sorted(out.values(), key=lambda q: (q["triaged"] or "9999", q["title"]))


def diff_queue(previous_ids: set[str], queue: list[dict[str, Any]]) -> dict[str, list[str]]:
    ids = {q["id"] for q in queue}
    return {"added": sorted(ids - previous_ids), "removed": sorted(previous_ids - ids)}


def summary_line(queue: list[dict[str, Any]], diff: dict[str, list[str]]) -> str:
    n = len(queue)
    if n == 0:
        return "Acquisition backlog: none — every wiki-judged candidate has a copy."
    parts = [f"Acquisition backlog: {n} wiki-judged paper(s) without a copy"]
    if diff["added"] or diff["removed"]:
        parts.append(f"(+{len(diff['added'])} new, −{len(diff['removed'])} acquired/removed)")
    parts.append(f"— ledger: Drive `_triage/{LEDGER_NAME}`; drop copies into `_triage/wiki`.")
    return " ".join(parts)


def render_ledger(queue: list[dict[str, Any]], today: dt.date, diff: dict[str, list[str]] | None = None) -> str:
    by_type: dict[str, int] = {}
    for q in queue:
        by_type[q["source_type"] or "?"] = by_type.get(q["source_type"] or "?", 0) + 1
    lines = [f"# Needs acquisition — wiki-judged papers without a copy (as of {today.isoformat()})", "",
             f"{len(queue)} record(s). Triage judged each of these `wiki` but no text could be obtained "
             "(paywall, bot wall, rate limit). To get one into the wiki, download it yourself and drop the "
             "file into Drive `_triage/wiki` under any name; the daily drain ingests it and the row disappears "
             "here once its DOI matches a wiki source. To give up on one, reply in #research-digest: "
             "`reject <record id> — <reason>`. This file is regenerated by every triage run; do not edit it.", "",
             "By type: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())) + ".", ""]
    if diff and (diff["added"] or diff["removed"]):
        lines.append(f"Since the last run: +{len(diff['added'])} added, −{len(diff['removed'])} removed.")
        lines.append("")
    lines.append("| # | Waiting | Judged | Title | Year | Type | Venue | Venue tier | Link | Record id |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for i, q in enumerate(queue, 1):
        link = q["url"] or (f"https://doi.org/{q['doi']}" if q["doi"] else "")
        wait = f"{q['days_waiting']}d" if q["days_waiting"] is not None else "?"
        title = q["title"].replace("|", "/")[:110]
        venue = (q["venue"] or "").replace("|", "/")[:40]
        lines.append(f"| {i} | {wait} | {q['triaged'] or '?'} | {title} | {q['year'] or ''} | {q['source_type']} | "
                     f"{venue} | {q['venue_tier']} | {link} | `{q['id']}` |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Local + Drive side
# ---------------------------------------------------------------------------

def compute(out_root: str, wiki_dir: Path, today: dt.date, previous_ids: set[str] | None = None) -> dict[str, Any]:
    from scan_triage_apply import load_local_manifests  # local import: avoids a cycle at module load
    manifests = load_local_manifests(out_root)
    sources_dir = wiki_dir / "sources"
    wiki_ids = c.load_wiki_source_ids(sources_dir)
    wiki_titles = {c.normalize_title(t) for _, t in c.load_wiki_source_titles(sources_dir)}
    queue = build_queue(manifests, wiki_ids, wiki_titles, today)
    diff = diff_queue(previous_ids or set(), queue)
    return {"queue": queue, "diff": diff, "ledger": render_ledger(queue, today, diff),
            "summary": summary_line(queue, diff),
            "state": {"generated": today.isoformat(), "ids": [q["id"] for q in queue]}}


def load_previous_state(service) -> set[str]:
    fid = c.drive_find(service, cfg.TRIAGE_FOLDER_ID, STATE_NAME)
    if not fid:
        return set()
    try:
        return set(json.loads(c.drive_download_text(service, fid)).get("ids", []))
    except Exception:  # noqa: BLE001
        return set()


def upload(service, result: dict[str, Any]) -> None:
    for name, text, mime in ((LEDGER_NAME, result["ledger"], "text/markdown"),
                             (STATE_NAME, json.dumps(result["state"], indent=1), "application/json")):
        fid = c.drive_find(service, cfg.TRIAGE_FOLDER_ID, name)
        if fid:
            c.drive_update_bytes(service, fid, text.encode("utf-8"), mime)
        else:
            c.drive_upload_text(service, cfg.TRIAGE_FOLDER_ID, name, text, mime)


def refresh(out_root: str, wiki_dir: Path, token_path: str, execute: bool) -> dict[str, Any]:
    """Used by scan_triage_apply.py after each run: compute (+ upload when executing)."""
    today = c.utc_now().date()
    service = c.build_drive_service(token_path) if execute else None
    previous = load_previous_state(service) if service else set()
    result = compute(out_root, wiki_dir, today, previous)
    if service:
        upload(service, result)
    return result


def _default_wiki_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "wiki"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Wiki-judged-but-unacquired ledger")
    p.add_argument("--out-root", default=cfg.DEFAULT_OUT_ROOT)
    p.add_argument("--wiki-dir", type=Path, default=_default_wiki_dir())
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--execute", action="store_true", help="Upload the ledger + state to Drive _triage/")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    result = refresh(args.out_root, args.wiki_dir, args.token_path, args.execute)
    print(result["summary"] if args.summary_only else result["ledger"] + "\n" + result["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
