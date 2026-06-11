from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".numbers", ".csv", ".jsonl", ".sqlite", ".sqlite3", ".db",
}

FORBIDDEN_NAMES = {
    ".env", "auth.json", "google_token.json", "state.db", "drive_inventory_raw.json",
    "pdf_triage.csv", "pdf_triage.jsonl", "SUMMARY.md",
}

FORBIDDEN_PARTS = {
    "downloads", "outputs", "exports", "backlog", "runs",
    "research-wiki-runs", "sessions", "logs", "cache",
}


def tracked_files():
    ignored_parts = {".git", ".pytest_cache", "__pycache__"}
    for path in ROOT.rglob("*"):
        if path.is_file() and not any(part in ignored_parts for part in path.parts):
            yield path


def test_no_corpus_or_runtime_artifacts_in_repo():
    offenders = []
    for path in tracked_files():
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            offenders.append(str(rel))
        if path.name in FORBIDDEN_NAMES:
            offenders.append(str(rel))
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            offenders.append(str(rel))
    assert not offenders, "Forbidden corpus/runtime artifacts present: " + ", ".join(sorted(offenders))


def test_expected_research_wiki_skills_present():
    expected = [
        ROOT / "skills" / "manual-research-pdf-summary" / "SKILL.md",
        ROOT / "skills" / "research-wiki-graph-lint" / "SKILL.md",
        ROOT / "skills" / "research-wiki-pdf-backlog-triage" / "SKILL.md",
        ROOT / "skills" / "research-wiki-review" / "SKILL.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in expected if not p.exists()]
    assert not missing, "Missing expected skills: " + ", ".join(missing)
