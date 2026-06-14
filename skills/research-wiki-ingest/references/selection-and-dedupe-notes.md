# Selection and Dedupe Notes

Session-derived refinements for manual research-wiki PDF processing.

## Multiple PDFs in `_inbox`

Default remains conservative: if multiple plausible PDFs are present and the user did not specify a selection rule, stop and ask.

Allowed exception: if the user explicitly asks for the "most recent", "latest", or otherwise gives a deterministic selection rule, apply that rule without asking. For "most recent/latest", sort candidate PDFs by Drive `modifiedTime` descending, choose the first, and report both the chosen file and the other candidates in the completion note.

## Duplicate checks worth doing in dry-run

Before proposing apply mode, run duplicate checks across both storage layers where feasible:

- Notion: search for DOI/permanent ID first; then exact or near-exact title; then distinctive author strings.
- Drive destination: check for the proposed canonical filename before suggesting a move/rename.
- If no duplicates are found, say exactly what was checked rather than the vague phrase "no duplicates".

## Completion note shape

For dry-run, explicitly include:

- Target PDF selected and why.
- Whether any other PDFs were present.
- Confirmation that no Drive or Notion mutations were performed.
- Local path of the generated summary artifact, if one was written.
- Boundary flags and prompt-injection flags.
- Proposed canonical filename.
- Clear next action for apply mode.
