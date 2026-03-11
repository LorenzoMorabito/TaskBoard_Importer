import os

from taskboard_importer.workspace import init_project, read_yaml


def test_init_project_creates_structure(tmp_path):
    root = tmp_path / "proj"
    path = init_project(
        path=str(root),
        slug="demo",
        title="Demo Project",
        owner="Tester",
        template_profile="standard",
    )

    assert os.path.exists(os.path.join(path, "project.yaml"))
    assert os.path.exists(os.path.join(path, "README.md"))
    assert os.path.exists(os.path.join(path, "roadmap", "roadmap.md"))
    assert os.path.exists(os.path.join(path, "docs", "architecture.md"))
    assert os.path.exists(os.path.join(path, "state", "current_status.md"))
    assert os.path.exists(os.path.join(path, "rules", "publish_rules.yml"))

    config = read_yaml(os.path.join(path, "project.yaml"))
    assert config.get("slug") == "demo"
    assert config.get("title") == "Demo Project"
    assert config.get("paths")
