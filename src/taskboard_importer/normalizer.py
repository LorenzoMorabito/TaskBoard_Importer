from __future__ import annotations

import os
from typing import Optional

from .schema import ProjectImport, Task
from .dedupe import compute_task_hash


def _fallback_title(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


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
            task.content_hash = compute_task_hash(task)

    return project
