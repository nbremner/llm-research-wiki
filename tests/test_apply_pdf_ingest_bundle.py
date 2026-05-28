import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "research-wiki-tools" / "apply_pdf_ingest_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("apply_pdf_ingest_bundle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeExecute:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class FakeFiles:
    def __init__(self):
        self.calls = []

    def update(self, **kwargs):
        self.calls.append(("update", kwargs))
        return FakeExecute({"id": kwargs["fileId"], "name": kwargs["body"]["name"], "parents": ["dest"]})

    def get(self, **kwargs):
        self.calls.append(("get", kwargs))
        return FakeExecute({"id": kwargs["fileId"], "name": "canonical.pdf", "parents": ["dest"]})


class FakeDriveService:
    def __init__(self):
        self.files_resource = FakeFiles()

    def files(self):
        return self.files_resource


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.text)

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.posts = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.posts.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return FakeResponse({"id": f"page-{len(self.posts)}", "url": f"https://notion.test/{len(self.posts)}"})


def valid_manifest():
    return {
        "schema_version": "2026-05-24.1",
        "drive": {
            "file_id": "file123",
            "original_parent_id": "inbox",
            "destination_parent_id": "dest",
            "final_filename": "2026-01-01_author_title.pdf",
        },
        "notion": {
            "inbox_database_id": "inbox-db",
            "log_database_id": "log-db",
            "inbox": {
                "properties": {"Name": {"title": [{"text": {"content": "Candidate"}}]}},
                "markdown": "# Candidate Source Summary\n\nFinal Drive filename: 2026-01-01_author_title.pdf",
            },
            "log": {
                "properties": {"Name": {"title": [{"text": {"content": "Applied bundle"}}]}},
                "markdown": "Drive and Notion applied.",
            },
        },
    }


def test_validate_manifest_requires_drive_before_notion_fields():
    module = load_module()
    manifest = valid_manifest()
    manifest["drive"].pop("final_filename")

    errors = module.validate_manifest(manifest)

    assert "drive.final_filename is required" in errors


def test_apply_drive_filing_renames_moves_and_verifies_stable_file_id():
    module = load_module()
    drive = FakeDriveService()

    result = module.apply_drive_filing(
        drive,
        file_id="file123",
        final_filename="canonical.pdf",
        original_parent_id="inbox",
        destination_parent_id="dest",
    )

    assert result["verified"] is True
    assert result["file_id_stable"] is True
    assert drive.files_resource.calls[0] == (
        "update",
        {
            "fileId": "file123",
            "body": {"name": "canonical.pdf"},
            "addParents": "dest",
            "removeParents": "inbox",
            "fields": "id,name,parents,webViewLink",
        },
    )
    assert drive.files_resource.calls[1][0] == "get"


def test_create_notion_pages_creates_inbox_then_log_with_markdown():
    module = load_module()
    session = FakeSession()
    manifest = valid_manifest()

    result = module.create_notion_pages(session, "secret", manifest["notion"])

    assert result["inbox_page_id"] == "page-1"
    assert result["log_page_id"] == "page-2"
    assert len(session.posts) == 2
    assert session.posts[0]["json"]["parent"] == {"database_id": "inbox-db"}
    assert session.posts[0]["json"]["markdown"].startswith("# Candidate Source Summary")
    assert session.posts[1]["json"]["parent"] == {"database_id": "log-db"}


def test_run_bundle_dry_run_has_no_side_effects_and_reports_order():
    module = load_module()
    manifest = valid_manifest()

    result = module.run_bundle(manifest, dry_run=True)

    assert result["status"] == "dry-run"
    assert result["side_effects"] == []
    assert result["planned_order"] == [
        "validate manifest",
        "rename and move Drive file",
        "verify Drive state",
        "create Notion Inbox page",
        "create Notion Log page",
    ]
