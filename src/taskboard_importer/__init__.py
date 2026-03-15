"""Taskboard Importer - Markdown roadmap to GitHub Tasks/Project importer.

New modular architecture:
- domain/: Core data models and business logic
- parsing/: Markdown parsing and source mapping
- policies/: Task classification and publishing rules
- sync/: Deduplication and manifest management
- infrastructure/: GitHub integration and workspace management
- application/: Orchestrators combining multiple modules
- presentation/: CLI and user interfaces
"""

# Domain exports
from .domain import (
    ImportRun,
    Phase,
    ProjectImport,
    PublishResult,
    Task,
    ValidationError,
    generate_phase_id,
    generate_run_id,
    generate_task_id,
    validate_project,
)

# Parsing exports
from .parsing import parse_markdown, read_markdown_file

# Policies exports
from .policies import classify_task, normalize_project

# Sync exports
from .sync import (
    DedupeDecision,
    compute_task_hash,
    detect_drift,
    load_manifest,
    load_manifest_details,
    plan_dedupe,
    save_manifest,
)

# Application exports
from .application import bootstrap_github, import_roadmap, init_workspace

# Infrastructure exports (expose via submodules)
from . import infrastructure

# Presentation exports
from .presentation import render_preview

__all__ = [
    # Domain
    "Task",
    "Phase",
    "ProjectImport",
    "PublishResult",
    "ImportRun",
    "ValidationError",
    "validate_project",
    "generate_task_id",
    "generate_phase_id",
    "generate_run_id",
    # Parsing
    "parse_markdown",
    "read_markdown_file",
    # Policies
    "classify_task",
    "normalize_project",
    # Sync
    "compute_task_hash",
    "load_manifest",
    "load_manifest_details",
    "save_manifest",
    "plan_dedupe",
    "DedupeDecision",
    "detect_drift",
    # Application
    "import_roadmap",
    "init_workspace",
    "bootstrap_github",
    # Infrastructure (submodules)
    "infrastructure",
    # Presentation
    "render_preview",
]

