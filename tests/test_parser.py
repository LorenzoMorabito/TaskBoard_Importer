"""Tests for Markdown parsing using new parsing module."""
from taskboard_importer.parsing import parse_markdown


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


def test_parse_bold_labels_and_inline_values(tmp_path):
    content = """# Title
# 1. Phase
## 1.1 Task
**Attività**: Primo passo
**Verifica**:
- Check 1
**Output atteso**: Output inline
**Done quando**: Done inline
**Tracking**: Owner: Team
**Stato**: TODO
"""
    path = tmp_path / "bold.md"
    path.write_text(content, encoding="utf-8")

    project = parse_markdown(str(path))
    task = project.phases[0].tasks[0]

    assert task.activities[0] == "Primo passo"
    assert task.verification == ["Check 1"]
    assert task.expected_output == "Output inline"
    assert task.done_when == "Done inline"
    assert "Owner: Team" in task.tracking_template
    assert task.initial_status == "TODO"


def test_preamble_before_first_phase_attaches_to_summary(tmp_path):
    content = """# Doc Title
## Scopo del documento
## Come usare questa roadmap
# 1. Phase
## 1.1 Task
Attività
- A
"""
    path = tmp_path / "preamble.md"
    path.write_text(content, encoding="utf-8")

    project = parse_markdown(str(path))
    assert len(project.phases) == 1
    phase = project.phases[0]
    assert "Scopo del documento" in project.summary
    assert "Come usare questa roadmap" in project.summary
    assert len(phase.tasks) == 1
