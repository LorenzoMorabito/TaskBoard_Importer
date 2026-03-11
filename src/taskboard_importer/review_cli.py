from __future__ import annotations

from typing import List

from .schema import ProjectImport


def render_preview(project: ProjectImport) -> str:
    lines: List[str] = []
    lines.append(f"Project: {project.title}")
    lines.append(f"Phases: {len(project.phases)}")
    if project.summary.strip():
        summary_lines = [line for line in project.summary.splitlines() if line.strip()]
        lines.append(f"Project summary lines: {len(summary_lines)}")
        for line in summary_lines:
            lines.append(f"  {line}")
    lines.append("")

    for phase in project.phases:
        lines.append(f"[{phase.phase_id}] {phase.title}")
        if not phase.tasks and phase.summary.strip():
            summary_lines = [line for line in phase.summary.splitlines() if line.strip()]
            lines.append(f"  summary-only phase | summary lines: {len(summary_lines)}")
            for line in summary_lines:
                lines.append(f"  {line}")
        for task in phase.tasks:
            lines.append(
                f"  - ({task.section_ref}) {task.title} | type: {task.task_type} | policy: {task.publish_policy} | "
                f"activities: {len(task.activities)} | verification: {len(task.verification)} | status: {task.initial_status}"
            )
        lines.append("")

    return "\n".join(lines).strip()


def confirm_publish() -> bool:
    response = input("Publish to GitHub? (yes/no): ").strip().lower()
    return response in {"y", "yes"}
