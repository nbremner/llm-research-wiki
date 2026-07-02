# GenAI persuasion / validation topic assessment

Use this pattern when ingesting sources whose central claim is that GenAI shapes, persuades, defends, justifies, or otherwise influences the human who is trying to validate its output.

## Topic placement

Default existing topics to review:

- `human-ai-collaboration` — if the source changes what "human in the loop," validation, review burden, or collaboration quality means.
- `critical-thinking` — if the source concerns verification, stewardship, judgment, external validation, or the conditions under which scrutiny is preserved or captured.
- `responsible-ai-deployment` — if the source implies governance, design, monitoring, uncertainty-surfacing, or validation-process safeguards.
- `automation-complacency` — only if the mechanism is reduced effort/attention/reliance; do not force persuasion into complacency when the user is actively scrutinizing the model.
- `ai-supported-knowledge-synthesis` — only if the source is specifically about evidence navigation, source grounding, synthesis interfaces, citations, or audit trails.

## New-topic threshold

Do **not** immediately promote a broad `ai-mediated-persuasion` topic from one source. Defer into the watchlist or existing verification/collaboration pages unless there are multiple sources showing persuasion as a recurring design/governance mechanism across tasks.

Promote a new topic when at least two sources make persuasion/influence the focal construct and the synthesis would otherwise get flattened into generic collaboration, critical thinking, or adoption. Candidate slugs could include `ai-mediated-persuasion`, `ai-validation-and-persuasion`, or `ai-stewardship-and-verification`, depending on the accumulated evidence.

## Synthesis move

Frame the contribution as distinct from simple complacency: the worker may be actively validating, pushing back, or thinking critically, yet the validation channel can still be captured if it occurs inside the same persuasive conversational system. The design question becomes when to externalize verification into independent evidence, tools, reviewers, critique agents, uncertainty displays, or work routines.

## Provenance pitfall

For HBS / working-paper PDFs, DOI regexes may pick up unrelated DOIs from the references section. Do not treat a DOI found anywhere in extracted text as the source DOI until its local context, title page, or landing-page metadata shows it belongs to the paper itself. HBS item pages and public `ris/Publication Files/...pdf` URLs are acceptable public provenance when the PDF is a Harvard Business School working paper and no source DOI exists.
