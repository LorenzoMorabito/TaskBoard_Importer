"""Identifier generation and management."""

import uuid
from datetime import datetime, timezone


def generate_task_id(phase_id: str, task_index: int) -> str:
    """Generate a task ID.
    
    Args:
        phase_id: ID of parent phase
        task_index: Index of task in phase (1-based)
        
    Returns:
        Task ID in format "phase_id.task_index"
    """
    return f"{phase_id}.{task_index}"


def generate_phase_id(phase_index: int) -> str:
    """Generate a phase ID.
    
    Args:
        phase_index: Index of phase (1-based)
        
    Returns:
        Phase ID
    """
    return str(phase_index)


def generate_run_id() -> str:
    """Generate a unique run ID.
    
    Returns:
        Run ID combining timestamp and UUID
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_suffix = str(uuid.uuid4())[:8]
    return f"run_{timestamp}_{unique_suffix}"
