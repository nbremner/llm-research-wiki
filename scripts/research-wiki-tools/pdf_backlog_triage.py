#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "google-auth-httplib2",
#   "pymupdf",
# ]
# ///
"""
Dry-run backlog indexer for the public research-wiki Google Drive PDF _inbox.

Default behavior is intentionally conservative:
- reads Drive metadata;
- downloads PDFs to a local run directory;
- extracts PDF metadata and text signals with PyMuPDF;
- computes SHA-256;
- emits JSONL, CSV, and markdown summary artifacts;
- performs no Drive or Notion mutations.

Run with:
  uv run /root/research-wiki-tools/pdf_backlog_triage.py

Useful options:
  uv run /root/research-wiki-tools/pdf_backlog_triage.py --max-files 10
  uv run /root/research-wiki-tools/pdf_backlog_triage.py --no-download
  uv run /root/research-wiki-tools/pdf_backlog_triage.py --out-root /root/research-wiki-runs
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import textwrap
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

DEFAULT_INBOX_FOLDER_ID = "1qVcWuLSudOtjN4J_r8ILEA8-zGJrE6o1"
DEFAULT_OUT_ROOT = "/root/research-wiki-runs"
DEFAULT_TOKEN_PATH = "/root/.hermes/google_token.json"
SCHEMA_VERSION = "2026-05-24.1"
PROCESSED_BY = "Hermes / NicholasJunior"

APPROVED_TOPICS = [
    "workforce-transformation-strategy",
    "work-redesign",
    "workforce-planning",
    "ai-adoption",
    "job-architecture",
    "skills-and-capabilities",
    "human-ai-collaboration",
    "automation-and-substitution",
    "organizational-change",
    "people-analytics",
    "behavioral-science",
    "io-psychology",
    "productivity-and-efficiency",
    "governance-and-policy",
    "case-study",
]

TOPIC_KEYWORDS = {
    "workforce-transformation-strategy": ["workforce transformation", "future of work", "strategic workforce", "workforce strategy"],
    "work-redesign": ["work redesign", "job redesign", "job design", "work design", "task design", "autonomy", "job crafting"],
    "workforce-planning": ["workforce planning", "talent planning", "labor market", "labour market", "staffing", "headcount"],
    "ai-adoption": ["artificial intelligence", "generative ai", "genai", "machine learning", "algorithmic", "ai adoption"],
    "job-architecture": ["job architecture", "job family", "job level", "competency model", "role architecture"],
    "skills-and-capabilities": ["skills", "capabilities", "competenc", "reskill", "upskill", "human capital"],
    "human-ai-collaboration": ["human-ai", "human ai", "human-machine", "human machine", "augmentation", "collaboration with ai"],
    "automation-and-substitution": ["automation", "substitution", "displacement", "replace workers", "task replacement"],
    "organizational-change": ["organizational change", "organisation change", "change management", "implementation", "adoption"],
    "people-analytics": ["people analytics", "hr analytics", "human resource analytics", "workforce analytics", "selection", "validity", "turnover"],
    "behavioral-science": ["behavioral science", "behavioural science", "psychological", "motivation", "decision", "behavior"],
    "io-psychology": ["i-o psychology", "io psychology", "industrial-organizational", "organizational psychology", "occupational psychology"],
    "productivity-and-efficiency": ["productivity", "efficiency", "performance", "effectiveness"],
    "governance-and-policy": ["governance", "policy", "regulation", "ethics", "responsible ai", "compliance"],
    "case-study": ["case study", "case studies", "field study", "intervention", "experiment"],
}

SOURCE_TYPE_KEYWORDS = {
    "academic-article": ["journal", "doi", "abstract", "references", "academy of management", "personnel psychology"],
    "working-paper": ["working paper", "nber", "ssrn", "arxiv", "iza discussion", "discussion paper"],
    "report": ["report", "white paper", "whitepaper", "oecd", "mckinsey", "cipd", "deloitte", "pwc", "world economic forum"],
    "book-chapter": ["chapter", "edited by", "handbook"],
}

# Ops-layer candidate clusters. These are deliberately NOT Schema-approved
# canonical topics. They capture Nicholas's human-review feedback from the first
# PDF backlog pass and provide evidence for possible future Schema expansion.
DOMAIN_CLUSTER_KEYWORDS = {
    "selection-and-assessment": [
        "selection", "personnel selection", "employment interview", "situational judgment",
        "assessment center", "employee assessment", "predictor", "hiring", "vocational interests",
    ],
    "psychometrics-and-measurement": [
        "psychometric", "measurement", "scale", "questionnaire", "inventory", "forced-choice",
        "reliability", "validity", "construct validity", "personality test", "test manual",
    ],
    "validity-and-utility": [
        "validity", "utility", "validation", "criterion-related", "incremental validity",
        "synthetic validity", "generalizability", "local validation", "effect size", "meta-analysis",
    ],
    "teams-and-team-effectiveness": [
        "team", "teams", "team performance", "team diversity", "high-performing teams",
        "collective", "unit-level", "group performance",
    ],
    "leadership": ["leadership", "leader", "transformational", "emotional intelligence"],
    "employee-attitudes-and-commitment": [
        "commitment", "job involvement", "engagement", "core self-evaluations", "job satisfaction",
        "life satisfaction", "well-being", "wellbeing", "trust repair",
    ],
    "turnover-and-retention": ["turnover", "retention", "mobility", "internal mobility"],
    "job-design-and-work-motivation": [
        "job design", "job diagnostic", "job characteristics", "work relationships", "motivation",
        "proactive behaviors", "job demands-resources", "jdr",
    ],
    "training-and-development": ["training", "on-the-job training", "development", "learning organization"],
    "csr-and-sustainability": [
        "corporate social responsibility", "csr", "sustainability", "pro-environmental",
        "environmental csr", "stakeholder pressure",
    ],
    "organizational-culture": ["organizational culture", "organisational culture", "competing values"],
    "organizational-network-analysis": [
        "network analysis", "social network analysis", "network structure", "knowledge transfer",
    ],
    "research-methods-and-statistics": [
        "statistical", "regression", "relative importance", "tree boosting", "big data",
        "web scraping", "null hypothesis", "clinical versus statistical", "prediction",
    ],
    "competency-modeling": ["competency", "competency modeling", "great eight", "job analysis"],
    "legal-ethical-and-professional-standards": [
        "ethics code", "standards for educational and psychological testing", "aedt",
        "automated employment decision tools", "legal", "policy faq", "affirmative action",
    ],
    "ai-and-algorithmic-assessment": [
        "machine learning", "algorithmic", "artificial intelligence", "ai assessment",
        "automated employment decision", "big data", "new talent signals",
    ],
    "organizational-theory-and-strategy": [
        "resource-based", "building theory", "organizational theory", "theory about theory",
        "surveying organizations",
    ],
}

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all previous", "system prompt", "developer message",
    "reveal your", "api key", "secret token", "do not log", "skip provenance", "bypass",
]

PRIVATE_RISK_PATTERNS = [
    # Keep this conservative. Phrases like "do not distribute" often appear in
    # publisher boilerplate on otherwise public academic PDFs, so they should not
    # create a boundary block by themselves. Regexes are used so "nda" does not
    # match ordinary words like "standardized".
    r"\bconfidential\b",
    r"\binternal use only\b",
    r"\bnon-public\b",
    r"\bnot for public release\b",
    r"\bproprietary and confidential\b",
    r"\bnda\b",
    r"\buber confidential\b",
]

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
URL_RE = re.compile(r"https?://[^\s)>\]}\"']+", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def utc_now_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_filename(name: str, fallback: str) -> str:
    stem = name or fallback
    stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip(".-_")
    return stem[:160] or fallback


def normalize_title(s: str | None) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"\b(pdf|preprint|accepted manuscript|online first|in press)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slugify(s: str, max_len: int = 70) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s[:max_len].strip("-") or "untitled"


def build_drive_service(token_path: str):
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_authorized_user_file(token_path, scopes)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_inbox_pdfs(service, folder_id: str) -> list[dict[str, Any]]:
    q = f"'{folder_id}' in parents and trashed=false and mimeType='application/pdf'"
    fields = "nextPageToken, files(id,name,mimeType,createdTime,modifiedTime,size,parents,webViewLink,md5Checksum,owners(displayName,emailAddress))"
    files: list[dict[str, Any]] = []
    page_token = None
    while True:
        res = service.files().list(
            q=q,
            fields=fields,
            pageSize=1000,
            orderBy="modifiedTime desc",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return files


def download_file(service, file_id: str, out_path: Path) -> None:
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _status, done = downloader.next_chunk()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def likely_title_from_text(text: str, metadata_title: str | None, filename: str) -> str:
    candidates = []
    if metadata_title and metadata_title.strip() and len(metadata_title.strip()) > 8:
        mt = re.sub(r"\s+", " ", metadata_title.strip())
        if not mt.lower().endswith(".pdf") and "microsoft word" not in mt.lower():
            candidates.append(mt)
    lines = [re.sub(r"\s+", " ", ln.strip()) for ln in text[:6000].splitlines()]
    lines = [ln for ln in lines if 8 <= len(ln) <= 220]
    skip = ("abstract", "introduction", "references", "copyright", "journal", "volume", "issue", "page ")
    for ln in lines[:40]:
        low = ln.lower()
        if any(x in low for x in skip):
            continue
        if len(ln.split()) >= 4:
            candidates.append(ln)
            break
    if candidates:
        return candidates[0]
    return Path(filename).stem


def extract_pdf(path: Path, max_pages_text: int = 4) -> dict[str, Any]:
    result: dict[str, Any] = {
        "extract_ok": False,
        "page_count": None,
        "metadata": {},
        "text_sample": "",
        "text_sample_chars": 0,
        "total_text_chars_estimate": None,
        "extraction_confidence": "low",
        "needs_ocr": False,
        "error": None,
    }
    try:
        doc = fitz.open(path)
        result["page_count"] = doc.page_count
        result["metadata"] = dict(doc.metadata or {})
        samples = []
        char_counts = []
        pages_to_read = min(doc.page_count, max_pages_text)
        for i in range(pages_to_read):
            txt = doc.load_page(i).get_text("text") or ""
            samples.append(txt)
            char_counts.append(len(txt))
        # Estimate total by first pages. This is enough for triage; full summaries can re-extract later.
        avg = sum(char_counts) / len(char_counts) if char_counts else 0
        result["total_text_chars_estimate"] = int(avg * doc.page_count) if doc.page_count else sum(char_counts)
        text = "\n".join(samples)
        result["text_sample"] = text[:20000]
        result["text_sample_chars"] = len(text)
        result["extract_ok"] = True
        if doc.page_count and result["text_sample_chars"] < max(300, 50 * pages_to_read):
            result["extraction_confidence"] = "low"
            result["needs_ocr"] = True
        elif result["text_sample_chars"] < 1500:
            result["extraction_confidence"] = "medium"
        else:
            result["extraction_confidence"] = "high"
        doc.close()
    except Exception as e:  # noqa: BLE001 - report and continue for batch robustness
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def infer_topics(text: str, filename: str) -> list[str]:
    hay = f"{filename}\n{text[:12000]}".lower()
    scored = []
    for topic, kws in TOPIC_KEYWORDS.items():
        score = sum(hay.count(kw.lower()) for kw in kws)
        if score:
            scored.append((score, topic))
    scored.sort(reverse=True)
    return [topic for _score, topic in scored[:4]]


def infer_domain_clusters(text: str, filename: str) -> list[str]:
    """Infer ops-layer domain clusters for backlog review.

    These are intentionally separate from Schema-approved topics. They can be
    used later as evidence for topic taxonomy expansion, but the indexer should
    not treat them as canonical public-wiki topics.
    """
    hay = f"{filename}\n{text[:16000]}".lower()
    scored = []
    for cluster, kws in DOMAIN_CLUSTER_KEYWORDS.items():
        score = sum(hay.count(kw.lower()) for kw in kws)
        if score:
            scored.append((score, cluster))
    scored.sort(reverse=True)
    return [cluster for _score, cluster in scored[:5]]


def infer_source_type(text: str, filename: str) -> str:
    hay = f"{filename}\n{text[:12000]}".lower()
    scores = []
    for st, kws in SOURCE_TYPE_KEYWORDS.items():
        scores.append((sum(hay.count(kw) for kw in kws), st))
    scores.sort(reverse=True)
    return scores[0][1] if scores and scores[0][0] else "unknown"


def infer_evidence_type(text: str, filename: str) -> str:
    hay = f"{filename}\n{text[:12000]}".lower()
    if any(k in hay for k in ["meta-analysis", "systematic review", "literature review"]):
        return "review-or-meta-analysis"
    if any(k in hay for k in ["randomized", "experiment", "field experiment", "quasi-experiment"]):
        return "experimental-or-quasi-experimental"
    if any(k in hay for k in ["survey", "regression", "sample", "participants", "study 1"]):
        return "empirical-study"
    if any(k in hay for k in ["report", "white paper", "practice summary"]):
        return "practice-report"
    return "unknown"


def detect_flags(text: str, filename: str, extract: dict[str, Any], doi: str | None, urls: list[str]) -> list[str]:
    hay = f"{filename}\n{text[:20000]}".lower()
    flags = []
    if extract.get("needs_ocr") or extract.get("extraction_confidence") == "low" or not extract.get("extract_ok"):
        flags.append("extraction-low-confidence")
    if not doi and not urls:
        flags.append("provenance-missing")
    elif not doi:
        flags.append("public-verification-needed")
    if any(p in hay for p in PROMPT_INJECTION_PATTERNS):
        flags.append("prompt-injection-risk")
    if any(re.search(p, hay) for p in PRIVATE_RISK_PATTERNS):
        flags.append("private-boundary-risk")
    return sorted(set(flags)) or ["none"]


def extract_biblio_signals(text: str, metadata: dict[str, Any], filename: str) -> dict[str, Any]:
    doi_match = DOI_RE.search(text)
    urls = URL_RE.findall(text[:20000])
    urls = [u.rstrip(".,;") for u in urls]
    # Deduplicate keeping order.
    seen = set(); urls_unique = []
    for u in urls:
        if u not in seen:
            urls_unique.append(u); seen.add(u)
    title = likely_title_from_text(text, metadata.get("title"), filename)
    years = YEAR_RE.findall(text[:5000] + "\n" + filename)
    # YEAR_RE with group returns prefix only; redo simpler.
    years2 = re.findall(r"\b(?:19|20)\d{2}\b", text[:5000] + "\n" + filename)
    pub_year = min(years2) if years2 else None
    author = metadata.get("author") or None
    return {
        "detected_title": title,
        "normalized_title": normalize_title(title),
        "metadata_author": author,
        "publication_year_candidate": pub_year,
        "doi": doi_match.group(0).rstrip(".,;") if doi_match else None,
        "urls": urls_unique[:10],
    }


def proposed_filename(row: dict[str, Any]) -> str:
    year = row.get("publication_year_candidate") or (row.get("drive_created_time") or "")[:4] or dt.date.today().isoformat()[:4]
    date = f"{year}-01-01" if re.fullmatch(r"\d{4}", year) else dt.date.today().isoformat()
    author = row.get("metadata_author") or Path(row.get("original_filename", "source")).stem.split("(")[0]
    source_slug = slugify(author, 30)
    title_slug = slugify(row.get("detected_title") or row.get("original_filename") or "untitled", 70)
    return f"{date}_{source_slug}_{title_slug}.pdf"


def make_row(file_meta: dict[str, Any], local_path: Path | None, do_extract: bool) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "processed_by": PROCESSED_BY,
        "mode": "dry-run-index",
        "drive_file_id": file_meta.get("id"),
        "original_filename": file_meta.get("name"),
        "mime_type": file_meta.get("mimeType"),
        "drive_created_time": file_meta.get("createdTime"),
        "drive_modified_time": file_meta.get("modifiedTime"),
        "drive_size_bytes": int(file_meta.get("size", 0)) if file_meta.get("size") else None,
        "drive_md5": file_meta.get("md5Checksum"),
        "drive_parents": ";".join(file_meta.get("parents", [])),
        "drive_link": file_meta.get("webViewLink"),
        "local_path": str(local_path) if local_path else None,
        "sha256": None,
    }
    text = ""
    extract = {"extract_ok": False, "page_count": None, "metadata": {}, "text_sample_chars": 0, "total_text_chars_estimate": None, "extraction_confidence": "not-run", "needs_ocr": None, "error": None}
    if local_path and local_path.exists():
        row["sha256"] = sha256_file(local_path)
        if do_extract:
            extract = extract_pdf(local_path)
            text = extract.get("text_sample") or ""
    biblio = extract_biblio_signals(text, extract.get("metadata") or {}, row["original_filename"] or "")
    topics = infer_topics(text, row["original_filename"] or "")
    domain_clusters = infer_domain_clusters(text, row["original_filename"] or "")
    source_type = infer_source_type(text, row["original_filename"] or "")
    evidence_type = infer_evidence_type(text, row["original_filename"] or "")
    flags = detect_flags(text, row["original_filename"] or "", extract, biblio.get("doi"), biblio.get("urls") or [])

    row.update({
        "page_count": extract.get("page_count"),
        "pdf_metadata_title": (extract.get("metadata") or {}).get("title"),
        "pdf_metadata_author": (extract.get("metadata") or {}).get("author"),
        "text_sample_chars": extract.get("text_sample_chars"),
        "total_text_chars_estimate": extract.get("total_text_chars_estimate"),
        "extraction_confidence": extract.get("extraction_confidence"),
        "needs_ocr": extract.get("needs_ocr"),
        "extraction_error": extract.get("error"),
        **biblio,
        "canonical_url_candidate": (biblio.get("urls") or [None])[0],
        "suggested_topics": ";".join(topics),
        "domain_cluster_candidate": ";".join(domain_clusters),
        "suggested_source_type": source_type,
        "suggested_evidence_type": evidence_type,
        "boundary_flags": ";".join(flags),
    })
    row["proposed_canonical_filename"] = proposed_filename(row)
    return row


GENERIC_TITLES = {
    "industrial and organizational psychology",
    "journal of applied psychology",
    "personnel psychology",
    "academy of management journal",
    "academy of management review",
    "organizational behavior and human decision processes",
}


def mark_duplicates(rows: list[dict[str, Any]]) -> None:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(rows):
        for key_name in ["sha256", "drive_md5", "doi"]:
            val = r.get(key_name)
            if val:
                groups[f"{key_name}:{val.lower() if isinstance(val, str) else val}"].append(i)
        title = r.get("normalized_title")
        if title and len(title) >= 25 and title not in GENERIC_TITLES:
            groups[f"normalized_title:{title}"].append(i)
    dup_indices: dict[int, list[str]] = defaultdict(list)
    for key, idxs in groups.items():
        if len(idxs) > 1:
            for idx in idxs:
                dup_indices[idx].append(key)
    for i, r in enumerate(rows):
        flags = set((r.get("boundary_flags") or "none").split(";"))
        if i in dup_indices:
            flags.discard("none")
            flags.add("possible-duplicate")
            r["duplicate_keys"] = ";".join(sorted(dup_indices[i])[:10])
        else:
            r["duplicate_keys"] = ""
        r["boundary_flags"] = ";".join(sorted(flags)) if flags else "none"


def write_outputs(rows: list[dict[str, Any]], run_dir: Path, files: list[dict[str, Any]], args: argparse.Namespace) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "drive_inventory_raw.json").write_text(json.dumps(files, indent=2), encoding="utf-8")
    with (run_dir / "pdf_triage.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    fieldnames = sorted({k for r in rows for k in r.keys()})
    with (run_dir / "pdf_triage.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    flag_counts = Counter()
    topic_counts = Counter()
    domain_cluster_counts = Counter()
    confidence_counts = Counter()
    for r in rows:
        for f in (r.get("boundary_flags") or "none").split(";"):
            flag_counts[f] += 1
        for t in (r.get("suggested_topics") or "").split(";"):
            if t:
                topic_counts[t] += 1
        for c in (r.get("domain_cluster_candidate") or "").split(";"):
            if c:
                domain_cluster_counts[c] += 1
        confidence_counts[r.get("extraction_confidence") or "unknown"] += 1

    high_attention = [r for r in rows if any(f in (r.get("boundary_flags") or "") for f in ["private-boundary-risk", "possible-duplicate", "extraction-low-confidence", "provenance-missing"])]
    md = f"""
