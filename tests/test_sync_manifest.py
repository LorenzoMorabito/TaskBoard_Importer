"""Tests for manifest loading and sync planning."""

import json

from taskboard_importer.parsing import parse_markdown
from taskboard_importer.policies import normalize_project
from taskboard_importer.sync import load_manifest_details, plan_dedupe


def test_plan_dedupe_skip_for_unchanged_task():
    project = parse_markdown("tests/fixtures/databricks_setup_environment_roadmap.md")
    project = normalize_project(project)
    task = project.phases[0].tasks[0]
    previous = {task.section_ref: task.content_hash}

    decisions = plan_dedupe([task], previous, policy="skip")
    assert decisions[0].action == "skip"


def test_load_manifest_details_maps_task_and_section_keys(tmp_path):
    manifest = {
        "task_fingerprints": {"1.1": "hash"},
        "publish_results": [
            {
                "task_id": "t-1",
                "section_ref": "1.1",
                "github_issue_number": 42,
                "project_item_id": "item-1",
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    fingerprints, issue_map, project_item_map = load_manifest_details(str(path))

    assert fingerprints["1.1"] == "hash"
    assert issue_map["t-1"] == 42
    assert issue_map["1.1"] == 42
    assert project_item_map["t-1"] == "item-1"
    assert project_item_map["1.1"] == "item-1"
