# Drive filename and provenance notes from manual PDF summary runs

Use these notes when processing public research PDFs from the research-wiki Drive `_inbox`.

## Filename convention pitfall

The active raw-source filename convention is:

```text
YYYY-MM-DD_source-slug_short-title-slug.pdf
```

For academic papers, the `source-slug` should usually be the author/source key, not the journal or venue. Prefer:

```text
2026-03-26_almog_barriers-ai-adoption-image-concerns-work.pdf
2025-11-20_landers-nakamoto_ethical-use-ai-iop.pdf
```

Avoid filenames like:

```text
2025-11-20_practice-innovations_ethical-use-ai-iop.pdf
```

That includes a date and title, but uses the venue while omitting the author/source key. If the source is an organizational report rather than an authored paper, use the organization as the source slug, e.g. `oecd`, `mckinsey`, `wef`.

## Working-paper provenance

If a PDF is a job market paper or working paper and contains only a Google Drive "latest version" link plus preregistration links, treat it as public-plausible but not fully public-verified. Use:

- Boundary flag: `public-verification-needed`
- Public provenance status: `public-plausible / public-verification-needed`
- Promotion note: ask LC/human to confirm a stable author, institutional, SSRN, NBER, IDEAS/RePEc, arXiv, DOI, or publisher landing page before canonical Source promotion.

Do not block dry-run summarization solely because a working paper lacks a DOI, but do not claim full public verification without a stable public landing page.

## Filename consistency after corrections

If a filed Drive filename is corrected after apply mode, rename the Drive file in place so the file ID remains stable. It is acceptable for the old filename to remain only as historical "previous filename" text in correction/audit notes.
