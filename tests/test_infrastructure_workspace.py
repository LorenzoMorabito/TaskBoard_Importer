"""Tests for workspace configuration loading."""

from taskboard_importer.infrastructure.workspace.project_config import (
    get_config_value,
    load_project_config,
)


def test_load_project_config_reads_yaml(tmp_path):
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        "github:\n  repo_owner: owner\n  repo_name: repo\npublishing:\n  default_status: Ready\n",
        encoding="utf-8",
    )

    config = load_project_config(str(tmp_path))

    assert config["github"]["repo_owner"] == "owner"
    assert get_config_value(config, "publishing.default_status") == "Ready"
