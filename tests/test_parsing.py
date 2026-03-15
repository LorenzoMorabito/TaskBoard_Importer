"""Tests for parsing module."""

import pytest

from taskboard_importer.parsing import parse_markdown


class TestMarkdownParsing:
    """Test Markdown roadmap parsing."""

    def test_parse_markdown_basic(self):
        project = parse_markdown(
            "tests/fixtures/databricks_setup_environment_roadmap.md"
        )
        assert project.title == "Databricks Setup Environment Roadmap"
        assert len(project.phases) >= 1
        assert project.source_file == "tests/fixtures/databricks_setup_environment_roadmap.md"

    def test_parse_markdown_with_tasks(self):
        project = parse_markdown(
            "tests/fixtures/databricks_setup_environment_roadmap.md"
        )
        total_tasks = sum(len(phase.tasks) for phase in project.phases)
        assert total_tasks > 0

    def test_parse_markdown_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_markdown("nonexistent.md")

    def test_parse_markdown_field_aliases(self, tmp_path):
        content = """# Title
# 1. Phase
## 1.1 Task
**Attività**: Do this
**Verifica**: Check this
**Output atteso**: Expected result
**Done quando**: When complete
"""
        path = tmp_path / "test.md"
        path.write_text(content, encoding="utf-8")

        project = parse_markdown(str(path))
        task = project.phases[0].tasks[0]

        assert "Do this" in task.activities
        assert "Check this" in task.verification
        assert "Expected result" in task.expected_output
        assert "When complete" in task.done_when

    def test_parse_markdown_multiple_phases(self, tmp_path):
        content = """# Title
# 1. Phase One
## 1.1 Task One
- Activity
# 2. Phase Two
## 2.1 Task Two
- Activity
"""
        path = tmp_path / "multi.md"
        path.write_text(content, encoding="utf-8")

        project = parse_markdown(str(path))
        assert len(project.phases) == 2
        assert project.phases[0].title.startswith("1.")
        assert project.phases[1].title.startswith("2.")
