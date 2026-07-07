# OSF rung-4 direct download pattern

Use this when a daily scan manifest has a clear `wiki` candidate with an OSF DOI but no acquired artifact.
Keep attempts within `MAX_RUNG4_BROWSER_PER_RUN`.

## URL shape

For DOI URLs such as:

- `https://doi.org/10.31234/osf.io/8hbp9_v1`
- `https://doi.org/10.31235/osf.io/e9qw5_v1`

extract the OSF id before `_v1` and use:

```bash
mkdir -p /root/research-wiki-runs/<scan-run>/files
curl -L --fail --max-time 60 -A 'Mozilla/5.0' \
  -o /root/research-wiki-runs/<scan-run>/files/osf-<id>.pdf \
  https://osf.io/<id>/download
```

## Verification

First check the file signature:

```bash
file /root/research-wiki-runs/<scan-run>/files/osf-<id>.pdf
python - <<'PY'
from pathlib import Path
p = Path('/root/research-wiki-runs/<scan-run>/files/osf-<id>.pdf')
print(p.stat().st_size)
print(p.read_bytes()[:8])
PY
```

Expected: `file` reports PDF and the first bytes begin with `%PDF`.

If `pdftotext` is present, use it for a text smoke test. If not, `pypdf` is enough:

```bash
python - <<'PY'
import pypdf
f = '/root/research-wiki-runs/<scan-run>/files/osf-<id>.pdf'
r = pypdf.PdfReader(f)
print('pages', len(r.pages))
print((r.pages[0].extract_text() or '')[:300].replace('\n', ' '))
PY
```

If page count and text look real, include the local path as `acquired_path` in the dispositions JSON so the applier uploads it to the wiki inbox.

## Stop rule

If this direct URL fails, do not spend the whole run probing OSF. Fall back to the regular bounded browser attempt, and if blocked, omit `acquired_path` so the applier surfaces manual acquisition.
