"""Guardrail tests for the triage disposition applier (pure logic only).

Covers validation (unknown / already-disposed / invalid entries), the hybrid-
autonomy plan (auto-move, cap overflow, needs-acquisition, ambiguous surfacing,
missing-judgment surfacing), digest rendering, and latest-manifest discovery.
No network, no Drive. Runs under pytest and standalone.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import scan_triage_apply as sta  # noqa: E402


def _manifest():
    return {
        "generated": "2026-07-04T20:10:08+00:00",
        "records": [
            {"id": "doi:10.1/a", "title": "Clear wiki paper with artifact",
             "url": "https://x/a", "acq_state": "full-pdf",
             "artifact_drive_id": "drv-a", "rank_score": 0.9, "disposition": None},
            {"id": "doi:10.1/b", "title": "Clear wiki paper without artifact",
             "url": "https://x/b", "acq_state": "abstract-only",
             "artifact_drive_id": None, "rank_score": 0.8, "disposition": None},
            {"id": "doi:10.1/c", "title": "Adjacent-domain manufacturing review",
             "url": "https://x/c", "acq_state": "abstract-only",
             "abstract": "industry 5.0 manufacturing", "rank_score": 0.7, "disposition": None},
            {"id": "doi:10.1/d", "title": "Ambiguous borderline paper",
             "url": "https://x/d", "acq_state": "full-pdf",
             "artifact_drive_id": "drv-d", "rank_score": 0.6, "disposition": None},
            {"id": "doi:10.1/e", "title": "Duplicate under second DOI",
             "url": "https://x/e", "acq_state": "link-only", "rank_score": 0.5,
             "disposition": None},
            {"id": "doi:10.1/f", "title": "Not judged this run",
             "url": "https://x/f", "acq_state": "link-only", "rank_score": 0.4,
             "disposition": None},
            {"id": "doi:10.1/z", "title": "Previously disposed",
             "url": "https://x/z", "acq_state": "full-pdf", "rank_score": 0.3,
             "disposition": "wiki"},
        ],
    }


def _dispositions():
    return {"judged_by": "test", "entries": [
        {"id": "doi:10.1/a", "disposition": "wiki", "confidence": "clear", "reason": "rct evidence"},
        {"id": "doi:10.1/b", "disposition": "wiki", "confidence": "clear", "reason": "theory"},
        {"id": "doi:10.1/c", "disposition": "read-once", "confidence": "clear",
         "reason": "manufacturing context", "summary": "Industry 5.0 HMC review."},
        {"id": "doi:10.1/d", "disposition": "wiki", "confidence": "ambiguous", "reason": "unsure fit"},
        {"id": "doi:10.1/e", "disposition": "discard", "confidence": "clear", "reason": "duplicate"},
    ]}


def test_plan_routes_each_bucket():
    manifest, plan = sta.apply_dispositions(_manifest(), _dispositions())
    assert [m["id"] for m in plan["moves"]] == ["doi:10.1/a"]
    assert [m["id"] for m in plan["needs_acquisition"]] == ["doi:10.1/b"]
    assert [m["id"] for m in plan["read_once"]] == ["doi:10.1/c"]
    assert plan["read_once"][0]["summary"] == "Industry 5.0 HMC review."
    ncall = {m["id"] for m in plan["needs_call"]}
    assert ncall == {"doi:10.1/d", "doi:10.1/f"}  # ambiguous + missing judgment
    assert [m["id"] for m in plan["discard"]] == ["doi:10.1/e"]
    rec = {r["id"]: r for r in manifest["records"]}
    assert rec["doi:10.1/a"]["disposition"] == "wiki"
    assert rec["doi:10.1/f"]["disposition"] is None  # unjudged stays pending
    assert rec["doi:10.1/z"]["disposition"] == "wiki"  # untouched


def test_acquired_path_becomes_upload():
    d = _dispositions()
    d["entries"][1]["acquired_path"] = "/tmp/b.pdf"
    _, plan = sta.apply_dispositions(_manifest(), d)
    assert [u["id"] for u in plan["uploads"]] == ["doi:10.1/b"]
    assert plan["needs_acquisition"] == []


def test_auto_move_cap_overflows_to_needs_call():
    _, plan = sta.apply_dispositions(_manifest(), _dispositions(), max_auto_wiki=0)
    assert plan["moves"] == []
    over = [m for m in plan["needs_call"] if m["id"] == "doi:10.1/a"]
    assert over and "cap" in over[0]["reason"]


def test_validation_fails_loud():
    for entries, msg in [
        ([{"id": "doi:10.9/nope", "disposition": "wiki", "confidence": "clear"}], "not in manifest"),
        ([{"id": "doi:10.1/z", "disposition": "wiki", "confidence": "clear"}], "already-disposed"),
        ([{"id": "doi:10.1/a", "disposition": "keep", "confidence": "clear"}], "invalid"),
        ([{"id": "doi:10.1/a", "disposition": "wiki", "confidence": "sure"}], "invalid"),
    ]:
        try:
            sta.apply_dispositions(_manifest(), {"entries": entries})
            raise AssertionError(f"expected ValueError containing {msg!r}")
        except ValueError as e:
            assert msg in str(e), (msg, str(e))


def test_digest_sections_and_counts():
    manifest, plan = sta.apply_dispositions(_manifest(), _dispositions())
    digest = sta.render_digest(manifest, plan, executed=False)
    assert "DRY RUN" in digest
    assert "Needs your call" in digest and "Ambiguous borderline paper" in digest
    assert "Queued to wiki inbox (auto)" in digest and "Clear wiki paper with artifact" in digest
    assert "needs manual acquisition" in digest and "without artifact" in digest
    assert "Read-once" in digest and "Industry 5.0 HMC review." in digest
    assert "Discarded (1)" in digest
    executed = sta.render_digest(manifest, plan, executed=True)
    assert "executed" in executed and "DRY RUN" not in executed


def test_find_latest_manifest_skips_fully_triaged():
    root = Path(tempfile.mkdtemp())
    done = root / "scan-1"; done.mkdir()
    (done / "manifest-1.json").write_text(json.dumps(
        {"records": [{"id": "x", "disposition": "wiki"}]}), encoding="utf-8")
    pend = root / "scan-2"; pend.mkdir()
    pending_path = pend / "manifest-2.json"
    pending_path.write_text(json.dumps(
        {"records": [{"id": "y", "disposition": None}]}), encoding="utf-8")
    assert sta.find_latest_manifest(str(root)) == pending_path
    pending_path.write_text(json.dumps(
        {"records": [{"id": "y", "disposition": "discard"}]}), encoding="utf-8")
    assert sta.find_latest_manifest(str(root)) is None


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