# PDF Backlog Triage Summary

- Run ID: `{run_dir.name}`
- Mode: dry-run-index
- Schema version: `{SCHEMA_VERSION}`
- Processed by: {PROCESSED_BY}
- Inbox folder ID: `{args.folder_id}`
- Drive/Notion mutations: none
- PDFs found in inbox query: {len(files)}
- PDFs indexed this run: {len(rows)}
- Downloads: {'enabled' if not args.no_download else 'disabled'}
- Extraction: {'enabled' if not args.no_extract else 'disabled'}

## Output artifacts

- CSV: `{run_dir / 'pdf_triage.csv'}`
- JSONL: `{run_dir / 'pdf_triage.jsonl'}`
- Raw Drive inventory: `{run_dir / 'drive_inventory_raw.json'}`
- Download cache: `{run_dir / 'downloads'}`

## Boundary / workflow flags

{chr(10).join(f'- {k}: {v}' for k, v in flag_counts.most_common()) or '- none'}

## Extraction confidence

{chr(10).join(f'- {k}: {v}' for k, v in confidence_counts.most_common()) or '- none'}

## Suggested topic counts

{chr(10).join(f'- {k}: {v}' for k, v in topic_counts.most_common()) or '- none detected'}

## Ops-layer domain cluster candidate counts

