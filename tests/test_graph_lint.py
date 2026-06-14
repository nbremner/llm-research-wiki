import datetime as dt
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools" / "graph_lint.py"
spec = importlib.util.spec_from_file_location("graph_lint", MODULE_PATH)
assert spec is not None and spec.loader is not None
graph_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph_lint)


def source(slug, links=None, url="https://example.org/x", doi="null", file_hash="abc123"):
    fm = {"source_type": "paper", "url": url, "doi": doi, "file_hash": file_hash}
    return {"slug": slug, "kind": "source", "path": f"sources/{slug}.md", "frontmatter": fm, "links": links or [], "body": ""}


def topic(slug, links=None, status="active", updated="2026-06-14"):
    fm = {"status": status, "updated": updated}
    return {"slug": slug, "kind": "topic", "path": f"topics/{slug}.md", "frontmatter": fm, "links": links or [], "body": ""}


def doc(slug, links=None):
    return {"slug": slug, "kind": "doc", "path": f"{slug}.md", "frontmatter": {}, "links": links or [], "body": ""}


def test_clean_graph_has_no_findings():
    pages = [
        doc("overview", links=["ai-adoption"]),
        topic("ai-adoption", links=["2026-kim"]),
        source("2026-kim", links=["ai-adoption"]),
    ]
    assert graph_lint.build_findings(pages, today=dt.date(2026, 6, 15)) == []


def test_broken_wikilink_flagged():
    pages = [topic("ai-adoption", links=["2026-kim", "nonexistent"]), source("2026-kim", links=["ai-adoption"]),
             doc("overview", links=["ai-adoption"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    broken = [f for f in findings if f["check"] == "Broken wikilink"]
    assert broken and broken[0]["page"] == "ai-adoption"
    assert graph_lint.summarize_counts(findings)["High"] >= 1


def test_orphan_and_feeds_no_topic():
    # source links to nothing, and nothing links to it
    pages = [source("2026-orphan", links=[]), topic("ai-adoption", links=["2026-other"]),
             source("2026-other", links=["ai-adoption"]), doc("overview", links=["ai-adoption"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    checks = {(f["check"], f["page"]) for f in findings}
    assert ("Orphan source", "2026-orphan") in checks
    assert ("Source feeds no topic", "2026-orphan") in checks


def test_topic_cites_no_source():
    pages = [topic("lonely-topic", links=[]), doc("overview", links=["lonely-topic"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert any(f["check"] == "Topic cites no source" for f in findings)


def test_stub_topic_not_flagged_for_no_source():
    pages = [topic("stub-topic", links=[], status="stub"), doc("overview", links=["stub-topic"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert not any(f["check"] == "Topic cites no source" for f in findings)


def test_missing_provenance_and_hash():
    pages = [source("2026-noprov", links=["ai-adoption"], url="", doi="null", file_hash=""),
             topic("ai-adoption", links=["2026-noprov"]), doc("overview", links=["ai-adoption"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    checks = {f["check"] for f in findings}
    assert "Source missing public url/doi" in checks
    assert "Source missing file_hash" in checks


def test_stale_topic_flagged():
    pages = [topic("old-topic", links=["2026-kim"], updated="2025-01-01"), source("2026-kim", links=["old-topic"]),
             doc("overview", links=["old-topic"])]
    findings = graph_lint.build_findings(pages, stale_days=180, today=dt.date(2026, 6, 15))
    assert any(f["check"].startswith("Topic stale") for f in findings)


def test_doi_satisfies_provenance():
    pages = [source("2026-kim", links=["ai-adoption"], url="", doi="10.1234/x"),
             topic("ai-adoption", links=["2026-kim"]), doc("overview", links=["ai-adoption"])]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert not any(f["check"] == "Source missing public url/doi" for f in findings)


def test_render_markdown_has_required_sections():
    run = {
        "run_date": "2026-06-15T00:00:00",
        "wiki_dir": "/tmp/wiki",
        "pages_checked": 3,
        "summary": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        "findings": [],
    }
    md = graph_lint.render_markdown(run)
    assert "# Research Wiki Graph-Lint Report" in md
    assert "## Summary" in md
    assert "clean" in md
