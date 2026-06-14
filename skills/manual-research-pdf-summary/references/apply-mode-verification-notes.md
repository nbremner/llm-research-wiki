# Apply-mode verification notes

Session-derived notes from applying a Drive + Notion ingest bundle for a public research PDF.

## Manifest hygiene before `--apply`

When converting a dry-run manifest into an apply manifest, remove stale dry-run language before writing Notion:

- Inbox `notes` should say the Drive PDF was filed before Notion page creation.
- Inbox `provenance_notes` should use `Final Drive filename`, not `Proposed final Drive filename`.
- Summary markdown should switch `Mode: manual-dry-run` to `Mode: manual-apply` and include the final Drive folder.
- Log properties should be fully typed according to the Log data source schema, not just a title-only placeholder.
- Log markdown should include file ID, final filename, destination, boundary flags, canonical URL, and next action.

Always run the helper once without `--apply` on the finalized apply manifest before applying:

```bash
uv run /root/research-wiki-tools/apply_pdf_ingest_bundle.py /tmp/.../apply_manifest_apply.json
uv run /root/research-wiki-tools/apply_pdf_ingest_bundle.py /tmp/.../apply_manifest_apply.json --apply
```

## Pre-apply duplicate checks

Before `--apply`, verify at least:

- Drive target file is still in `_inbox` and not trashed.
- Destination has no same-name collision for the proposed canonical filename.
- Notion Inbox has no row containing the Drive file ID.
- Notion Sources has no row containing the DOI/permanent ID when one is available.

## Verification after `--apply`

After the helper reports success, independently re-fetch:

- Drive metadata: `id`, `name`, `parents`, `webViewLink`, `trashed`.
- Notion Inbox page markdown.
- Notion Log page markdown.

Do not rely only on the helper's returned JSON. Confirm:

- Drive file ID is stable.
- Final filename matches.
- Destination parent is present.
- `_inbox` parent is absent.
- Notion Inbox markdown contains the final Drive filename and substantive summary sections such as `Abstract or short summary` and `Key claims`.
- Notion Log markdown contains the final Drive filename and apply summary.

Notion's `/pages/{id}/markdown` may omit or normalize a top-level `# Candidate Source Summary` heading from page-created markdown. Treat absence of that exact H1 as non-fatal if the body length, final filename, and substantive sections are present.

## Completion note

Report the concrete handles:

- Drive file ID and final filename/folder.
- Notion Inbox URL.
- Notion Log URL.
- Boundary flags.
- Explicit statement that no canonical Source or Concept rows were created unless separately approved.
