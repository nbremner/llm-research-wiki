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


EXPECTED_SKILLS = [
    "research-wiki-ingest",
    "research-wiki-graph-lint",
    "research-scan-triage",
    "research-wiki-query",
]


def test_expected_research_wiki_skills_present():
    missing = [s for s in EXPECTED_SKILLS if not (ROOT / "skills" / s / "SKILL.md").exists()]
    assert not missing, "Missing expected skills: " + ", ".join(missing)


def test_allowlist_matches_skill_dirs():
    allowlist = {
        line.strip().rstrip("/").split("/")[-1]
        for line in (ROOT / "skills.allowlist").read_text().splitlines()
        if line.strip()
    }
    assert allowlist == set(EXPECTED_SKILLS), f"skills.allowlist out of sync: {allowlist}"
    # the allowlist must not name a retired skill that still has a dir
    on_disk = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    assert allowlist == on_disk, f"allowlist vs skills/ dirs mismatch: {allowlist} != {on_disk}"


def test_ingest_skill_drain_mode_guardrails():
    """The scheduled drain is the only unattended writer of wiki pages; its
    non-negotiables must stay written into the skill text."""
    text = (ROOT / "skills" / "research-wiki-ingest" / "SKILL.md").read_text(encoding="utf-8")
    assert "### Scheduled source drain" in text
    for phrase in (
        "up to **5 sources per run, oldest first**",
        "step 9 is out of scope",
        "no `updated:` bump anywhere",
        "**existing topic slugs only**",
        "--fail-on High",
        "Orphan-source Medium findings are expected",
        "never work around bot checks, CAPTCHAs, or logins",
        "Dispatch one subagent per file in a single `delegate_task` call",
        "Children never run git",
        "drive_review_sync.py --execute",
        "`human_reviewed: false`",
    ):
        assert phrase in text, phrase
    assert "### Weekly synthesis batch" in text
    assert "### Owner rejection command" in text
    for phrase in ("act only on a message from the owner", "delete
   nothing", "Never trash a Drive file"):
        assert phrase in text, phrase
    for phrase in (
        "up to **12 sources, oldest first**",
        "synthesis_pr.py status --json",
        "never rebase or merge the stale draft",
        "one subagent per affected topic page",
        "--allow-check \"Orphan source\"",
        "git mv wiki/sources/unreviewed/<slug>.md wiki/sources/<slug>.md",
        "`git checkout main` so the clone is back on a clean main",
    ):
        assert phrase in text, phrase
    lint = (ROOT / "skills" / "research-wiki-graph-lint" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in ("## Claim-fidelity audit", "claim_audit.py --sample", "**one task per sampled claim**",
                   "spot-checks at least two", "Staleness is a signal, not a defect", "quote it verbatim"):
        assert phrase in lint, phrase


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
