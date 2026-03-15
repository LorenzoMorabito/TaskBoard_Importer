"""Markdown roadmap parsing into domain models.

Parses structured Markdown roadmaps into tasks, phases, and projects.
Supports field aliases in Italian and English.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from ..domain import Phase, ProjectImport, Task, utc_now_iso
from .markdown_reader import compute_file_hash, read_markdown_file


# Regex patterns for Markdown structures
LIST_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
ORDERED_BULLET_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
HORIZONTAL_RULE_RE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
NUM_PREFIX_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\b")
H1_RE = re.compile(r"^#\s+(.*)$")
H2_RE = re.compile(r"^##\s+(.*)$")

# Field aliases (Italian and English)
FIELD_ALIASES = {
    "attivita": "activities",
    "attività": "activities",
    "attivita'": "activities",
    "attività principali": "activities",
    "verifica": "verification",
    "output atteso": "expected_output",
    "done quando": "done_when",
    "definition of done": "done_when",
    "tracking": "tracking_template",
    "stato": "initial_status",
}


@dataclass
class ParsedTaskBuffer:
    """Temporary buffer for accumulating task data during parsing."""

    title: str
    section_ref: str
    phase_id: str
    activities: List[str] = field(default_factory=list)
    verification: List[str] = field(default_factory=list)
    expected_output_lines: List[str] = field(default_factory=list)
    done_when_lines: List[str] = field(default_factory=list)
    tracking_lines: List[str] = field(default_factory=list)
    initial_status_lines: List[str] = field(default_factory=list)

    def to_task(self) -> Task:
        """Convert buffer to Task domain model."""
        return Task(
            task_id=self.section_ref,
            phase_id=self.phase_id,
            section_ref=self.section_ref,
            title=self.title.strip(),
            activities=[s.strip() for s in self.activities if s.strip()],
            verification=[s.strip() for s in self.verification if s.strip()],
            expected_output="\n".join(
                s.strip() for s in self.expected_output_lines if s.strip()
            ),
            done_when="\n".join(
                s.strip() for s in self.done_when_lines if s.strip()
            ),
            tracking_template="\n".join(
                s.strip() for s in self.tracking_lines if s.strip()
            ),
            initial_status=" ".join(
                s.strip() for s in self.initial_status_lines if s.strip()
            ),
        )


def _extract_numeric_prefix(text: str) -> Optional[str]:
    """Extract numeric prefix from text (e.g., '1.2' from '1.2 Title')."""
    match = NUM_PREFIX_RE.match(text.strip())
    return match.group(1) if match else None


def _strip_inline_markdown(text: str) -> str:
    """Remove inline Markdown formatting from text."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[*_]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_field_label_and_rest(text: str) -> tuple[Optional[str], str]:
    """Extract field label and remaining content from line.
    
    Supports aliases like 'attività:' or 'activities - description'
    """
    cleaned = _strip_inline_markdown(text)
    lowered = cleaned.lower()

    for alias, field_name in FIELD_ALIASES.items():
        if lowered == alias:
            return field_name, ""

        for separator in (":", " - ", " – ", " — "):
            prefix = f"{alias}{separator}"
            if lowered.startswith(prefix):
                return field_name, cleaned[len(alias) + len(separator) :].strip()

    return None, ""


def _append_to_field(
    task: ParsedTaskBuffer, field_name: Optional[str], text: str
) -> None:
    """Append text to appropriate field in task buffer."""
    value = text.strip()
    if not value:
        return

    if field_name == "verification":
        task.verification.append(value)
    elif field_name == "expected_output":
        task.expected_output_lines.append(value)
    elif field_name == "done_when":
        task.done_when_lines.append(value)
    elif field_name == "tracking_template":
        task.tracking_lines.append(value)
    elif field_name == "initial_status":
        task.initial_status_lines.append(value)
    else:
        task.activities.append(value)


