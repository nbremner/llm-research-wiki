"""
scan_config.py -- the editable rubric/config for the research-scan harness.

This is DATA, not machinery: seed queries, the wiki concept vocabulary, source
authority weights, ranking weights, and run caps. Edit this to retune what the
scan looks for and how it ranks -- no code change needed. See
docs/research-scrape-plan.md for the architecture.

Anchored on the wiki's mission (AI workforce transformation x I-O psychology, per
wiki/overview.md; the live topic list is wiki/topic-map.md), NOT the wrapped-up
applied "U4B / B2B-sales" research questions.
A future applied project = a new profile here, not a rebuild.
"""

from __future__ import annotations

# --- Google Drive layout (folder IDs are pointers, not secrets) -------------
# One stateful triage area. Folder location is the owner-facing workflow state.
TRIAGE_FOLDER_ID = "1tXLfXs2z8LkbAurlrw8G7IYfQu1mCXh8"
TRIAGE_PENDING_FOLDER_ID = "1_9TRp4H1Qqm0M4QI8hGiMkWNs9hc_GXg"
TRIAGE_WIKI_FOLDER_ID = "1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1"
TRIAGE_READ_ONCE_FOLDER_ID = "1RQdnNN1d_iWegTWSqr4jZ7lYV86vtL8o"
TRIAGE_DISCARDED_FOLDER_ID = "1fNRrNYxwxB87lQeXtfiZ7Fc6S5FMcwNx"
TRIAGE_LEDGER_FOLDER_ID = "1Fw7J30oerCSCYSLcEB5k0mbbdfOGwyx1"

# Drive OAuth token used by NJ's research tooling (authorized-user JSON).
DEFAULT_TOKEN_PATH = "/root/.hermes/google_token.json"
DEFAULT_OUT_ROOT = "/root/research-wiki-runs"

# Polite-pool contact for OpenAlex / Crossref / Unpaywall (a courtesy, not a secret).
CONTACT_MAILTO = "nicholasbremner@gmail.com"

SCHEMA_VERSION = "2026-08-20.1"
PRODUCED_BY = "Hermes / NicholasJunior (research-scan harness)"

# --- Source authority weights (0..1) for pre-rank ---------------------------
# Higher = more trusted as primary evidence for the wiki. Practitioner/news are
# still captured (usually read-once) but rank lower for wiki candidacy.
SOURCE_AUTHORITY = {
    "peer-reviewed": 1.0,
    "working-paper": 0.8,   # NBER, SSRN, IZA
    "preprint": 0.7,        # arXiv
    "gov": 0.7,             # BLS, Fed, OECD, ILO, IMF
    "think-tank": 0.55,     # Brookings, MGI, WEF
    "industry": 0.4,        # vendor / consulting reports
    "news": 0.3,
    "other": 0.3,
}

# Per-host source-type hints, used when the discovery API does not classify it.
HOST_SOURCE_TYPE = {
    "arxiv.org": "preprint",
    "nber.org": "working-paper",
    "www2.nber.org": "working-paper",
    "papers.ssrn.com": "working-paper",
    "ssrn.com": "working-paper",
    "iza.org": "working-paper",
    "docs.iza.org": "working-paper",
    "bls.gov": "gov",
    "www.bls.gov": "gov",
    "federalreserve.gov": "gov",
    "www.federalreserve.gov": "gov",
    "oecd.org": "gov",
    "www.oecd.org": "gov",
    "ilo.org": "gov",
    "imf.org": "gov",
    "www.imf.org": "gov",
    "brookings.edu": "think-tank",
    "www.brookings.edu": "think-tank",
    "weforum.org": "think-tank",
    "www.weforum.org": "think-tank",
    "mckinsey.com": "industry",
    "www.mckinsey.com": "industry",
}

