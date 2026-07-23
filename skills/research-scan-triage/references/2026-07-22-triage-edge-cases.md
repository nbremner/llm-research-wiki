# 2026-07-22 scan triage edge cases

Session-specific examples worth reusing when future batches surface similar material.

## OSF DOI direct-download variant

For a Crossref DOI like `10.31235/osf.io/3gty8_v1`, the bounded rung-4 direct path worked by stripping the OSF id and version suffix:

```bash
curl -L --fail -A 'Mozilla/5.0' \
  -o /root/research-wiki-runs/<run>/files/osf-3gty8.pdf \
  https://osf.io/3gty8/download
file /root/research-wiki-runs/<run>/files/osf-3gty8.pdf
python - <<'PY'
import pypdf
p = '/root/research-wiki-runs/<run>/files/osf-3gty8.pdf'
r = pypdf.PdfReader(p)
print('pages', len(r.pages))
print((r.pages[0].extract_text() or '')[:500])
PY
```

Use this only inside the normal rung-4 cap.

## Landing-page artifact means ambiguous when metadata is thin

A manifest row may say `acq_state: full-text` with an `artifact_drive_id`, but the Drive file can still be a Jina/SAGE navigation page. Example: **Responsible Use of AI and Wearable Technologies in Occupational Safety** had no manifest abstract and the artifact contained mostly SAGE navigation/account/menu text. Proposed `wiki`, but set `confidence: ambiguous` because title/venue alone were not enough for a durable rubric call.

## Disposition examples from this batch

- **wiki / clear**: workplace AI-use evidence with employed adults and job-task/work-organization predictors; practitioner/framework chapters on AI transition and skill erosion; socio-technical AI safety frameworks centered on workflows, organizational oversight, auditability, and overreliance; contact-center cognitive-load/workload-balancing evidence.
- **read-once / clear**: computing-education/team-assessment studies without genuine work/labor setting; drone-computing infrastructure visions with only adjacent workforce-development language; clinical AI collaboration/accountability frameworks centered on a different profession's work product; automotive manufacturing automation/deskilling without a direct AI×work center.
- **discard / clear**: pure robotics/world-modeling or creative-generation methods papers with no real work, workforce, labor, or organizational angle.

## Digest-writing pitfall

The applier truncates read-once summaries in the digest. Put the disposition-relevant takeaway first; do not lead with long bibliographic or setup language.