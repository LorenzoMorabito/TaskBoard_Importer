"""Tests for policies module."""

import pytest

from taskboard_importer.domain import Phase, ProjectImport, Task
from taskboard_importer.policies import classify_task, normalize_project


class TestTaskClassification:
    """Test task classification rules."""

    def test_classify_operational_task(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Implement feature",
            activities=["Do something"],
            verification=["Check it"],
            expected_output="Feature working",
            done_when="Tests pass",
        )
        classify_task(task, "Phase 1")

        assert task.task_type == "operational_task"
        assert task.publish_policy == "publish_as_issue"

    def test_classify_checklist(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Pre-deployment checklist",
            activities=[
                "- [ ] Item 1",
                "- [ ] Item 2",
                "- [ ] Item 3",
            ],
        )
        classify_task(task, "Phase 1")

        assert task.task_type == "checklist"
        assert task.publish_policy == "publish_as_doc_issue"

    def test_classify_status_register(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Status table",
            activities=[
                "| Component | Status |",
                "|-----------|--------|",
                "| A | Done |",
            ],
        )
        classify_task(task, "Phase 1")

        assert task.task_type == "status_register"
        assert task.publish_policy == "publish_as_note"

    def test_classify_documentation(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Best practices guide",
            activities=["Some best practices"],
        )
        classify_task(task, "Riferimenti")

        assert task.task_type == "documentation"
        assert task.publish_policy == "publish_as_note"


class TestNormalization:
    """Test project normalization."""

    def test_normalize_project_fills_defaults(self):
        task = Task(
            task_id="",
            phase_id="",
            section_ref="",
            title="Task 1",
            verification=["Check"],
        )
        phase = Phase(phase_id="", order=1, title="Phase 1", tasks=[task])
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="Test",
            imported_at="2024-01-01T00:00:00",
            phases=[phase],
        )

        normalized = normalize_project(project)

        # Phase ID should be assigned
        assert normalized.phases[0].phase_id != ""
        # Task ID should be assigned
        assert normalized.phases[0].tasks[0].task_id != ""
        # Task should be classified
        assert normalized.phases[0].tasks[0].task_type != ""
        # Hash should be computed
        assert normalized.phases[0].tasks[0].content_hash != ""

    def test_normalize_project_computes_hashes(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="Task 1",
            verification=["Check"],
        )
        phase = Phase(phase_id="1", order=1, title="Phase 1", tasks=[task])
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="Test",
            imported_at="2024-01-01T00:00:00",
            phases=[phase],
        )

        normalized = normalize_project(project)
        assert normalized.phases[0].tasks[0].content_hash != ""
        assert len(normalized.phases[0].tasks[0].content_hash) == 64  # SHA256 hex
