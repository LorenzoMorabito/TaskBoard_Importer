"""Tests for the application import pipeline."""

import json

from taskboard_importer.application.import_roadmap import import_roadmap


def _write_markdown(path, body):
    path.write_text(body, encoding="utf-8")


def test_import_roadmap_dry_run_writes_outputs(tmp_path):
    source = tmp_path / "roadmap.md"
    output_json = tmp_path / "import.json"
    manifest_json = tmp_path / "manifest.json"
    _write_markdown(
        source,
        """# Demo
# 1. Phase
## 1.1 Operational task
Attività
- Step A
Verifica
- Check A
Output atteso
Done
Done quando
Validated
## 1.2 Checklist
- [ ] One
- [ ] Two
- [ ] Three
""",
    )

    project, results, run = import_roadmap(
        input_path=str(source),
        output_json=str(output_json),
        manifest_json=str(manifest_json),
        publish_to_github=False,
        dry_run=True,
    )

    assert project.title == "Demo"
    assert len(results) == 2
    assert results[0].action == "dry_run"
    assert results[0].publish_status == "dry_run"
    assert results[1].action == "doc_issue_deferred"
    assert output_json.exists()
    assert manifest_json.exists()

    manifest_data = json.loads(manifest_json.read_text(encoding="utf-8"))
    assert manifest_data["result_summary"]["total_tasks"] == 2
    assert run.result_summary["policy_counts"]["publish_as_issue"] == 1


def test_import_roadmap_updates_existing_issue(monkeypatch, tmp_path):
    source = tmp_path / "roadmap.md"
    manifest_path = tmp_path / "previous_manifest.json"
    _write_markdown(
        source,
        """# Demo
# 1. Phase
## 1.1 Operational task
Attività
- Changed step
Verifica
- Check A
Output atteso
Done
Done quando
Validated
""",
    )
    manifest_path.write_text(
        json.dumps(
            {
                "task_fingerprints": {"1.1": "old_hash"},
                "publish_results": [
                    {
                        "task_id": "1.1",
                        "section_ref": "1.1",
                        "github_issue_number": 42,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    calls = {"updated": []}

    class FakeIssuesClient:
        def __init__(self, token, dry_run=False):
            self.token = token

        def create_issue(self, **kwargs):
            raise AssertionError("create_issue should not be used for update path")

        def update_issue(self, **kwargs):
            calls["updated"].append(kwargs)

        def get_issue(self, **kwargs):
            return {"node_id": "ISSUE_NODE"}

    class FakeProjectsClient:
        def __init__(self, token, dry_run=False):
            self.token = token

        def get_project_id(self, repo_owner, repo_name, project_number):
            return "PROJECT_ID"

        def add_issue_to_project(self, project_id, content_id):
            return "ITEM_ID"

    monkeypatch.setattr(
        "taskboard_importer.infrastructure.github.IssuesClient", FakeIssuesClient
    )
    monkeypatch.setattr(
        "taskboard_importer.infrastructure.github.ProjectsV2Client",
        FakeProjectsClient,
    )

    _, results, _ = import_roadmap(
        input_path=str(source),
        previous_manifest=str(manifest_path),
        dedupe_policy="update",
        publish_to_github=True,
        repo_owner="owner",
        repo_name="repo",
        token="token",
        dry_run=False,
    )

    assert len(calls["updated"]) == 1
    assert calls["updated"][0]["issue_number"] == 42
    assert results[0].action == "updated"
    assert results[0].github_issue_number == 42
    assert results[0].publish_status == "published"
