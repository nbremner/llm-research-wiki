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
drain_queue.py -- the order in which the daily source drain takes files from
Drive `_triage/wiki` (owner decision 2026-09-08).

Owner-dropped files come first: a paper the owner fetched by hand has already
passed the strictest gate there is, and it should not wait three weeks behind
scan candidates. A file is owner-dropped when no scan manifest ever uploaded it
(its Drive id is not any record's `artifact_drive_id`). Within each group,
oldest first (Drive `createdTime`). Deterministic; the drain's parent runs this
and dispatches its subagents from the list.

  uv run drain_queue.py --limit 5          # JSON: the next files to drain, in order
  uv run drain_queue.py --counts           # one line: how many of each origin are waiting
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402


# ---------------------------------------------------------------------------
# Pure core
# ---------------------------------------------------------------------------

def order_queue(files: list[dict[str, Any]], scan_artifact_ids: set[str]) -> list[dict[str, Any]]:
    """Owner-dropped (no scan record uploaded it) first, then scan-promoted; each
    group oldest first by createdTime. Adds `origin` to every entry."""
    out = []
    for f in files:
        out.append({**f, "origin": "scan" if f["id"] in scan_artifact_ids else "owner"})
    return sorted(out, key=lambda f: (0 if f["origin"] == "owner" else 1, f.get("createdTime") or "", f.get("name") or ""))


def counts(queue: list[dict[str, Any]]) -> dict[str, int]:
    out = {"owner": 0, "scan": 0}
    for f in queue:
        out[f["origin"]] = out.get(f["origin"], 0) + 1
    out["total"] = len(queue)
    return out


# ---------------------------------------------------------------------------
# Drive / manifests
# ---------------------------------------------------------------------------

def scan_artifact_ids(out_root: str) -> set[str]:
    ids: set[str] = set()
    for p in glob.glob(f"{out_root}/*/manifest-*.json"):
        try:
            for r in json.load(open(p, encoding="utf-8")).get("records", []):
                if r.get("artifact_drive_id"):
                    ids.add(r["artifact_drive_id"])
        except (OSError, json.JSONDecodeError):
            continue
    return ids


def list_triage_wiki(service) -> list[dict[str, Any]]:
    out, tok = [], None
    while True:
        res = service.files().list(
            q=f"'{cfg.TRIAGE_WIKI_FOLDER_ID}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
            fields="nextPageToken,files(id,name,mimeType,createdTime,size)", pageSize=500, pageToken=tok,
            supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        out += res.get("files", []); tok = res.get("nextPageToken")
        if not tok:
            return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Drain order for Drive _triage/wiki (owner-dropped first)")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--counts", action="store_true", help="Print only the waiting counts by origin")
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--out-root", default=cfg.DEFAULT_OUT_ROOT)
    args = p.parse_args(argv)
    service = c.build_drive_service(args.token_path)
    queue = order_queue(list_triage_wiki(service), scan_artifact_ids(args.out_root))
    n = counts(queue)
    if args.counts:
        print(f"_triage/wiki: {n['total']} waiting ({n['owner']} owner-dropped, {n['scan']} scan-promoted)")
        return 0
    print(json.dumps({"counts": n, "next": queue[:args.limit]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
