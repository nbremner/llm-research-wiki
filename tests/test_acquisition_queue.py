"""Guardrail tests for the needs-acquisition ledger (pure logic only)."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import acquisition_queue as aq  # noqa: E402

TODAY = dt.date(2026, 9, 8)


def _manifests():
    return [{"records": [
        {"id": "doi:10.1/paywalled", "title": "Paywalled but wanted", "doi": "10.1/paywalled", "url": "https://doi.org/10.1/paywalled",
         "disposition": "wiki", "disposition_confidence": "clear", "triaged_at": "2026-07-04T15:30:00+00:00",
         "source_type": "peer-reviewed", "venue": "J", "venue_tier": "unlisted", "acq_state": "abstract-only", "year": "2026"},
        {"id": "doi:10.1/acquired", "title": "Has an artifact", "disposition": "wiki", "artifact_drive_id": "drv-x", "triaged_at": "2026-07-05T15:30:00+00:00"},
        {"id": "doi:10.1/inwiki", "title": "Already in the wiki by DOI", "doi": "10.1/inwiki", "disposition": "wiki", "triaged_at": "2026-07-06T15:30:00+00:00"},
        {"id": "doi:10.1/titlematch", "title": "The Cybernetic Teammate: A Field Experiment on Generative AI and Teamwork", "disposition": "wiki", "triaged_at": "2026-07-07T15:30:00+00:00"},
        {"id": "doi:10.1/readonce", "title": "Read once", "disposition": "read-once", "triaged_at": "2026-07-08T15:30:00+00:00"},
        {"id": "doi:10.1/ambig", "title": "Ambiguous wiki", "disposition": "wiki", "disposition_confidence": "ambiguous"},
        {"id": "doi:10.1/rejected", "title": "Owner rejected later", "disposition": "discard", "proposal_history": [{"kind": "amend", "amended_from": "wiki"}]},
        {"id": "arxiv:2608.1", "title": "Recent preprint waiting", "url": "https://arxiv.org/abs/2608.1", "disposition": "wiki",
         "triaged_at": "2026-09-01T15:30:00+00:00", "source_type": "preprint", "acq_state": "link-only"},
    ]}]


def test_queue_excludes_acquired_ingested_rejected_and_non_wiki():
    wiki_ids = {"doi:10.1/inwiki"}
    wiki_titles = {aq.c.normalize_title("The Cybernetic Teammate — A Field Experiment on Generative AI and Teamwork")}
    q = aq.build_queue(_manifests(), wiki_ids, wiki_titles, TODAY)
    assert [x["id"] for x in q] == ["doi:10.1/paywalled", "arxiv:2608.1"]      # oldest first
    assert q[0]["days_waiting"] == 66 and q[0]["venue_tier"] == "unlisted" and q[1]["days_waiting"] == 7


def test_diff_summary_and_ledger():
    q = aq.build_queue(_manifests(), set(), set(), TODAY)
    diff = aq.diff_queue({"doi:10.1/paywalled", "doi:10.1/gone"}, q)
    assert diff == {"added": ["arxiv:2608.1", "doi:10.1/inwiki", "doi:10.1/titlematch"], "removed": ["doi:10.1/gone"]}
    line = aq.summary_line(q, diff)
    assert line.startswith("Acquisition backlog: 4 wiki-judged paper(s) without a copy (+3 new, −1 acquired/removed)")
    assert "_triage/needs-acquisition.md" in line
    assert aq.summary_line([], {"added": [], "removed": []}).startswith("Acquisition backlog: none")
    ledger = aq.render_ledger(q, TODAY, diff)
    assert "# Needs acquisition" in ledger and "| 1 | 66d | 2026-07-04 | Paywalled but wanted |" in ledger
    assert "reject <record id>" in ledger and "peer-reviewed 1" in ledger and "preprint 1" in ledger
    assert "https://doi.org/10.1/inwiki" in ledger     # DOI-only records still get a link


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
