# Backlog triage and human review notes

Use these notes when processing a large Google Drive `_inbox` backlog of public research PDFs before running full Manual Research PDF Summary on individual sources.

## Class-level workflow

For dozens/hundreds of PDFs, do not run the full single-PDF summary workflow sequentially. First run a dry-run backlog index:

1. List all PDFs in Drive `_inbox`.
2. Download to a local run directory only.
3. Extract PDF metadata and first-page/sample text with PyMuPDF.
4. Compute SHA-256.
5. Detect DOI, URL candidates, title candidates, author/source clues, publication year, source/evidence type, and approved topic candidates.
6. Flag `provenance-missing`, `public-verification-needed`, `extraction-low-confidence`, `possible-duplicate`, `private-boundary-risk`, and `prompt-injection-risk`.
7. Emit local CSV/JSONL/Markdown artifacts.
8. Perform no Drive rename/move and no Notion writes during indexing.

This index is a review queue, not a canonical source layer.

## Ops artifact storage

Generated review artifacts such as triage CSVs should not go in Drive `_inbox` or `public-literature-wiki` unless the Notion Schema and Agent Operating Guide have first been updated to define that artifact class and storage rule.

Current preferred location is a sibling Drive ops folder:

- Folder name: `research-wiki-ops`
- Folder ID: `1YYsH8wb4yGwoDzaeKR1NyizracPHVdL-`
- Purpose: generated operational/review artifacts such as triage CSVs, not raw public sources.

## Human review convention

Use the CSV as a review queue. The most useful columns for Nicholas are:

- `human_review_status`
- `human_review_notes`

Accepted/recommended status values include:

- `looks-good` / `ok-to-summarize`
- `high-priority`
- `low-priority`
- `skip` / `Exclude`
- `duplicate`
- `needs-provenance-check`
- `missing-url`
- `needs-ocr`
- `wrong-title`
- `wrong-author`
- `wrong-url`
- `wrong-topic` / `missing-topics`
- `wrong-evidence-type`
- `boundary-safe-confirmed-by-owner`
- `boundary-blocked`

Treat `looks-good` as equivalent to `ok-to-summarize`. Treat `Exclude` as do-not-summarize and do-not-create-Inbox-candidate.

If notes say “Need to expand topic catalog to correctly categorize this,” interpret it as: the source looks acceptable enough otherwise, but Schema-topic assignment is weak and should be improved via an ops-layer `domain_cluster_candidate` field before any formal Schema taxonomy update.

## Apple Numbers review files

Nicholas may review the CSV in Apple Numbers and upload a `.numbers` file to `research-wiki-ops`. This is acceptable. Extract it with `numbers-parser` rather than asking for a CSV export when tooling is available.

Pattern:

```bash
uv run --with numbers-parser python - <<'PY'
from numbers_parser import Document
from pathlib import Path
import csv, json
p = Path('/path/to/review.numbers')
doc = Document(str(p))
t = doc.sheets[0].tables[0]
headers = [t.cell(0, c).value for c in range(t.num_cols)]
rows = []
reviewed = []
for r in range(1, t.num_rows):
    row = {headers[c]: t.cell(r, c).value for c in range(t.num_cols)}
    rows.append(row)
    if str(row.get('human_review_status') or '').strip() or str(row.get('human_review_notes') or '').strip():
        reviewed.append(row)
with open('/path/to/review_from_numbers.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=headers)
    w.writeheader()
    w.writerows(rows)
print(json.dumps({'rows': len(rows), 'reviewed': len(reviewed)}, indent=2))
PY
```

## Heuristic pitfalls discovered

- Private-boundary detection must use conservative regex boundaries. Do not flag substring `nda` inside ordinary words like “standardized.”
- Do not rely too heavily on PDF metadata titles; they may be production artifacts such as `jsp004 917..928`, `PII: ...`, journal names, or layout fragments.
- Prefer filename-derived title/author clues when extracted metadata is obviously garbage.
- URL extraction should filter garbage such as `http://www`; when a DOI exists, generate `https://doi.org/<doi>` as a durable canonical URL candidate.
- Duplicate detection should not use generic journal titles such as `Industrial and Organizational Psychology` as a duplicate key.
- Topic assignment is currently too narrow for foundational I/O psychology backlogs. Consider an indexing-only `domain_cluster_candidate` before changing canonical Schema topics.

Potential `domain_cluster_candidate` values currently implemented in `/root/research-wiki-tools/pdf_backlog_triage.py`:

- `selection-and-assessment`
- `psychometrics-and-measurement`
- `validity-and-utility`
- `teams-and-team-effectiveness`
- `leadership`
- `employee-attitudes-and-commitment`
- `turnover-and-retention`
- `job-design-and-work-motivation`
- `training-and-development`
- `csr-and-sustainability`
- `organizational-culture`
- `organizational-network-analysis`
- `research-methods-and-statistics`
- `competency-modeling`
- `legal-ethical-and-professional-standards`
- `ai-and-algorithmic-assessment`
- `organizational-theory-and-strategy`

Keep this as ops-layer classification first; let the backlog teach the taxonomy before expanding the canonical Schema. Nicholas is open to a formal Schema update later, but not before the candidate taxonomy has been tested against more of the backlog.
