"""Guardrail tests for the Drive review-folder reconciler (pure logic only)."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import drive_review_sync as drs  # noqa: E402

SRC, UNREV, ROOT = "fold-sources", "fold-unreviewed", "fold-root"


def _wiki(tmp: Path) -> Path:
    (tmp / "sources" / "unreviewed").mkdir(parents=True)
    (tmp / "sources" / "2026-a.md").write_text("---\ntitle: A\nhuman_reviewed: true\ndrive_file_id: id-a\n---\n# A\n", encoding="utf-8")
    (tmp / "sources" / "unreviewed" / "2026-b.md").write_text("---\ntitle: B\nhuman_reviewed: false\ndrive_file_id: id-b\n---\n# B\n", encoding="utf-8")
    (tmp / "sources" / "2026-c.md").write_text("---\ntitle: C\nhuman_reviewed: true\ndrive_file_id: id-c\n---\n# C\n", encoding="utf-8")
    (tmp / "sources" / "2026-noid.md").write_text("---\ntitle: N\nhuman_reviewed: true\n---\n# N\n", encoding="utf-8")
    return tmp


def test_load_records_reads_flag_folder_and_id():
    recs = {r["slug"]: r for r in drs.load_records(_wiki(Path(tempfile.mkdtemp())))}
    assert recs["2026-a"] == {"slug": "2026-a", "path": "2026-a.md", "in_unreviewed_dir": False,
                              "flag": "true", "drive_file_id": "id-a"}
    assert recs["2026-b"]["in_unreviewed_dir"] is True and recs["2026-b"]["flag"] == "false"
    assert recs["2026-noid"]["drive_file_id"] is None


def test_plan_moves_migration_and_idempotence():
    recs = drs.load_records(_wiki(Path(tempfile.mkdtemp())))
    locations = {
        "id-a": {"name": "a.pdf", "parents": [ROOT], "trashed": False},       # still in the flat root -> move
        "id-b": {"name": "b.md", "parents": [SRC], "trashed": False},         # reviewed folder but unreviewed record -> move down
        "id-c": {"name": "c.pdf", "parents": [SRC], "trashed": False},        # already right
        "id-stray": {"name": "Copy of x.pdf", "parents": [ROOT], "trashed": False},
        "id-else": {"name": "elsewhere.pdf", "parents": ["fold-triage"], "trashed": False},
    }
    plan = drs.plan_moves(recs, locations, SRC, UNREV, managed_ids={ROOT, SRC, UNREV})
    assert [(m["slug"], m["to_label"]) for m in plan["moves"]] == [("2026-a", "_sources"), ("2026-b", "_sources/_unreviewed")]
    assert plan["moves"][0]["from"] == [ROOT] and plan["moves"][0]["to"] == SRC
    assert [o["slug"] for o in plan["ok"]] == ["2026-c"]
    assert [n["slug"] for n in plan["no_drive_id"]] == ["2026-noid"]
    assert [s["name"] for s in plan["strays"]] == ["Copy of x.pdf"]  # managed folders only; elsewhere is ignored
    # apply the plan -> a second pass finds nothing to do
    for mv in plan["moves"]:
        locations[mv["drive_file_id"]]["parents"] = [mv["to"]]
    again = drs.plan_moves(recs, locations, SRC, UNREV, managed_ids={ROOT, SRC, UNREV})
    assert again["moves"] == [] and len(again["ok"]) == 3


def test_plan_reports_missing_and_mismatch():
    tmp = _wiki(Path(tempfile.mkdtemp()))
    (tmp / "sources" / "unreviewed" / "2026-wrong.md").write_text(
        "---\ntitle: W\nhuman_reviewed: true\ndrive_file_id: id-w\n---\n# W\n", encoding="utf-8")
    recs = drs.load_records(tmp)
    locations = {"id-a": {"name": "a", "parents": [SRC], "trashed": True},
                 "id-c": {"name": "c", "parents": [SRC], "trashed": False}}
    plan = drs.plan_moves(recs, locations, SRC, UNREV)
    assert [m["slug"] for m in plan["mismatch"]] == ["2026-wrong"]
    missing = {m["slug"]: m["trashed"] for m in plan["missing"]}
    assert missing == {"2026-a": True, "2026-b": False}
    text = drs.render_plan(plan, executed=False)
    assert "DRY RUN" in text and "MISMATCH" in text and "is trashed" in text and "not found" in text


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
