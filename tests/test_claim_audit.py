"""Guardrail tests for the claim-fidelity audit sampler/recorder (pure logic only)."""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools"
sys.path.insert(0, str(_TOOLS))

import claim_audit as ca  # noqa: E402

DIFF = """diff --git a/wiki/topics/ai-adoption.md b/wiki/topics/ai-adoption.md
--- a/wiki/topics/ai-adoption.md
+++ b/wiki/topics/ai-adoption.md
@@ -3 +3 @@
-updated: 2026-08-01
+updated: 2026-09-08
@@ -10,0 +11,2 @@
+[[2026-shoghli-persona-migration-expectation-recalibration]] adds post-use expectation recalibration in a longitudinal Copilot pilot, where early enthusiasts and sceptics migrated between adoption personas.
+Organizations should therefore expect adoption attitudes to move after first use rather than settle on day one, which changes when readiness should be measured.
@@ -20,0 +23 @@
+- Relates to [[ai-receptivity]] via willingness-to-use dynamics.
diff --git a/wiki/topics/work-redesign.md b/wiki/topics/work-redesign.md
--- a/wiki/topics/work-redesign.md
+++ b/wiki/topics/work-redesign.md
@@ -5,0 +6 @@
+## Contradictions & open questions
@@ -7,0 +9 @@
+- [[2026-liu-organizational-ai-adoption-job-crafting]] and [[2025-x-other]] disagree on whether adoption raises or lowers autonomy-linked crafting — surfaced, not resolved, in a three-wave survey.
"""
SOURCES = {"2026-shoghli-persona-migration-expectation-recalibration", "2026-liu-organizational-ai-adoption-job-crafting", "2025-x-other"}
TOPICS = {"ai-adoption", "ai-receptivity", "work-redesign"}


def test_extract_added_claims_keeps_prose_skips_navigation_and_frontmatter():
    claims = ca.extract_added_claims(DIFF, "abc123def456", "2026-09-08", SOURCES, TOPICS)
    texts = [c["text"][:30] for c in claims]
    assert len(claims) == 3, texts
    assert claims[0]["topic"] == "ai-adoption" and claims[0]["cited_sources"] == ["2026-shoghli-persona-migration-expectation-recalibration"]
    assert claims[1]["uncited"] is True and claims[1]["cited_sources"] == []      # uncited prose is a candidate
    assert claims[2]["topic"] == "work-redesign" and set(claims[2]["cited_sources"]) == {"2026-liu-organizational-ai-adoption-job-crafting", "2025-x-other"}
    assert not any("Relates to" in c["text"] for c in claims)                      # Connections bullet skipped
    assert not any(c["text"].startswith(("updated:", "#")) for c in claims)
    assert all(len(c["id"]) == 10 for c in claims) and claims[0]["commit"] == "abc123def4"


def test_sampling_is_deterministic_per_seed_and_bounded():
    claims = ca.extract_added_claims(DIFF, "abc123def456", "2026-09-08", SOURCES, TOPICS)
    a = ca.sample_claims(claims, 2, "2026-09"); b = ca.sample_claims(claims, 2, "2026-09")
    assert [x["id"] for x in a] == [x["id"] for x in b] and len(a) == 2
    assert len(ca.sample_claims(claims, 10, "2026-09")) == 3      # k larger than the pool
    assert ca.sample_claims([], 5, "s") == [] and ca.sample_claims(claims, 0, "s") == []
    assert ca.dedupe(claims + claims) == claims


def test_grade_validation_and_summary():
    claims = ca.extract_added_claims(DIFF, "abc123def456", "2026-09-08", SOURCES, TOPICS)
    grades = [{"id": claims[0]["id"], "grade": "cited-supported", "note": "matches abstract"},
              {"id": claims[1]["id"], "grade": "uncited"},
              {"id": claims[2]["id"], "grade": "reasoning-error", "note": "causal reading of a survey"}]
    graded = ca.validate_grades(claims, grades)
    s = ca.summarize(graded)
    assert s["n"] == 3 and s["counts"]["cited-supported"] == 1 and s["counts"]["reasoning-error"] == 1
    assert s["supported_rate"] == 0.333
    for bad, msg in [
        (grades[:2], "ungraded"),
        (grades + [{"id": "nope", "grade": "uncited"}], "unknown claim id"),
        (grades + [grades[0]], "graded twice"),
        ([{**grades[0], "grade": "fine"}] + grades[1:], "not in"),
    ]:
        try:
            ca.validate_grades(claims, bad); raise AssertionError(msg)
        except ValueError as e:
            assert msg in str(e)
    digest = ca.render_digest({**s, "stamp": "20261001T160000Z"}, [{"stamp": "20260901T160000Z", "supported_rate": 0.9}],
                              graded, 35, 40, executed=True)
    assert "3 claims sampled from 40" in digest and "supported rate 33%" in digest
    assert "Trend" in digest and "2026-09: 90%" in digest and "Needs a look" in digest
    assert "[reasoning-error] `work-redesign`" in digest and "spot-check at least 2" in digest


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
