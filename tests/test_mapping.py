from taskboard_importer.normalizer import normalize_project
from taskboard_importer.parser_markdown import parse_markdown


def test_normalize_defaults():
    project = parse_markdown("tests/fixtures/databricks_setup_environment_roadmap.md")
    project = normalize_project(project, default_status="Backlog")
    task = project.phases[0].tasks[1]
    assert task.task_id
    assert task.section_ref
    assert task.initial_status in {"Backlog", "Todo"}
    assert task.content_hash
