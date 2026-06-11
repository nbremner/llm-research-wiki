# End-of-session artifact drift check

Use this after research-wiki workflow-spine changes, especially when both repo files and live Hermes skills were touched.

## Purpose

Prevent the public research-wiki operating layer from splitting into competing versions: Git repo, Hermes skill store, Notion operating pages, generated runtime outputs, and test expectations.

## Verification pattern

1. Confirm repo state:
   - current branch is expected (`main` unless deliberately on a feature branch);
   - `HEAD` matches `origin/main` after push;
   - `git status --short` is clean before final wrap-up.
2. Run the full workflow-spine test suite, not only the new test file.
3. Run at least one read-only smoke check when the edited workflow has a live query path, such as:
   - `python scripts/research-wiki-tools/graph_lint.py --max-pages 25`
4. Check generated artifacts remain outside the repo:
   - reports, JSON outputs, Drive inventories, downloads, and caches belong under runtime directories such as `/root/research-wiki-runs/`, not in Git.
5. Check skill mirrors:
   - if `/root/.hermes/skills/...` was patched during the session, mirror durable changes into `/root/work/llm-research-wiki/skills/...`;
   - if repo skills were updated, ensure the live Hermes skill has the same operational guidance or an explicit reason for divergence.
6. Check documentation pointers:
   - root `README.md` lists new durable scripts/skills;
   - tool README explains how to run the workflow;
   - roadmap marks completed acceptance criteria without overstating unfinished work;
   - SKILL.md points to any new `references/`, `templates/`, or `scripts/` support file.
7. Commit and push any missing sync/docs changes, then rerun tests and check clean Git state.

## Pitfall captured

A session can be technically complete but still leave drift if a live Hermes skill support file exists only in `~/.hermes/skills` and not in the portable Git workflow spine. Treat that as a real artifact drift issue and fix it before ending the session.

## Reporting shape

Final wrap-up should include:

- repo path, branch, `HEAD`, and whether it matches remote;
- test result;
- live smoke-check result if applicable;
- list of synced artifacts;
- explicit note that generated runtime artifacts were not committed;
- next clean restart point.