# --- Wiki concept vocabulary (topic slug -> keywords) -----------------------
# Drives concept-match scoring. Derived from wiki/topic-map.md topics. Keep roughly
# in sync as topics are added; extra or stale keys are harmless.
WIKI_CONCEPTS = {
    "automation-and-substitution": ["automation", "substitution", "displacement", "augmentation", "labor demand", "task exposure"],
    "task-level-ai-adoption": ["task", "occupation", "generative ai use", "task exposure", "o*net"],
    "ai-adoption": ["ai adoption", "diffusion", "technology acceptance", "adoption barrier"],
    "ai-readiness": ["ai readiness", "maturity", "organizational capability", "data readiness"],
    "work-redesign": ["work redesign", "job redesign", "workflow", "human-agent", "reorganization"],
    "human-ai-collaboration": ["human-ai", "human ai collaboration", "centaur", "cyborg", "augmentation"],
    "human-ai-task-allocation": ["task allocation", "delegate to ai", "routing", "defer to human", "allocation policy"],
    "human-ai-task-taxonomy": ["task taxonomy", "task classification", "task dimensions"],
    "agentic-delegation": ["ai agent", "agentic", "delegation", "execution authority", "autonomy"],
    "ai-agent-benchmark-validity": ["agent benchmark", "benchmark validity", "task benchmark", "capability evaluation"],
    "ai-workforce-impact-measurement": ["workforce impact", "productivity measurement", "impact evaluation", "applicability"],
    "algorithmic-assessment": ["algorithmic hiring", "automated employment decision", "aedt", "selection", "assessment"],
    "job-analysis": ["job analysis", "ksao", "work analysis", "task analysis", "o*net"],
    "competency-modeling": ["competency model", "competency modeling", "capability model"],
    "construct-validity": ["construct validity", "measurement", "psychometric", "validity"],
    "responsible-ai-deployment": ["responsible ai", "ai governance", "audit", "accountability", "worker rights"],
    "moral-boundaries-of-ai-automation": ["moral", "repugnance", "human presence", "dignity", "acceptability"],
    "ai-induced-skill-erosion": ["deskilling", "skill erosion", "skill atrophy", "expertise loss", "cognitive debt"],
    "ai-mediated-learning": ["learning", "skill formation", "training", "cognitive debt", "transfer"],
    "critical-thinking": ["critical thinking", "judgment", "verification", "cognitive offloading"],
    "automation-complacency": ["automation complacency", "over-reliance", "vigilance", "monitoring"],
    "cognitive-load-in-ai-assisted-work": ["cognitive load", "mental workload", "extraneous load", "task switching"],
    "ai-mediated-work-experience": ["autonomy", "job quality", "meaningful work", "worker experience", "well-being"],
    "ai-enabled-job-crafting": ["job crafting", "work engagement", "proactive", "task crafting"],
    "ai-supported-knowledge-synthesis": ["knowledge work", "sensemaking", "synthesis", "decision support"],
    "ai-literacy": ["ai literacy", "understanding ai", "calibrated use", "mental model"],
    "ai-receptivity": ["ai receptivity", "willingness to use", "adoption intention", "acceptance"],
    "ai-use-image-concerns": ["image concern", "social evaluation", "stigma", "impression management"],
    "novice-risk-work": ["novice", "reverse mentoring", "junior", "risk mitigation"],
    "ai-mediated-teamwork": ["team", "teamwork", "coordination", "cybernetic teammate"],
    "ai-mediated-organizational-networks": ["organizational network", "knowledge sharing", "centrality", "collaboration network"],
    "employee-engagement": ["employee engagement", "engagement"],
    "human-capital-resource-measurement": ["human capital", "collective capability", "human capital resource"],
    "inclusive-hr-systems": ["inclusion", "diversity", "fairness", "inclusive hr"],
    "evidence-based-management": ["evidence-based management", "evidence quality"],
    "complex-collaborative-problem-solving": ["collaborative problem solving", "complex problem", "21st century skills"],
}

# On-mission gate: a candidate must touch BOTH an AI/tech term AND a work/labor
# term. The wiki is AI x work, so a paper with no labor angle (e.g. a computer-
# vision method that merely says "task"/"model") is off-mission and dropped.
# Tightened after the 2026-07-04 smoke test surfaced a CV preprint into the top 5.
AI_TERMS = [
    "artificial intelligence", "generative ai", "genai", "large language model", "llm",
    "machine learning", " ai ", "ai-", "ai agent", "algorithmic", "automation",
    "chatgpt", "copilot", "generative model", "foundation model",
]
WORK_TERMS = [
    "future of work", "workforce", "worker", "employee", "employer", "labor", "labour",
    "job", "occupation", "employment", "hiring", "human capital", "workplace",
    "productivity", "skill demand", "reskilling", "upskilling", "wage",
    "task allocation", "knowledge work", "organization", "organisation",
]

