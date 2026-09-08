import datetime as dt
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools" / "graph_lint.py"
spec = importlib.util.spec_from_file_location("graph_lint", MODULE_PATH)
assert spec is not None and spec.loader is not None
graph_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph_lint)


def source(slug, links=None, url="https://example.org/x", doi="null", file_hash="abc123", retrieved="2026-06-01",
           reviewed="true", unreviewed_dir=False):
    fm = {"source_type": "paper", "url": url, "doi": doi, "file_hash": file_hash}
    if retrieved:
        fm["retrieved"] = retrieved
    if reviewed is not None:
        fm["human_reviewed"] = reviewed
    sub = "unreviewed/" if unreviewed_dir else ""
    return {"slug": slug, "kind": "source", "path": f"sources/{sub}{slug}.md", "frontmatter": fm,
            "links": links or [], "body": "", "unreviewed_dir": unreviewed_dir}


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


def test_topic_missing_updated_flagged_stub_exempt():
    pages = [
        topic("undated-topic", links=["2026-kim"], updated=None),
        source("2026-kim", links=["undated-topic"]),
        doc("overview", links=["undated-topic"]),
    ]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert any(f["check"] == "Topic missing updated date" and f["page"] == "undated-topic"
               for f in findings)
    pages[0] = topic("undated-topic", links=["2026-kim"], status="stub", updated=None)
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert not any(f["check"] == "Topic missing updated date" for f in findings)


def test_source_missing_retrieved_flagged():
    pages = [
        topic("ai-adoption", links=["2026-kim"]),
        source("2026-kim", links=["ai-adoption"], retrieved=None),
        doc("overview", links=["ai-adoption"]),
    ]
    findings = graph_lint.build_findings(pages, today=dt.date(2026, 6, 15))
    assert any(f["check"] == "Source missing retrieved date" and f["page"] == "2026-kim"
               for f in findings)


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


def test_pair_coverage_warning_when_gate_overflows_cap():
    # Many recently edited topics sharing sources -> far more gated pairs than the cap.
    srcs = [f"2026-s{i}" for i in range(3)]
    pages = [topic(f"t{i}", links=srcs, updated="2026-06-14") for i in range(8)]
    pages += [source(s, links=["t0"]) for s in srcs] + [doc("overview", links=[f"t{i}" for i in range(8)])]
    out = graph_lint.contradiction_pairs(pages, today=dt.date(2026, 6, 15), max_pairs=4, tail_slots=1)
    assert out["gated_total"] == 28 and out["dropped_gated"] >= 4
    assert "coverage degraded" in out["warning"]
    calm = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15))
    assert "warning" not in calm


def test_pair_selection_is_deterministic():
    a = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15))
    b = graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15))
    assert a == b


def test_tail_rotation_advances_monthly():
    # max_pairs=1, tail_slots=1 -> head is empty, the single slot is pure tail
    # over rest = both eligible pairs; the offset must advance across months and
    # hold within a month (the cron is monthly).
    def tail_on(day):
        out = graph_lint.contradiction_pairs(_pair_fixture(), today=day,
                                             max_pairs=1, tail_slots=1)
        return [tuple(e["pair"]) for e in out["pairs"]]

    june = tail_on(dt.date(2026, 6, 15))
    july = tail_on(dt.date(2026, 7, 15))
    assert june != july                       # consecutive months rotate
    assert tail_on(dt.date(2026, 6, 1)) == tail_on(dt.date(2026, 6, 28)) == june


def test_window_days_zero_raises():
    try:
        graph_lint.contradiction_pairs(_pair_fixture(), today=dt.date(2026, 6, 15),
                                       window_days=0)
        raise AssertionError("expected ValueError for window_days=0")
    except ValueError as e:
        assert "window_days" in str(e)


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


def _checks(pages):
    return {(f["severity"], f["check"], f["page"]) for f in graph_lint.build_findings(pages, today=dt.date(2026, 9, 7))}


