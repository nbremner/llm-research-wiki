# Inspecting acquired Drive artifacts during scan triage

Use this when a manifest record has `artifact_drive_id` but the manifest abstract is empty or thin. The scanner's acquired artifact may be a real PDF, a Jina Markdown extraction, or just a bot-check/paywall page.

## What to check

- Download or inspect the Drive artifact before making a `confidence: clear` judgment.
- If the artifact is a real PDF, verify it begins with `%PDF-`, has a page count, and has an extractable text sample.
- If the artifact is Markdown/text, read the first section and confirm it contains abstract/body content, not just navigation, cookie text, paywall language, or a Cloudflare/security page.
- If it is only a bot-check/CAPTCHA/login/paywall page and title/metadata are insufficient for a clean rubric decision, set the proposed disposition but use `confidence: ambiguous`.

## Bounded pattern

A short Python probe can use `scan_common.build_drive_service(...)` plus `googleapiclient.http.MediaIoBaseDownload` to fetch each `artifact_drive_id`; then:

- PDF: use PyMuPDF (`fitz`) to sample the first 1–3 pages.
- Text/Markdown: decode UTF-8 and inspect the first ~1,500 characters.

Do not turn this into an acquisition battle. The purpose is judgment quality: distinguish usable full text from bot-check artifacts before auto-queueing into the wiki inbox.