# --- Curated journal watchlist ------------------------------------------------
# Owner-supplied roster (2026-08-20), drawn from the workbook's primary and
# supplementary tabs. Low-relevance rows are intentionally excluded. ISSNs were
# verified against the Scopus Source List; prefer electronic ISSN when present.
# High/medium are provenance metadata, not different retrieval thresholds: every
# journal is scanned comprehensively, then the same AI x work gate is applied.
JOURNAL_WATCHLIST = [
    {"name": "Annual Review of Psychology", "issn": "1545-2085", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Psychological Bulletin", "issn": "0033-2909", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Academy of Management Review", "issn": "0363-7425", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Academy of Management Annals", "issn": "1941-6067", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Annual Review of Organizational Psychology and Organizational Behavior", "issn": "2327-0616", "relevance": "high", "field": "Psychology", "tab": "primary"},
    {"name": "International Journal of Management Reviews", "issn": "1468-2370", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Academy of Management Journal", "issn": "0001-4273", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Journal of Management", "issn": "0149-2063", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Organizational Research Methods", "issn": "1094-4281", "relevance": "high", "field": "Methods", "tab": "primary"},
    {"name": "Long Range Planning", "issn": "0024-6301", "relevance": "medium", "field": "Management", "tab": "primary"},
    {"name": "Administrative Science Quarterly", "issn": "0001-8392", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Annual Review of Sociology", "issn": "1545-2115", "relevance": "high", "field": "Sociology", "tab": "primary"},
    {"name": "Journal of Management Studies", "issn": "1467-6486", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Psychological Methods", "issn": "1082-989X", "relevance": "medium", "field": "Methods", "tab": "primary"},
    {"name": "Research Policy", "issn": "0048-7333", "relevance": "high", "field": "Interdisciplinary", "tab": "primary"},
    {"name": "Strategic Management Journal", "issn": "1097-0266", "relevance": "medium", "field": "Management", "tab": "primary"},
    {"name": "Academy of Management Perspectives", "issn": "1943-4529", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Human Resource Management Review", "issn": "1053-4822", "relevance": "high", "field": "HRM", "tab": "primary"},
    {"name": "MIS Quarterly", "issn": "0276-7783", "relevance": "high", "field": "Information Systems", "tab": "primary"},
    {"name": "Journal of Applied Psychology", "issn": "0021-9010", "relevance": "high", "field": "Psychology", "tab": "primary"},
    {"name": "The Leadership Quarterly", "issn": "1048-9843", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "American Sociological Review", "issn": "0003-1224", "relevance": "high", "field": "Sociology", "tab": "primary"},
    {"name": "British Journal of Management", "issn": "1467-8551", "relevance": "medium", "field": "Management", "tab": "primary"},
    {"name": "Big Data & Society", "issn": "2053-9517", "relevance": "high", "field": "Interdisciplinary", "tab": "primary"},
    {"name": "Journal of Organizational Behavior", "issn": "1099-1379", "relevance": "high", "field": "Psychology", "tab": "primary"},
    {"name": "Personnel Psychology", "issn": "0031-5826", "relevance": "high", "field": "Psychology", "tab": "primary"},
    {"name": "Human Resource Management", "issn": "1099-050X", "relevance": "high", "field": "HRM", "tab": "primary"},
    {"name": "Organizational Psychology Review", "issn": "2041-3874", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Journal of Management Information Systems", "issn": "0742-1222", "relevance": "medium", "field": "Information Systems", "tab": "primary"},
    {"name": "Journal of Vocational Behavior", "issn": "1095-9084", "relevance": "high", "field": "Psychology", "tab": "primary"},
    {"name": "Work & Stress", "issn": "1464-5335", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Human Resource Management Journal", "issn": "0954-5395", "relevance": "high", "field": "HRM", "tab": "primary"},
    {"name": "Information and Organization", "issn": "1471-7727", "relevance": "high", "field": "Information Systems", "tab": "primary"},
    {"name": "Journal of Occupational Health Psychology", "issn": "1076-8998", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Applied Psychology: An International Review", "issn": "0269-994X", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Organization Science", "issn": "1526-5455", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "New Technology, Work and Employment", "issn": "1468-005X", "relevance": "high", "field": "Interdisciplinary", "tab": "primary"},
    {"name": "Organization Studies", "issn": "0170-8406", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Management Science", "issn": "1526-5501", "relevance": "medium", "field": "Management", "tab": "primary"},
    {"name": "International Journal of Human Resource Management", "issn": "1466-4399", "relevance": "medium", "field": "HRM", "tab": "primary"},
    {"name": "Strategic Organization", "issn": "1741-315X", "relevance": "medium", "field": "Management", "tab": "primary"},
    {"name": "American Journal of Sociology", "issn": "1537-5390", "relevance": "medium", "field": "Sociology", "tab": "primary"},
    {"name": "Socio-Economic Review", "issn": "1475-1461", "relevance": "medium", "field": "Sociology", "tab": "primary"},
    {"name": "Journal of Occupational and Organizational Psychology", "issn": "0963-1798", "relevance": "medium", "field": "Psychology", "tab": "primary"},
    {"name": "Human Relations", "issn": "0018-7267", "relevance": "high", "field": "Management", "tab": "primary"},
    {"name": "Work, Employment and Society", "issn": "0950-0170", "relevance": "high", "field": "Sociology", "tab": "supplementary"},
    {"name": "European Journal of Work and Organizational Psychology", "issn": "1359-432X", "relevance": "medium", "field": "Psychology", "tab": "supplementary"},
    {"name": "Journal of Business and Psychology", "issn": "1573-353X", "relevance": "medium", "field": "Psychology", "tab": "supplementary"},
    {"name": "Organizational Behavior and Human Decision Processes", "issn": "1095-9920", "relevance": "high", "field": "Psychology", "tab": "supplementary"},
    {"name": "European Sociological Review", "issn": "1468-2672", "relevance": "medium", "field": "Sociology", "tab": "supplementary"},
    {"name": "Gender & Society", "issn": "0891-2432", "relevance": "medium", "field": "Sociology", "tab": "supplementary"},
    {"name": "Social Forces", "issn": "1534-7605", "relevance": "medium", "field": "Sociology", "tab": "supplementary"},
    {"name": "ILR Review", "issn": "0019-7939", "relevance": "high", "field": "Employment Relations", "tab": "supplementary"},
    {"name": "British Journal of Industrial Relations", "issn": "1467-8543", "relevance": "medium", "field": "Employment Relations", "tab": "supplementary"},
    {"name": "International Journal of Selection and Assessment", "issn": "1468-2389", "relevance": "medium", "field": "Psychology", "tab": "supplementary"},
]
JOURNAL_LOOKBACK_DAYS = 14
MAX_DISCOVERY_PER_JOURNAL = 500  # cursor-paginated cap; absorbs publisher bulk re-index events
JOURNAL_MAX_WORKERS = 4          # bounded Crossref concurrency; results are processed in roster order
MIN_JOURNAL_SURFACED_PER_RUN = 4

# --- Seed queries (derived from wiki open-questions + thin areas) ------------
# Each becomes an API search. This is the demand spec for the scan -- edit freely.
SEED_QUERIES = [
    "generative AI automation versus augmentation labor demand",
    "AI task exposure occupation wages employment",
    "large language model knowledge work field experiment",
    "generative AI worker productivity randomized experiment",
    "human-AI collaboration task allocation accountability",
    "AI agent delegation workplace autonomy outcomes",
    "AI agent benchmark work-relevant capability validity",
    "AI adoption organizational readiness barriers enablers",
    "algorithmic hiring assessment construct validity fairness",
    "automated employment decision tools audit bias",
    "AI deskilling skill erosion expertise professional judgment",
    "AI assistance learning skill formation cognitive debt",
    "generative AI critical thinking cognitive offloading",
    "automation complacency over-reliance AI advice oversight",
    "cognitive load AI assisted work mental workload",
    "AI job crafting work engagement autonomy",
    "worker experience autonomy meaning AI-mediated work",
    "AI literacy calibrated use workers",
    "AI receptivity willingness to use employees",
    "visible AI use image concern social evaluation workplace",
    "novice reverse mentoring AI adoption junior employees",
    "AI teamwork coordination cybernetic teammate",
    "generative AI organizational network knowledge sharing centrality",
    "responsible AI deployment governance worker rights accountability",
    "moral boundaries AI automation human presence acceptability",
    "AI workforce impact measurement productivity applicability",
    "job analysis KSAO AI changing definition of work",
    "human capital resource measurement collective capability",
    "work redesign human-agent workflow organization",
    "AI substitution complementarity firm-level hiring skill demand",
]

# --- Ranking weights (need not sum to 1; component scores are 0..1) ---------
RANK_WEIGHTS = {
    "recency": 0.30,             # newer ranks higher, decayed by RECENCY_HALFLIFE_DAYS
    "authority": 0.25,           # SOURCE_AUTHORITY
    "concept_match": 0.30,       # overlap with WIKI_CONCEPTS / thin areas
    "citation_proximity": 0.15,  # cites / cited-by an existing wiki source
}
RECENCY_HALFLIFE_DAYS = 365

# --- Run caps (daily trickle: comprehensive in, small out) ------------------
MAX_DISCOVERY_PER_QUERY = 40  # results pulled per seed query per source, pre-dedup
MAX_ACQUIRE_PER_RUN = 25      # upper cap; acquisition is also bounded by surfaced count
MAX_SURFACED_PER_RUN = 12     # top-N pre-ranked records handed to triage per day

# Triage-stage caps (enforced by scan_triage_apply.py / the triage skill).
MAX_AUTO_WIKI_PER_RUN = 10    # auto-moves _triage/pending -> _triage/wiki per run; overflow surfaces
MAX_RUNG4_BROWSER_PER_RUN = 3 # bounded browser-acquisition attempts per triage run

# --- Feeds for later phases (RSS/Atom, polled by feedparser) ----------------
ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.HC", "econ.GN"]
FEED_SOURCES = [
    # (name, url, source_type)
    ("nber-new", "https://www2.nber.org/rss/new.xml", "working-paper"),
]