def test_review_flag_and_folder_must_agree():
    base = [topic("ai-adoption", links=["2026-ok"]), doc("overview", links=["ai-adoption"]),
            source("2026-ok", links=["ai-adoption"])]
    # consistent unreviewed record: only the expected orphan / feeds-no-topic signals, nothing High
    pending = source("2026-pending", links=["ai-adoption"], reviewed="false", unreviewed_dir=True)
    found = _checks(base + [pending])
    assert not any(sev == "High" for sev, _, _ in found)
    assert ("Medium", "Orphan source", "2026-pending") in found
    # missing flag -> Medium
    assert ("Medium", "Source missing human_reviewed", "2026-noflag") in _checks(
        base + [source("2026-noflag", links=["ai-adoption"], reviewed=None)])
    # flag says reviewed but the file sits in unreviewed/ -> High, and vice versa
    assert ("High", "Source review flag mismatch", "2026-a") in _checks(
        base + [source("2026-a", links=["ai-adoption"], reviewed="true", unreviewed_dir=True)])
    assert ("High", "Source review flag mismatch", "2026-b") in _checks(
        base + [source("2026-b", links=["ai-adoption"], reviewed="false", unreviewed_dir=False)])


def test_topic_must_not_cite_unreviewed_source():
    pages = [topic("ai-adoption", links=["2026-pending"]), doc("overview", links=["ai-adoption"]),
             source("2026-pending", links=["ai-adoption"], reviewed="false", unreviewed_dir=True)]
    assert ("High", "Topic cites unreviewed source", "ai-adoption") in _checks(pages)
    moved = [topic("ai-adoption", links=["2026-pending"]), doc("overview", links=["ai-adoption"]),
             source("2026-pending", links=["ai-adoption"])]
    assert not any(c == "Topic cites unreviewed source" for _, c, _ in _checks(moved))


def test_load_pages_marks_unreviewed_folder():
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "sources" / "unreviewed").mkdir(parents=True); (d / "topics").mkdir()
    (d / "sources" / "unreviewed" / "2026-x.md").write_text("---\ntitle: X\nhuman_reviewed: false\n---\n# X\n", encoding="utf-8")
    (d / "sources" / "2026-y.md").write_text("---\ntitle: Y\nhuman_reviewed: true\n---\n# Y\n", encoding="utf-8")
    pages = {p["slug"]: p for p in graph_lint.load_pages(d)}
    assert pages["2026-x"]["kind"] == "source" and pages["2026-x"]["unreviewed_dir"] is True
    assert pages["2026-y"]["kind"] == "source" and pages["2026-y"]["unreviewed_dir"] is False


def _accreted(n_sources, words):
    srcs = [f"2026-s{i}" for i in range(n_sources)]
    pages = [topic("big-topic", links=srcs)] + [source(s, links=["big-topic"]) for s in srcs]
    pages.append(doc("overview", links=["big-topic"]))
    pages[0]["body"] = "word " * words
    return pages


def _accretion_level(n_sources, words, status="active"):
    pages = _accreted(n_sources, words)
    pages[0]["frontmatter"]["status"] = status
    found = [f for f in graph_lint.build_findings(pages, today=dt.date(2026, 9, 7))
             if f["check"] == "Topic accretion"]
    return found[0]["severity"] if found else None


def test_topic_accretion_thresholds():
    assert _accretion_level(24, 100) is None
    assert _accretion_level(25, 100) == "Low" and _accretion_level(1, 2500) == "Low"
    assert _accretion_level(34, 3499) == "Low"
    assert _accretion_level(35, 100) == "Medium" and _accretion_level(1, 3500) == "Medium"
    assert _accretion_level(40, 100, status="stub") is None  # stubs are exempt
    assert graph_lint.accretion_severity(35, 0) == "Medium"
    assert graph_lint.accretion_severity(0, 0) is None
    detail = next(f["detail"] for f in graph_lint.build_findings(_accreted(36, 10), today=dt.date(2026, 9, 7))
                  if f["check"] == "Topic accretion")
    assert detail.startswith("36 cited sources, 10 words") and "split candidate" in detail


def test_should_fail_honours_allow_check():
    findings = [
        {"severity": "Medium", "check": "Orphan source", "page": "s", "detail": ""},
        {"severity": "Medium", "check": "Topic accretion", "page": "t", "detail": ""},
    ]
    assert graph_lint.should_fail(findings, "Medium")
    assert graph_lint.should_fail(findings, "Medium", ["Orphan source"])
    assert not graph_lint.should_fail(findings, "Medium", ["Orphan source", "Topic accretion"])
    assert not graph_lint.should_fail(findings, "High")
    assert not graph_lint.should_fail(findings, "never")
    assert not graph_lint.should_fail([], "Low")


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
