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
claim_audit.py -- the deterministic half of the monthly claim-fidelity audit
(docs/wiki-redesign-plan.md §5; the WikiCrow statement-level rubric).

  --sample   Walk the synthesis commits of the last --days (commits touching
             wiki/topics/), collect every added prose line as a candidate claim,
             draw --k of them with a month-keyed seed (re-runs in the same month
             re-draw the same sample), resolve the cited source records, and
             write the audit sheet (JSON + markdown). No judgment here.
  --record   Take the judge's grades (JSON), validate them against the sample
             (every sampled claim graded, grades from the fixed set), compute the
             counts and the supported rate, pull earlier audits from the Drive
             ledger for the trend, render the digest block, and -- with
             --execute -- store this audit in the ledger. The LLM never writes
             state; it hands grades to this script.

Grades: cited-supported | cited-unsupported | uncited | reasoning-error.
State lives in Drive _triage/ledger/claim_audit-<UTCSTAMP>.json (external, like
the scan manifests) -- nothing new in git.

  uv run claim_audit.py --sample --out /root/research-wiki-runs/audit-202610
  uv run claim_audit.py --record /root/research-wiki-runs/audit-202610/grades.json --execute
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan_common as c  # noqa: E402
import scan_config as cfg  # noqa: E402

GRADES = ("cited-supported", "cited-unsupported", "uncited", "reasoning-error")
DEFAULT_DAYS = 35
DEFAULT_K = 10
MIN_CLAIM_CHARS = 60
RECORD_PREFIX = "claim_audit"

_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
_FRONTMATTER_KEYS = ("title:", "status:", "updated:", "---")


# ---------------------------------------------------------------------------
# Pure core: candidates, sampling, validation, summary
# ---------------------------------------------------------------------------

def stamp_date(stamp: str) -> str:
    """'20261001T160000Z' -> '2026-10-01' (a bare 'YYYY-MM' or date passes through)."""
    s = str(stamp or "")
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) >= 8 and s[:8].isdigit() else s[:10]


def claim_id(commit: str, topic: str, text: str) -> str:
    return hashlib.sha1(f"{commit}\n{topic}\n{text[:160]}".encode("utf-8")).hexdigest()[:10]


def extract_added_claims(diff_text: str, commit: str, date: str, source_slugs: set[str],
                         topic_slugs: set[str]) -> list[dict[str, Any]]:
    """Added prose lines from a `git show --unified=0` over wiki/topics/.

    A candidate is an added line of body prose (not frontmatter, not a heading,
    not blank) that either cites at least one source record or carries no
    wikilink at all (an uncited claim). Lines whose only links are topic links
    (Connections bullets) are navigation, not claims, and are skipped."""
    out: list[dict[str, Any]] = []
    topic = None
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            m = re.search(r"wiki/topics/([^/]+)\.md$", line)
            topic = m.group(1) if m else None
            continue
        if topic is None or not line.startswith("+") or line.startswith("++"):
            continue
        text = line[1:].strip()
        if not text or text.startswith("#") or any(text.startswith(k) for k in _FRONTMATTER_KEYS):
            continue
        body = text.lstrip("-*> ").strip()
        if len(body) < MIN_CLAIM_CHARS:
            continue
        links = [l.strip() for l in _WIKILINK_RE.findall(body)]
        cited = [l for l in links if l in source_slugs]
        only_topic_links = links and not cited and all(l in topic_slugs for l in links)
        if only_topic_links:
            continue
        out.append({"id": claim_id(commit, topic, body), "topic": topic, "commit": commit[:10],
                    "date": date, "text": body, "cited_sources": cited, "uncited": not cited})
    return out


