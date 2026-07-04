"""
scan_config.py -- the editable rubric/config for the research-scan harness.

This is DATA, not machinery: seed queries, the wiki concept vocabulary, source
authority weights, ranking weights, and run caps. Edit this to retune what the
scan looks for and how it ranks -- no code change needed. See
docs/research-scrape-plan.md for the architecture.

Anchored on the wiki's mission (AI workforce transformation x I-O psychology, per
wiki/overview.md), NOT the wrapped-up applied "U4B / B2B-sales" research questions.
A future applied project = a new profile here, not a rebuild.
"""

from __future__ import annotations

# --- Google Drive layout (folder IDs are pointers, not secrets) -------------
# Triage store = the general inbox, upstream of and distinct from the wiki _inbox.
TRIAGE_FOLDER_ID = "1tXLfXs2z8LkbAurlrw8G7IYfQu1mCXh8"
TRIAGE_FILES_FOLDER_ID = "1_9TRp4H1Qqm0M4QI8hGiMkWNs9hc_GXg"
TRIAGE_LEDGER_FOLDER_ID = "1Fw7J30oerCSCYSLcEB5k0mbbdfOGwyx1"
# Promotion target: the wiki's existing PDF front door (unchanged).
WIKI_INBOX_FOLDER_ID = "1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1"

# Reuse the Drive OAuth token the backlog-triage tool already uses.
DEFAULT_TOKEN_PATH = "/root/.hermes/google_token.json"
DEFAULT_OUT_ROOT = "/root/research-wiki-runs"

# Polite-pool contact for OpenAlex / Crossref / Unpaywall (a courtesy, not a secret).
CONTACT_MAILTO = "nicholasbremner@gmail.com"

SCHEMA_VERSION = "2026-07-03.1"
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
# Drives concept-match scoring. Derived from wiki/overview.md topics. Keep roughly
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
MAX_ACQUIRE_PER_RUN = 25      # cap on full (rung 1-3) acquisitions per run
MAX_SURFACED_PER_RUN = 12     # top-N pre-ranked records handed to triage per day

# --- Feeds for later phases (RSS/Atom, polled by feedparser) ----------------
ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.HC", "econ.GN"]
FEED_SOURCES = [
    # (name, url, source_type)
    ("nber-new", "https://www2.nber.org/rss/new.xml", "working-paper"),
]
