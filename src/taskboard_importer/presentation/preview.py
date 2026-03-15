"""Preview rendering for CLI display."""

from typing import List

from ..domain import ProjectImport, Task


def render_preview(project: ProjectImport) -> str:
    """Render project preview for terminal display.
    
    Args:
        project: Project to preview
        
    Returns:
        Formatted preview string
    """
    lines: List[str] = []

    lines.append("=" * 80)
    lines.append(f"PROJECT: {project.title}")
    lines.append("=" * 80)

    if project.summary:
        lines.append(f"\nSummary: {project.summary}\n")

    lines.append(f"Source: {project.source_file}")
    lines.append(f"Phases: {len(project.phases)}")

    total_tasks = sum(len(phase.tasks) for phase in project.phases)
    lines.append(f"Total Tasks: {total_tasks}\n")

    # Phase summaries
    for phase in project.phases:
        lines.append(f"[{phase.phase_id}] {phase.title}")
        if phase.summary:
            lines.append(f"    Summary: {phase.summary[:100]}...")
        lines.append(f"    Tasks: {len(phase.tasks)}")

        # Task previews
        for task in phase.tasks:
            policy = task.publish_policy or "unknown"
            task_type = task.task_type or "unknown"
            lines.append(
                f"      - [{task.task_id}] {task.title} "
                f"(type: {task_type}, policy: {policy})"
            )

            if task.activities:
                lines.append(f"        Activities: {len(task.activities)} items")
            if task.verification:
                lines.append(f"        Verification: {len(task.verification)} criteria")

        lines.append("")

    return "\n".join(lines)


def render_decision_summary(decisions: List) -> str:
    """Render summary of deduplication decisions.
    
    Args:
        decisions: List of DedupeDecision objects
        
    Returns:
        Formatted summary
    """
    lines: List[str] = []

    create_count = len([d for d in decisions if d.action == "create"])
    update_count = len([d for d in decisions if d.action == "update"])
    skip_count = len([d for d in decisions if d.action == "skip"])

    lines.append("\n" + "=" * 80)
    lines.append("SYNC PLAN")
    lines.append("=" * 80)
    lines.append(f"Create: {create_count} new tasks")
    lines.append(f"Update: {update_count} changed tasks")
    lines.append(f"Skip:   {skip_count} unchanged tasks")
    lines.append(f"Total:  {len(decisions)} tasks")
    lines.append("")

    return "\n".join(lines)
