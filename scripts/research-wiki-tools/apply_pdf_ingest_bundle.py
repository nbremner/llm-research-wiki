#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "google-auth-httplib2",
#   "requests",
# ]
# ///
"""
Apply-mode bundle helper for one public research-wiki PDF.

This script deliberately does not summarize PDFs. The agent supplies a reviewed
manifest containing the final Drive filename plus typed Notion properties and
markdown. The script applies the side-effect bundle in one fixed order:

1. validate manifest;
2. rename/move Drive file out of `_inbox`;
3. verify Drive state;
4. create Notion Inbox page;
5. create Notion Log page.

Dry-run mode validates and prints the planned order without mutating Drive or
Notion.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

NOTION_VERSION = "2025-09-03"
DEFAULT_GOOGLE_TOKEN_PATH = "/root/.hermes/google_token.json"
PLANNED_ORDER = [
    "validate manifest",
    "rename and move Drive file",
    "verify Drive state",
    "create Notion Inbox page",
    "create Notion Log page",
]


def _get_path(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors for an ingest manifest."""
    required = [
        "schema_version",
        "drive.file_id",
        "drive.original_parent_id",
        "drive.destination_parent_id",
        "drive.final_filename",
        "notion.inbox_database_id",
        "notion.log_database_id",
        "notion.inbox.properties",
        "notion.inbox.markdown",
        "notion.log.properties",
        "notion.log.markdown",
    ]
    errors: list[str] = []
    for dotted in required:
        value = _get_path(manifest, dotted)
        if value in (None, "", {}, []):
            errors.append(f"{dotted} is required")

    final_filename = _get_path(manifest, "drive.final_filename")
    if final_filename and not str(final_filename).lower().endswith(".pdf"):
        errors.append("drive.final_filename must end with .pdf")

    inbox_markdown = _get_path(manifest, "notion.inbox.markdown")
    if inbox_markdown and final_filename and str(final_filename) not in str(inbox_markdown):
        errors.append("notion.inbox.markdown should include the final Drive filename")

    return errors


def apply_drive_filing(
    drive_service: Any,
    *,
    file_id: str,
    final_filename: str,
    original_parent_id: str,
    destination_parent_id: str,
) -> dict[str, Any]:
    """Rename/move a Drive file in-place and verify the final state."""
    files = drive_service.files()
    update_result = files.update(
        fileId=file_id,
        body={"name": final_filename},
        addParents=destination_parent_id,
        removeParents=original_parent_id,
        fields="id,name,parents,webViewLink",
    ).execute()

    verified = files.get(
        fileId=file_id,
        fields="id,name,parents,webViewLink",
    ).execute()

    parents = set(verified.get("parents") or [])
    return {
        "updated": update_result,
        "verified_metadata": verified,
        "file_id_stable": verified.get("id") == file_id,
        "filename_matches": verified.get("name") == final_filename,
        "destination_parent_present": destination_parent_id in parents,
        "original_parent_removed": original_parent_id not in parents,
        "verified": (
            verified.get("id") == file_id
            and verified.get("name") == final_filename
            and destination_parent_id in parents
            and original_parent_id not in parents
        ),
    }


def notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def create_notion_page(
    session: Any,
    token: str,
    *,
    database_id: str,
    properties: dict[str, Any],
    markdown: str,
) -> dict[str, Any]:
    response = session.post(
        "https://api.notion.com/v1/pages",
        headers=notion_headers(token),
        json={
            "parent": {"database_id": database_id},
            "properties": properties,
            "markdown": markdown,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def create_notion_pages(session: Any, token: str, notion_manifest: dict[str, Any]) -> dict[str, Any]:
    """Create Inbox first, then Log, using caller-supplied typed properties."""
    inbox = create_notion_page(
        session,
        token,
        database_id=notion_manifest["inbox_database_id"],
        properties=notion_manifest["inbox"]["properties"],
        markdown=notion_manifest["inbox"]["markdown"],
    )
    log = create_notion_page(
        session,
        token,
        database_id=notion_manifest["log_database_id"],
        properties=notion_manifest["log"]["properties"],
        markdown=notion_manifest["log"]["markdown"],
    )
    return {
        "inbox_page_id": inbox.get("id"),
        "inbox_url": inbox.get("url"),
        "log_page_id": log.get("id"),
        "log_url": log.get("url"),
        "raw": {"inbox": inbox, "log": log},
    }


def run_bundle(
    manifest: dict[str, Any],
    *,
    dry_run: bool,
    drive_service: Any | None = None,
    notion_session: Any | None = None,
    notion_token: str | None = None,
) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if errors:
        return {"status": "invalid", "errors": errors, "planned_order": PLANNED_ORDER, "side_effects": []}

    if dry_run:
        return {"status": "dry-run", "planned_order": PLANNED_ORDER, "side_effects": []}

    if drive_service is None:
        raise ValueError("drive_service is required when dry_run=False")
    if notion_session is None:
        raise ValueError("notion_session is required when dry_run=False")
    if not notion_token:
        raise ValueError("notion_token is required when dry_run=False")

    side_effects: list[str] = []
    drive_cfg = manifest["drive"]
    drive_result = apply_drive_filing(
        drive_service,
        file_id=drive_cfg["file_id"],
        final_filename=drive_cfg["final_filename"],
        original_parent_id=drive_cfg["original_parent_id"],
        destination_parent_id=drive_cfg["destination_parent_id"],
    )
    side_effects.append("drive_rename_move")
    if not drive_result["verified"]:
        return {
            "status": "partial",
            "error": "Drive rename/move did not verify; Notion writes were not attempted.",
            "drive": drive_result,
            "planned_order": PLANNED_ORDER,
            "side_effects": side_effects,
        }

    notion_result = create_notion_pages(notion_session, notion_token, manifest["notion"])
    side_effects.extend(["notion_inbox_create", "notion_log_create"])
    return {
        "status": "success",
        "planned_order": PLANNED_ORDER,
        "side_effects": side_effects,
        "drive": drive_result,
        "notion": notion_result,
    }


def build_drive_service(token_path: str = DEFAULT_GOOGLE_TOKEN_PATH) -> Any:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_authorized_user_file(token_path, scopes)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def build_requests_session() -> Any:
    import requests

    return requests.Session()


def load_manifest(path: str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Manifest JSON must be an object")
    return data


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a research-wiki PDF Drive+Notion ingest bundle")
    parser.add_argument("manifest", help="Path to manifest JSON with Drive and Notion payloads")
    parser.add_argument("--apply", action="store_true", help="Actually mutate Drive and Notion; default is dry-run")
    parser.add_argument("--google-token", default=DEFAULT_GOOGLE_TOKEN_PATH, help="Google OAuth token path")
    parser.add_argument("--notion-token-env", default="NOTION_API_KEY", help="Environment variable holding Notion token")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    manifest = load_manifest(args.manifest)

    if not args.apply:
        result = run_bundle(manifest, dry_run=True)
    else:
        notion_token = os.environ.get(args.notion_token_env)
        if not notion_token:
            print(json.dumps({"status": "invalid", "errors": [f"{args.notion_token_env} is not set"]}, indent=2), file=sys.stderr)
            return 2
        result = run_bundle(
            manifest,
            dry_run=False,
            drive_service=build_drive_service(args.google_token),
            notion_session=build_requests_session(),
            notion_token=notion_token,
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"dry-run", "success"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
