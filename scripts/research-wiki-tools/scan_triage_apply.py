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
    "manifest": "manifest-20260704T201008Z.json",   # informational; ids may span manifests
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
the Drive moves/uploads and persists the updated manifest(s). See
docs/research-scrape-plan.md and skills/research-scan-triage/SKILL.md.

The judging set is the OPEN SET (2026-09-07). The scan writes a manifest every
day, so a "newest manifest" rule stranded every record that stayed unresolved --
ambiguous, unjudged, or from a day the triage run failed: "Needs your call" reset
each morning and nothing re-judged the old ones. `--latest` now loads every local
manifest inside a --carryover-days window (default 7) that still has unresolved
records and merges them into one judging set. A dispositions file may reference
records across those manifests; each record is stamped back onto its own
manifest. The digest gains a "Carried over (age)" section plus warnings for
records that age out of the window after this run and for unresolved records
already outside it -- nothing may disappear silently.

Ambiguous judgments are never stamped as dispositions (the record stays pending
for a later clear call) but each one is appended to the record's
`proposal_history`, so the friction signal persists across re-judgments.
--friction prints a recent-ambiguity report after the digest: every ambiguous
proposal dated within the last N days (default 14), across all local manifests
regardless of manifest age. The triage skill reads it to decide whether to
append a rubric proposal to the digest; this script only collects and counts --
clustering reasons is judgment.

--amend re-disposes an ALREADY-disposed record -- the ingest rejection path: the
owner rejected a source that triage had stamped `wiki`, the PDF is already in
Drive `discarded`, but the manifest still says `wiki` and the applier refuses
to re-dispose it. The amend appends the change to the record's
`proposal_history` and moves nothing in Drive.

Examples:
  uv run scan_triage_apply.py --show-open                        # the judging set (JSON)
  uv run scan_triage_apply.py --latest --dispositions /tmp/disp.json            # dry run
  uv run scan_triage_apply.py --latest --dispositions /tmp/disp.json --execute --friction
  uv run scan_triage_apply.py --latest --carryover-days 60 --dispositions d.json  # backfill
  uv run scan_triage_apply.py --friction                                        # report only
  uv run scan_triage_apply.py --amend --drive-file-id <id> --to discard \
      --reason "owner rejected at ingest: ..." --execute
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402

DISPOSITIONS = {"wiki", "read-once", "discard"}
CONFIDENCES = {"clear", "ambiguous"}
# Friendly spellings accepted from the CLI / dispositions files; normalized
# before validation so "--to discarded" (the Drive folder name) just works.
DISPOSITION_ALIASES = {"discarded": "discard", "read_once": "read-once",
                       "readonce": "read-once", "read once": "read-once"}
DEFAULT_CARRYOVER_DAYS = 7
DEFAULT_AMEND_BY = "research-wiki-ingest"
EXIT_NO_MATCH = 3  # --amend: no manifest record matches (a hand-dropped source)

_MANIFEST_STAMP_RE = re.compile(r"manifest-(\d{4})(\d{2})(\d{2})T\d{6}Z\.json$")


def normalize_disposition(value: str | None) -> str | None:
    if value is None:
        return None
    v = str(value).strip().lower()
    return DISPOSITION_ALIASES.get(v, v)


def is_unresolved(rec: dict[str, Any]) -> bool:
    """Pending for judgment: never disposed, or only ambiguously (legacy stamp)."""
    return not rec.get("disposition") or rec.get("disposition_confidence") == "ambiguous"


# ---------------------------------------------------------------------------
# Pure core: validate + plan
# ---------------------------------------------------------------------------

def apply_dispositions(manifest: dict[str, Any], dispositions: dict[str, Any],
                       max_auto_wiki: int = cfg.MAX_AUTO_WIKI_PER_RUN,
                       ) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    """Validate judgments against the manifest and compute the action plan.

    Mutates a copy of the manifest (stamping disposition fields) and returns
    (manifest, plan). Fails loud on unknown or already-disposed ids; records the
    skill failed to judge are surfaced as needs_call, never guessed. Works the
    same on a single manifest and on the merged open set.
    """
    manifest = json.loads(json.dumps(manifest))  # deep copy; never mutate caller's dict
    records = {r["id"]: r for r in manifest.get("records", [])}
    pending = {rid for rid, r in records.items() if is_unresolved(r)}

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
    for e in entries.values():
        e["disposition"] = normalize_disposition(e.get("disposition"))
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
        item = {"id": rid, "title": c.clean_title(rec.get("title", "")), "url": rec.get("url"),
                "acq_state": rec.get("acq_state"), "rank": rec.get("rank_score"),
                "venue_tier": rec.get("venue_tier")}
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
            artifact_kind(e["acquired_path"])  # fail loud at plan time, not mid-execution
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


