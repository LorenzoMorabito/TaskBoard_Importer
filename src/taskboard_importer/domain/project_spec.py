"""Project specification domain models.

Defines the core data structures for tasks, phases, and project imports.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Task:
    """Represents a single task item in a phase.
    
    Attributes:
        task_id: Unique identifier for the task
        phase_id: ID of the phase this task belongs to
        section_ref: Section reference for tracking
        title: Task title
        activities: List of activities to perform
        verification: Criteria for verification
        expected_output: Description of expected output
        done_when: Conditions for task completion
        tracking_template: Template for tracking this task
        initial_status: Initial status in tracking system
        content_hash: SHA256 hash of task content for deduplication
        task_type: Classification (operational_task, checklist, documentation, status_register)
        publish_policy: Policy for publishing (publish_as_issue, publish_as_doc_issue, publish_as_note, skip)
        content_kind: Type of content (list, table, mixed)
    """

    task_id: str
    phase_id: str
    section_ref: str
    title: str
    activities: List[str] = field(default_factory=list)
    verification: List[str] = field(default_factory=list)
    expected_output: str = ""
    done_when: str = ""
    tracking_template: str = ""
    initial_status: str = ""
    content_hash: str = ""
    task_type: str = ""
    publish_policy: str = ""
    content_kind: str = ""

    def to_dict(self) -> Dict[str, object]:
        """Convert task to dictionary representation."""
        return asdict(self)


@dataclass
class Phase:
    """Represents a phase/section of tasks.
    
    Attributes:
        phase_id: Unique identifier for the phase
        order: Sequential order in project
        title: Phase title
        summary: Phase summary description
        dependencies: List of dependent phase IDs
        tasks: List of tasks in this phase
    """

    phase_id: str
    order: int
    title: str
    summary: str = ""
    dependencies: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Convert phase to dictionary representation."""
        data = asdict(self)
        data["tasks"] = [task.to_dict() for task in self.tasks]
        return data


@dataclass
class ProjectImport:
    """Represents a complete project roadmap import.
    
    Attributes:
        source_file: Path to source markdown file
        source_hash: SHA256 hash of source file content
        title: Project title
        imported_at: ISO format timestamp of import
        summary: Project summary description
        phases: List of phases in project
    """

    source_file: str
    source_hash: str
    title: str
    imported_at: str
    summary: str = ""
    phases: List[Phase] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Convert project to dictionary representation."""
        return {
            "source_file": self.source_file,
            "source_hash": self.source_hash,
            "title": self.title,
            "imported_at": self.imported_at,
            "summary": self.summary,
            "phases": [phase.to_dict() for phase in self.phases],
        }


def utc_now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()
