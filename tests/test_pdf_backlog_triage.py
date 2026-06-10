import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "research-wiki-tools" / "pdf_backlog_triage.py"
spec = importlib.util.spec_from_file_location("pdf_backlog_triage", MODULE_PATH)
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)


def test_doi_preferred_as_canonical_url_and_garbage_urls_filtered():
    text = """
    https://creativecommons.org/licenses/by/4.0/
    https://doi.org/10.1017/iop.2022.112
    DOI: 10.1017/iop.2022.112
    """

    signals = triage.extract_biblio_signals(text, {}, "Watts et al. (2023) How Relevant is the APA Ethics Code to IO Psychology.pdf")

    assert signals["doi"] == "10.1017/iop.2022.112"
    assert signals["canonical_url_candidate"] == "https://doi.org/10.1017/iop.2022.112"
    assert "https://creativecommons.org/licenses/by/4.0/" not in signals["urls"]


def test_filename_author_candidates_and_confidence_for_academic_filename():
    signals = triage.extract_biblio_signals(
        "A simulation of the impacts of machine learning to combine predictors\nAbstract\n...",
        {},
        "Landers (2023) Simulation of Machine Learning Impacts on Psychometric Employee Assessment.pdf",
    )

    assert signals["filename_author_candidate"] == "Landers"
    assert signals["author_confidence"] == "filename-only"


def test_title_detection_rejects_layout_garbage_and_uses_filename_title():
    title = triage.likely_title_from_text(
        "1984, Vol96, No. 1,72-98\nJournal of Applied Psychology\nAbstract\n...",
        "1984, Vol96, No. 1,72-98",
        "Hunter and Hunter (1984) Validity and Utility of Alternative Predictors of Job Performance.pdf",
    )

    assert title == "Validity and Utility of Alternative Predictors of Job Performance"


def test_title_detection_rejects_journal_header_and_author_line():
    assert triage.likely_title_from_text(
        "ORGANIZATIONAL BEHAVIOR AND HUMAN PERFORMANCE 25, 15-31 (1980)\nAbstract",
        None,
        "Moch (1980) work relationships and job involvement.pdf",
    ) == "work relationships and job involvement"
    assert triage.likely_title_from_text(
        "Sujin K. Horwitz and Irwin B. Horwitz\nAbstract",
        None,
        "Horwitz & Horwitz (2007) The_effects_of_team_diversity_on_team_ou.pdf",
    ) == "The effects of team diversity on team ou"


def test_policy_standards_slide_and_book_classification_overrides():
    assert triage.infer_source_type("", "(Non-Academic) NYC Assessment AI Policy FAQ.pdf") == "policy-guide"
    assert triage.infer_evidence_type("", "(Non-Academic) NYC Assessment AI Policy FAQ.pdf") == "policy-guide"
    assert triage.infer_source_type("", "(Non-Academic) APA (2014) Standards for Educational and Psychological Testing.pdf") == "standards-manual"
    assert triage.infer_evidence_type("", "(Non-Academic) NYC AEDT Program Block 6 - AI Legal Update and Affirmative Action.pdf") == "slide-deck"
    assert triage.infer_source_type("", "Cameron and Quinn (2011) Diagnosing and Changing Organizational Culture.pdf") == "book"
    assert triage.infer_source_type("DOI abstract recommendations for future research in personnel selection", "Landers (2023) Simulation of Machine Learning Impacts on Psychometric Employee Assessment.pdf") == "academic-article"
