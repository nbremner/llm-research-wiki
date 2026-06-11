import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools" / "graph_lint.py"
spec = importlib.util.spec_from_file_location("graph_lint", MODULE_PATH)
assert spec is not None and spec.loader is not None
graph_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph_lint)


def page(title, props=None, page_id=None, created="2026-01-01T00:00:00.000Z"):
    page_id = page_id or title.lower().replace(" ", "-")
    return {
        "id": page_id,
        "url": f"https://notion.so/{page_id}",
        "created_time": created,
        "last_edited_time": created,
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": title}]},
            **(props or {}),
        },
    }


def relation(ids):
    return {"type": "relation", "relation": [{"id": x} for x in ids]}


def rich(text):
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def select(text):
    return {"type": "select", "select": {"name": text}}


def url(text):
    return {"type": "url", "url": text}


def test_build_findings_flags_orphans_and_missing_provenance():
    records = {
        "Concepts": [page("Unsupported concept")],
        "Sources": [page("Disconnected source")],
        "Reviews": [],
        "Inbox": [],
    }

    findings = graph_lint.build_findings(records, stale_days=30)
    checks = {f["check"] for f in findings}

    assert "Concept has no linked Sources" in checks
    assert "Source has no linked Concepts" in checks
    assert "Source lacks DOI/canonical URL signal" in checks
    assert graph_lint.summarize_counts(findings)["High"] == 2


def test_build_findings_ignores_connected_source_with_provenance():
    records = {
        "Concepts": [page("Supported concept", {"Sources": relation(["source-1"])})],
        "Sources": [page("Connected source", {"Concepts": relation(["concept-1"]), "DOI": rich("10.1234/example")})],
        "Reviews": [],
        "Inbox": [],
    }

    findings = graph_lint.build_findings(records, stale_days=30)

    assert not findings


def test_duplicate_sources_by_doi_and_concepts_by_title():
    records = {
        "Concepts": [page("Job autonomy"), page("Job Autonomy")],
        "Sources": [
            page("Study A", {"DOI": rich("10.1234/example"), "Concepts": relation(["c1"])}),
            page("Study B", {"DOI": rich("10.1234/example"), "Concepts": relation(["c1"])}),
        ],
        "Reviews": [],
        "Inbox": [],
    }

    findings = graph_lint.build_findings(records, stale_days=30)
    checks = [f["check"] for f in findings]

    assert "Duplicate Sources by DOI" in checks
    assert "Duplicate Concepts by title" in checks


def test_review_and_stale_inbox_checks():
    records = {
        "Concepts": [],
        "Sources": [],
        "Reviews": [page("AI adoption review", {"Notes": rich("This review proposes candidate concept updates.")})],
        "Inbox": [page("Old inbox item", {"Status": select("Needs review")}, created="2025-01-01T00:00:00.000Z")],
    }

    findings = graph_lint.build_findings(records, stale_days=30)
    checks = {f["check"] for f in findings}

    assert "Review has no Reviewed Sources" in checks
    assert "Review appears concept-bearing but has no Related Concepts" in checks
    assert any(check.startswith("Inbox item older than 30 days") for check in checks)


def test_archived_review_is_not_active_lint_work():
    records = {
        "Concepts": [],
        "Sources": [],
        "Reviews": [page("Validation Review Setup Row — archived")],
        "Inbox": [],
    }

    findings = graph_lint.build_findings(records, stale_days=30)

    assert findings == []


def test_render_markdown_has_required_sections():
    run = {
        "run_date": "2026-06-11T00:00:00+00:00",
        "scope": "test",
        "databases_checked": ["Sources", "Concepts"],
        "canonical_pages_checked": ["Schema", "Agent Operating Guide", "Research Map / Overview"],
        "summary": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        "findings": [],
    }

    md = graph_lint.render_markdown(run)

    assert "# Research Wiki Graph-Lint Report" in md
    assert "## Candidate Concept Update Bundle queue" in md
    assert "## Automation readiness notes" in md
