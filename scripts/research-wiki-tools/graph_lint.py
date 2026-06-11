#!/usr/bin/env python3
"""
Read-only graph-semantic lint for Nicholas's public research wiki Notion layer.

The script reads canonical operating pages and database rows, emits a markdown
report plus machine-readable JSON, and performs no Notion mutations.

Run:
  python scripts/research-wiki-tools/graph_lint.py --max-pages 100
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib import error, request

NOTION_VERSION = "2025-09-03"
DEFAULT_OUT_ROOT = "/root/research-wiki-runs"

CANONICAL_PAGES = {
    "Schema": "36accc4a-237c-81a9-8de2-c667d2a95796",
    "Agent Operating Guide": "36bccc4a-237c-813c-b884-c89702815b03",
    "Research Map / Overview": "37cccc4a-237c-81cc-b455-ff673f15e97c",
}

DATA_SOURCES = {
    "Sources": "2491c01c-8c1d-42b7-9272-ab235ea64586",
    "Concepts": "f578eaf9-81bb-4668-8bdc-191fdea8e5f1",
    "Reviews": "eb454605-2dea-4b8b-a173-407be60184ed",
    "Inbox": "56bea68b-7a43-4494-bf80-23f15202ef1c",
}

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]
OPEN_STATUS_WORDS = {"new", "todo", "to do", "pending", "needs review", "needs-review", "triage", "untriaged", "blocked", "in progress", "draft"}
CLOSED_STATUS_WORDS = {"done", "complete", "completed", "applied", "archived", "exclude", "excluded", "closed", "processed", "promoted"}
WEAK_EVIDENCE_WORDS = {"weak", "low", "single", "thin", "mixed", "uncertain", "unknown"}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_stamp() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def normalize_id(notion_id: str) -> str:
    s = notion_id.replace("-", "")
    if len(s) == 32:
        return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"
    return notion_id


def normalize_text(s: str | None) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"\b(the|a|an|pdf|draft|copy|final)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


class NotionClient:
    def __init__(self, token: str):
        self.token = token

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"https://api.notion.com/v1/{path.lstrip('/')}",
            data=body,
            method=method,
            headers=notion_headers(self.token),
        )
        try:
            with request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed Notion API host
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Notion {method} {path} failed: HTTP {e.code}: {detail}") from e

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"pages/{normalize_id(page_id)}")

    def block_children_sample(self, block_id: str, page_size: int = 10) -> dict[str, Any]:
        return self.request("GET", f"blocks/{normalize_id(block_id)}/children?page_size={page_size}")

    def query_data_source(self, data_source_id: str, max_pages: int | None = None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        cursor = None
        while True:
            payload: dict[str, Any] = {"page_size": min(100, max_pages or 100)}
            if cursor:
                payload["start_cursor"] = cursor
            res = self.request("POST", f"data_sources/{normalize_id(data_source_id)}/query", payload)
            rows.extend(res.get("results", []))
            if max_pages and len(rows) >= max_pages:
                return rows[:max_pages]
            if not res.get("has_more"):
                return rows
            cursor = res.get("next_cursor")


def rich_text_plain(items: list[dict[str, Any]] | None) -> str:
    return "".join((item.get("plain_text") or "") for item in (items or []))


def prop_text(prop: dict[str, Any]) -> str:
    typ = prop.get("type")
    if typ == "title":
        return rich_text_plain(prop.get("title"))
    if typ == "rich_text":
        return rich_text_plain(prop.get("rich_text"))
    if typ == "url":
        return prop.get("url") or ""
    if typ == "email":
        return prop.get("email") or ""
    if typ == "phone_number":
        return prop.get("phone_number") or ""
    if typ == "select":
        return (prop.get("select") or {}).get("name") or ""
    if typ == "status":
        return (prop.get("status") or {}).get("name") or ""
    if typ == "multi_select":
        return ", ".join(x.get("name", "") for x in prop.get("multi_select", []))
    if typ == "number":
        n = prop.get("number")
        return "" if n is None else str(n)
    if typ == "checkbox":
        return "true" if prop.get("checkbox") else "false"
    if typ == "date":
        d = prop.get("date") or {}
        return d.get("start") or ""
    if typ == "relation":
        return ", ".join(x.get("id", "") for x in prop.get("relation", []))
    if typ == "formula":
        return prop_text(prop.get("formula") or {})
    if typ == "rollup":
        roll = prop.get("rollup") or {}
        if roll.get("type") == "array":
            return ", ".join(prop_text(x) for x in roll.get("array", []))
        return prop_text(roll)
    return ""


def title_for_page(page: dict[str, Any]) -> str:
    for prop in (page.get("properties") or {}).values():
        if prop.get("type") == "title":
            txt = prop_text(prop).strip()
            if txt:
                return txt
    return "Untitled"


def page_url(page: dict[str, Any]) -> str:
    return page.get("url") or f"https://www.notion.so/{page.get('id', '').replace('-', '')}"


def relation_count(page: dict[str, Any], name_words: list[str]) -> int:
    total = 0
    for name, prop in (page.get("properties") or {}).items():
        if prop.get("type") != "relation":
            continue
        lname = name.lower()
        if any(word in lname for word in name_words):
            total += len(prop.get("relation", []))
    return total


def first_prop_text(page: dict[str, Any], name_words: list[str]) -> str:
    for name, prop in (page.get("properties") or {}).items():
        lname = name.lower()
        if any(word in lname for word in name_words):
            txt = prop_text(prop).strip()
            if txt:
                return txt
    return ""


def all_prop_text(page: dict[str, Any]) -> str:
    return "\n".join(prop_text(p) for p in (page.get("properties") or {}).values())


def date_from_page(page: dict[str, Any]) -> dt.datetime | None:
    candidates = [page.get("last_edited_time"), page.get("created_time")]
    for words in (["updated", "modified", "processed", "date"], ["created", "added"]):
        txt = first_prop_text(page, words)
        if txt:
            candidates.insert(0, txt)
    for raw in candidates:
        if not raw:
            continue
        try:
            s = str(raw).replace("Z", "+00:00")
            return dt.datetime.fromisoformat(s if "T" in s else f"{s}T00:00:00+00:00")
        except ValueError:
            continue
    return None


def is_closed_or_archived(page: dict[str, Any]) -> bool:
    """Return true for records that should not create active lint work."""
    if page.get("archived") or page.get("in_trash"):
        return True
    status = first_prop_text(page, ["status", "state"]).lower()
    title = title_for_page(page).lower()
    hay = f"{status}\n{title}"
    return any(word in hay for word in CLOSED_STATUS_WORDS)


def make_finding(severity: str, category: str, check: str, page: dict[str, Any], why: str, recommendation: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "category": category,
        "check": check,
        "title": title_for_page(page),
        "page_id": page.get("id"),
        "url": page_url(page),
        "why": why,
        "recommendation": recommendation,
    }


def duplicate_findings(rows: list[dict[str, Any]], database: str, field_words: list[str], label: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        raw = first_prop_text(row, field_words) if field_words else title_for_page(row)
        key = normalize_text(raw)
        if key and len(key) >= 8:
            buckets[key].append(row)
    findings = []
    for _key, pages in buckets.items():
        if len(pages) < 2:
            continue
        exemplar = pages[0]
        names = "; ".join(f"{title_for_page(p)} ({p.get('id')})" for p in pages[:6])
        findings.append(make_finding(
            "Medium",
            "Structural graph integrity",
            f"Duplicate {database} by {label}",
            exemplar,
            f"Potential duplicate records share normalized {label}: {names}",
            "Review duplicates before promotion; merge only through approved canonical update path.",
        ))
    return findings


def build_findings(records: dict[str, list[dict[str, Any]]], stale_days: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    sources = records.get("Sources", [])
    concepts = records.get("Concepts", [])
    reviews = records.get("Reviews", [])
    inbox = records.get("Inbox", [])

    for concept in concepts:
        if relation_count(concept, ["source", "evidence", "citation"]) == 0:
            findings.append(make_finding(
                "High", "Structural graph integrity", "Concept has no linked Sources", concept,
                "A canonical Concept without source/evidence links can become unsupported wiki memory.",
                "Add source relations or route through a Candidate Concept Update Bundle if the Concept should be revised.",
            ))
        text = all_prop_text(concept).lower()
        if any(w in text for w in WEAK_EVIDENCE_WORDS) and not first_prop_text(concept, ["confidence", "evidence status", "contested"]):
            findings.append(make_finding(
                "Medium", "Confidence / contested signals", "Weak-evidence Concept lacks explicit confidence signal", concept,
                "The Concept appears to contain weak/mixed/thin evidence language but no obvious confidence or contested property is populated.",
                "Add explicit confidence/contested signal or create a Review/Gap Map to resolve evidence status.",
            ))

    for source in sources:
        if relation_count(source, ["concept"]) == 0:
            findings.append(make_finding(
                "High", "Structural graph integrity", "Source has no linked Concepts", source,
                "A canonical Source disconnected from Concepts is less likely to compound into the wiki graph.",
                "Link to existing Concepts, create candidate Concepts, or mark as staging/supporting source.",
            ))
        doi = first_prop_text(source, ["doi"])
        url = first_prop_text(source, ["canonical url", "url", "link", "provenance"])
        if not doi and not url:
            findings.append(make_finding(
                "Medium", "Provenance and evidence quality", "Source lacks DOI/canonical URL signal", source,
                "The Source has no obvious DOI, URL, link, or provenance property populated.",
                "Resolve public provenance before relying on this Source for promoted claims.",
            ))

    for review in reviews:
        if is_closed_or_archived(review):
            continue
        reviewed_sources = relation_count(review, ["reviewed source", "source"])
        related_concepts = relation_count(review, ["related concept", "concept"])
        text = all_prop_text(review).lower()
        if reviewed_sources == 0:
            findings.append(make_finding(
                "High", "Review and promotion workflow health", "Review has no Reviewed Sources", review,
                "A Review without source relations has weak traceability.",
                "Attach Reviewed Sources or mark the artifact as exploratory/non-canonical.",
            ))
        if related_concepts == 0 and any(word in text for word in ["concept", "construct", "claim", "update"]):
            findings.append(make_finding(
                "Medium", "Review and promotion workflow health", "Review appears concept-bearing but has no Related Concepts", review,
                "The Review mentions concepts/constructs/updates but has no obvious Concept relation.",
                "Link Related Concepts or prepare a Candidate Concept Update Bundle.",
            ))
        if "candidate concept" in text and "bundle" not in text:
            findings.append(make_finding(
                "Medium", "Review and promotion workflow health", "Review proposes Concept updates without bundle signal", review,
                "The Review appears to propose Concept work but lacks a visible Candidate Concept Update Bundle signal.",
                "Create or attach a Candidate Concept Update Bundle before canonical Concept mutation.",
            ))

    cutoff = utc_now() - dt.timedelta(days=stale_days)
    for item in inbox:
        if is_closed_or_archived(item):
            continue
        status = first_prop_text(item, ["status", "state"]).lower()
        item_date = date_from_page(item)
        if not status:
            findings.append(make_finding(
                "Medium", "Staleness and drift", "Inbox item has no visible processing status", item,
                "Inbox items need explicit status to avoid silent accumulation.",
                "Set a processing status or archive/exclude if no longer relevant.",
            ))
        elif item_date and item_date < cutoff and not any(word in status for word in CLOSED_STATUS_WORDS):
            findings.append(make_finding(
                "Medium", "Staleness and drift", f"Inbox item older than {stale_days} days remains open", item,
                f"Status is `{status}` and date signal is {item_date.date().isoformat()}.",
                "Triage, promote to Review/Source workflow, or explicitly archive/exclude.",
            ))

    findings.extend(duplicate_findings(sources, "Sources", ["doi"], "DOI"))
    findings.extend(duplicate_findings(sources, "Sources", ["canonical url", "url", "link"], "canonical URL"))
    findings.extend(duplicate_findings(sources, "Sources", [], "title"))
    findings.extend(duplicate_findings(concepts, "Concepts", [], "title"))

    return findings


def summarize_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(f["severity"] for f in findings)
    return {sev: counts.get(sev, 0) for sev in SEVERITY_ORDER}


def render_markdown(run: dict[str, Any]) -> str:
    findings = run["findings"]
    counts = run["summary"]
    lines = [
        "# Research Wiki Graph-Lint Report",
        "",
        "## Run metadata",
        f"- Run date: {run['run_date']}",
        "- Mode: read-only",
        f"- Scope: {run['scope']}",
        f"- Databases checked: {', '.join(run['databases_checked'])}",
        f"- Canonical pages checked: {', '.join(run['canonical_pages_checked'])}",
        "",
        "## Executive summary",
        *[f"- {sev}: {counts.get(sev, 0)}" for sev in SEVERITY_ORDER],
        "",
    ]
    for sev in SEVERITY_ORDER:
        title = {
            "Critical": "Critical issues",
            "High": "High-priority issues",
            "Medium": "Medium-priority issues",
            "Low": "Low-priority housekeeping",
        }[sev]
        lines.extend([f"## {title}", ""])
        sev_findings = [f for f in findings if f["severity"] == sev]
        if not sev_findings:
            lines.extend(["None found in automated checks.", ""])
            continue
        for f in sev_findings:
            lines.extend([
                f"### {f['check']}: {f['title']}",
                f"- Category: {f['category']}",
                f"- Page: {f['url']}",
                f"- Why it matters: {f['why']}",
                f"- Recommended action: {f['recommendation']}",
                "",
            ])
    lines.extend([
        "## Candidate Concept Update Bundle queue",
        "Route any canonical Concept mutations implied by findings through a Candidate Concept Update Bundle before applying changes.",
        "",
        "## Suggested Review / Gap Map queue",
        "Prioritize High findings with missing Reviewed Sources or unsupported Concepts.",
        "",
        "## Suggested Schema / Research Map pressure",
        "Automated checks do not yet infer taxonomy pressure; inspect repeated tags/domain_cluster_candidate values in follow-up runs.",
        "",
        "## Automation readiness notes",
        "This is a read-only lint. Do not enable apply-mode cleanup until duplicate/provenance/status findings are reviewed.",
        "",
        "## Recommended next actions",
        "1. Review High findings first.",
        "2. Resolve duplicate/provenance issues before relying on affected records for synthesis.",
        "3. Convert Concept-changing recommendations into Candidate Concept Update Bundles.",
    ])
    return "\n".join(lines) + "\n"


def run_lint(client: NotionClient, *, max_pages: int | None, stale_days: int) -> dict[str, Any]:
    canonical_checked = []
    for name, page_id in CANONICAL_PAGES.items():
        page = client.retrieve_page(page_id)
        client.block_children_sample(page_id, page_size=5)
        canonical_checked.append(f"{name} ({page.get('id')})")

    records = {name: client.query_data_source(ds_id, max_pages=max_pages) for name, ds_id in DATA_SOURCES.items()}
    findings = build_findings(records, stale_days=stale_days)
    return {
        "run_date": utc_now().isoformat(),
        "mode": "read-only",
        "scope": f"Sources, Concepts, Reviews, Inbox; max_pages={max_pages or 'all'}; stale_days={stale_days}",
        "databases_checked": list(records.keys()),
        "canonical_pages_checked": canonical_checked,
        "record_counts": {name: len(rows) for name, rows in records.items()},
        "summary": summarize_counts(findings),
        "findings": findings,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run read-only graph lint against research-wiki Notion databases")
    parser.add_argument("--notion-token-env", default="NOTION_API_KEY", help="Environment variable containing Notion token")
    parser.add_argument("--max-pages", type=int, default=None, help="Max rows per database for smoke tests")
    parser.add_argument("--stale-days", type=int, default=30, help="Inbox open-item stale threshold")
    parser.add_argument("--out-root", default=DEFAULT_OUT_ROOT, help="Output root for lint run artifacts")
    parser.add_argument("--stdout", action="store_true", help="Also print markdown report to stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    token = os.environ.get(args.notion_token_env)
    if not token:
        print(json.dumps({"status": "invalid", "errors": [f"{args.notion_token_env} is not set"]}, indent=2), file=sys.stderr)
        return 2

    run = run_lint(NotionClient(token), max_pages=args.max_pages, stale_days=args.stale_days)
    out_dir = Path(args.out_root) / f"graph-lint-{utc_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = render_markdown(run)
    (out_dir / "graph_lint.json").write_text(json.dumps(run, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": "success", "out_dir": str(out_dir), "record_counts": run["record_counts"], "summary": run["summary"]}, indent=2, sort_keys=True))
    if args.stdout:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
