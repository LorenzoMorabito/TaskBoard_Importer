from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_yaml(path: str, data: Dict[str, object]) -> None:
    lines = []

    def emit(key: str, value: object, indent: int) -> None:
        prefix = "  " * indent
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            for sub_key, sub_val in value.items():
                emit(sub_key, sub_val, indent + 1)
        else:
            if value is None:
                value_str = ""
            else:
                value_str = str(value)
            lines.append(f"{prefix}{key}: {value_str}")

    for k, v in data.items():
        emit(k, v, 0)

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def read_yaml(path: str) -> Dict[str, object]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    root: Dict[str, object] = {}
    stack = [(0, root)]

    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError("Invalid indentation in project.yaml")
        key_val = raw.strip().split(":", 1)
        key = key_val[0].strip()
        value = key_val[1].strip() if len(key_val) > 1 else ""

        while stack and indent < stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError("Invalid YAML structure")
        current = stack[-1][1]

        if value == "":
            new_map: Dict[str, object] = {}
            current[key] = new_map
            stack.append((indent + 2, new_map))
        else:
            current[key] = value

    return root


def ensure_dirs(*paths: str) -> None:
    for path in paths:
        os.makedirs(path, exist_ok=True)


def load_template(template_root: str, rel_path: str, fallback: str) -> str:
    template_path = os.path.join(template_root, rel_path)
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as handle:
            return handle.read()
    return fallback


def init_project(
    path: str,
    slug: str,
    title: str,
    owner: str,
    template_profile: str = "standard",
    description: str = "",
) -> str:
    project_id = str(uuid.uuid4())
    root = os.path.abspath(path)

    dirs = {
        "roadmap": os.path.join(root, "roadmap"),
        "docs": os.path.join(root, "docs"),
        "state": os.path.join(root, "state"),
        "outputs": os.path.join(root, "outputs"),
        "rules": os.path.join(root, "rules"),
        "attachments": os.path.join(root, "attachments"),
    }
    ensure_dirs(*dirs.values())

    template_root = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "templates", template_profile)
    template_root = os.path.abspath(template_root)

    project_yaml = {
        "project_id": project_id,
        "slug": slug,
        "title": title,
        "description": description,
        "owner": owner,
        "created_at": utc_now_iso(),
        "engine_version": "0.1.0",
        "workspace_version": "1",
        "github": {
            "repo_owner": "",
            "repo_name": "",
            "project_number": "",
        },
        "publishing": {
            "default_policy_profile": "standard",
        },
        "labels": {
            "default": "phase",
        },
        "templates": {
            "profile": template_profile,
        },
        "paths": {
            "roadmap": "roadmap/roadmap.md",
            "docs": "docs",
            "state": "state",
            "outputs": "outputs",
            "rules": "rules/publish_rules.yml",
            "attachments": "attachments",
        },
    }

    write_yaml(os.path.join(root, "project.yaml"), project_yaml)

    readme = load_template(
        template_root,
        "README.md",
        f"# {title}\n\nProject initialized by taskboard initializer.\n",
    )
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as handle:
        handle.write(readme)

    roadmap = load_template(template_root, "roadmap.md", f"# {title} Roadmap\n")
    with open(os.path.join(dirs["roadmap"], "roadmap.md"), "w", encoding="utf-8") as handle:
        handle.write(roadmap)

    for name in ["architecture.md", "decisions.md", "glossary.md"]:
        content = load_template(template_root, name, f"# {name.split('.')[0].title()}\n")
        with open(os.path.join(dirs["docs"], name), "w", encoding="utf-8") as handle:
            handle.write(content)

    for name in ["current_status.md", "backlog_notes.md", "risks.md"]:
        content = load_template(template_root, name, f"# {name.split('.')[0].replace('_', ' ').title()}\n")
        with open(os.path.join(dirs["state"], name), "w", encoding="utf-8") as handle:
            handle.write(content)

    rules = load_template(
        template_root,
        "publish_rules.yml",
        "# publish rules\nprofiles:\n  standard:\n    publish_as_issue: true\n",
    )
    with open(os.path.join(dirs["rules"], "publish_rules.yml"), "w", encoding="utf-8") as handle:
        handle.write(rules)

    return root


def get_project_config(project_path: str) -> Dict[str, object]:
    config_path = os.path.join(project_path, "project.yaml")
    return read_yaml(config_path)
