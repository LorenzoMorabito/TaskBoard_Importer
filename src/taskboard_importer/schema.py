from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Optional


@dataclass
class Task:
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

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class Phase:
    phase_id: str
    order: int
    title: str
    summary: str = ""
    dependencies: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["tasks"] = [task.to_dict() for task in self.tasks]
        return data


@dataclass
class ProjectImport:
    source_file: str
    source_hash: str
    title: str
    imported_at: str
    phases: List[Phase] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_file": self.source_file,
            "source_hash": self.source_hash,
            "title": self.title,
            "imported_at": self.imported_at,
            "phases": [phase.to_dict() for phase in self.phases],
        }


@dataclass
class PublishResult:
    task_id: str
    github_issue_number: Optional[int]
    project_item_id: Optional[str]
    publish_status: str
    action: str = ""
    phase_label: str = ""
    section_ref: str = ""
    matched_by: str = ""
    previous_hash: str = ""
    new_hash: str = ""
    updated_issue_number: Optional[int] = None
    project_sync_status: str = ""
    error_message: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class ImportRun:
    run_id: str
    actor: str
    source_version: str
    target_project: str
    result_summary: Dict[str, object]
    task_fingerprints: Dict[str, str]
    publish_results: List[PublishResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "run_id": self.run_id,
            "actor": self.actor,
            "source_version": self.source_version,
            "target_project": self.target_project,
            "result_summary": self.result_summary,
            "task_fingerprints": self.task_fingerprints,
            "publish_results": [result.to_dict() for result in self.publish_results],
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_project(project: ProjectImport) -> List[str]:
    errors: List[str] = []
    if not project.title:
        errors.append("Project title is required.")
    if not project.phases:
        errors.append("At least one phase is required.")
    for phase in project.phases:
        if not phase.title:
            errors.append(f"Phase {phase.phase_id} title is required.")
        if not phase.tasks:
            errors.append(f"Phase {phase.phase_id} has no tasks.")
        for task in phase.tasks:
            if not task.title:
                errors.append(f"Task in phase {phase.phase_id} missing title.")
            if not task.section_ref:
                errors.append(f"Task '{task.title}' missing section_ref.")
    return errors
