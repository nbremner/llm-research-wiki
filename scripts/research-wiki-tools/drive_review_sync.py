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
drive_review_sync.py -- keep Drive artifacts in the folder their record's review
status says (the Drive mirror of the git human-review split, 2026-09-07).

  wiki/sources/<slug>.md             human_reviewed: true   -> Drive _sources/
  wiki/sources/unreviewed/<slug>.md  human_reviewed: false  -> Drive _sources/_unreviewed/

Deterministic and idempotent: read every source record's `drive_file_id` and its
folder, look up where the artifact currently sits, and compute the moves needed.
Default is a DRY RUN that prints the plan; --execute performs the moves (Drive
`addParents`/`removeParents`, file ids never change). Nothing is ever trashed or
deleted. Fails loud (exit 2, no moves) if any record's flag disagrees with its
folder -- the graph lint owns that rule; fix git first. Records whose file cannot
be found, and files in the managed folders that no record points to, are
reported, never touched.

Used by: the ingest skill after every approval (record moves up -> artifact
moves up), the scheduled drain after each run (defence in depth), and the
one-time 2026-09-07 migration out of the flat public-literature-wiki root.

Examples:
  uv run drive_review_sync.py                       # dry run against the repo's wiki/
  uv run drive_review_sync.py --execute             # perform the moves
  uv run drive_review_sync.py --json                # machine-readable plan
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402

UNREVIEWED_DIR = "unreviewed"
REVIEW_FLAG = "human_reviewed"
EXIT_MISMATCH = 2
EXIT_MISSING = 3

_FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


# ---------------------------------------------------------------------------
# Pure core
# ---------------------------------------------------------------------------

def load_records(wiki_dir: Path) -> list[dict[str, Any]]:
    """One entry per source record: slug, folder-derived review state, flag, drive id."""
    out: list[dict[str, Any]] = []
    sources = wiki_dir / "sources"
    for md in sorted(sources.rglob("*.md")):
        rel = md.relative_to(sources)
        m = _FM_RE.match(md.read_text(encoding="utf-8"))
        fm = m.group(1) if m else ""
        def field(key: str) -> str | None:
            mm = re.search(rf"^{key}:\s*(.+?)\s*$", fm, re.M)
            return mm.group(1).strip().strip('"').strip("'") if mm else None
        out.append({
            "slug": md.stem,
            "path": str(rel),
            "in_unreviewed_dir": len(rel.parts) > 1 and rel.parts[0] == UNREVIEWED_DIR,
            "flag": (field(REVIEW_FLAG) or "").lower() or None,
            "drive_file_id": field("drive_file_id"),
        })
    return out


def expected_folder(rec: dict[str, Any], sources_id: str, unreviewed_id: str) -> str:
    return unreviewed_id if rec["in_unreviewed_dir"] else sources_id


def plan_moves(records: list[dict[str, Any]], locations: dict[str, dict[str, Any]],
               sources_id: str, unreviewed_id: str, managed_ids: set[str] | None = None,
               ) -> dict[str, Any]:
    """Compute the reconciliation plan.

    `locations` maps drive_file_id -> {"name", "parents": [...], "trashed": bool}
    for every file the caller could resolve. Returns {"moves", "ok", "missing",
    "mismatch", "no_drive_id", "strays"}; `strays` lists files present in the
    managed folders that no record references (informational)."""
    plan: dict[str, list[dict[str, Any]]] = {
        "moves": [], "ok": [], "missing": [], "mismatch": [], "no_drive_id": [], "strays": [],
    }
    for rec in records:
        flag_says_unreviewed = rec["flag"] == "false"
        if rec["flag"] in ("true", "false") and flag_says_unreviewed != rec["in_unreviewed_dir"]:
            plan["mismatch"].append({"slug": rec["slug"], "path": rec["path"], "flag": rec["flag"]})
            continue
        fid = rec.get("drive_file_id")
        if not fid:
            plan["no_drive_id"].append({"slug": rec["slug"], "path": rec["path"]})
            continue
        loc = locations.get(fid)
        if not loc or loc.get("trashed"):
            plan["missing"].append({"slug": rec["slug"], "drive_file_id": fid,
                                    "trashed": bool(loc and loc.get("trashed"))})
            continue
        want = expected_folder(rec, sources_id, unreviewed_id)
        parents = list(loc.get("parents") or [])
        if want in parents and len(parents) == 1:
            plan["ok"].append({"slug": rec["slug"], "drive_file_id": fid})
        else:
            plan["moves"].append({"slug": rec["slug"], "drive_file_id": fid, "name": loc.get("name", ""),
                                  "from": parents, "to": want,
                                  "to_label": "_sources/_unreviewed" if want == unreviewed_id else "_sources"})
    referenced = {r.get("drive_file_id") for r in records if r.get("drive_file_id")}
    for fid, loc in sorted(locations.items(), key=lambda kv: kv[1].get("name", "")):
        if fid in referenced or loc.get("trashed"):
            continue
        if managed_ids and set(loc.get("parents") or []) & managed_ids:
            plan["strays"].append({"drive_file_id": fid, "name": loc.get("name", ""),
                                   "parents": list(loc.get("parents") or [])})
    return plan


