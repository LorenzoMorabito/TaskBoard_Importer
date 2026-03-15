"""Tests for domain module."""

import pytest

from taskboard_importer.domain import (
    Phase,
    ProjectImport,
    Task,
    ValidationError,
    generate_phase_id,
    generate_run_id,
    generate_task_id,
    raise_if_invalid,
    validate_project,
)


class TestIdentifiers:
    """Test ID generation functions."""

    def test_generate_task_id(self):
        task_id = generate_task_id("1", 1)
        assert task_id == "1.1"

        task_id = generate_task_id("2", 5)
        assert task_id == "2.5"

    def test_generate_phase_id(self):
        phase_id = generate_phase_id(1)
        assert phase_id == "1"

        phase_id = generate_phase_id(99)
        assert phase_id == "99"

    def test_generate_run_id(self):
        run_id = generate_run_id()
        assert run_id.startswith("run_")
        assert len(run_id) > 20  # Contains timestamp + uuid


class TestValidation:
    """Test project validation."""

    def test_validate_project_valid(self):
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="Test",
            imported_at="2024-01-01T00:00:00",
            phases=[
                Phase(
                    phase_id="1",
                    order=1,
                    title="Phase 1",
                    tasks=[
                        Task(
                            task_id="1.1",
                            phase_id="1",
                            section_ref="1.1",
                            title="Task 1",
                        )
                    ],
                )
            ],
        )
        errors = validate_project(project)
        assert errors == []

    def test_validate_project_missing_title(self):
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="",
            imported_at="2024-01-01T00:00:00",
            phases=[],
        )
        errors = validate_project(project)
        assert any("title is required" in e for e in errors)

    def test_validate_project_no_phases(self):
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="Test",
            imported_at="2024-01-01T00:00:00",
            phases=[],
        )
        errors = validate_project(project)
        assert any("At least one phase" in e for e in errors)

    def test_raise_if_invalid(self):
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="",
            imported_at="2024-01-01T00:00:00",
            phases=[],
        )
        with pytest.raises(ValidationError):
            raise_if_invalid(project)


class TestDataModels:
    """Test data model serialization."""

    def test_task_to_dict(self):
        task = Task(
            task_id="1.1",
            phase_id="1",
            section_ref="1.1",
            title="My Task",
            activities=["Do something"],
            verification=["Check it"],
            expected_output="Result",
            done_when="Done",
            content_hash="abc123",
            task_type="operational_task",
            publish_policy="publish_as_issue",
        )
        data = task.to_dict()
        assert data["task_id"] == "1.1"
        assert data["title"] == "My Task"
        assert data["activities"] == ["Do something"]

    def test_phase_to_dict(self):
        task = Task(task_id="1.1", phase_id="1", section_ref="1.1", title="Task")
        phase = Phase(phase_id="1", order=1, title="Phase 1", tasks=[task])
        data = phase.to_dict()
        assert data["phase_id"] == "1"
        assert data["title"] == "Phase 1"
        assert len(data["tasks"]) == 1

    def test_project_to_dict(self):
        task = Task(task_id="1.1", phase_id="1", section_ref="1.1", title="Task")
        phase = Phase(phase_id="1", order=1, title="Phase 1", tasks=[task])
        project = ProjectImport(
            source_file="test.md",
            source_hash="abc",
            title="Test",
            imported_at="2024-01-01T00:00:00",
            phases=[phase],
        )
        data = project.to_dict()
        assert data["title"] == "Test"
        assert len(data["phases"]) == 1
