#!/usr/bin/env python3
"""
Graph-semantic lint for the markdown research wiki.

Walks `wiki/`, parses frontmatter + `[[wikilinks]]`, and reports broken links,
orphans, claims-without-source, provenance gaps, and stale topics. Read-only:
it never edits the wiki. The old version linted the Notion layer; the wiki is
now plain markdown in git, so this operates on files.

Run:
  python scripts/research-wiki-tools/graph_lint.py            # markdown report to stdout
  python scripts/research-wiki-tools/graph_lint.py --json     # JSON findings
  python scripts/research-wiki-tools/graph_lint.py --wiki-dir /root/work/llm-research-wiki/wiki
  python scripts/research-wiki-tools/graph_lint.py --pairs               # contradiction shortlist (JSON)
  python scripts/research-wiki-tools/graph_lint.py --pairs --bootstrap --max-pairs 35  # first sweep

--pairs emits the candidate topic pairs for the monthly semantic contradiction
lint (see skills/research-wiki-graph-lint): pairs sharing >= 2 cited sources or
directly linked, change-gated to pairs where at least one member's `updated`
falls inside --window-days (a contradiction can only be introduced by an edit),
ranked by shared-source count, capped, with a few rotating tail slots so
never-checked pairs eventually get coverage. The LLM judges the shortlist; this
script only selects it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]

# schema.md is documentation full of illustrative template links; never lint its
# links/claims. READMEs are directory placeholders, not wiki pages.
SKIP_SLUGS = {"schema"}
SKIP_FILENAMES = {"README.md"}

DEFAULT_STALE_DAYS = 180

# Evidence-staleness: flag a topic when this many linked sources were retrieved
# after its last synthesis. One straggler is normal inbox lag; two+ is a queue.
EVIDENCE_STALE_MIN_SOURCES = 2

# Contradiction-pair shortlist defaults (see module docstring).
PAIR_MIN_SHARED_SOURCES = 2
DEFAULT_PAIR_WINDOW_DAYS = 35
DEFAULT_MAX_PAIRS = 15
DEFAULT_TAIL_SLOTS = 4

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Minimal YAML-ish frontmatter parse (flat key: value pairs)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, m.group(2)


def strip_code(text: str) -> str:
    """Remove fenced + inline code so template/example links aren't linted."""
    return _INLINE_CODE_RE.sub(" ", _FENCE_RE.sub(" ", text))


def extract_wikilinks(body: str) -> list[str]:
    """Wikilink targets outside code, normalised to the bare slug."""
    return [m.split("|")[0].split("#")[0].strip() for m in _WIKILINK_RE.findall(strip_code(body))]


def load_pages(wiki_dir: Path) -> list[dict[str, Any]]:
    """Parse every wiki markdown file into a page dict for build_findings."""
    pages: list[dict[str, Any]] = []
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.name in SKIP_FILENAMES:
            continue
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        rel = path.relative_to(wiki_dir)
        kind = rel.parts[0] if len(rel.parts) > 1 else "doc"  # sources | topics | doc
        kind = {"sources": "source", "topics": "topic"}.get(kind, "doc")
        pages.append(
            {
                "slug": path.stem,
                "kind": kind,
                "path": str(rel),
                "frontmatter": fm,
                "links": extract_wikilinks(body),
                "body": strip_code(body),
            }
        )
    return pages


def _parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value.strip()[:10])
    except (ValueError, AttributeError):
        return None