def render_plan(plan: dict[str, Any], executed: bool) -> str:
    mode = "executed" if executed else "DRY RUN — no Drive changes made"
    lines = [f"drive_review_sync ({mode}): {len(plan['ok'])} already in place · "
             f"{len(plan['moves'])} to move · {len(plan['missing'])} missing · "
             f"{len(plan['mismatch'])} flag/folder mismatches · {len(plan['no_drive_id'])} without drive_file_id · "
             f"{len(plan['strays'])} stray files in managed folders"]
    for mv in plan["moves"]:
        lines.append(f"  move  {mv['slug']} -> {mv['to_label']}  ({mv['name'][:60]})")
    for m in plan["mismatch"]:
        lines.append(f"  MISMATCH  {m['path']}: {REVIEW_FLAG}: {m['flag']} disagrees with its folder — fix git first")
    for m in plan["missing"]:
        lines.append(f"  MISSING   {m['slug']}: drive_file_id {m['drive_file_id']} "
                     f"{'is trashed' if m['trashed'] else 'not found'}")
    for m in plan["no_drive_id"]:
        lines.append(f"  NO-ID     {m['path']}: record has no drive_file_id")
    for s_ in plan["strays"]:
        lines.append(f"  stray     {s_['name'][:70]} (no record points to it; left alone)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Drive side
# ---------------------------------------------------------------------------

def _list_folder(service, folder_id: str) -> list[dict[str, Any]]:
    out, tok = [], None
    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
            fields="nextPageToken,files(id,name,parents,trashed)", pageSize=500, pageToken=tok,
            supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        out += res.get("files", []); tok = res.get("nextPageToken")
        if not tok:
            return out


def resolve_locations(service, records: list[dict[str, Any]], managed_ids: list[str]) -> dict[str, dict[str, Any]]:
    """id -> location for every file in the managed folders, plus a per-file lookup
    for referenced ids that live elsewhere (e.g. still in _triage/wiki)."""
    locations: dict[str, dict[str, Any]] = {}
    for folder in managed_ids:
        for f in _list_folder(service, folder):
            locations[f["id"]] = {"name": f["name"], "parents": f.get("parents", []), "trashed": f.get("trashed", False)}
    for rec in records:
        fid = rec.get("drive_file_id")
        if fid and fid not in locations:
            try:
                f = service.files().get(fileId=fid, fields="id,name,parents,trashed", supportsAllDrives=True).execute()
                locations[fid] = {"name": f.get("name", ""), "parents": f.get("parents", []), "trashed": f.get("trashed", False)}
            except Exception:  # noqa: BLE001 - not found / no access -> reported as missing
                pass
    return locations


def execute_moves(service, plan: dict[str, Any]) -> None:
    for mv in plan["moves"]:
        service.files().update(
            fileId=mv["drive_file_id"], addParents=mv["to"], removeParents=",".join(mv["from"]),
            fields="id,parents", supportsAllDrives=True).execute()
        print(f"moved -> {mv['to_label']}: {mv['name'][:70]}", flush=True)


def _default_wiki_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "wiki"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Reconcile Drive artifact folders with source review status")
    p.add_argument("--wiki-dir", type=Path, default=_default_wiki_dir())
    p.add_argument("--execute", action="store_true", help="Perform the moves (default: dry run)")
    p.add_argument("--json", action="store_true", help="Print the plan as JSON")
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--allow-missing", action="store_true",
                   help="Do not fail when a record's artifact cannot be found (still reported)")
    args = p.parse_args(argv)

    records = load_records(args.wiki_dir)
    managed = [cfg.PUBLIC_ROOT_FOLDER_ID, cfg.PUBLIC_SOURCES_FOLDER_ID, cfg.PUBLIC_UNREVIEWED_FOLDER_ID]
    service = c.build_drive_service(args.token_path)
    locations = resolve_locations(service, records, managed)
    plan = plan_moves(records, locations, cfg.PUBLIC_SOURCES_FOLDER_ID, cfg.PUBLIC_UNREVIEWED_FOLDER_ID,
                      managed_ids=set(managed))

    if plan["mismatch"]:
        print(render_plan(plan, executed=False), file=sys.stderr)
        print("refusing to move anything while flag/folder mismatches exist", file=sys.stderr)
        return EXIT_MISMATCH
    executed = False
    if args.execute and plan["moves"]:
        execute_moves(service, plan)
        executed = True
    print(json.dumps(plan, indent=2) if args.json else render_plan(plan, executed=executed or (args.execute and not plan["moves"])))
    if plan["missing"] and not args.allow_missing:
        return EXIT_MISSING
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
