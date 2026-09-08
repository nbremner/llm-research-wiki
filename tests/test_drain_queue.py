"""Guardrail tests for the drain order (owner-dropped files first)."""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import drain_queue as dq  # noqa: E402


def test_owner_dropped_first_then_oldest():
    files = [
        {"id": "s-old", "name": "2025-a.pdf", "createdTime": "2026-07-13T00:00:00Z"},
        {"id": "o-new", "name": "pgag030.pdf", "createdTime": "2026-09-08T06:29:00Z"},
        {"id": "s-new", "name": "2026-b.md", "createdTime": "2026-09-07T00:00:00Z"},
        {"id": "o-old", "name": "ssrn-7239598.pdf", "createdTime": "2026-09-08T06:24:00Z"},
    ]
    q = dq.order_queue(files, scan_artifact_ids={"s-old", "s-new"})
    assert [f["id"] for f in q] == ["o-old", "o-new", "s-old", "s-new"]
    assert [f["origin"] for f in q] == ["owner", "owner", "scan", "scan"]
    assert dq.counts(q) == {"owner": 2, "scan": 2, "total": 4}
    assert dq.order_queue([], set()) == [] and dq.counts([]) == {"owner": 0, "scan": 0, "total": 0}


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