def dedupe(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out = []
    for cl in claims:
        if cl["id"] in seen:
            continue
        seen.add(cl["id"]); out.append(cl)
    return out


def sample_claims(candidates: list[dict[str, Any]], k: int, seed: str) -> list[dict[str, Any]]:
    """Deterministic sample: the same (candidates, seed) always yields the same
    claims, in a stable order (by topic, then text)."""
    if k <= 0 or not candidates:
        return []
    ordered = sorted(candidates, key=lambda cl: (cl["topic"], cl["text"]))
    rng = random.Random(seed)
    picked = rng.sample(ordered, min(k, len(ordered)))
    return sorted(picked, key=lambda cl: (cl["topic"], cl["text"]))


def validate_grades(sample: list[dict[str, Any]], grades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every sampled claim graded exactly once with a known grade; returns the
    grades joined to their claims. Fails loud on anything else."""
    by_id = {cl["id"]: cl for cl in sample}
    seen: dict[str, dict[str, Any]] = {}
    problems = []
    for g in grades:
        cid = g.get("id")
        if cid not in by_id:
            problems.append(f"grade for unknown claim id {cid!r}")
            continue
        if cid in seen:
            problems.append(f"claim {cid} graded twice")
            continue
        if g.get("grade") not in GRADES:
            problems.append(f"claim {cid}: grade {g.get('grade')!r} not in {list(GRADES)}")
            continue
        seen[cid] = g
    missing = [cid for cid in by_id if cid not in seen]
    if missing:
        problems.append(f"ungraded claims: {missing}")
    if problems:
        raise ValueError("; ".join(problems))
    return [{**by_id[cid], "grade": g["grade"], "note": (g.get("note") or "")[:400],
             "evidence": (g.get("evidence") or "")[:400]} for cid, g in seen.items()]


def summarize(graded: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {g: 0 for g in GRADES}
    for row in graded:
        counts[row["grade"]] += 1
    n = len(graded)
    return {"n": n, "counts": counts,
            "supported_rate": round(counts["cited-supported"] / n, 3) if n else None}


def render_digest(summary: dict[str, Any], history: list[dict[str, Any]], graded: list[dict[str, Any]],
                  window_days: int, candidates_total: int, executed: bool) -> str:
    c_ = summary["counts"]
    rate = summary["supported_rate"]
    lines = [f"**Claim-fidelity audit — {stamp_date(summary.get('stamp', ''))}** "
             f"({'recorded' if executed else 'DRY RUN — not recorded'})",
             f"{summary['n']} claims sampled from {candidates_total} added in the last {window_days} days · "
             f"supported {c_['cited-supported']} · unsupported {c_['cited-unsupported']} · "
             f"uncited {c_['uncited']} · reasoning errors {c_['reasoning-error']} · "
             f"supported rate {int(rate * 100) if rate is not None else '—'}%"]
    if history:
        trend = " → ".join(f"{stamp_date(h['stamp'])[:7]}: {int((h.get('supported_rate') or 0) * 100)}%"
                           for h in history[-3:])
        lines.append(f"Trend (supported rate, last audits): {trend} → now {int(rate * 100) if rate is not None else '—'}%")
    flagged = [r for r in graded if r["grade"] != "cited-supported"]
    if flagged:
        lines.append("\n**Needs a look** (owner: spot-check at least 2 graded claims, including these)")
        for r in flagged:
            lines.append(f"- [{r['grade']}] `{r['topic']}` — “{r['text'][:140]}…” — {r['note'][:160]}")
    lines.append("\n**All graded claims**")
    for r in graded:
        src = ", ".join(f"[[{s}]]" for s in r["cited_sources"]) or "(no citation)"
        lines.append(f"- {r['id']} · {r['grade']} · `{r['topic']}` ← {src}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Git / wiki side
# ---------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True, timeout=120).stdout


def collect_candidates(repo: Path, since: dt.date) -> tuple[list[dict[str, Any]], list[str]]:
    wiki = repo / "wiki"
    source_slugs = {p.stem for p in (wiki / "sources").rglob("*.md")}
    topic_slugs = {p.stem for p in (wiki / "topics").glob("*.md")}
    log = _git(repo, "log", f"--since={since.isoformat()}", "--format=%H|%cs", "--", "wiki/topics")
    commits = [ln.split("|") for ln in log.splitlines() if "|" in ln]
    claims: list[dict[str, Any]] = []
    for sha, date in commits:
        diff = _git(repo, "show", "--format=", "--unified=0", sha, "--", "wiki/topics")
        claims.extend(extract_added_claims(diff, sha, date, source_slugs, topic_slugs))
    return dedupe(claims), [s for s, _ in commits]


def resolve_sources(repo: Path, slugs: set[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for md in (repo / "wiki" / "sources").rglob("*.md"):
        if md.stem not in slugs:
            continue
        head = md.read_text(encoding="utf-8")[:2000]
        def field(k: str) -> str | None:
            m = re.search(rf"^{k}:\s*(.+?)\s*$", head, re.M)
            return m.group(1).strip().strip('"') if m else None
        out[md.stem] = {"path": str(md.relative_to(repo)), "title": field("title"), "url": field("url"),
                        "doi": field("doi"), "drive_file_id": field("drive_file_id"),
                        "human_reviewed": field("human_reviewed")}
    return out


def render_sheet(sample: list[dict[str, Any]], sources: dict[str, dict[str, Any]], meta: dict[str, Any]) -> str:
    lines = [f"# Claim-fidelity audit sheet — {stamp_date(meta['stamp'])}",
             f"{len(sample)} sampled of {meta['candidates_total']} candidate claims added in the last "
             f"{meta['window_days']} days ({meta['commits']} synthesis commits); seed `{meta['seed']}`.", ""]
    for i, cl in enumerate(sample, 1):
        lines.append(f"## {i}. `{cl['id']}` — {cl['topic']} ({cl['date']}, {cl['commit']})")
        lines.append(f"> {cl['text']}")
        if cl["cited_sources"]:
            for s in cl["cited_sources"]:
                src = sources.get(s, {})
                lines.append(f"- source [[{s}]] — {src.get('title') or ''} — {src.get('url') or src.get('doi') or ''} — "
                             f"Drive `{src.get('drive_file_id') or '?'}`")
        else:
            lines.append("- (no citation — grade `uncited` unless the surrounding paragraph cites it)")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Drive ledger (external state)
# ---------------------------------------------------------------------------

def load_history(service) -> list[dict[str, Any]]:
    names = c.drive_list_names(service, cfg.TRIAGE_LEDGER_FOLDER_ID, RECORD_PREFIX)
    out = []
    for name in sorted(names):
        if not name.startswith(RECORD_PREFIX + "-"):
            continue
        try:
            rec = json.loads(c.drive_download_text(service, names[name]))
            out.append({"stamp": rec.get("stamp", name), "n": rec.get("summary", {}).get("n"),
                        "supported_rate": rec.get("summary", {}).get("supported_rate")})
        except Exception:  # noqa: BLE001
            continue
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Monthly claim-fidelity audit: sample + record")
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--sample", action="store_true", help="Draw this month's sample and write the sheet")
    p.add_argument("--record", default=None, metavar="GRADES_JSON", help="Validate grades and render/record the audit")
    p.add_argument("--out", default=None, help="Run dir for sample.json / sheet.md (default: <out-root>/audit-YYYYMM)")
    p.add_argument("--days", type=int, default=DEFAULT_DAYS)
    p.add_argument("--k", type=int, default=DEFAULT_K)
    p.add_argument("--seed", default=None, help="Sampling seed (default: YYYY-MM, so a month re-samples identically)")
    p.add_argument("--execute", action="store_true", help="With --record: store the audit in the Drive ledger")
    p.add_argument("--no-drive", action="store_true", help="With --record: skip the Drive trend lookup/upload")
    p.add_argument("--token-path", default=cfg.DEFAULT_TOKEN_PATH)
    p.add_argument("--out-root", default=cfg.DEFAULT_OUT_ROOT)
    args = p.parse_args(argv)

    today = c.utc_now().date()
    stamp = c.utc_now_stamp()
    out_dir = Path(args.out or (Path(args.out_root) / f"audit-{today.strftime('%Y%m')}"))
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.sample:
        since = today - dt.timedelta(days=args.days)
        candidates, commits = collect_candidates(args.repo, since)
        seed = args.seed or today.strftime("%Y-%m")
        sample = sample_claims(candidates, args.k, seed)
        sources = resolve_sources(args.repo, {s for cl in sample for s in cl["cited_sources"]})
        meta = {"stamp": stamp, "window_days": args.days, "since": since.isoformat(), "seed": seed,
                "candidates_total": len(candidates), "commits": len(commits), "k": args.k}
        (out_dir / "sample.json").write_text(json.dumps({"meta": meta, "sample": sample, "sources": sources},
                                                        indent=2, ensure_ascii=False), encoding="utf-8")
        sheet = render_sheet(sample, sources, meta)
        (out_dir / "sheet.md").write_text(sheet, encoding="utf-8")
        print(sheet)
        print(f"\nwrote {out_dir / 'sample.json'} and sheet.md")
        return 0

    if args.record:
        sample_file = out_dir / "sample.json"
        if not sample_file.exists():
            print(f"no sample at {sample_file}; run --sample first", file=sys.stderr)
            return 2
        data = json.loads(sample_file.read_text(encoding="utf-8"))
        grades = json.loads(Path(args.record).read_text(encoding="utf-8"))
        grades = grades.get("grades", grades) if isinstance(grades, dict) else grades
        graded = validate_grades(data["sample"], grades)
        summary = {**summarize(graded), "stamp": stamp}
        history: list[dict[str, Any]] = []
        service = None
        if not args.no_drive:
            service = c.build_drive_service(args.token_path)
            history = load_history(service)
        record = {"stamp": stamp, "meta": data["meta"], "summary": summary, "graded": graded}
        (out_dir / f"{RECORD_PREFIX}-{stamp}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False),
                                                              encoding="utf-8")
        executed = False
        if args.execute and service is not None:
            c.drive_upload_text(service, cfg.TRIAGE_LEDGER_FOLDER_ID, f"{RECORD_PREFIX}-{stamp}.json",
                                json.dumps(record, indent=2, ensure_ascii=False))
            executed = True
        print(render_digest(summary, history, graded, data["meta"]["window_days"],
                            data["meta"]["candidates_total"], executed))
        return 0

    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
