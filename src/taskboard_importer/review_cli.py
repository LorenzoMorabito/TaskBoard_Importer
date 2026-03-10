from __future__ import annotations

from typing import List

from .schema import ProjectImport


def render_preview(project: ProjectImport) -> str:
    lines: List[str] = []
    lines.append(f"Project: {project.title}")
    lines.append(f"Phases: {len(project.phases)}")
    lines.append("")

    for phase in project.phases:
        lines.append(f"[{phase.phase_id}] {phase.title}")
        for task in phase.tasks:
            lines.append(f"  - ({task.section_ref}) {task.title} | activities: {len(task.activities)} | verification: {len(task.verification)} | status: {task.initial_status}")
        lines.append("")

    return "\n".join(lines).strip()


def confirm_publish() -> bool:
    response = input("Publish to GitHub? (yes/no): ").strip().lower()
    return response in {"y", "yes"}
