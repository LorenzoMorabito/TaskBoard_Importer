from taskboard_importer.parser_markdown import parse_markdown


def test_parse_markdown_basic():
    project = parse_markdown("tests/fixtures/databricks_setup_environment_roadmap.md")
    assert project.title == "Databricks Setup Environment Roadmap"
    assert len(project.phases) == 2
    assert project.phases[0].title.startswith("1.")
    assert len(project.phases[0].tasks) == 2
    first_task = project.phases[0].tasks[0]
    assert first_task.section_ref == "1.1"
    assert "Create workspace" in first_task.activities
    assert first_task.expected_output.startswith("Workspace")