def outcome_by_id(plan: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    """What this run did with each judged record, for the carryover section."""
    out: dict[str, str] = {}
    for i in plan["moves"] + plan["uploads"]:
        out[i["id"]] = "→ triage/wiki"
    for i in plan["needs_acquisition"]:
        out[i["id"]] = "→ wiki (needs manual acquisition)"
    for i in plan["read_once"]:
        out[i["id"]] = "→ read-once"
    for i in plan["discard"]:
        out[i["id"]] = "→ discarded"
    for i in plan["needs_call"]:
        out[i["id"]] = "still needs your call"
    return out


# ---------------------------------------------------------------------------
# Pure core: the open set (carryover across manifests)
# ---------------------------------------------------------------------------

def manifest_date(manifest: dict[str, Any], path: Path | None = None) -> dt.date | None:
    """Surface date of a manifest: its `generated` stamp, else the filename stamp."""
    try:
        return dt.date.fromisoformat(str(manifest.get("generated") or "")[:10])
    except ValueError:
        pass
    if path is not None:
        m = _MANIFEST_STAMP_RE.search(path.name)
        if m:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def load_manifests(out_root: str) -> list[tuple[Path, dict[str, Any]]]:
    """Every parseable local manifest with its path (unparseable files skipped)."""
    out: list[tuple[Path, dict[str, Any]]] = []
    for mp in sorted(Path(out_root).glob("*/manifest-*.json")):
        try:
            out.append((mp, json.loads(mp.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def open_set(manifests: list[tuple[Path, dict[str, Any]]], today: dt.date,
             carryover_days: int = DEFAULT_CARRYOVER_DAYS) -> dict[str, Any]:
    """Split manifests that still have unresolved records into the judging
    window (`open`, oldest first) and those already outside it (`stranded`).

    Each entry: {"path", "manifest", "date", "age_days", "unresolved": [ids]}.
    A manifest with no parseable date counts as inside the window — the rule
    is that nothing drops out silently.
    """
    if carryover_days < 0:
        raise ValueError("carryover_days must be >= 0")
    cutoff = today - dt.timedelta(days=carryover_days)
    result: dict[str, Any] = {"today": today.isoformat(), "window_days": carryover_days,
                              "cutoff": cutoff.isoformat(), "open": [], "stranded": []}
    for path, m in manifests:
        unresolved = [r["id"] for r in m.get("records", []) if r.get("id") and is_unresolved(r)]
        if not unresolved:
            continue
        d = manifest_date(m, path)
        age = (today - d).days if d else None
        entry = {"path": path, "manifest": m, "date": d.isoformat() if d else None,
                 "age_days": age, "unresolved": unresolved}
        bucket = "stranded" if (age is not None and age > carryover_days) else "open"
        result[bucket].append(entry)
    for bucket in ("open", "stranded"):
        result[bucket].sort(key=lambda e: (e["date"] or "", str(e["path"])))
    return result


def merge_open_set(entries: list[dict[str, Any]], today: dt.date | None = None,
                   ) -> tuple[dict[str, Any], dict[str, Path]]:
    """One virtual manifest over EVERY record of every open manifest (disposed
    ones too, so the unknown-id / already-disposed validation keeps its
    meaning) plus id -> source manifest path. An id present in more than one
    open manifest fails loud — the dup-id rule, extended across manifests.
    `generated` is the run date (`today`) so the digest header reads as the
    day it was judged, not the surface date of whichever manifest is open."""
    merged: dict[str, Any] = {
        "generated": today.isoformat() if today else max((e["date"] or "" for e in entries), default=""),
        "open_set": [e["path"].name for e in entries],
        "records": [],
    }
    origin: dict[str, Path] = {}
    dupes: dict[str, list[Path]] = {}
    for e in entries:
        for r in e["manifest"].get("records", []):
            rid = r.get("id")
            if not rid:
                continue
            if rid in origin:
                dupes.setdefault(rid, [origin[rid]]).append(e["path"])
                continue
            origin[rid] = e["path"]
            merged["records"].append(json.loads(json.dumps(r)))
    if dupes:
        detail = "; ".join(f"{rid} in {[p.name for p in paths]}" for rid, paths in sorted(dupes.items()))
        raise ValueError(f"record id present in more than one open manifest: {detail}")
    return merged, origin


def stamp_back(merged: dict[str, Any], origin: dict[str, Path],
               entries: list[dict[str, Any]]) -> list[Path]:
    """Copy each (possibly updated) record from the merged manifest back onto
    its own manifest, in place. Returns the paths whose content changed."""
    updated = {r["id"]: r for r in merged.get("records", []) if r.get("id")}
    touched: list[Path] = []
    for e in entries:
        changed = False
        recs = e["manifest"].get("records", [])
        for i, r in enumerate(recs):
            rid = r.get("id")
            if rid and origin.get(rid) == e["path"]:
                new = updated.get(rid)
                if new is not None and new != r:
                    recs[i] = json.loads(json.dumps(new))
                    changed = True
        if changed:
            touched.append(e["path"])
    return touched


def carryover_summary(entries: list[dict[str, Any]], stranded: list[dict[str, Any]],
                      plan: dict[str, list[dict[str, Any]]],
                      window_days: int = DEFAULT_CARRYOVER_DAYS) -> dict[str, Any]:
    """Digest input: which judged records were carried over from earlier days
    (age >= 1) and what happened to them, which unresolved records age out of
    the window after this run, and how many are already stranded outside it."""
    outcome = outcome_by_id(plan)
    still_pending = {i["id"] for i in plan["needs_call"]}
    items: list[dict[str, Any]] = []
    aging: list[dict[str, Any]] = []
    for e in entries:
        age = e["age_days"]
        titles = {r.get("id"): c.clean_title(r.get("title", "")) for r in e["manifest"].get("records", [])}
        for rid in e["unresolved"]:
            if age is not None and age >= 1:
                items.append({"id": rid, "title": titles.get(rid, ""), "age_days": age,
                              "manifest": e["path"].name,
                              "outcome": outcome.get(rid, "still needs your call")})
            if age is not None and age >= window_days and rid in still_pending:
                aging.append({"id": rid, "title": titles.get(rid, ""), "age_days": age})
    stranded_ids = [rid for e in stranded for rid in e["unresolved"]]
    return {
        "window_days": window_days,
        "items": items,
        "aging_out": aging,
        "stranded": {
            "count": len(stranded_ids),
            "manifests": len(stranded),
            "oldest": min((e["date"] for e in stranded if e["date"]), default=None),
            "carryover_days_needed": max((e["age_days"] for e in stranded
                                          if e["age_days"] is not None), default=None),
        },
    }


# ---------------------------------------------------------------------------
# Pure core: digest
# ---------------------------------------------------------------------------

def render_digest(manifest: dict[str, Any], plan: dict[str, list[dict[str, Any]]],
                  executed: bool, carryover: dict[str, Any] | None = None) -> str:
    """Owner-facing daily digest, action-first ordering."""
    n_judged = sum(len(plan[k]) for k in ("moves", "uploads", "needs_call",
                                           "needs_acquisition", "read_once", "discard"))
    mode = "executed" if executed else "DRY RUN — no Drive changes made"
    if carryover and carryover.get("items"):
        n_carried = len(carryover["items"])
        head = f"{n_judged} judged ({n_judged - n_carried} new, {n_carried} carried over)"
    else:
        head = f"{n_judged} surfaced"
    lines = [
        f"**Research scan triage — {manifest.get('generated', '')[:10]}** ({mode})",
        f"{head} · {len(plan['moves']) + len(plan['uploads'])} → triage/wiki · "
        f"{len(plan['needs_call'])} need your call · {len(plan['read_once'])} read-once · "
        f"{len(plan['discard'])} discarded",
    ]
    if carryover:
        aging = carryover.get("aging_out") or []
        if aging:
            lines.append(f"⚠ {len(aging)} unresolved record(s) age out of the "
                         f"{carryover['window_days']}-day carryover window after this run — "
                         "resolve in reply or they strand: "
                         + "; ".join(i["title"][:60] for i in aging))
        st = carryover.get("stranded") or {}
        if st.get("count"):
            lines.append(f"⚠ Stranded: {st['count']} unresolved record(s) in {st['manifests']} "
                         f"manifest(s) older than the window (oldest {st.get('oldest')}) are not in "
                         f"this judging set — rerun with --carryover-days "
                         f"{st.get('carryover_days_needed')} to recover them.")

    def venue_tag(i: dict[str, Any]) -> str:
        # Only the tiers that should change the reader's mind are shown.
        return {"unlisted": " [venue: unlisted]", "unknown": " [venue: unknown]"}.get(i.get("venue_tier") or "", "")

    def section(title: str, items: list[dict[str, Any]], fmt) -> None:
        if items:
            lines.append(f"\n**{title}**")
            lines.extend(fmt(i) + venue_tag(i) for i in items)

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
    items = (carryover or {}).get("items") or []
    if items:
        lines.append(f"\n**Carried over (age)** — {len(items)} from earlier manifests")
        lines.extend(f"- {i['title'][:80]} — {i['age_days']}d ({i['manifest']}) {i['outcome']}"
                     for i in items)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Pure core: amend (the ingest rejection writeback)
# ---------------------------------------------------------------------------

def amend_disposition(manifest: dict[str, Any], rid: str, to: str, reason: str,
                      by: str = DEFAULT_AMEND_BY, now: str | None = None,
                      ) -> tuple[dict[str, Any], bool]:
    """Re-dispose a record regardless of its current disposition and append the
    change to `proposal_history` (kind: amend, amended_from). Returns (copy,
    changed); an identical clear disposition is a no-op. Pure — Drive untouched."""
    to_norm = normalize_disposition(to)
    if to_norm not in DISPOSITIONS:
        raise ValueError(f"invalid disposition {to!r}; expected one of {sorted(DISPOSITIONS)}")
    manifest = json.loads(json.dumps(manifest))
    rec = next((r for r in manifest.get("records", []) if r.get("id") == rid), None)
    if rec is None:
        raise ValueError(f"record {rid} not in manifest")
    if rec.get("disposition") == to_norm and rec.get("disposition_confidence") == "clear":
        return manifest, False
    at = now or c.utc_now_iso()
    rec.setdefault("proposal_history", []).append({
        "at": at, "kind": "amend", "amended_from": rec.get("disposition"),
        "proposed": to_norm, "reason": reason, "by": by,
    })
    rec.update({"disposition": to_norm, "disposition_confidence": "clear",
                "disposition_reason": reason, "amended_by": by, "amended_at": at})
    return manifest, True


def find_record(manifests: list[tuple[Path, dict[str, Any]]], *, rid: str | None = None,
                drive_file_id: str | None = None,
                ) -> tuple[Path, dict[str, Any], dict[str, Any]] | None:
    """Locate one record across manifests by id or artifact Drive file id
    (stable across the ingest rename/move). Two matches is an error."""
    if not rid and not drive_file_id:
        raise ValueError("find_record needs rid or drive_file_id")
    matches = []
    for path, m in manifests:
        for r in m.get("records", []):
            if (rid and r.get("id") == rid) or (drive_file_id and r.get("artifact_drive_id") == drive_file_id):
                matches.append((path, m, r))
    if len(matches) > 1:
        raise ValueError("ambiguous: record matches in " + ", ".join(p.name for p, _, _ in matches))
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# Pure core: rubric friction (recent-ambiguity report)
# ---------------------------------------------------------------------------

def collect_friction(manifests: list[dict[str, Any]], today: dt.date,
                     window_days: int = 14) -> list[dict[str, Any]]:
    """Ambiguous proposals from records' `proposal_history` — the rubric-friction
    signal. Each history entry carries its own timestamp (a manifest can span
    several judgment days now that ambiguous records stay pending), and history
    survives a later clear call — `resolved` shows what it became. Amend entries
    (kind: amend) are owner rulings, not friction, and are skipped. Newest
    first; the skill clusters causes, this just collects.
    """
    cutoff = today - dt.timedelta(days=window_days)
    items = []
    for m in manifests:
        for r in m.get("records", []):
            rid = r.get("id")
            if not rid:
                continue
            for h in r.get("proposal_history") or []:
                if not isinstance(h, dict) or h.get("kind") == "amend":
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


def load_local_manifests(out_root: str, exclude: Path | set[Path] | None = None,
                         ) -> list[dict[str, Any]]:
    excluded = {p.resolve() for p in (exclude if isinstance(exclude, set) else {exclude} if exclude else set())}
    manifests = []
    for mp in sorted(Path(out_root).glob("*/manifest-*.json")):
        if mp.resolve() in excluded:
            continue
        try:
            manifests.append(json.loads(mp.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return manifests


# ---------------------------------------------------------------------------
# Execution (Drive side effects)
# ---------------------------------------------------------------------------

# Acquired artifacts handed to the applier via `acquired_path`: a real PDF, or a
# full-text markdown render (Jina reader / rung 3) — the same two artifact
# classes the harness itself writes to _triage/pending.
ARTIFACT_KINDS = {
    ".pdf": ("application/pdf", "full-pdf"),
    ".md": ("text/markdown", "full-text"),
    ".txt": ("text/plain", "full-text"),
}


def artifact_kind(path: str | Path) -> tuple[str, str]:
    """(mime type, acq_state) for an acquired artifact, by extension; unknown
    extensions fail loud rather than being uploaded as a PDF."""
    ext = Path(path).suffix.lower()
    if ext not in ARTIFACT_KINDS:
        raise ValueError(f"unsupported acquired artifact type {ext!r} for {path}; "
                         f"expected one of {sorted(ARTIFACT_KINDS)}")
    return ARTIFACT_KINDS[ext]


def execute_drive_actions(service, manifest: dict[str, Any],
                          plan: dict[str, list[dict[str, Any]]]) -> None:
    """Perform the plan's Drive moves/uploads and stamp executed_at on records."""
    records = {r["id"]: r for r in manifest.get("records", [])}
    for mv in plan["moves"]:
        c.drive_move(service, mv["drive_file_id"], cfg.TRIAGE_WIKI_FOLDER_ID,
                     cfg.TRIAGE_PENDING_FOLDER_ID)
        records[mv["id"]]["executed_at"] = c.utc_now_iso()
        print(f"moved -> _triage/wiki: {mv['title'][:70]}", flush=True)
    for up in plan["uploads"]:
        mime, acq_state = artifact_kind(up["path"])
        data = Path(up["path"]).read_bytes()
        name = Path(up["path"]).name
        fid = c.drive_upload_bytes(service, cfg.TRIAGE_WIKI_FOLDER_ID, name, data, mime)
        records[up["id"]].update({"artifact_drive_id": fid, "acq_state": acq_state,
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


def persist_manifest(service, manifest: dict[str, Any], manifest_path: Path) -> None:
    """Write the manifest locally and update (or create) its Drive _triage copy."""
    text = json.dumps(manifest, indent=2, ensure_ascii=False)
    manifest_path.write_text(text, encoding="utf-8")
    fid = c.drive_find(service, cfg.TRIAGE_FOLDER_ID, manifest_path.name)
    if fid:
        c.drive_update_bytes(service, fid, text.encode("utf-8"), "application/json")
    else:
        c.drive_upload_text(service, cfg.TRIAGE_FOLDER_ID, manifest_path.name, text)


def execute_plan(manifest: dict[str, Any], plan: dict[str, list[dict[str, Any]]],
                 manifest_path: Path, token_path: str) -> None:
    """Single-manifest execute (explicit --manifest)."""
    service = c.build_drive_service(token_path)
    execute_drive_actions(service, manifest, plan)
    persist_manifest(service, manifest, manifest_path)


def execute_open_set(merged: dict[str, Any], plan: dict[str, list[dict[str, Any]]],
                     entries: list[dict[str, Any]], token_path: str,
                     origin: dict[str, Path] | None = None) -> list[Path]:
    """Open-set execute: Drive actions once over the merged set, then stamp
    every record back onto its own manifest and persist only those that changed."""
    if origin is None:
        _, origin = merge_open_set(entries)
    service = c.build_drive_service(token_path)
    execute_drive_actions(service, merged, plan)
    touched = stamp_back(merged, origin, entries)
    by_path = {e["path"]: e["manifest"] for e in entries}
    for path in touched:
        persist_manifest(service, by_path[path], path)
        print(f"manifest updated: {path.name}", flush=True)
    return touched


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def find_latest_manifest(out_root: str) -> Path | None:
    """Legacy single-manifest discovery (newest by mtime with unresolved
    records). The CLI judges the open set now; kept for callers/tests."""
    candidates = sorted(Path(out_root).glob("*/manifest-*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for p in candidates:
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if any(is_unresolved(r) for r in m.get("records", [])):
            return p
    return None


def _stranded_note(osr: dict[str, Any]) -> str:
    st = osr["stranded"]
    if not st:
        return ""
    n = sum(len(e["unresolved"]) for e in st)
    need = max((e["age_days"] for e in st if e["age_days"] is not None), default="?")
    return (f"{n} unresolved record(s) in {len(st)} manifest(s) older than the "
            f"{osr['window_days']}-day window; rerun with --carryover-days {need} to recover them.")


def run_show_open(args: argparse.Namespace, today: dt.date) -> int:
    osr = open_set(load_manifests(args.out_root), today, args.carryover_days)
    if osr["open"]:
        merge_open_set(osr["open"])  # validation only: fail loud on cross-manifest dup ids
    records: list[dict[str, Any]] = []
    for e in osr["open"]:
        wanted = set(e["unresolved"])
        for r in e["manifest"].get("records", []):
            if r.get("id") in wanted:
                records.append({**r, "title": c.clean_title(r.get("title", "")),
                                "_manifest": str(e["path"]), "_age_days": e["age_days"]})
    st = osr["stranded"]
    out = {
        "today": osr["today"], "window_days": osr["window_days"], "cutoff": osr["cutoff"],
        "manifests": [{"path": str(e["path"]), "date": e["date"], "age_days": e["age_days"],
                       "unresolved": len(e["unresolved"])} for e in osr["open"]],
        "records": records,
        "aging_out_after_this_run": [rid for e in osr["open"]
                                     if e["age_days"] is not None and e["age_days"] >= osr["window_days"]
                                     for rid in e["unresolved"]],
        "stranded_outside_window": {
            "count": sum(len(e["unresolved"]) for e in st),
            "manifests": len(st),
            "oldest": min((e["date"] for e in st if e["date"]), default=None),
            "carryover_days_needed": max((e["age_days"] for e in st
                                          if e["age_days"] is not None), default=None),
            "ids": [rid for e in st for rid in e["unresolved"]],
        },
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def run_amend(args: argparse.Namespace) -> int:
    if not args.to:
        print("--amend needs --to <wiki|read-once|discard>.", file=sys.stderr)
        return 2
    if not (args.id or args.drive_file_id):
        print("--amend needs --id <record id> or --drive-file-id <artifact id>.", file=sys.stderr)
        return 2
    if args.manifest:
        manifests = [(Path(args.manifest), json.loads(Path(args.manifest).read_text(encoding="utf-8")))]
    else:
        manifests = load_manifests(args.out_root)
    found = find_record(manifests, rid=args.id, drive_file_id=args.drive_file_id)
    if found is None:
        print("No manifest record matches (a source dropped into _triage/wiki by hand has no "
              "scan record — nothing to amend).", file=sys.stderr)
        return EXIT_NO_MATCH
    path, manifest, rec = found
    updated, changed = amend_disposition(manifest, rec["id"], args.to, args.reason, by=args.by)
    print(f"{rec['id']} — {rec.get('title', '')[:70]} ({path.name}): "
          f"{rec.get('disposition')} -> {normalize_disposition(args.to)}"
          + ("" if changed else " (already; no change)"))
    if not changed:
        return 0
    if args.execute:
        service = c.build_drive_service(args.token_path)
        persist_manifest(service, updated, path)
        print("manifest updated locally + Drive _triage copy; Drive artifacts untouched.")
    else:
        print("DRY RUN — add --execute to persist (local manifest + Drive copy). "
              "--amend never moves Drive artifacts.")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Apply triage dispositions to scan manifests")
    p.add_argument("--manifest", default=None, help="Path to ONE manifest JSON (explicit single-manifest mode)")
    p.add_argument("--latest", action="store_true",
                   help="Judge the open set: every manifest under --out-root within "
                        "--carryover-days that still has unresolved records")
    p.add_argument("--carryover-days", type=int, default=DEFAULT_CARRYOVER_DAYS,
                   help=f"Open-set window in days (default {DEFAULT_CARRYOVER_DAYS}); "
                        "raise it once to backfill stranded records")
    p.add_argument("--show-open", action="store_true",
                   help="Print the judging set (unresolved records across the open set) as JSON and exit")
    p.add_argument("--dispositions", default=None,
                   help="Dispositions JSON from the triage skill (omit for --friction-only)")
    p.add_argument("--execute", action="store_true", help="Perform Drive moves/updates (default: dry run)")
    p.add_argument("--friction", action="store_true",
                   help="Print the recent-ambiguity report after the digest")
    p.add_argument("--friction-days", type=int, default=14)
    p.add_argument("--digest-out", default=None)
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--out-root", default=cfg.DEFAULT_OUT_ROOT)
    amend = p.add_argument_group("amend", "re-dispose an already-disposed record (ingest rejection writeback)")
    amend.add_argument("--amend", action="store_true")
    amend.add_argument("--id", default=None, help="record id, e.g. doi:10.1234/abc")
    amend.add_argument("--drive-file-id", default=None, help="the record's artifact Drive file id")
    amend.add_argument("--to", default=None, help="new disposition: wiki | read-once | discard(ed)")
    amend.add_argument("--reason", default="", help="one line, e.g. 'owner rejected at ingest: ...'")
    amend.add_argument("--by", default=DEFAULT_AMEND_BY)
    args = p.parse_args(argv)
    today = c.utc_now().date()

    if args.amend:
        return run_amend(args)
    if args.show_open:
        return run_show_open(args, today)

    merged: dict[str, Any] | None = None
    manifest_path: Path | None = None
    entries: list[dict[str, Any]] = []
    stranded: list[dict[str, Any]] = []
    origin: dict[str, Path] = {}
    if args.dispositions:
        if args.manifest:
            manifest_path = Path(args.manifest)
            merged = json.loads(manifest_path.read_text(encoding="utf-8"))
        elif args.latest:
            osr = open_set(load_manifests(args.out_root), today, args.carryover_days)
            entries, stranded = osr["open"], osr["stranded"]
            if not entries:
                print("No unresolved manifest in the carryover window.", file=sys.stderr)
                note = _stranded_note(osr)
                if note:
                    print("Stranded: " + note, file=sys.stderr)
                return 1
            merged, origin = merge_open_set(entries, today=today)
        else:
            print("Provide --manifest or --latest.", file=sys.stderr)
            return 2

        dispositions = json.loads(Path(args.dispositions).read_text(encoding="utf-8"))
        merged, plan = apply_dispositions(merged, dispositions)
        carry = None if manifest_path else carryover_summary(entries, stranded, plan, args.carryover_days)
        if args.execute:
            if manifest_path:
                execute_plan(merged, plan, manifest_path, args.token_path)
            else:
                execute_open_set(merged, plan, entries, args.token_path, origin=origin)

        digest = render_digest(merged, plan, executed=args.execute, carryover=carry)
        if args.digest_out:
            Path(args.digest_out).write_text(digest, encoding="utf-8")
        print(digest)
    elif not args.friction:
        print("Provide --dispositions (triage), --show-open, --amend, and/or --friction.", file=sys.stderr)
        return 2

    if args.friction:
        exclude = {manifest_path} if manifest_path else {e["path"] for e in entries}
        manifests = load_local_manifests(args.out_root, exclude=exclude)
        if merged is not None:
            manifests.append(merged)  # this run's history (open set or single), even on dry runs
        items = collect_friction(manifests, today, args.friction_days)
        print(render_friction(items, args.friction_days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
