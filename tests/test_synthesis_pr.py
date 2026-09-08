"""Guardrail tests for the synthesis-batch PR helper (pure logic only)."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import synthesis_pr as sp  # noqa: E402


def _pr(number, branch, created, state="open", merged=None):
    return {"number": number, "head": {"ref": branch}, "state": state, "merged_at": merged,
            "created_at": f"{created}T09:00:00Z", "html_url": f"https://github.com/x/pull/{number}", "title": "t"}


def test_credential_fill_parsing_never_needs_the_token_in_code():
    assert sp.parse_credential_fill("protocol=https\nhost=github.com\nusername=x\npassword=ghp_abc\n") == "ghp_abc"
    assert sp.parse_credential_fill("protocol=https\nhost=github.com\n") is None


def test_synthesis_prs_filters_and_orders():
    prs = sp.synthesis_prs([_pr(3, "synthesis/2026-09-21", "2026-09-21"), _pr(1, "feature/x", "2026-01-01"),
                            _pr(2, "synthesis/2026-09-14", "2026-09-14", state="closed", merged="2026-09-15T00:00:00Z")])
    assert [p["number"] for p in prs] == [2, 3]
    assert prs[0]["merged"] is True and prs[1]["merged"] is False


def test_one_open_batch_rule():
    today = dt.date(2026, 9, 21)
    assert sp.classify([], today)["action"] == "go"
    fresh = sp.synthesis_prs([_pr(5, "synthesis/2026-09-16", "2026-09-16")])
    d = sp.classify(fresh, today); assert d["action"] == "skip" and d["age_days"] == 5
    stale = sp.synthesis_prs([_pr(4, "synthesis/2026-09-14", "2026-09-14")])
    d = sp.classify(stale, today); assert d["action"] == "regenerate" and d["age_days"] == 7
    two = sp.synthesis_prs([_pr(4, "synthesis/2026-09-14", "2026-09-14"), _pr(5, "synthesis/2026-09-16", "2026-09-16")])
    assert sp.classify(two, today)["action"] == "manual"
    assert sp.classify(sp.synthesis_prs([_pr(6, "synthesis/x", "not-a-date")]), today)["action"] == "skip"  # unknown age never regenerates


def test_prunable_only_when_every_pr_for_the_branch_is_closed():
    prs = sp.synthesis_prs([_pr(1, "synthesis/a", "2026-09-01", state="closed", merged="2026-09-02T00:00:00Z"),
                            _pr(2, "synthesis/b", "2026-09-08"),
                            _pr(3, "synthesis/c", "2026-09-10", state="closed")])
    assert sp.prunable(["synthesis/a", "synthesis/b", "synthesis/c", "synthesis/orphan"], prs) == ["synthesis/a", "synthesis/c"]


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
