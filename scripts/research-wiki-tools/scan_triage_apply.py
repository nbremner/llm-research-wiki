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
scan_triage_apply.py -- deterministic applier for research-scan triage dispositions.

The research-scan-triage skill (NicholasJunior) JUDGES each surfaced record and
writes a dispositions JSON; this script does everything mechanical: validates the
judgments, enforces caps, moves artifacts among Drive _triage state folders,
stamps dispositions into the manifest (local + Drive copy), and renders the owner
digest. The LLM never touches Drive mechanics directly.

Dispositions file schema (written by the triage skill):
  {
    "manifest": "manifest-20260704T201008Z.json",
    "judged_by": "NicholasJunior (research-scan-triage)",
    "entries": [
      {"id": "doi:10.2139/ssrn.6246347",
       "disposition": "wiki" | "read-once" | "discard",
       "confidence": "clear" | "ambiguous",        # default ambiguous
       "reason": "one line, cites the rubric",
       "summary": "1-2 sentence digest summary",    # for read-once (optional)
       "acquired_path": "/root/.../paper.pdf"}      # only if rung-4 acquisition succeeded
    ]
  }

Default is a DRY RUN (prints plan + digest, changes nothing). --execute performs
the Drive moves/uploads and persists the updated manifest. See
docs/research-scrape-plan.md and skills/research-scan-triage/SKILL.md.

Ambiguous judgments are never stamped as dispositions (the record stays pending
for a later clear call) but each one is appended to the record's
`proposal_history`, so the friction signal persists across re-judgments.
--friction prints a recent-ambiguity report after the digest: every ambiguous
proposal dated within the last N days (default 14), across all local manifests
regardless of manifest age. The
triage skill reads it to decide whether to append a rubric proposal to the
digest; this script only collects and counts — clustering reasons is judgment.

Examples:
  uv run scan_triage_apply.py --latest --dispositions /tmp/disp.json            # dry run
  uv run scan_triage_apply.py --manifest <path> --dispositions <path> --execute --friction
  uv run scan_triage_apply.py --friction                                        # report only
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402

DISPOSITIONS = {"wiki", "read-once", "discard"}
CONFIDENCES = {"clear", "ambiguous"}


# ---------------------------------------------------------------------------
# Pure core: validate + plan
# ---------------------------------------------------------------------------