def parse_markdown(path: str) -> ProjectImport:
    """Parse a Markdown roadmap file into a ProjectImport.
    
    Extracts:
    - Project title (H1)
    - Phases (H2 sections)
    - Tasks with fields (activities, verification, expected_output, done_when, etc.)
    
    Args:
        path: Path to Markdown roadmap file
        
    Returns:
        ProjectImport with parsed phases and tasks
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    lines = read_markdown_file(path)
    source_hash = compute_file_hash(path)

    # Extract title
    doc_title: Optional[str] = None
    h1_positions = []

    for idx, line in enumerate(lines):
        match = H1_RE.match(line.strip())
        if match:
            h1_text = match.group(1).strip()
            h1_positions.append((idx, h1_text, _extract_numeric_prefix(h1_text)))

    # Prefer numeric-prefixed H1 as structure title
    if len(h1_positions) >= 2:
        first = h1_positions[0]
        second = h1_positions[1]
        if first[2] is None and second[2] is not None:
            doc_title = first[1]

    # Fall back to first H1 or filename
    if doc_title is None:
        for line in lines:
            if line.strip():
                match = H1_RE.match(line.strip())
                if match:
                    doc_title = match.group(1).strip()
                else:
                    doc_title = line.strip()
                break

    if doc_title is None:
        doc_title = os.path.splitext(os.path.basename(path))[0]

    # Parse structure
    phases: List[Phase] = []
    current_phase: Optional[Phase] = None
    current_task: Optional[ParsedTaskBuffer] = None
    current_field: Optional[str] = None
    phase_counter = 0
    preamble_lines: List[str] = []
    seen_numbered_phase = False

    def flush_task() -> None:
        nonlocal current_task
        if current_task and current_phase:
            current_phase.tasks.append(current_task.to_task())
        current_task = None

    def flush_phase() -> None:
        nonlocal current_phase
        if current_phase:
            phases.append(current_phase)
        current_phase = None

    for line in lines:
        stripped = line.strip()
        if not stripped or HORIZONTAL_RULE_RE.match(stripped):
            continue

        # Process H1 (project/section title)
        h1_match = H1_RE.match(stripped)
        if h1_match:
            flush_task()
            flush_phase()

            h1_text = h1_match.group(1).strip()
            numeric_prefix = _extract_numeric_prefix(h1_text)

            # Skip document title H1
            if doc_title and h1_text == doc_title and numeric_prefix is None:
                current_phase = None
                current_field = None
                continue

            phase_counter += 1
            current_phase = Phase(
                phase_id=numeric_prefix or str(phase_counter),
                order=phase_counter,
                title=h1_text,
                summary="",
            )
            if numeric_prefix:
                seen_numbered_phase = True
            current_field = None
            continue

        # Process H2 (task/section header)
        h2_match = H2_RE.match(stripped)
        if h2_match:
            flush_task()
            h2_text = h2_match.group(1).strip()

            # Preamble text before any H2
            if current_phase is None and not seen_numbered_phase:
                preamble_lines.append(h2_text)
                current_field = None
                continue

            # Create phase if needed
            if current_phase is None:
                phase_counter += 1
                current_phase = Phase(
                    phase_id=str(phase_counter),
                    order=phase_counter,
                    title=f"Phase {phase_counter}",
                    summary="",
                )

            # Create task buffer
            section_ref = _extract_numeric_prefix(h2_text) or f"{current_phase.phase_id}.{len(current_phase.tasks) + 1}"
            current_task = ParsedTaskBuffer(
                title=h2_text,
                section_ref=section_ref,
                phase_id=current_phase.phase_id,
            )
            current_field = None
            continue

        # Content lines (between headers)
        if current_task is None:
            if current_phase:
                if current_phase.summary:
                    current_phase.summary += "\n" + stripped
                else:
                    current_phase.summary = stripped
            elif not seen_numbered_phase:
                preamble_lines.append(stripped)
            continue

        # Try to extract field label
        field_label, field_inline_value = _extract_field_label_and_rest(stripped)
        if field_label:
            current_field = field_label
            if field_inline_value:
                _append_to_field(current_task, current_field, field_inline_value)
            continue

        # Process list items
        list_match = LIST_BULLET_RE.match(stripped) or ORDERED_BULLET_RE.match(
            stripped
        )
        if list_match:
            _append_to_field(current_task, current_field, list_match.group(1).strip())
            continue

        # Add as content to current field
        _append_to_field(current_task, current_field, stripped)

    flush_task()
    flush_phase()

    return ProjectImport(
        source_file=path,
        source_hash=source_hash,
        title=doc_title,
        imported_at=utc_now_iso(),
        summary="\n".join(preamble_lines).strip(),
        phases=phases,
    )
