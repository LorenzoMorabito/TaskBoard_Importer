"""Tests for mapping, normalization and validation using new modules."""
from taskboard_importer.policies import normalize_project
from taskboard_importer.parsing import parse_markdown
from taskboard_importer.domain import validate_project


def test_normalize_defaults():
    project = parse_markdown("tests/fixtures/databricks_setup_environment_roadmap.md")
    project = normalize_project(project, default_status="Backlog")
    task = project.phases[0].tasks[1]
    assert task.task_id
    assert task.section_ref
    assert task.initial_status in {"Backlog", "Todo"}
    assert task.content_hash


def test_phase_without_tasks_allowed_when_summary_present(tmp_path):
    content = """# Title
# 1. Phase
This is a descriptive phase without tasks.
# 2. Phase
## 2.1 Task
Attività
- A
"""
    path = tmp_path / "phase_summary.md"
    path.write_text(content, encoding="utf-8")

    project = parse_markdown(str(path))
    errors = validate_project(project)
    assert errors == []


def test_task_classification_rules(tmp_path):
    content = """# Title
# 1. Phase
## 1.1 Registro
| ID | Stato |
|---|---|
| 1 | TODO |
## 1.2 Checklist
- [ ] Uno
- [ ] Due
- [ ] Tre
## 1.3 Best practice
Attività
- Da fare sempre
## 1.4 Operativo
Attività
- A
Verifica
- V
Output atteso
X
Done quando
Y
"""
    path = tmp_path / "classify.md"
    path.write_text(content, encoding="utf-8")

    project = parse_markdown(str(path))
    project = normalize_project(project)

    t1 = project.phases[0].tasks[0]
    t2 = project.phases[0].tasks[1]
    t3 = project.phases[0].tasks[2]
    t4 = project.phases[0].tasks[3]

    assert t1.task_type == "status_register"
    assert t1.publish_policy == "publish_as_note"
    assert t1.content_kind == "table"

    assert t2.task_type == "checklist"
    assert t2.publish_policy == "publish_as_doc_issue"

    assert t3.task_type == "documentation"
    assert t3.publish_policy == "publish_as_note"

    assert t4.task_type == "operational_task"
    assert t4.publish_policy == "publish_as_issue"
