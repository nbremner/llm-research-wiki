# Upstream research-scan service troubleshooting

Use this when `research-scan-triage` reports no new scan but the upstream deterministic harness is suspected to be failing, or when the user says `research-scan.service failed`.

## Tight loop

The red/green loop is the systemd service plus the newest journal excerpt:

```bash
systemctl status research-scan --no-pager -l || true
journalctl -u research-scan --no-pager -n 160 -o short-iso
```

The service should complete with `Deactivated successfully` and write a new `/root/research-wiki-runs/scan-*/manifest-*.json`. If it exits before discovery/acquisition, inspect the stack trace before touching scan code.

## Common Drive OAuth failure

If the journal shows:

```text
google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked.
```

and the failing frame is a Drive call such as `drive_list_names(...)`, the root cause is not the scan rubric or manifest logic. The local Google OAuth token is revoked/expired and must be reauthorized.

Verify with:

```bash
python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --check || true
python /root/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "name contains 'agentic-research-wiki'" --max 3 || true
```

If both fail with `invalid_grant`, generate a Drive-only OAuth URL using the `google-workspace` skill's `references/drive-only-oauth-headless.md` flow rather than requesting broad Workspace scopes. After the user returns the redirected `localhost:1` URL/code:

```bash
python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code '<returned-url-or-code>'
python /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --check || true
python /root/.hermes/skills/productivity/google-workspace/scripts/google_api.py drive search "name contains 'agentic-research-wiki'" --max 3
systemctl reset-failed research-scan.service
systemctl start research-scan.service
systemctl status research-scan --no-pager -l
journalctl -u research-scan --no-pager -n 80 -o short-iso
```

A Drive-only token may report `AUTHENTICATED (partial)` in older setup scripts because non-Drive scopes are absent. Treat a targeted Drive API search as the real verification for this pipeline.

## Boundaries

Do not change scan code until the service log identifies a code/data bug. OAuth failures are credential repair, not pipeline repair. Do not paste refresh tokens or client secrets into the chat; only exchange the authorization URL/code through the setup script.