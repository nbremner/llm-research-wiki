import datetime as dt
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools" / "graph_lint.py"
spec = importlib.util.spec_from_file_location("graph_lint", MODULE_PATH)
assert spec is not None and spec.loader is not None
graph_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph_lint)


def source(slug, links=None, url="https://example.org/x", doi="null", file_hash="abc123", retrieved=None):
    fm = {"source_type": "paper", "url": url, "doi": doi, "file_hash": file_hash}
    if retrieved:
        fm["retrieved"] = retrieved
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


def test_evidence_stale_fires_at_two_newer_sources():
    pages = [
        topic("busy-topic", links=["2026-a", "2026-b", "2026-c"], updated="2026-06-01"),
        source("2026-a", links=["busy-topic"], retrieved="2026-06-10"),
        source("2026-b", links=["busy-topic"], retrieved="2026-06-12"),
        source("2026-c", links=["busy-topic"], retrieved="2026-05-01"),  # older than synthesis
        doc("overview", links=["busy-topic"]),
    ]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    es = [f for f in findings if f["check"] == "Topic evidence-stale"]
    assert es and es[0]["page"] == "busy-topic"
    assert "2 sources retrieved since updated 2026-06-01" in es[0]["detail"]
    assert "2026-a" in es[0]["detail"] and "2026-c" not in es[0]["detail"]


def test_evidence_stale_needs_two_and_skips_stubs():
    one_newer = [
        topic("calm-topic", links=["2026-a", "2026-b"], updated="2026-06-01"),
        source("2026-a", links=["calm-topic"], retrieved="2026-06-10"),
        source("2026-b", links=["calm-topic"], retrieved="2026-05-01"),
        doc("overview", links=["calm-topic"]),
    ]
    findings = graph_lint.build_findings(one_newer, today=dt.date(2026, 6, 15))
    assert not any(f["check"] == "Topic evidence-stale" for f in findings)
    stub = [
        topic("stub-topic", links=["2026-a", "2026-b"], status="stub", updated="2026-06-01"),
        source("2026-a", links=["stub-topic"], retrieved="2026-06-10"),
        source("2026-b", links=["stub-topic"], retrieved="2026-06-12"),
        doc("overview", links=["stub-topic"]),
    ]
    findings = graph_lint.build_findings(stub, today=dt.date(2026, 6, 15))
    assert not any(f["check"] == "Topic evidence-stale" for f in findings)


def _pair_fixture():
    """Four topics: a<->b share 2 sources; b->c direct link; d isolated."""
    return [
        topic("topic-a", links=["2026-s1", "2026-s2"], updated="2026-06-14"),
        topic("topic-b", links=["2026-s1", "2026-s2", "topic-c"], updated="2026-01-01"),
        topic("topic-c", links=["2026-s3"], updated="2026-01-01"),
        topic("topic-d", links=["2026-s4"], updated="2026-01-01"),
        source("2026-s1", links=["topic-a"]), source("2026-s2", links=["topic-b"]),
        source("2026-s3", links=["topic-c"]), source("2026-s4", links=["topic-d"]),
        doc("overview", links=["topic-a", "topic-b", "topic-c", "topic-d"]),
    ]


def test_pair_eligibility_shared_and_direct():
    out = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15),
                                         bootstrap=True, max_pairs=10)
    got = {tuple(e["pair"]) for e in out["pairs"]}
    assert got == {("topic-a", "topic-b"), ("topic-b", "topic-c")}
    ab = next(e for e in out["pairs"] if e["pair"] == ["topic-a", "topic-b"])
    assert ab["shared_sources"] == 2 and set(ab["shared"]) == {"2026-s1", "2026-s2"}
    assert not ab["direct_link"]
    bc = next(e for e in out["pairs"] if e["pair"] == ["topic-b", "topic-c"])
    assert bc["direct_link"] and bc["shared_sources"] == 0
    assert out["mode"] == "bootstrap" and out["eligible_total"] == 2


def test_pair_change_gate_and_tail():
    # Only topic-a was edited inside the window -> a<->b gated in; b<->c is cold.
    out = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15),
                                         window_days=35, max_pairs=2, tail_slots=1)
    assert out["mode"] == "gated" and out["gated_total"] == 1
    pairs = [tuple(e["pair"]) for e in out["pairs"]]
    assert pairs[0] == ("topic-a", "topic-b")          # gated head, ranked first
    assert ("topic-b", "topic-c") in pairs             # cold pair reached via tail slot
    # No tail slots -> only the gated head survives.
    out = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15),
                                         window_days=35, max_pairs=2, tail_slots=0)
    assert [tuple(e["pair"]) for e in out["pairs"]] == [("topic-a", "topic-b")]


def test_pair_selection_is_deterministic():
    a = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15))
    b = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15))
    assert a == b


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


def _run_standalone() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"ok   {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
