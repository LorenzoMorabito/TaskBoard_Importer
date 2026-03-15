"""Template loading and management."""

import os
from typing import Optional


def find_template(template_name: str, search_paths: Optional[list[str]] = None) -> Optional[str]:
    """Find template directory by name.
    
    Args:
        template_name: Template name (e.g., "standard")
        search_paths: List of paths to search in
        
    Returns:
        Path to template directory or None if not found
    """
    if search_paths is None:
        search_paths = []

    for search_path in search_paths:
        template_path = os.path.join(search_path, template_name)
        if os.path.isdir(template_path):
            return template_path

    return None


def list_templates(templates_dir: str) -> list[str]:
    """List available templates in directory.
    
    Args:
        templates_dir: Directory containing templates
        
    Returns:
        List of template names
    """
    if not os.path.isdir(templates_dir):
        return []

    templates = []
    for item in os.listdir(templates_dir):
        item_path = os.path.join(templates_dir, item)
        if os.path.isdir(item_path):
            templates.append(item)

    return sorted(templates)


def get_template_file(
    template_dir: str, relative_path: str
) -> Optional[str]:
    """Get path to file within template.
    
    Args:
        template_dir: Template directory
        relative_path: Path relative to template
        
    Returns:
        Full path if file exists, None otherwise
    """
    full_path = os.path.join(template_dir, relative_path)
    if os.path.exists(full_path):
        return full_path
    return None
