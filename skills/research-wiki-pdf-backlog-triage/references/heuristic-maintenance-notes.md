# PDF triage heuristic maintenance notes

Use this reference when improving `/root/research-wiki-tools/pdf_backlog_triage.py` or its mirrored copy in `/root/work/llm-research-wiki/scripts/research-wiki-tools/pdf_backlog_triage.py`.

## Pattern that worked

Treat Nicholas's reviewed rows as regression fixtures, not just subjective feedback. Convert each reviewed failure class into tests in the portable repo before editing the script.

Known valuable test classes:

- DOI-derived canonical URL should beat generic extracted URLs: `https://doi.org/<doi>`.
- Filter boilerplate/garbage URLs such as Creative Commons license links, W3C links, Adobe/Microsoft boilerplate, and truncated `http://www` fragments.
- Extract filename-derived author candidates and record `author_confidence`, especially when PDF metadata lacks author fields.
- Reject title metadata/layout garbage such as `PII: ...`, `1984, Vol...`, `peps_...`, `principles.qxd`, `PowerPoint Presentation`, journal headers, and author-only lines.
- Fall back to filename-derived titles for common backlog forms like `Author (YYYY) Title.pdf` and `(Non-Academic) Org (YYYY) Title.pdf`.
- Add explicit source/evidence handling for policy guides, standards manuals, slide decks, books/book chapters, methods papers, empirical studies, reviews/meta-analyses, and practice reports.

## Required maintenance sequence

1. Add/update tests under `/root/work/llm-research-wiki/tests/` first.
2. Verify the new test fails for the expected behavior gap.
3. Patch the mirrored script in `/root/work/llm-research-wiki/scripts/research-wiki-tools/pdf_backlog_triage.py`.
4. Run `python -m pytest tests/ -q` in `/root/work/llm-research-wiki`.
5. Copy the mirrored script back to `/root/research-wiki-tools/pdf_backlog_triage.py`.
6. Run a smoke triage with `--max-files 20` and inspect the reviewed-row examples.
7. Run the full triage, update `/root/research-wiki-runs/latest-pdf-triage`, then commit and push the portable repo.

## Selection after heuristic refresh

After a clean full run, first manual-summary candidates should usually be rows with:

- `boundary_flags == none`
- high extraction confidence
- DOI or strong canonical URL
- non-slide evidence type
- central domain clusters such as selection/assessment, validity/utility, teams, job design, commitment, turnover, or AI/algorithmic assessment

Do not summarize rows marked slide deck or with unresolved private-boundary risk unless Nicholas explicitly selects them.