def apply_dispositions(manifest: dict[str, Any], dispositions: dict[str, Any],
                       max_auto_wiki: int = cfg.MAX_AUTO_WIKI_PER_RUN,
                       ) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    """Validate judgments against the manifest and compute the action plan.

    Mutates a copy of the manifest (stamping disposition fields) and returns
    (manifest, plan). Fails loud on unknown or already-disposed ids; records the
    skill failed to judge are surfaced as needs_call, never guessed.
    """
    manifest = json.loads(json.dumps(manifest))  # deep copy; never mutate caller's dict
    records = {r["id"]: r for r in manifest.get("records", [])}
    pending = {rid for rid, r in records.items()
               if not r.get("disposition") or r.get("disposition_confidence") == "ambiguous"}

    entry_list = dispositions.get("entries", [])
    no_id = [i for i, e in enumerate(entry_list) if not e.get("id")]
    if no_id:
        raise ValueError(f"dispositions entries missing an id at positions: {no_id}")
    dupes = sorted(rid for rid, n in Counter(e["id"] for e in entry_list).items() if n > 1)
    if dupes:
        raise ValueError(f"duplicate ids in dispositions: {dupes}")
    entries = {e["id"]: e for e in entry_list}
    unknown = sorted(set(entries) - set(records))
    if unknown:
        raise ValueError(f"dispositions reference ids not in manifest: {unknown}")
    already = sorted(set(entries) & (set(records) - pending))
    if already:
        raise ValueError(f"dispositions reference already-disposed ids: {already}")
    bad = sorted(e["id"] for e in entries.values()
                 if e.get("disposition") not in DISPOSITIONS
                 or e.get("confidence", "ambiguous") not in CONFIDENCES)
    if bad:
        raise ValueError(f"invalid disposition/confidence for: {bad}")

    plan: dict[str, list[dict[str, Any]]] = {
        "moves": [], "uploads": [], "needs_call": [],
        "needs_acquisition": [], "read_once": [], "discard": [],
    }
    judged_by = dispositions.get("judged_by", "research-scan-triage")
    auto_wiki = 0

    for rid in sorted(pending, key=lambda i: -(records[i].get("rank_score") or 0)):
        rec = records[rid]
        item = {"id": rid, "title": rec.get("title", ""), "url": rec.get("url"),
                "acq_state": rec.get("acq_state"), "rank": rec.get("rank_score")}
        if rec.get("artifact_drive_id"):
            item["drive_file_id"] = rec["artifact_drive_id"]
        e = entries.get(rid)
        if e is None:
            plan["needs_call"].append({**item, "reason": "no judgment provided"})
            continue

        disp = e["disposition"]
        conf = e.get("confidence", "ambiguous")
        reason = e.get("reason", "")
        item["reason"] = reason

        if conf == "ambiguous":
            # Not a disposition — the record stays pending — but the friction
            # signal must survive the eventual clear re-judgment. An identical
            # judgment (same proposal/reason/judge) appends nothing, so a
            # replayed dispositions file can't inflate the friction count.
            history = rec.setdefault("proposal_history", [])
            if not any(isinstance(h, dict)
                       and (h.get("proposed"), h.get("reason"), h.get("by"))
                       == (disp, reason, judged_by)
                       for h in history):
                history.append({"at": c.utc_now_iso(), "proposed": disp,
                                "reason": reason, "by": judged_by})
            plan["needs_call"].append({**item, "proposed": disp})
            continue

        stamp = {"disposition": disp, "disposition_confidence": conf,
                 "disposition_reason": reason, "triaged_by": judged_by,
                 "triaged_at": c.utc_now_iso()}
        if disp == "discard":
            rec.update(stamp)
            plan["discard"].append(item)
        elif disp == "read-once":
            rec.update(stamp)
            plan["read_once"].append({**item, "summary": e.get("summary")
                                      or (rec.get("abstract") or "")[:280]})
        elif e.get("acquired_path"):
            rec.update(stamp)
            plan["uploads"].append({**item, "path": e["acquired_path"]})
        elif rec.get("artifact_drive_id"):
            if auto_wiki < max_auto_wiki:
                auto_wiki += 1
                rec.update(stamp)
                plan["moves"].append(item)
            else:
                plan["needs_call"].append({**item, "proposed": "wiki",
                                           "reason": f"over auto-move cap ({max_auto_wiki}); remains pending"})
        else:
            rec.update(stamp)
            plan["needs_acquisition"].append(item)

    return manifest, plan


# ---------------------------------------------------------------------------
# Pure core: digest
# ---------------------------------------------------------------------------

def render_digest(manifest: dict[str, Any], plan: dict[str, list[dict[str, Any]]],
                  executed: bool) -> str:
    """Owner-facing daily digest, action-first ordering."""
    n_records = len(manifest.get("records", []))
    mode = "executed" if executed else "DRY RUN — no Drive changes made"
    lines = [
        f"**Research scan triage — {manifest.get('generated', '')[:10]}** ({mode})",
        f"{n_records} surfaced · {len(plan['moves']) + len(plan['uploads'])} → triage/wiki · "
        f"{len(plan['needs_call'])} need your call · {len(plan['read_once'])} read-once · "
        f"{len(plan['discard'])} discarded",
    ]

    def section(title: str, items: list[dict[str, Any]], fmt) -> None:
        if items:
            lines.append(f"\n**{title}**")
            lines.extend(fmt(i) for i in items)

    section("Needs your call", plan["needs_call"],
            lambda i: f"- {i['title'][:90]} — {i.get('proposed', '?')}: "
                      f"{i.get('reason', '')} — {i.get('url', '')}")
    section("Queued to triage/wiki (auto)", plan["moves"] + plan["uploads"],
            lambda i: f"- {i['title'][:90]} — {i.get('reason', '')}")
    section("Wiki candidates — no OA copy, needs manual acquisition", plan["needs_acquisition"],
            lambda i: f"- {i['title'][:90]} — {i.get('url', '')}")
    section("Read-once", plan["read_once"],
            lambda i: f"- {i['title'][:90]}: {(i.get('summary') or '').strip()[:220]}")
    if plan["discard"]:
        lines.append(f"\n**Discarded ({len(plan['discard'])})** — "
                     + "; ".join(i["title"][:50] for i in plan["discard"]))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Pure core: rubric friction (recent-ambiguity report)
