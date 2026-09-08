"""Guardrail tests for the triage disposition applier (pure logic only).

Covers validation (unknown / already-disposed / invalid entries), the hybrid-
autonomy plan (auto-move, cap overflow, needs-acquisition, ambiguous surfacing,
missing-judgment surfacing), digest rendering, latest-manifest discovery, the
open-set carryover across manifests (window, stranding, stamp-back, digest
section), and the amend writeback. No network, no Drive. Runs under pytest and
standalone.
"""

from __future__ import annotations

import datetime as dt
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
             "artifact_drive_id": "drv-c", "abstract": "industry 5.0 manufacturing",
             "rank_score": 0.7, "disposition": None},
            {"id": "doi:10.1/d", "title": "Ambiguous borderline paper",
             "url": "https://x/d", "acq_state": "full-pdf",
             "artifact_drive_id": "drv-d", "rank_score": 0.6, "disposition": None},
            {"id": "doi:10.1/e", "title": "Duplicate under second DOI",
             "url": "https://x/e", "acq_state": "full-pdf", "artifact_drive_id": "drv-e", "rank_score": 0.5,
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
    assert plan["read_once"][0]["drive_file_id"] == "drv-c"
    ncall = {m["id"] for m in plan["needs_call"]}
    assert ncall == {"doi:10.1/d", "doi:10.1/f"}  # ambiguous + missing judgment
    assert [m["id"] for m in plan["discard"]] == ["doi:10.1/e"]
    assert plan["discard"][0]["drive_file_id"] == "drv-e"
    rec = {r["id"]: r for r in manifest["records"]}
    assert rec["doi:10.1/a"]["disposition"] == "wiki"
    assert rec["doi:10.1/f"]["disposition"] is None  # unjudged stays pending
    assert rec["doi:10.1/d"]["disposition"] is None  # ambiguous stays physically pending
    assert rec["doi:10.1/z"]["disposition"] == "wiki"  # untouched


def test_acquired_path_becomes_upload():
    d = _dispositions()
    d["entries"][1]["acquired_path"] = "/tmp/b.pdf"
    _, plan = sta.apply_dispositions(_manifest(), d)
    assert [u["id"] for u in plan["uploads"]] == ["doi:10.1/b"]
    assert plan["needs_acquisition"] == []


def test_acquired_markdown_uploads_as_full_text():
    d = _dispositions()
    d["entries"][1]["acquired_path"] = "/tmp/b.md"
    manifest, plan = sta.apply_dispositions(_manifest(), d)
    assert [u["id"] for u in plan["uploads"]] == ["doi:10.1/b"]
    assert sta.artifact_kind("/tmp/b.md") == ("text/markdown", "full-text")
    assert sta.artifact_kind("/tmp/b.PDF") == ("application/pdf", "full-pdf")
    d["entries"][1]["acquired_path"] = "/tmp/b.docx"
    try:
        sta.apply_dispositions(_manifest(), d)
        raise AssertionError("expected ValueError for an unsupported artifact type")
    except ValueError as e:
        assert "unsupported acquired artifact type" in str(e)
    # execution uploads with the markdown mime and stamps full-text
    uploads = []
    saved = (sta.c.build_drive_service, sta.c.drive_move, sta.c.drive_find, sta.c.drive_upload_bytes)
    with tempfile.TemporaryDirectory() as td:
        art = Path(td) / "b.md"; art.write_text("Title: x\n\nMarkdown Content:\nbody", encoding="utf-8")
        d["entries"][1]["acquired_path"] = str(art)
        manifest, plan = sta.apply_dispositions(_manifest(), d)
        try:
            sta.c.build_drive_service = lambda _t: object()
            sta.c.drive_move = lambda *_a: None
            sta.c.drive_find = lambda *_a: None
            sta.c.drive_upload_bytes = lambda _s, folder, name, data, mime: (uploads.append((folder, name, mime)) or "new-id")
            sta.execute_plan(manifest, plan, Path(td) / "manifest-x.json", "/unused")
        finally:
            sta.c.build_drive_service, sta.c.drive_move, sta.c.drive_find, sta.c.drive_upload_bytes = saved
    assert (sta.cfg.TRIAGE_WIKI_FOLDER_ID, "b.md", "text/markdown") in uploads
    rec = next(r for r in manifest["records"] if r["id"] == "doi:10.1/b")
    assert rec["acq_state"] == "full-text" and rec["artifact_drive_id"] == "new-id"


def test_cap_is_enforced():
    manifest, plan = sta.apply_dispositions(_manifest(), _dispositions(), max_auto_wiki=0)
    assert plan["moves"] == []
    assert any("over auto-move cap" in x.get("reason", "") for x in plan["needs_call"])
    rec = next(r for r in manifest["records"] if r["id"] == "doi:10.1/a")
    assert rec["disposition"] is None  # stays pending for the next run


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


def test_duplicate_and_missing_ids_fail_loud():
    for entries, msg in [
        ([{"id": "doi:10.1/a", "disposition": "wiki", "confidence": "clear"},
          {"id": "doi:10.1/a", "disposition": "discard", "confidence": "clear"}], "duplicate ids"),
        ([{"disposition": "wiki", "confidence": "clear"}], "missing an id"),
    ]:
        try:
            sta.apply_dispositions(_manifest(), {"entries": entries})
            raise AssertionError(f"expected ValueError containing {msg!r}")
        except ValueError as e:
            assert msg in str(e), (msg, str(e))


def test_ambiguous_replay_does_not_duplicate_history():
    manifest, _ = sta.apply_dispositions(_manifest(), _dispositions())
    replay = {"judged_by": "test", "entries": [
        {"id": "doi:10.1/d", "disposition": "wiki", "confidence": "ambiguous",
         "reason": "unsure fit"}]}
    manifest2, _ = sta.apply_dispositions(manifest, replay)
    rec = next(r for r in manifest2["records"] if r["id"] == "doi:10.1/d")
    assert len(rec["proposal_history"]) == 1  # identical judgment appends nothing
    # A different reason is genuine new signal and still appends.
    manifest3, _ = sta.apply_dispositions(manifest2, {"judged_by": "test", "entries": [
        {"id": "doi:10.1/d", "disposition": "wiki", "confidence": "ambiguous",
         "reason": "second look, still unsure"}]})
    rec3 = next(r for r in manifest3["records"] if r["id"] == "doi:10.1/d")
    assert len(rec3["proposal_history"]) == 2


def test_null_rank_score_tolerated():
    manifest = _manifest()
    manifest["records"][0]["rank_score"] = None
    _, plan = sta.apply_dispositions(manifest, _dispositions())
    assert [m["id"] for m in plan["moves"]] == ["doi:10.1/a"]


def test_clear_judgment_can_resolve_legacy_ambiguous_record():
    manifest = _manifest()
    prior = next(r for r in manifest["records"] if r["id"] == "doi:10.1/z")
    prior["disposition_confidence"] = "ambiguous"
    updated, plan = sta.apply_dispositions(manifest, {"entries": [
        {"id": "doi:10.1/z", "disposition": "discard", "confidence": "clear",
         "reason": "owner resolved"},
    ]})
    rec = next(r for r in updated["records"] if r["id"] == "doi:10.1/z")
    assert rec["disposition"] == "discard"
    assert [r["id"] for r in plan["discard"]] == ["doi:10.1/z"]


def test_digest_sections_and_counts():
    src = _manifest()
    src["records"][3]["title"] = "Ambiguous\n   <scp>borderline</scp>\n   paper"  # Crossref JATS + newlines
    manifest, plan = sta.apply_dispositions(src, _dispositions())
    digest = sta.render_digest(manifest, plan, executed=False)
    assert "- Ambiguous borderline paper — wiki: unsure fit" in digest  # one clean line
    assert "DRY RUN" in digest
    assert "Needs your call" in digest and "Ambiguous borderline paper" in digest
    assert "Queued to triage/wiki (auto)" in digest and "Clear wiki paper with artifact" in digest
    assert "needs manual acquisition" in digest and "without artifact" in digest
    assert "Read-once" in digest and "Industry 5.0 HMC review." in digest
    assert "Discarded (1)" in digest


def test_execute_routes_artifacts_to_visible_state_folders():
    manifest, plan = sta.apply_dispositions(_manifest(), _dispositions())
    moves = []
    uploads = []
    original_build = sta.c.build_drive_service
    original_move = sta.c.drive_move
    original_find = sta.c.drive_find
    original_upload = sta.c.drive_upload_bytes
    try:
        sta.c.build_drive_service = lambda _token: object()
        sta.c.drive_move = lambda _svc, fid, dest, source: moves.append(
            (fid, dest, source))
        sta.c.drive_find = lambda _svc, _folder, _name: None
        sta.c.drive_upload_bytes = lambda _svc, folder, name, data, mime: (
            uploads.append((folder, name, mime)) or "manifest-id")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest-test.json"
            sta.execute_plan(manifest, plan, path, "/unused/token.json")
    finally:
        sta.c.build_drive_service = original_build
        sta.c.drive_move = original_move
        sta.c.drive_find = original_find
        sta.c.drive_upload_bytes = original_upload

    assert ("drv-a", sta.cfg.TRIAGE_WIKI_FOLDER_ID,
            sta.cfg.TRIAGE_PENDING_FOLDER_ID) in moves
    assert ("drv-c", sta.cfg.TRIAGE_READ_ONCE_FOLDER_ID,
            sta.cfg.TRIAGE_PENDING_FOLDER_ID) in moves
    assert ("drv-e", sta.cfg.TRIAGE_DISCARDED_FOLDER_ID,
            sta.cfg.TRIAGE_PENDING_FOLDER_ID) in moves
    assert uploads == [(sta.cfg.TRIAGE_FOLDER_ID, "manifest-test.json",
                        "application/json")]
    executed = sta.render_digest(manifest, plan, executed=True)
    assert "executed" in executed and "DRY RUN" not in executed


def test_ambiguous_appends_proposal_history_and_stays_pending():
    manifest, _ = sta.apply_dispositions(_manifest(), _dispositions())
    rec = next(r for r in manifest["records"] if r["id"] == "doi:10.1/d")
    assert rec["disposition"] is None
    assert len(rec["proposal_history"]) == 1
    h = rec["proposal_history"][0]
    assert h["proposed"] == "wiki" and h["reason"] == "unsure fit" and h["at"]
    # A second ambiguous judgment on the still-pending record appends, not replaces.
    manifest2, _ = sta.apply_dispositions(manifest, {"entries": [
        {"id": "doi:10.1/d", "disposition": "read-once", "confidence": "ambiguous",
         "reason": "still unsure"}]})
    rec2 = next(r for r in manifest2["records"] if r["id"] == "doi:10.1/d")
    assert [x["proposed"] for x in rec2["proposal_history"]] == ["wiki", "read-once"]


def test_collect_friction_window_and_resolution():
    today = dt.date(2026, 7, 20)
    manifests = [
        {"records": [
            {"id": "doi:10.1/hot", "title": "Recent ambiguous", "url": "https://x/h",
             "disposition": None, "proposal_history": [
                 {"at": "2026-07-18T08:35:00+00:00", "proposed": "wiki", "reason": "practitioner survey"}]},
            {"id": "doi:10.1/settled", "title": "Later resolved", "url": "https://x/s",
             "disposition": "read-once", "proposal_history": [
                 {"at": "2026-07-10T08:35:00+00:00", "proposed": "wiki", "reason": "adjacent domain?"}]},
            {"id": "doi:10.1/clear", "title": "Never ambiguous", "disposition": "wiki"},
        ]},
        {"records": [
            {"id": "doi:10.1/old", "title": "Outside window", "disposition": None,
             "proposal_history": [
                 {"at": "2026-07-01T08:35:00+00:00", "proposed": "discard", "reason": "old"}]},
            {"id": "doi:10.1/bad", "proposal_history": [{"proposed": "wiki"}]},  # no date -> skipped
            {"title": "Record without id", "proposal_history": [
                {"at": "2026-07-18T08:35:00+00:00", "proposed": "wiki"}]},  # no id -> skipped
            {"id": "doi:10.1/mangled", "proposal_history": ["not-a-dict"]},  # -> skipped
        ]},
    ]
    items = sta.collect_friction(manifests, today, window_days=14)
    assert [i["id"] for i in items] == ["doi:10.1/hot", "doi:10.1/settled"]  # newest first
    assert items[0]["resolved"] is None
    assert items[1]["resolved"] == "read-once"


def test_render_friction_empty_and_populated():
    empty = sta.render_friction([], 14)
    assert "no ambiguous proposals" in empty
    report = sta.render_friction([
        {"date": "2026-07-18", "id": "doi:10.1/hot", "title": "Recent ambiguous",
         "proposed": "wiki", "reason": "practitioner survey", "resolved": None},
        {"date": "2026-07-10", "id": "doi:10.1/settled", "title": "Later resolved",
         "proposed": "wiki", "reason": "adjacent domain?", "resolved": "read-once"},
    ], 14)
    assert "Rubric friction — 2 ambiguous" in report
    assert "Recent ambiguous — proposed wiki: practitioner survey" in report
    assert "[later resolved: read-once]" in report


def test_load_local_manifests_excludes_current_and_bad_json():
    root = Path(tempfile.mkdtemp())
    a = root / "scan-a"; a.mkdir()
    (a / "manifest-1.json").write_text(json.dumps(
        {"generated": "2026-07-10", "records": []}), encoding="utf-8")
    b = root / "scan-b"; b.mkdir()
    current = b / "manifest-2.json"
    current.write_text(json.dumps({"generated": "2026-07-18", "records": []}), encoding="utf-8")
    (b / "manifest-3.json").write_text("{not json", encoding="utf-8")
    loaded = sta.load_local_manifests(str(root), exclude=current)
    assert [m["generated"] for m in loaded] == ["2026-07-10"]


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

    pending_path.write_text(json.dumps({"records": [
        {"id": "y", "disposition": "wiki", "disposition_confidence": "ambiguous"},
    ]}), encoding="utf-8")
    assert sta.find_latest_manifest(str(root)) == pending_path


# ---------------------------------------------------------------------------
# Open set (carryover across manifests) + amend
# ---------------------------------------------------------------------------

def _rec(rid, title, disposition=None, **kw):
    tail = rid.split("/")[-1]
    return {"id": rid, "title": title, "url": f"https://x/{tail}", "acq_state": "full-pdf",
            "artifact_drive_id": f"drv-{tail}", "rank_score": 0.5, "disposition": disposition, **kw}


def _write_manifest(root, generated, records):
    stamp = generated.replace("-", "") + "T150000Z"
    d = root / f"scan-{stamp}"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"manifest-{stamp}.json"
    path.write_text(json.dumps({"generated": f"{generated}T15:00:00+00:00", "records": records}),
                    encoding="utf-8")
    return path


def _open_root():
    """Manifests as seen on 2026-09-07: today's (2 unresolved), a 4-day-old
    ambiguous item, one exactly at the 7-day edge, one stranded at 9 days, and
    one fully resolved (must not appear)."""
    root = Path(tempfile.mkdtemp())
    paths = {
        "today": _write_manifest(root, "2026-09-07", [
            _rec("doi:10.1/t1", "Today one"), _rec("doi:10.1/t2", "Today two")]),
        "amb": _write_manifest(root, "2026-09-03", [
            _rec("doi:10.1/amb", "Ambiguous four days old", proposal_history=[
                {"at": "2026-09-03T15:30:00+00:00", "proposed": "wiki", "reason": "unsure"}]),
            _rec("doi:10.1/done", "Resolved earlier", disposition="wiki",
                 disposition_confidence="clear")]),
        "edge": _write_manifest(root, "2026-08-31", [_rec("doi:10.1/edge", "Exactly seven days old")]),
        "old": _write_manifest(root, "2026-08-29", [_rec("doi:10.1/old", "Nine days old, stranded")]),
        "resolved": _write_manifest(root, "2026-09-05", [
            _rec("doi:10.1/r", "All resolved", disposition="discard", disposition_confidence="clear")]),
    }
    return root, paths


def test_open_set_windows_and_strands():
    root, p = _open_root()
    today = dt.date(2026, 9, 7)
    osr = sta.open_set(sta.load_manifests(str(root)), today, carryover_days=7)
    assert [e["path"] for e in osr["open"]] == [p["edge"], p["amb"], p["today"]]  # oldest first
    assert [e["unresolved"] for e in osr["open"]] == [
        ["doi:10.1/edge"], ["doi:10.1/amb"], ["doi:10.1/t1", "doi:10.1/t2"]]
    assert [e["age_days"] for e in osr["open"]] == [7, 4, 0]
    assert [e["path"] for e in osr["stranded"]] == [p["old"]]
    assert osr["stranded"][0]["age_days"] == 9
    # a wider window recovers the stranded manifest (the one-off backfill)
    wide = sta.open_set(sta.load_manifests(str(root)), today, carryover_days=9)
    assert p["old"] in [e["path"] for e in wide["open"]] and wide["stranded"] == []
    # no window at all: only today's manifest is open, everything older strands
    zero = sta.open_set(sta.load_manifests(str(root)), today, carryover_days=0)
    assert [e["path"] for e in zero["open"]] == [p["today"]]
    assert len(zero["stranded"]) == 3


def test_open_set_manifest_without_date_stays_in_window():
    root = Path(tempfile.mkdtemp())
    d = root / "scan-x"; d.mkdir()
    path = d / "manifest-undated.json"
    path.write_text(json.dumps({"records": [_rec("doi:10.1/u", "Undated")]}), encoding="utf-8")
    osr = sta.open_set(sta.load_manifests(str(root)), dt.date(2026, 9, 7), carryover_days=7)
    assert [e["path"] for e in osr["open"]] == [path] and osr["open"][0]["age_days"] is None


def test_open_set_dispositions_span_manifests_and_stamp_back():
    root, p = _open_root()
    osr = sta.open_set(sta.load_manifests(str(root)), dt.date(2026, 9, 7))
    merged0, origin = sta.merge_open_set(osr["open"])
    assert origin["doi:10.1/amb"] == p["amb"] and origin["doi:10.1/t1"] == p["today"]
    assert "doi:10.1/done" in origin  # disposed records travel too, so validation still sees them
    assert merged0["generated"] == "2026-09-07"  # newest open manifest when no run date is given
    only_old = [e for e in osr["open"] if e["path"] == p["amb"]]
    assert sta.merge_open_set(only_old)[0]["generated"] == "2026-09-03"
    assert sta.merge_open_set(only_old, today=dt.date(2026, 9, 7))[0]["generated"] == "2026-09-07"
    disp = {"judged_by": "test", "entries": [
        {"id": "doi:10.1/amb", "disposition": "read-once", "confidence": "clear", "reason": "owner resolved"},
        {"id": "doi:10.1/t1", "disposition": "wiki", "confidence": "clear", "reason": "evidence"},
        {"id": "doi:10.1/edge", "disposition": "wiki", "confidence": "ambiguous", "reason": "still unsure"},
    ]}
    merged1, plan = sta.apply_dispositions(merged0, disp)
    assert [m["id"] for m in plan["moves"]] == ["doi:10.1/t1"]
    assert [m["id"] for m in plan["read_once"]] == ["doi:10.1/amb"]
    assert {m["id"] for m in plan["needs_call"]} == {"doi:10.1/edge", "doi:10.1/t2"}
    touched = sta.stamp_back(merged1, origin, osr["open"])
    assert set(touched) == {p["amb"], p["today"], p["edge"]}  # edge changed: history appended
    amb_manifest = next(e["manifest"] for e in osr["open"] if e["path"] == p["amb"])
    by_id = {r["id"]: r for r in amb_manifest["records"]}
    assert by_id["doi:10.1/amb"]["disposition"] == "read-once"
    assert by_id["doi:10.1/done"]["disposition"] == "wiki"  # untouched neighbour
    edge_manifest = next(e["manifest"] for e in osr["open"] if e["path"] == p["edge"])
    assert edge_manifest["records"][0]["disposition"] is None
    assert edge_manifest["records"][0]["proposal_history"][0]["reason"] == "still unsure"
    # already-disposed validation keeps its meaning across the merged set
    try:
        sta.apply_dispositions(merged0, {"entries": [
            {"id": "doi:10.1/done", "disposition": "discard", "confidence": "clear"}]})
        raise AssertionError("expected already-disposed ValueError")
    except ValueError as e:
        assert "already-disposed" in str(e)


def test_open_set_duplicate_id_across_manifests_fails_loud():
    root = Path(tempfile.mkdtemp())
    _write_manifest(root, "2026-09-06", [_rec("doi:10.1/dup", "Same id, day one")])
    _write_manifest(root, "2026-09-07", [_rec("doi:10.1/dup", "Same id, day two")])
    osr = sta.open_set(sta.load_manifests(str(root)), dt.date(2026, 9, 7))
    try:
        sta.merge_open_set(osr["open"])
        raise AssertionError("expected ValueError for a cross-manifest duplicate id")
    except ValueError as e:
        assert "more than one open manifest" in str(e) and "doi:10.1/dup" in str(e)


def test_digest_carryover_section_and_warnings():
    root, p = _open_root()
    osr = sta.open_set(sta.load_manifests(str(root)), dt.date(2026, 9, 7), carryover_days=7)
    merged0, _ = sta.merge_open_set(osr["open"])
    merged1, plan = sta.apply_dispositions(merged0, {"entries": [
        {"id": "doi:10.1/amb", "disposition": "read-once", "confidence": "clear", "reason": "r"},
        {"id": "doi:10.1/t1", "disposition": "wiki", "confidence": "clear", "reason": "r"},
    ]})
    carry = sta.carryover_summary(osr["open"], osr["stranded"], plan, window_days=7)
    assert [i["id"] for i in carry["items"]] == ["doi:10.1/edge", "doi:10.1/amb"]  # age >= 1 only
    assert carry["items"][0]["outcome"] == "still needs your call"
    assert carry["items"][1] == {"id": "doi:10.1/amb", "title": "Ambiguous four days old",
                                 "age_days": 4, "manifest": p["amb"].name, "outcome": "→ read-once"}
    assert [a["id"] for a in carry["aging_out"]] == ["doi:10.1/edge"]  # still pending at age == window
    assert carry["stranded"] == {"count": 1, "manifests": 1, "oldest": "2026-08-29",
                                 "carryover_days_needed": 9}
    digest = sta.render_digest(merged1, plan, executed=False, carryover=carry)
    assert "**Carried over (age)** — 2 from earlier manifests" in digest
    assert "4 judged (2 new, 2 carried over)" in digest
    assert "Ambiguous four days old — 4d" in digest and "→ read-once" in digest
    assert "age out of the 7-day carryover window" in digest and "Exactly seven days old" in digest
    assert "Stranded: 1 unresolved" in digest and "--carryover-days 9" in digest
    # once the edge item is resolved, the aging-out warning disappears
    merged2, plan2 = sta.apply_dispositions(merged0, {"entries": [
        {"id": "doi:10.1/edge", "disposition": "discard", "confidence": "clear", "reason": "dup"}]})
    carry2 = sta.carryover_summary(osr["open"], [], plan2, window_days=7)
    assert carry2["aging_out"] == [] and carry2["stranded"]["count"] == 0
    digest2 = sta.render_digest(merged2, plan2, executed=False, carryover=carry2)
    assert "age out" not in digest2 and "Stranded" not in digest2
    assert "Exactly seven days old — 7d" in digest2 and "→ discarded" in digest2
    # no carryover argument -> the single-manifest digest is unchanged
    assert "Carried over" not in sta.render_digest(merged1, plan, executed=False)


def test_execute_open_set_persists_only_touched_manifests():
    root, p = _open_root()
    osr = sta.open_set(sta.load_manifests(str(root)), dt.date(2026, 9, 7))
    merged0, origin = sta.merge_open_set(osr["open"])
    merged1, plan = sta.apply_dispositions(merged0, {"entries": [
        {"id": "doi:10.1/amb", "disposition": "read-once", "confidence": "clear", "reason": "r"}]})
    moves, uploads = [], []
    saved = (sta.c.build_drive_service, sta.c.drive_move, sta.c.drive_find, sta.c.drive_upload_bytes)
    try:
        sta.c.build_drive_service = lambda _token: object()
        sta.c.drive_move = lambda _svc, fid, dest, source: moves.append((fid, dest, source))
        sta.c.drive_find = lambda _svc, _folder, _name: None
        sta.c.drive_upload_bytes = lambda _svc, folder, name, data, mime: (
            uploads.append(name) or "manifest-id")
        touched = sta.execute_open_set(merged1, plan, osr["open"], "/unused/token.json", origin=origin)
    finally:
        sta.c.build_drive_service, sta.c.drive_move, sta.c.drive_find, sta.c.drive_upload_bytes = saved
    assert touched == [p["amb"]]
    assert uploads == [p["amb"].name]
    assert moves == [("drv-amb", sta.cfg.TRIAGE_READ_ONCE_FOLDER_ID, sta.cfg.TRIAGE_PENDING_FOLDER_ID)]
    on_disk = json.loads(p["amb"].read_text(encoding="utf-8"))
    assert next(r for r in on_disk["records"] if r["id"] == "doi:10.1/amb")["disposition"] == "read-once"
    assert json.loads(p["today"].read_text(encoding="utf-8"))["records"][0]["disposition"] is None


def test_digest_tags_unlisted_venues():
    src = _manifest()
    src["records"][0]["venue_tier"] = "unlisted"     # clear wiki paper with artifact
    src["records"][3]["venue_tier"] = "watchlist"    # ambiguous borderline paper
    manifest, plan = sta.apply_dispositions(src, _dispositions())
    digest = sta.render_digest(manifest, plan, executed=False)
    assert "Clear wiki paper with artifact — rct evidence [venue: unlisted]" in digest
    assert "[venue: watchlist]" not in digest
    assert plan["moves"][0]["venue_tier"] == "unlisted"


def test_disposition_aliases_are_normalized():
    manifest, plan = sta.apply_dispositions(_manifest(), {"entries": [
        {"id": "doi:10.1/e", "disposition": "discarded", "confidence": "clear", "reason": "dup"}]})
    assert [m["id"] for m in plan["discard"]] == ["doi:10.1/e"]
    assert next(r for r in manifest["records"] if r["id"] == "doi:10.1/e")["disposition"] == "discard"
    assert sta.normalize_disposition("Read_Once") == "read-once"


def test_amend_redisposes_and_records_history():
    m = _manifest()
    updated, changed = sta.amend_disposition(
        m, "doi:10.1/z", "discarded", "owner rejected at ingest: not rigorous",
        by="research-wiki-ingest", now="2026-09-07T20:00:00+00:00")
    assert changed
    rec = next(r for r in updated["records"] if r["id"] == "doi:10.1/z")
    assert rec["disposition"] == "discard" and rec["disposition_confidence"] == "clear"
    assert rec["amended_by"] == "research-wiki-ingest" and rec["amended_at"] == "2026-09-07T20:00:00+00:00"
    assert rec["proposal_history"][-1] == {
        "at": "2026-09-07T20:00:00+00:00", "kind": "amend", "amended_from": "wiki",
        "proposed": "discard", "reason": "owner rejected at ingest: not rigorous",
        "by": "research-wiki-ingest"}
    assert next(r for r in m["records"] if r["id"] == "doi:10.1/z")["disposition"] == "wiki"  # caller untouched
    # idempotent: same clear disposition again changes nothing
    again, changed2 = sta.amend_disposition(updated, "doi:10.1/z", "discard", "again")
    assert not changed2
    assert len(next(r for r in again["records"] if r["id"] == "doi:10.1/z")["proposal_history"]) == 1
    # the ordinary applier still refuses to re-dispose the amended record
    try:
        sta.apply_dispositions(updated, {"entries": [
            {"id": "doi:10.1/z", "disposition": "wiki", "confidence": "clear"}]})
        raise AssertionError("expected already-disposed ValueError")
    except ValueError as e:
        assert "already-disposed" in str(e)
    for rid, to, msg in [("doi:10.9/none", "discard", "not in manifest"),
                         ("doi:10.1/z", "keep", "invalid disposition")]:
        try:
            sta.amend_disposition(m, rid, to, "x")
            raise AssertionError(f"expected ValueError containing {msg!r}")
        except ValueError as e:
            assert msg in str(e)
    # amend entries are owner rulings, not rubric friction
    assert sta.collect_friction([updated], dt.date(2026, 9, 8), window_days=14) == []


def test_find_record_by_drive_file_id_and_ambiguity():
    root = Path(tempfile.mkdtemp())
    _write_manifest(root, "2026-09-01", [_rec("doi:10.1/a", "A")])
    p2 = _write_manifest(root, "2026-09-02", [_rec("doi:10.1/b", "B", disposition="wiki")])
    found = sta.find_record(sta.load_manifests(str(root)), drive_file_id="drv-b")
    assert found[0] == p2 and found[2]["id"] == "doi:10.1/b"
    assert sta.find_record(sta.load_manifests(str(root)), rid="doi:10.1/nope") is None
    _write_manifest(root, "2026-09-03", [_rec("doi:10.1/b", "B again")])
    try:
        sta.find_record(sta.load_manifests(str(root)), rid="doi:10.1/b")
        raise AssertionError("expected ambiguity ValueError")
    except ValueError as e:
        assert "ambiguous" in str(e)


def test_cli_show_open_and_amend_dry_run(capsys=None):
    import io
    import contextlib
    root, p = _open_root()
    saved_now = sta.c.utc_now
    try:
        sta.c.utc_now = lambda: dt.datetime(2026, 9, 7, 16, 0, tzinfo=dt.timezone.utc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert sta.main(["--show-open", "--out-root", str(root)]) == 0
        out = json.loads(buf.getvalue())
        assert out["window_days"] == 7 and [r["id"] for r in out["records"]] == [
            "doi:10.1/edge", "doi:10.1/amb", "doi:10.1/t1", "doi:10.1/t2"]
        assert out["records"][0]["_age_days"] == 7 and out["aging_out_after_this_run"] == ["doi:10.1/edge"]
        assert out["stranded_outside_window"]["ids"] == ["doi:10.1/old"]
        assert out["stranded_outside_window"]["carryover_days_needed"] == 9
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert sta.main(["--amend", "--drive-file-id", "drv-done", "--to", "discarded",
                             "--reason", "owner rejected", "--out-root", str(root)]) == 0
        assert "wiki -> discard" in buf.getvalue() and "DRY RUN" in buf.getvalue()
        assert next(r for r in json.loads(p["amb"].read_text())["records"]
                    if r["id"] == "doi:10.1/done")["disposition"] == "wiki"  # dry run wrote nothing
        assert sta.main(["--amend", "--drive-file-id", "drv-nope", "--to", "discard",
                         "--out-root", str(root)]) == sta.EXIT_NO_MATCH
    finally:
        sta.c.utc_now = saved_now


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
