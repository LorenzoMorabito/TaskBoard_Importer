from __future__ import annotations

import os
import re
from typing import Optional

from .schema import ProjectImport, Task
from .dedupe import compute_task_hash


def _fallback_title(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


_CHECKLIST_RE = re.compile(r"^\s*[-*+]\s+\[ \]\s+")


def _has_checklist(items: list[str]) -> bool:
    return sum(1 for line in items if _CHECKLIST_RE.match(line)) >= 3


def _has_table(items: list[str]) -> bool:
    has_row = any(line.strip().startswith("|") and "|" in line.strip()[1:] for line in items)
    has_sep = any("|---" in line.replace(" ", "") for line in items)
    return has_row and has_sep


def _classify_task(task: Task, phase_title: str) -> None:
    phase_lower = phase_title.lower()
    title_lower = task.title.lower()

    if _has_table(task.activities):
        task.task_type = "status_register"
        task.publish_policy = "publish_as_note"
        task.content_kind = "table"
        return

    if "checklist" in title_lower or "checklist" in phase_lower:
        task.task_type = "checklist"
        task.publish_policy = "publish_as_doc_issue"
        task.content_kind = "list"
        return

    if _has_checklist(task.activities):
        task.task_type = "checklist"
        task.publish_policy = "publish_as_doc_issue"
        task.content_kind = "list"
        return

    doc_hints = [
        "best practice",
        "errori comuni",
        "stato attuale",
        "registro",
        "checklist",
        "criterio finale",
    ]
    if (
        not task.verification
        and not task.expected_output.strip()
        and not task.done_when.strip()
        and any(hint in title_lower or hint in phase_lower for hint in doc_hints)
    ):
        task.task_type = "documentation"
        task.publish_policy = "publish_as_note"
        task.content_kind = "list" if task.activities else "mixed"
        return

    if task.verification or task.expected_output.strip() or task.done_when.strip():
        task.task_type = "operational_task"
        task.publish_policy = "publish_as_issue"
        task.content_kind = "list" if task.activities else "mixed"
        return

    task.task_type = "documentation"
    task.publish_policy = "publish_as_note"
    task.content_kind = "list" if task.activities else "mixed"


def normalize_project(project: ProjectImport, default_status: str = "Backlog") -> ProjectImport:
    if not project.title:
        project.title = _fallback_title(project.source_file)

    for phase_index, phase in enumerate(project.phases, start=1):
        if not phase.phase_id:
            phase.phase_id = str(phase_index)
        phase.order = phase_index
        if not phase.title:
            phase.title = f"Phase {phase_index}"

        for task_index, task in enumerate(phase.tasks, start=1):
            if not task.task_id:
                task.task_id = f"{phase.phase_id}.{task_index}"
            if not task.section_ref:
                task.section_ref = task.task_id
            task.phase_id = phase.phase_id
            if not task.initial_status:
                task.initial_status = default_status
            if not task.tracking_template:
                task.tracking_template = "N/A"
            _classify_task(task, phase.title)
            task.content_hash = compute_task_hash(task)

    return project
