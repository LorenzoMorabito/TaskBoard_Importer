"""Project configuration loading."""

import json
import os
from typing import Any, Dict, Optional


def load_project_config(project_path: str) -> Dict[str, Any]:
    """Load project configuration from project.yaml or project.json.
    
    Args:
        project_path: Project root path
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If no config found
    """
    yaml_path = os.path.join(project_path, "project.yaml")
    json_path = os.path.join(project_path, "project.json")

    # Try YAML first
    if os.path.exists(yaml_path):
        try:
            import yaml
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except ImportError:
            pass

    # Try JSON
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)

    raise FileNotFoundError(f"No project config found in {project_path}")


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get nested value from config using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Path like "github.repo_owner"
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split(".")
    value = config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    return value if value is not None else default
