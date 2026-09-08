#!/usr/bin/env python3
"""
synthesis_pr.py -- the GitHub side effects of the weekly synthesis batch, kept
deterministic and out of the LLM turn (docs/wiki-redesign-plan.md §4).

The batch drafts topic synthesis on a `synthesis/YYYY-MM-DD` branch and opens a
pull request; the owner merging that PR *is* the approval. This script owns the
API calls: it lists synthesis PRs and branches, decides skip / regenerate / go
under the one-open-batch rule, opens or closes a PR, and prunes branches whose
PR is merged or closed. The token comes from git's credential store
(`git credential fill`, the same credentials the daily sync pushes with); it is
never printed and never lives in this repo.

  uv run synthesis_pr.py status [--json]                 # open/merged state + the decision
  uv run synthesis_pr.py open --branch synthesis/2026-09-14 --title "..." --body-file body.md
  uv run synthesis_pr.py close --number 12 --delete-branch
  uv run synthesis_pr.py prune                           # delete synthesis/* branches whose PR is closed/merged
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO = "nbremner/llm-research-wiki"
API = "https://api.github.com"
BRANCH_PREFIX = "synthesis/"
DEFAULT_STALE_DAYS = 7
EXIT_NO_TOKEN = 4


# ---------------------------------------------------------------------------
# Pure core
# ---------------------------------------------------------------------------

def parse_credential_fill(output: str) -> str | None:
    """Password field from `git credential fill` output (key=value lines)."""
    for line in output.splitlines():
        if line.startswith("password="):
            return line[len("password="):].strip() or None
    return None


def synthesis_prs(prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """PRs whose head branch is a synthesis branch, oldest first, reduced to what we use."""
    out = []
    for pr in prs:
        ref = ((pr.get("head") or {}).get("ref")) or ""
        if not ref.startswith(BRANCH_PREFIX):
            continue
        out.append({"number": pr.get("number"), "branch": ref, "state": pr.get("state"),
                    "merged": bool(pr.get("merged_at")), "created_at": pr.get("created_at"),
                    "url": pr.get("html_url"), "title": pr.get("title", "")})
    return sorted(out, key=lambda p: p.get("created_at") or "")


def age_days(created_at: str | None, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat(str(created_at)[:10])).days
    except (TypeError, ValueError):
        return None


def classify(open_prs: list[dict[str, Any]], today: dt.date,
             stale_days: int = DEFAULT_STALE_DAYS) -> dict[str, Any]:
    """The one-open-batch rule: no open PR -> go; open and younger than
    `stale_days` -> skip this run; open and stale -> regenerate (close it, draft
    afresh). More than one open PR is a state the bot must not untangle."""
    if not open_prs:
        return {"action": "go", "pr": None, "age_days": None}
    if len(open_prs) > 1:
        return {"action": "manual", "pr": open_prs, "age_days": None,
                "reason": "more than one open synthesis PR; owner must close the extras"}
    pr = open_prs[0]
    age = age_days(pr.get("created_at"), today)
    if age is None or age < stale_days:
        return {"action": "skip", "pr": pr, "age_days": age}
    return {"action": "regenerate", "pr": pr, "age_days": age}


def prunable(branches: list[str], prs: list[dict[str, Any]]) -> list[str]:
    """Remote synthesis branches whose PR is closed or merged (safe to delete);
    a branch with no PR at all, or with an open PR, is left alone."""
    by_branch: dict[str, list[dict[str, Any]]] = {}
    for pr in prs:
        by_branch.setdefault(pr["branch"], []).append(pr)
    out = []
    for b in branches:
        prs_for = by_branch.get(b) or []
        if prs_for and all(p.get("state") == "closed" for p in prs_for):
            out.append(b)
    return out


# ---------------------------------------------------------------------------
# GitHub / git side
# ---------------------------------------------------------------------------

def get_token() -> str | None:
    try:
        res = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                             capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return parse_credential_fill(res.stdout)


def api(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> Any:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method, headers={
        "Authorization": f"token {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "research-wiki-synthesis-batch", "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"GitHub API {method} {path} -> {e.code}: {detail}") from None


def list_prs(token: str, state: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = api("GET", f"/repos/{REPO}/pulls?state={state}&per_page=100&page={page}", token) or []
        out.extend(batch)
        if len(batch) < 100:
            return out
        page += 1


def remote_synthesis_branches(repo_dir: Path) -> list[str]:
    res = subprocess.run(["git", "-C", str(repo_dir), "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH_PREFIX}*"],
                         capture_output=True, text=True, timeout=60, check=False)
    return sorted(line.split("refs/heads/", 1)[1] for line in res.stdout.splitlines() if "refs/heads/" in line)


def delete_remote_branch(token: str, branch: str) -> None:
    api("DELETE", f"/repos/{REPO}/git/refs/heads/{branch}", token)


def _default_repo_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="GitHub side effects for the weekly synthesis batch")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true"); s.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS)
    o = sub.add_parser("open"); o.add_argument("--branch", required=True); o.add_argument("--title", required=True); o.add_argument("--body-file", required=True)
    c = sub.add_parser("close"); c.add_argument("--number", type=int, required=True); c.add_argument("--delete-branch", action="store_true")
    sub.add_parser("prune")
    for sp in (s, o, c):
        sp.add_argument("--repo-dir", type=Path, default=_default_repo_dir())
    args = p.parse_args(argv)
    repo_dir = getattr(args, "repo_dir", _default_repo_dir())

    token = get_token()
    if not token:
        print("no GitHub token in the git credential store (git credential fill returned nothing)", file=sys.stderr)
        return EXIT_NO_TOKEN
    today = dt.datetime.now(dt.timezone.utc).date()

    if args.cmd == "status":
        open_prs = synthesis_prs(list_prs(token, "open"))
        closed = synthesis_prs(list_prs(token, "closed"))
        branches = remote_synthesis_branches(repo_dir)
        decision = classify(open_prs, today, args.stale_days)
        out = {"today": today.isoformat(), "decision": decision, "open": open_prs,
               "branches": branches, "prunable": prunable(branches, open_prs + closed),
               "recently_closed": closed[-3:]}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"decision: {decision['action']}" + (f" (PR #{decision['pr']['number']}, {decision['age_days']}d)" if isinstance(decision.get('pr'), dict) else ""))
            for pr in open_prs:
                print(f"  open   #{pr['number']} {pr['branch']} ({age_days(pr['created_at'], today)}d) {pr['url']}")
            for b in out["prunable"]:
                print(f"  prunable branch: {b}")
        return 0

    if args.cmd == "open":
        body = Path(args.body_file).read_text(encoding="utf-8")
        pr = api("POST", f"/repos/{REPO}/pulls", token,
                 {"title": args.title, "head": args.branch, "base": "main", "body": body})
        print(json.dumps({"number": pr["number"], "url": pr["html_url"], "branch": args.branch}))
        return 0

    if args.cmd == "close":
        pr = api("PATCH", f"/repos/{REPO}/pulls/{args.number}", token, {"state": "closed"})
        branch = (pr.get("head") or {}).get("ref")
        print(f"closed PR #{args.number} ({branch})")
        if args.delete_branch and branch and branch.startswith(BRANCH_PREFIX):
            delete_remote_branch(token, branch)
            print(f"deleted branch {branch}")
        return 0

    if args.cmd == "prune":
        prs = synthesis_prs(list_prs(token, "all"))
        branches = remote_synthesis_branches(repo_dir)
        for b in prunable(branches, prs):
            delete_remote_branch(token, b)
            print(f"deleted merged/closed branch {b}")
        else:
            if not prunable(branches, prs):
                print("nothing to prune")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
