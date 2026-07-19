# SSRN rung-4 acquisition: bounded stop pattern

When a clear wiki-candidate lacks an artifact and its DOI is an SSRN DOI (`10.2139/ssrn.<id>`), a light public attempt is reasonable, but do not burn time fighting SSRN access controls.

Compact pattern:

1. Derive the abstract page from the DOI id: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=<id>`.
2. Try one browser or HTTP fetch with a normal user agent only to locate an obvious public download link.
3. If SSRN returns `403 Forbidden`, bot-check/CAPTCHA, login wall, or no obvious download link, stop immediately.
4. Leave `acquired_path` unset; keep the clear wiki disposition so the applier surfaces it under manual acquisition.

Why: the scan triage job routes candidates, not access work. A bounded failed SSRN probe is enough evidence to surface manual acquisition without delaying the cron run or risking non-public access flows.
