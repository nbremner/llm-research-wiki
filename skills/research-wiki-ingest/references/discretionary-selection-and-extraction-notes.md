# Discretionary Selection and Extraction Notes

Session-derived notes for manual research-wiki PDF summaries when the user grants selection discretion.

## "Pick any one" selection

When the user explicitly says to pick any article/PDF from Drive `_inbox`, treat that as a deterministic selection rule rather than ambiguity. Select the most recently modified PDF in `_inbox`, then report:

- the exact selected filename and Drive file ID;
- the selection rule used: "user granted discretion; selected most recently modified PDF";
- whether other PDFs were present;
- that no Drive/Notion mutations occurred in dry-run mode.

This is distinct from vague "the uploaded PDF" language, where multiple plausible candidates still require clarification unless another deterministic cue exists.

## Lightweight extraction fallback

For text-based PDFs, if PyMuPDF/`fitz` is unavailable in the runtime, use `pypdf` as a lightweight fallback before escalating to OCR/marker. Record the extraction method as `pypdf text extraction`, page count, extracted character count, and confidence. Do not encode the transient missing-package state as a durable limitation; the durable pattern is: use the best available lightweight text extractor first, then OCR only when text extraction is low-confidence.

## Dry-run verification pattern

After generating a candidate summary and dry-run apply manifest, run the bundle helper without `--apply` and independently verify the source file is still in `_inbox` and no Inbox row exists for the Drive file ID. This keeps dry-run claims honest.