# ---------------------------------------------------------------------------

def collect_friction(manifests: list[dict[str, Any]], today: dt.date,
                     window_days: int = 14) -> list[dict[str, Any]]:
    """Ambiguous proposals from records' `proposal_history` — the rubric-friction
    signal. Each history entry carries its own timestamp (a manifest can span
    several judgment days now that ambiguous records stay pending), and history
    survives a later clear call — `resolved` shows what it became. Newest first;
    the skill clusters causes, this just collects.
    """
    cutoff = today - dt.timedelta(days=window_days)
    items = []
    for m in manifests:
        for r in m.get("records", []):
            rid = r.get("id")
            if not rid:
                continue
            for h in r.get("proposal_history") or []:
                if not isinstance(h, dict):
                    continue
                day_str = (h.get("at") or "")[:10]
                try:
                    day = dt.date.fromisoformat(day_str)
                except ValueError:
                    continue
                if day < cutoff:
                    continue
                items.append({"date": day_str, "id": rid,
                              "title": r.get("title", ""),
                              "proposed": h.get("proposed"),
                              "reason": h.get("reason", ""),
                              "url": r.get("url"),
                              "resolved": r.get("disposition")})
    items.sort(key=lambda i: (i["date"], i["id"]), reverse=True)
    return items


def render_friction(items: list[dict[str, Any]], window_days: int) -> str:
    if not items:
        return f"Rubric friction: no ambiguous proposals in the last {window_days} days.\n"
    lines = [f"**Rubric friction — {len(items)} ambiguous in the last {window_days} days**"]
    for i in items:
        line = (f"- {i['date']} · {i['title'][:80]} — proposed {i.get('proposed') or '?'}: "
                f"{(i.get('reason') or '')[:160]}")
        if i.get("resolved"):
            line += f" [later resolved: {i['resolved']}]"
        lines.append(line)
    return "\n".join(lines) + "\n"


