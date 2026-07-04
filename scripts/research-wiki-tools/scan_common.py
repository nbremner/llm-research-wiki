"""
scan_common.py -- shared machinery for the research-scan harness.

Pure logic (ID/URL normalization, dedup, ranking, OA-location selection, boundary
flags, the record + ledger models) lives at the top and imports only the stdlib,
so it is unit-testable without network or the heavy deps. Network / Drive / PDF
helpers lazily import their heavy dependencies (httpx, google-api-python-client,
pymupdf) inside the function body, so importing this module for tests is cheap.

Reuses conventions from pdf_backlog_triage.py (Drive auth, DOI/URL/title utils,
PyMuPDF text-layer detection, boundary flags). See docs/research-scrape-plan.md.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# ---------------------------------------------------------------------------
# Regexes and time
# ---------------------------------------------------------------------------

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_cid", "mc_eid", "ref", "source", "src",
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def utc_now_iso() -> str:
    return utc_now().replace(microsecond=0).isoformat()


def utc_now_stamp() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# ID / URL normalization (pure)
# ---------------------------------------------------------------------------

def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = d.strip().rstrip(".,;)")
    m = DOI_RE.search(d)
    return m.group(0).rstrip(".,;)") if m else None


def arxiv_id_from(value: str | None) -> str | None:
    """Return a bare arXiv id (e.g. '2503.16774') from a url, id, or arxiv DOI."""
    if not value:
        return None
    v = value.strip().lower()
    if "arxiv" not in v and not re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", v):
        return None
    m = ARXIV_RE.search(v)
    return m.group(1) if m else None


def normalize_url(url: str | None) -> str | None:
    """Lowercase host, drop fragment and tracking params, strip trailing slash."""
    if not url:
        return None
    url = url.strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if not parts.scheme or not parts.netloc:
        return url
    host = parts.netloc.lower()
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=False)
             if k.lower() not in _TRACKING_PARAMS]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), host, path, urlencode(query), ""))


def url_hash(url: str) -> str:
    norm = normalize_url(url) or url
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def candidate_id(doi: str | None = None, arxiv_id: str | None = None,
                 url: str | None = None) -> str | None:
    """Canonical dedup id: prefer DOI, then arXiv id, then a URL hash."""
    d = normalize_doi(doi)
    if d:
        return f"doi:{d}"
    a = arxiv_id_from(arxiv_id) or arxiv_id_from(url)
    if a:
        return f"arxiv:{a}"
    if url:
        return f"url:{url_hash(url)}"
    return None


def slugify(s: str, max_len: int = 70) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s[:max_len].strip("-") or "untitled"


def normalize_title(s: str | None) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"\b(pdf|preprint|accepted manuscript|online first|in press)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Source type / authority (pure)
# ---------------------------------------------------------------------------

def host_of(url: str | None) -> str | None:
    if not url:
        return None
    try:
        return urlsplit(url).netloc.lower() or None
    except ValueError:
        return None


def source_type_for(url: str | None, api_type: str | None, host_map: dict[str, str]) -> str:
    """Best-effort source_type from an explicit API type, else a host hint."""
    if api_type:
        t = api_type.strip().lower()
        alias = {
            "journal-article": "peer-reviewed",
            "proceedings-article": "peer-reviewed",
            "posted-content": "preprint",
            "report": "gov",
            "article": "news",
        }
        if t in SOURCE_AUTHORITY_KEYS:
            return t
        if t in alias:
            return alias[t]
    h = host_of(url)
    if h and h in host_map:
        return host_map[h]
    return "other"


SOURCE_AUTHORITY_KEYS = {
    "peer-reviewed", "working-paper", "preprint", "gov", "think-tank",
    "industry", "news", "other",
}


def authority_score(source_type: str, authority_map: dict[str, float]) -> float:
    return float(authority_map.get(source_type, authority_map.get("other", 0.3)))


# ---------------------------------------------------------------------------
# Concept match + ranking (pure)
# ---------------------------------------------------------------------------

def concept_match(text: str, concepts: dict[str, list[str]]) -> tuple[float, list[str]]:
    """Return (0..1 score, matched topic slugs sorted by hit count)."""
    hay = (text or "").lower()
    if not hay:
        return 0.0, []
    hits: dict[str, int] = {}
    total = 0
    for topic, kws in concepts.items():
        c = sum(hay.count(kw.lower()) for kw in kws)
        if c:
            hits[topic] = c
            total += c
    matched = sorted(hits, key=lambda t: hits[t], reverse=True)
    score = min(1.0, 0.25 * len(matched) + 0.05 * total)
    return score, matched


def is_on_mission(text: str, ai_terms: Iterable[str], work_terms: Iterable[str]) -> bool:
    """On-mission = touches an AI/tech term AND a work/labor term (the wiki is AI x work)."""
    hay = (text or "").lower()
    has_ai = any(t.lower() in hay for t in ai_terms)
    has_work = any(t.lower() in hay for t in work_terms)
    return has_ai and has_work


def recency_score(date_value: str | int | None, halflife_days: int) -> float:
    """0..1, exponential decay by age. Unknown date -> neutral 0.4."""
    if date_value is None or date_value == "":
        return 0.4
    parsed: dt.date | None = None
    s = str(date_value)
    try:
        if re.fullmatch(r"\d{4}", s):
            parsed = dt.date(int(s), 7, 1)
        else:
            parsed = dt.date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        m = YEAR_RE.search(s)
        if m:
            parsed = dt.date(int(m.group(0)), 7, 1)
    if parsed is None:
        return 0.4
    age_days = max(0, (utc_now().date() - parsed).days)
    return math.pow(0.5, age_days / max(1, halflife_days))


def rank_record(recency: float, authority: float, concept: float,
                citation: float, weights: dict[str, float]) -> tuple[float, dict[str, float]]:
    comps = {
        "recency": round(recency, 4),
        "authority": round(authority, 4),
        "concept_match": round(concept, 4),
        "citation_proximity": round(citation, 4),
    }
    wsum = sum(weights.get(k, 0.0) for k in comps) or 1.0
    score = sum(comps[k] * weights.get(k, 0.0) for k in comps) / wsum
    return round(score, 4), comps


# ---------------------------------------------------------------------------
# OA-location selection (pure) -- operate on API response dicts
# ---------------------------------------------------------------------------

def openalex_pdf_url(work: dict[str, Any]) -> str | None:
    for loc_key in ("best_oa_location", "primary_location"):
        loc = work.get(loc_key) or {}
        if loc.get("pdf_url"):
            return loc["pdf_url"]
    oa = work.get("open_access") or {}
    return oa.get("oa_url") or None


def unpaywall_pdf_url(data: dict[str, Any]) -> str | None:
    for loc_key in ("best_oa_location", "first_oa_location"):
        loc = data.get(loc_key) or {}
        if loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
        if loc.get("url"):
            return loc["url"]
    return None


# ---------------------------------------------------------------------------
# Boundary flags (pure) -- reused from pdf_backlog_triage
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all previous", "system prompt",
    "developer message", "reveal your", "api key", "secret token",
    "do not log", "skip provenance", "bypass",
]
PRIVATE_RISK_PATTERNS = [
    r"\bconfidential\b", r"\binternal use only\b", r"\bnon-public\b",
    r"\bnot for public release\b", r"\bproprietary and confidential\b",
    r"\bnda\b", r"\buber confidential\b",
]


def boundary_flags(text: str) -> list[str]:
    hay = (text or "")[:20000].lower()
    flags: list[str] = []
    if any(p in hay for p in PROMPT_INJECTION_PATTERNS):
        flags.append("prompt-injection-risk")
    if any(re.search(p, hay) for p in PRIVATE_RISK_PATTERNS):
        flags.append("private-boundary-risk")
    return sorted(set(flags))


# ---------------------------------------------------------------------------
# Record model
# ---------------------------------------------------------------------------

# acq_state ladder: full-pdf > full-text > abstract-only > link-only.
ACQ_STATES = {"full-pdf", "full-text", "abstract-only", "link-only"}


@dataclass
class ScanRecord:
    id: str
    source: str = ""                # discovery channel (openalex, arxiv, crossref, citation-chase, feed)
    query: str = ""                 # seed query / feed that surfaced it
    url: str | None = None          # landing / canonical url
    pdf_url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: str | None = None
    venue: str | None = None
    source_type: str = "other"
    abstract: str = ""
    cited_by_count: int | None = None
    acq_state: str = "link-only"
    artifact_drive_id: str | None = None
    artifact_path: str | None = None
    needs_ocr: bool = False
    rank_score: float = 0.0
    rank_components: dict[str, float] = field(default_factory=dict)
    matched_topics: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    disposition: str | None = None  # set by the triage skill: wiki | read-once | discard
    first_seen: str = field(default_factory=utc_now_iso)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Ledger (local JSON files; Drive sync handled by the harness around a run)
# ---------------------------------------------------------------------------

class Ledger:
    """Coverage ledger: seen-index (dedup), failure-catalog, search-log.

    Files are plain JSON so they are human-inspectable in Drive. The seen-index
    starts empty and is warm-started from the existing wiki sources/ ids so the
    harness never re-surfaces what is already ingested.
    """

    def __init__(self, ledger_dir: str | Path):
        self.dir = Path(ledger_dir)
        self.seen_path = self.dir / "seen_index.json"
        self.failures_path = self.dir / "failure_catalog.json"
        self.search_log_path = self.dir / "search_log.jsonl"
        self.seen: dict[str, dict[str, Any]] = {}
        self.failures: dict[str, dict[str, Any]] = {}

    def load(self) -> "Ledger":
        if self.seen_path.exists():
            self.seen = json.loads(self.seen_path.read_text(encoding="utf-8") or "{}")
        if self.failures_path.exists():
            self.failures = json.loads(self.failures_path.read_text(encoding="utf-8") or "{}")
        return self

    def is_seen(self, cid: str | None) -> bool:
        return bool(cid) and cid in self.seen

    def mark_seen(self, cid: str, meta: dict[str, Any] | None = None) -> None:
        if not cid:
            return
        if cid not in self.seen:
            self.seen[cid] = {"first_seen": utc_now_iso(), **(meta or {})}

    def warm_start(self, ids: Iterable[str], note: str = "warm-start") -> int:
        n = 0
        for cid in ids:
            if cid and cid not in self.seen:
                self.seen[cid] = {"first_seen": utc_now_iso(), "origin": note}
                n += 1
        return n

    def record_failure(self, key: str, url: str, failure: str,
                       workaround: str | None = None) -> None:
        entry = self.failures.get(key, {"url": url, "count": 0})
        entry.update({
            "url": url,
            "failure": failure,
            "last_attempt": utc_now_iso(),
            "count": int(entry.get("count", 0)) + 1,
        })
        if workaround:
            entry["workaround"] = workaround
        self.failures[key] = entry

    def known_failure(self, key: str) -> dict[str, Any] | None:
        return self.failures.get(key)

    def log_search(self, query: str, source: str, hits: int, new: int) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps({
            "ts": utc_now_iso(), "query": query, "source": source,
            "hits": hits, "new": new,
        }, ensure_ascii=False)
        with self.search_log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.seen_path.write_text(json.dumps(self.seen, indent=2, ensure_ascii=False), encoding="utf-8")
        self.failures_path.write_text(json.dumps(self.failures, indent=2, ensure_ascii=False), encoding="utf-8")


def load_wiki_source_ids(sources_dir: str | Path) -> set[str]:
    """Warm-start ids from existing wiki/sources/*.md frontmatter (url/doi) +
    filename-year. Lets the harness skip papers already in the wiki."""
    ids: set[str] = set()
    d = Path(sources_dir)
    if not d.is_dir():
        return ids
    url_re = re.compile(r"^url:\s*(\S+)", re.I | re.M)
    for md in d.glob("*.md"):
        try:
            head = md.read_text(encoding="utf-8")[:1200]
        except OSError:
            continue
        for m in url_re.finditer(head):
            cid = candidate_id(url=m.group(1))
            doi = normalize_doi(m.group(1))
            if doi:
                ids.add(f"doi:{doi}")
            ax = arxiv_id_from(m.group(1))
            if ax:
                ids.add(f"arxiv:{ax}")
            if cid:
                ids.add(cid)
    return ids


# ---------------------------------------------------------------------------
# Network / Drive / PDF helpers (heavy deps imported lazily)
# ---------------------------------------------------------------------------

DEFAULT_UA = "research-wiki-scan/0.1 (+mailto:nicholasbremner@gmail.com)"


def http_get(url: str, params: dict[str, Any] | None = None, *, timeout: float = 30.0,
             headers: dict[str, str] | None = None, retries: int = 3):
    """GET with simple backoff. Returns an httpx.Response. Raises on final failure."""
    import time
    import httpx
    hdrs = {"User-Agent": DEFAULT_UA, **(headers or {})}
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, headers=hdrs, timeout=timeout,
                             follow_redirects=True)
            if resp.status_code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt + 1)
                continue
            resp.raise_for_status()
            return resp
        except Exception as e:  # noqa: BLE001 - retry loop
            last = e
            time.sleep(2 ** attempt + 1)
    raise last if last else RuntimeError(f"GET failed: {url}")


def http_get_json(url: str, params: dict[str, Any] | None = None, **kw) -> Any:
    return http_get(url, params=params, **kw).json()


def http_get_bytes(url: str, **kw) -> bytes:
    return http_get(url, **kw).content


def jina_read(url: str, *, timeout: float = 45.0) -> str:
    """Fetch clean article text via the Jina reader (server-side, JS-capable)."""
    resp = http_get(f"https://r.jina.ai/{url}", timeout=timeout)
    return resp.text


def looks_like_pdf(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def pdf_text_layer_ok(data: bytes, min_chars: int = 400) -> tuple[bool, int, int]:
    """(has_text_layer, page_count, sampled_chars) via PyMuPDF. Detects scanned
    PDFs with no extractable text (ladder rung 5)."""
    import fitz  # PyMuPDF
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        pages = doc.page_count
        chars = 0
        for i in range(min(pages, 4)):
            chars += len(doc.load_page(i).get_text("text") or "")
        return chars >= min_chars, pages, chars
    finally:
        doc.close()


def build_drive_service(token_path: str):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_authorized_user_file(token_path, scopes)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def drive_upload_bytes(service, folder_id: str, name: str, data: bytes,
                       mime_type: str) -> str:
    import io
    from googleapiclient.http import MediaIoBaseUpload
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime_type, resumable=False)
    meta = {"name": name, "parents": [folder_id]}
    created = service.files().create(
        body=meta, media_body=media, fields="id",
        supportsAllDrives=True).execute()
    return created["id"]


def drive_upload_text(service, folder_id: str, name: str, text: str,
                      mime_type: str = "application/json") -> str:
    return drive_upload_bytes(service, folder_id, name, text.encode("utf-8"), mime_type)


def drive_find(service, folder_id: str, name: str) -> str | None:
    safe = name.replace("'", "\\'")
    q = f"'{folder_id}' in parents and name='{safe}' and trashed=false"
    res = service.files().list(
        q=q, fields="files(id,name)", pageSize=5,
        supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def drive_download_text(service, file_id: str) -> str:
    return service.files().get_media(
        fileId=file_id, supportsAllDrives=True).execute().decode("utf-8")


def drive_move(service, file_id: str, new_parent_id: str, old_parent_id: str) -> None:
    service.files().update(
        fileId=file_id, addParents=new_parent_id, removeParents=old_parent_id,
        fields="id,parents", supportsAllDrives=True).execute()
