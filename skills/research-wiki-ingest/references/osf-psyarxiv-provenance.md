# OSF / PsyArXiv provenance pattern

Use this when a Drive inbox PDF has an OSF-style filename or URL such as `osf-8hbp9.pdf`, `https://osf.io/8hbp9/`, or a PsyArXiv DOI candidate.

## What worked

- The public download endpoint `https://osf.io/<id>/download` can return the exact PDF binary even when the OSF landing page is app-rendered HTML.
- Compare the Drive PDF SHA-256 against the public OSF download SHA-256. If they match, public provenance for the exact ingested file is verified.
- Crossref can resolve PsyArXiv preprint metadata by exact title even when the PDF itself contains no DOI. Query Crossref by bibliographic title and prefer the matching DOI such as `10.31234/osf.io/<id>_v1` when title/authors align.
- OSF API metadata can be queried with `https://api.osf.io/v2/preprints/?filter[title]=<urlencoded title>` when the title is known. This may expose title, abstract/description, tags, publication date, public status, version, and conflict-of-interest metadata.

## Ingest decisions

- Use the DOI URL (`https://doi.org/10.31234/osf.io/<id>_v1`) as canonical source frontmatter `url` when Crossref clearly matches the title/author/source.
- Use the OSF/PsyArXiv public download only for binary verification, not as the preferred durable URL when a DOI exists.
- Record the Drive-file binary hash in frontmatter and note the exact public OSF hash match in Evidence & limitations / completion notes.
- If multiple same-author PsyArXiv records overlap conceptually, treat them as possible related sources rather than duplicates until title, DOI, file hash, and central contribution are compared. A later or adjacent conceptual paper may warrant a separate source if its focal contribution differs.

## Minimal Python probe

```python
import hashlib, urllib.request
osf_id = "8hbp9"
with urllib.request.urlopen(urllib.request.Request(f"https://osf.io/{osf_id}/download", headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
    data = r.read()
print(r.geturl(), r.headers.get("content-type"), len(data), data[:4])
print(hashlib.sha256(data).hexdigest())
```
