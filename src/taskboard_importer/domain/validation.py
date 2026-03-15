"""Domain validation and business rules."""

from __future__ import annotations

from typing import List

from .project_spec import ProjectImport


class ValidationError(Exception):
    """Raised when domain validation fails."""

    pass


def validate_project(project: ProjectImport) -> List[str]:
    """Validate project structure and content.
    
    Args:
        project: ProjectImport to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []

    # Check project level
    if not project.title:
        errors.append("Project title is required.")
    if not project.phases:
        errors.append("At least one phase is required.")

    # Check phases
    for phase in project.phases:
        if not phase.title:
            errors.append(f"Phase {phase.phase_id} title is required.")

        # Phase must have tasks or summary
        if not phase.tasks:
            if not (phase.summary or "").strip():
                errors.append(
                    f"Phase {phase.phase_id} has no tasks or summary."
                )

        # Check tasks
        for task in phase.tasks:
            if not task.title:
                errors.append(
                    f"Task in phase {phase.phase_id} missing title."
                )
            if not task.section_ref:
                errors.append(
                    f"Task '{task.title}' missing section_ref."
                )

    return errors


def raise_if_invalid(project: ProjectImport) -> None:
    """Raise ValidationError if project is invalid.
    
    Args:
        project: ProjectImport to validate
        
    Raises:
        ValidationError: If validation fails
    """
    errors = validate_project(project)
    if errors:
        raise ValidationError("\n".join(errors))