def load_local_manifests(out_root: str, exclude: Path | None = None) -> list[dict[str, Any]]:
    manifests = []
    for mp in sorted(Path(out_root).glob("*/manifest-*.json")):
        if exclude and mp.resolve() == exclude.resolve():
            continue
        try:
            manifests.append(json.loads(mp.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return manifests


# ---------------------------------------------------------------------------
# Execution (Drive side effects)
# ---------------------------------------------------------------------------

def execute_plan(manifest: dict[str, Any], plan: dict[str, list[dict[str, Any]]],
                 manifest_path: Path, token_path: str) -> None:
    service = c.build_drive_service(token_path)
    records = {r["id"]: r for r in manifest.get("records", [])}
    for mv in plan["moves"]:
        c.drive_move(service, mv["drive_file_id"], cfg.TRIAGE_WIKI_FOLDER_ID,
                     cfg.TRIAGE_PENDING_FOLDER_ID)
        records[mv["id"]]["executed_at"] = c.utc_now_iso()
        print(f"moved -> _triage/wiki: {mv['title'][:70]}", flush=True)
    for up in plan["uploads"]:
        data = Path(up["path"]).read_bytes()
        name = Path(up["path"]).name
        fid = c.drive_upload_bytes(service, cfg.TRIAGE_WIKI_FOLDER_ID, name, data,
                                   "application/pdf")
        records[up["id"]].update({"artifact_drive_id": fid, "acq_state": "full-pdf",
                                  "executed_at": c.utc_now_iso()})
        print(f"uploaded -> _triage/wiki: {name}", flush=True)
    for bucket, folder_id, label in (
        ("read_once", cfg.TRIAGE_READ_ONCE_FOLDER_ID, "read-once"),
        ("discard", cfg.TRIAGE_DISCARDED_FOLDER_ID, "discarded"),
    ):
        for mv in plan[bucket]:
            if not mv.get("drive_file_id"):
                continue
            c.drive_move(service, mv["drive_file_id"], folder_id,
                         cfg.TRIAGE_PENDING_FOLDER_ID)
            records[mv["id"]]["executed_at"] = c.utc_now_iso()
            print(f"moved -> _triage/{label}: {mv['title'][:70]}", flush=True)

    text = json.dumps(manifest, indent=2, ensure_ascii=False)
    manifest_path.write_text(text, encoding="utf-8")
    fid = c.drive_find(service, cfg.TRIAGE_FOLDER_ID, manifest_path.name)
    if fid:
        c.drive_update_bytes(service, fid, text.encode("utf-8"), "application/json")
    else:
        c.drive_upload_text(service, cfg.TRIAGE_FOLDER_ID, manifest_path.name, text)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def find_latest_manifest(out_root: str) -> Path | None:
    """Newest local manifest that still has un-triaged records."""
    candidates = sorted(Path(out_root).glob("*/manifest-*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for p in candidates:
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if any(not r.get("disposition") or r.get("disposition_confidence") == "ambiguous"
               for r in m.get("records", [])):
            return p
    return None


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Apply triage dispositions to a scan manifest")
    p.add_argument("--manifest", default=None, help="Path to a manifest JSON")
    p.add_argument("--latest", action="store_true",
                   help=f"Use the newest unresolved manifest under {cfg.DEFAULT_OUT_ROOT}")
    p.add_argument("--dispositions", default=None,
                   help="Dispositions JSON from the triage skill (omit for --friction-only)")
    p.add_argument("--execute", action="store_true", help="Perform Drive moves/updates (default: dry run)")
    p.add_argument("--friction", action="store_true",
                   help="Print the recent-ambiguity report after the digest")
    p.add_argument("--friction-days", type=int, default=14)
    p.add_argument("--digest-out", default=None)
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--out-root", default=cfg.DEFAULT_OUT_ROOT)
    args = p.parse_args(argv)

    manifest = None
    manifest_path: Path | None = None
    if args.dispositions:
        if args.manifest:
            manifest_path = Path(args.manifest)
        elif args.latest:
            found = find_latest_manifest(args.out_root)
            if not found:
                print("No un-triaged manifest found.", file=sys.stderr)
                return 1
            manifest_path = found
        else:
            print("Provide --manifest or --latest.", file=sys.stderr)
            return 2

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        dispositions = json.loads(Path(args.dispositions).read_text(encoding="utf-8"))

        manifest, plan = apply_dispositions(manifest, dispositions)
        if args.execute:
            execute_plan(manifest, plan, manifest_path, args.token_path)

        digest = render_digest(manifest, plan, executed=args.execute)
        if args.digest_out:
            Path(args.digest_out).write_text(digest, encoding="utf-8")
        print(digest)
    elif not args.friction:
        print("Provide --dispositions (triage) and/or --friction.", file=sys.stderr)
        return 2

    if args.friction:
        manifests = load_local_manifests(args.out_root, exclude=manifest_path)
        if manifest is not None:
            manifests.append(manifest)  # current run's history, even on dry runs
        items = collect_friction(manifests, c.utc_now().date(), args.friction_days)
        print(render_friction(items, args.friction_days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