def topic_source_graph(pages: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Topic slug -> cited source slugs, counting a link in either direction."""
    topic_slugs = {p["slug"] for p in pages if p["kind"] == "topic"}
    source_slugs = {p["slug"] for p in pages if p["kind"] == "source"}
    cites: dict[str, set[str]] = {t: set() for t in topic_slugs}
    for p in pages:
        if p["kind"] == "topic":
            cites[p["slug"]].update(t for t in p["links"] if t in source_slugs)
        elif p["kind"] == "source":
            for t in p["links"]:
                if t in topic_slugs:
                    cites[t].add(p["slug"])
    return cites


def build_findings(
    pages: list[dict[str, Any]],
    stale_days: int = DEFAULT_STALE_DAYS,
    today: dt.date | None = None,
) -> list[dict[str, str]]:
    """Pure linter: list of pages in, list of findings out."""
    today = today or dt.date.today()
    slugs = {p["slug"] for p in pages}
    source_slugs = {p["slug"] for p in pages if p["kind"] == "source"}
    cites_map = topic_source_graph(pages)
    retrieved_dates = {p["slug"]: _parse_date(p["frontmatter"].get("retrieved", ""))
                       for p in pages if p["kind"] == "source"}
    inbound: dict[str, int] = {p["slug"]: 0 for p in pages}
    for p in pages:
        for target in p["links"]:
            if target in inbound:
                inbound[target] += 1

    findings: list[dict[str, str]] = []

    def add(severity: str, check: str, page: str, detail: str) -> None:
        findings.append({"severity": severity, "check": check, "page": page, "detail": detail})

    for p in pages:
        slug, kind, fm = p["slug"], p["kind"], p["frontmatter"]
        if slug in SKIP_SLUGS:
            continue

        # Broken wikilinks (any page).
        for target in p["links"]:
            if target not in slugs:
                add("High", "Broken wikilink", slug, f"[[{target}]] resolves to no page")

        if kind == "source":
            # Provenance: a public source needs a canonical url or doi.
            url = fm.get("url", "")
            doi = fm.get("doi", "")
            if not url and (not doi or doi.lower() == "null"):
                add("High", "Source missing public url/doi", slug, "no canonical public link in frontmatter")
            if not fm.get("file_hash"):
                add("Low", "Source missing file_hash", slug, "no provenance hash for dedup")
            if retrieved_dates.get(slug) is None:
                add("Low", "Source missing retrieved date", slug,
                    "no parseable `retrieved:` frontmatter — never counts toward evidence-staleness")
            # A source should feed at least one real topic.
            fed = [t for t in p["links"] if t in slugs]
            if not fed:
                add("Medium", "Source feeds no topic", slug, "no resolvable [[topic]] link — evidence not synthesised")

        if kind == "topic":
            if fm.get("status") == "stub":
                continue  # stubs are intentionally thin; don't flag them
            # Claims without source: an active topic that cites no source page.
            cites = [t for t in p["links"] if t in source_slugs]
            if not cites:
                add("Medium", "Topic cites no source", slug, "active topic makes claims with no [[source]] link")
            updated = _parse_date(fm.get("updated", ""))
            # Evidence-staleness: sources retrieved after the topic's last
            # synthesis. `updated` means "last synthesis edit" — mechanical
            # passes must not bump it (wiki/schema.md), or this check goes blind.
            if updated:
                newer = sorted(s for s in cites_map.get(slug, set())
                               if (rd := retrieved_dates.get(s)) and rd > updated)
                if len(newer) >= EVIDENCE_STALE_MIN_SOURCES:
                    shown = ", ".join(newer[:4]) + (", …" if len(newer) > 4 else "")
                    add("Medium", "Topic evidence-stale", slug,
                        f"{len(newer)} sources retrieved since updated {updated.isoformat()}: {shown}")
            else:
                # Without `updated:` this topic silently escapes evidence-stale,
                # calendar-stale, and the pair change-gate — surface the hole.
                add("Low", "Topic missing updated date", slug,
                    "no parseable `updated:` frontmatter — staleness checks and the pair change-gate skip this topic")
            # Calendar staleness (fallback signal; evidence-staleness is the sharper one).
            if updated and (today - updated).days > stale_days:
                add("Low", f"Topic stale > {stale_days} days", slug, f"updated {updated.isoformat()}")

        # Orphans: real wiki pages nothing links to (overview/doc pages exempt).
        if kind in ("source", "topic") and inbound.get(slug, 0) == 0:
            add("Medium", f"Orphan {kind}", slug, "no inbound wikilinks from any page")

    severity_rank = {s: i for i, s in enumerate(SEVERITY_ORDER)}
    findings.sort(key=lambda f: (severity_rank.get(f["severity"], 9), f["check"], f["page"]))
    return findings


def contradiction_pairs(
    pages: list[dict[str, Any]],
    today: dt.date | None = None,
    window_days: int = DEFAULT_PAIR_WINDOW_DAYS,
    max_pairs: int = DEFAULT_MAX_PAIRS,
    tail_slots: int = DEFAULT_TAIL_SLOTS,
    bootstrap: bool = False,
) -> dict[str, Any]:
    """Select candidate topic pairs for the semantic contradiction lint.

    Eligible: >= PAIR_MIN_SHARED_SOURCES shared cited sources (same evidence,
    synthesised twice — the contradiction mechanism) OR a direct topic<->topic
    link. Ranked by shared-source count. Normal mode change-gates to pairs where
    at least one member's `updated` is inside the window, then fills tail_slots
    from the remaining eligible pairs on a month-keyed rotation so cold pairs
    cycle through over successive monthly runs. Bootstrap ignores the gate
    (first sweep).
    """
    today = today or dt.date.today()
    if window_days < 1:
        raise ValueError("window_days must be >= 1")
    topics = {p["slug"]: p for p in pages
              if p["kind"] == "topic" and p["slug"] not in SKIP_SLUGS}
    cites = topic_source_graph(pages)

    direct: set[tuple[str, str]] = set()
    for slug, p in topics.items():
        for t in p["links"]:
            if t in topics and t != slug:
                direct.add(tuple(sorted((slug, t))))

    ordered = sorted(topics)
    eligible: list[dict[str, Any]] = []
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            shared = sorted(cites.get(a, set()) & cites.get(b, set()))
            is_direct = (a, b) in direct
            if len(shared) >= PAIR_MIN_SHARED_SOURCES or is_direct:
                eligible.append({
                    "pair": [a, b],
                    "shared_sources": len(shared),
                    "shared": shared[:8],
                    "direct_link": is_direct,
                    "updated": [topics[a]["frontmatter"].get("updated", ""),
                                topics[b]["frontmatter"].get("updated", "")],
                })
    eligible.sort(key=lambda e: (-e["shared_sources"], e["pair"]))

    if bootstrap:
        selected = eligible[:max_pairs]
        return {"mode": "bootstrap", "eligible_total": len(eligible),
                "selected": len(selected), "dropped": len(eligible) - len(selected),
                "pairs": selected}

    cutoff = today - dt.timedelta(days=window_days)
    def recently_edited(e: dict[str, Any]) -> bool:
        return any((d := _parse_date(u)) and d >= cutoff for u in e["updated"])

    gated = [e for e in eligible if recently_edited(e)]
    tail_slots = min(tail_slots, max_pairs)
    head = gated[:max_pairs - tail_slots]
    head_keys = {tuple(e["pair"]) for e in head}
    rest = [e for e in eligible if tuple(e["pair"]) not in head_keys]
    tail: list[dict[str, Any]] = []
    if rest and tail_slots:
        # Month-keyed: the cron is monthly, so each calendar month advances the
        # tail by exactly tail_slots (a window_days-keyed bucket collides with
        # the ~30-day cadence and repeats tails).
        offset = ((today.year * 12 + today.month) * tail_slots) % len(rest)
        tail = (rest + rest)[offset:offset + min(tail_slots, len(rest))]
    selected = head + tail
    return {"mode": "gated", "window_days": window_days,
            "eligible_total": len(eligible), "gated_total": len(gated),
            "selected": len(selected),
            "dropped_gated": max(0, len(gated) - len(head)),
            "pairs": selected}


def summarize_counts(findings: list[dict[str, str]]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return counts


def render_markdown(run: dict[str, Any]) -> str:
    lines = ["# Research Wiki Graph-Lint Report", ""]
    lines.append(f"- Run date: {run.get('run_date', '')}")
    lines.append(f"- Wiki dir: {run.get('wiki_dir', '')}")
    lines.append(f"- Pages checked: {run.get('pages_checked', 0)}")
    counts = run.get("summary", {})
    lines.append("")
    lines.append("## Summary")
    for s in SEVERITY_ORDER:
        lines.append(f"- {s}: {counts.get(s, 0)}")
    lines.append("")
    findings = run.get("findings", [])
    for s in SEVERITY_ORDER:
        rows = [f for f in findings if f["severity"] == s]
        if not rows:
            continue
        lines.append(f"## {s}")
        for f in rows:
            lines.append(f"- **{f['check']}** — `{f['page']}`: {f['detail']}")
        lines.append("")
    if not findings:
        lines.append("_No issues found. The wiki graph is clean._")
        lines.append("")
    return "\n".join(lines)


def _default_wiki_dir() -> Path:
    # repo_root/scripts/research-wiki-tools/graph_lint.py -> repo_root/wiki
    return Path(__file__).resolve().parents[2] / "wiki"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lint the markdown research wiki graph.")
    ap.add_argument("--wiki-dir", type=Path, default=_default_wiki_dir())
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--fail-on", choices=["never", *SEVERITY_ORDER], default="never",
                    help="exit non-zero if a finding at/above this severity exists")
    ap.add_argument("--pairs", action="store_true",
                    help="emit the contradiction-pair shortlist as JSON and exit")
    ap.add_argument("--bootstrap", action="store_true",
                    help="with --pairs: ignore the change-gate (first full sweep)")
    ap.add_argument("--window-days", type=int, default=DEFAULT_PAIR_WINDOW_DAYS)
    ap.add_argument("--max-pairs", type=int, default=DEFAULT_MAX_PAIRS)
    ap.add_argument("--tail-slots", type=int, default=DEFAULT_TAIL_SLOTS)
    args = ap.parse_args(argv)

    if not args.wiki_dir.is_dir():
        print(f"error: wiki dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2

    pages = load_pages(args.wiki_dir)

    if args.pairs:
        shortlist = contradiction_pairs(
            pages, window_days=args.window_days, max_pairs=args.max_pairs,
            tail_slots=args.tail_slots, bootstrap=args.bootstrap)
        print(json.dumps(shortlist, indent=2))
        return 0
    findings = build_findings(pages, stale_days=args.stale_days)
    run = {
        "run_date": dt.datetime.now().isoformat(timespec="seconds"),
        "wiki_dir": str(args.wiki_dir),
        "pages_checked": len(pages),
        "summary": summarize_counts(findings),
        "findings": findings,
    }
    print(json.dumps(run, indent=2) if args.json else render_markdown(run))

    if args.fail_on != "never":
        rank = {s: i for i, s in enumerate(SEVERITY_ORDER)}
        threshold = rank[args.fail_on]
        if any(rank.get(f["severity"], 9) <= threshold for f in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
