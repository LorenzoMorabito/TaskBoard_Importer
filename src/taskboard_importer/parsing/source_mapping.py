"""Source-to-domain mapping and traceback."""

from __future__ import annotations

from typing import Dict, Optional

from ..domain import Phase, ProjectImport, Task


class SourceMapping:
    """Tracks mapping between source lines and domain objects.
    
    Enables traceability from original Markdown to parsed entities.
    """

    def __init__(self):
        """Initialize source mapping."""
        self.task_to_lines: Dict[str, tuple[int, int]] = {}  # task_id -> (start_line, end_line)
        self.phase_to_lines: Dict[str, tuple[int, int]] = {}  # phase_id -> (start_line, end_line)

    def add_task_mapping(self, task_id: str, start_line: int, end_line: int) -> None:
        """Map task to its source lines.
        
        Args:
            task_id: Task identifier
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based)
        """
        self.task_to_lines[task_id] = (start_line, end_line)

    def add_phase_mapping(self, phase_id: str, start_line: int, end_line: int) -> None:
        """Map phase to its source lines.
        
        Args:
            phase_id: Phase identifier
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based)
        """
        self.phase_to_lines[phase_id] = (start_line, end_line)

    def get_task_lines(self, task_id: str) -> Optional[tuple[int, int]]:
        """Get source lines for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            (start_line, end_line) tuple or None if not found
        """
        return self.task_to_lines.get(task_id)

    def get_phase_lines(self, phase_id: str) -> Optional[tuple[int, int]]:
        """Get source lines for a phase.
        
        Args:
            phase_id: Phase identifier
            
        Returns:
            (start_line, end_line) tuple or None if not found
        """
        return self.phase_to_lines.get(phase_id)