These are not Schema-approved topics. Treat them as backlog triage signals and possible future Schema taxonomy candidates.

{chr(10).join(f'- {k}: {v}' for k, v in domain_cluster_counts.most_common()) or '- none detected'}

## High-attention rows

{chr(10).join(f"- `{r.get('original_filename')}` — flags: {r.get('boundary_flags')} — title: {r.get('detected_title')}" for r in high_attention[:40]) or '- none'}

## Recommended next action

Review `pdf_triage.csv`, especially rows with `private-boundary-risk`, `possible-duplicate`, `extraction-low-confidence`, or `provenance-missing`. After that, run full Manual Research PDF Summary only on selected high/medium-priority candidates. Do not promote to Sources/Concepts from this dry-run index alone.
""".strip() + "\n"
    (run_dir / "SUMMARY.md").write_text(md, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Dry-run index PDFs in research-wiki Drive _inbox")
    p.add_argument("--folder-id", default=DEFAULT_INBOX_FOLDER_ID)
    p.add_argument("--token-path", default=DEFAULT_TOKEN_PATH)
    p.add_argument("--out-root", default=DEFAULT_OUT_ROOT)
    p.add_argument("--run-id", default=None)
    p.add_argument("--max-files", type=int, default=None, help="Limit files for smoke tests or small batches")
    p.add_argument("--no-download", action="store_true", help="Only list Drive metadata; skip PDF download/hash/extraction")
    p.add_argument("--no-extract", action="store_true", help="Download/hash but skip PyMuPDF extraction")
    p.add_argument("--force-download", action="store_true", help="Redownload even if local cache path exists")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    run_id = args.run_id or f"pdf-triage-{utc_now_stamp()}"
    run_dir = Path(args.out_root) / run_id
    downloads = run_dir / "downloads"
    service = build_drive_service(args.token_path)
    files = list_inbox_pdfs(service, args.folder_id)
    if args.max_files:
        files_to_process = files[: args.max_files]
    else:
        files_to_process = files

    rows = []
    print(f"Found {len(files)} PDFs in Drive _inbox. Indexing {len(files_to_process)}. Run dir: {run_dir}", flush=True)
    for n, meta in enumerate(files_to_process, 1):
        fid = meta["id"]
        local_path = None
        if not args.no_download:
            fname = f"{safe_filename(meta.get('name') or fid, fid)}__{fid}.pdf"
            local_path = downloads / fname
            if args.force_download or not local_path.exists():
                print(f"[{n}/{len(files_to_process)}] downloading {meta.get('name')}", flush=True)
                try:
                    download_file(service, fid, local_path)
                except Exception as e:  # noqa: BLE001
                    print(f"WARN: download failed for {fid}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                    local_path = None
            else:
                print(f"[{n}/{len(files_to_process)}] cached {meta.get('name')}", flush=True)
        else:
            print(f"[{n}/{len(files_to_process)}] metadata only {meta.get('name')}", flush=True)
        try:
            row = make_row(meta, local_path, do_extract=not args.no_extract and not args.no_download)
        except Exception as e:  # noqa: BLE001
            row = {
                "schema_version": SCHEMA_VERSION,
                "processed_by": PROCESSED_BY,
                "mode": "dry-run-index",
                "drive_file_id": meta.get("id"),
                "original_filename": meta.get("name"),
                "drive_link": meta.get("webViewLink"),
                "boundary_flags": "extraction-low-confidence",
                "extraction_error": f"row_error {type(e).__name__}: {e}",
            }
        rows.append(row)

    mark_duplicates(rows)
    write_outputs(rows, run_dir, files, args)
    print(f"Wrote {run_dir / 'SUMMARY.md'}")
    print(f"Wrote {run_dir / 'pdf_triage.csv'}")
    print(f"Wrote {run_dir / 'pdf_triage.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
