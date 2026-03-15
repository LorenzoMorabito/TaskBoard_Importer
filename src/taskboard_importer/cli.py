"""CLI entry point and command handlers.

Supports:
- init-project: Initialize workspace
- import-roadmap: Run import pipeline
- bootstrap-github: Setup GitHub integration
"""

import argparse
import os
import sys
from typing import Optional

from .application import bootstrap_github, import_roadmap, init_workspace
from .infrastructure.workspace import load_project_config
from .presentation import render_preview


def _resolve_project_path(project_path: str, rel: str) -> str:
    """Resolve path relative to project root."""
    return os.path.abspath(os.path.join(project_path, rel))


def _cmd_init_project(args: argparse.Namespace) -> int:
    """Handler for init-project command."""
    try:
        init_workspace(
            project_path=args.path,
            title=args.title,
            template_path=args.template_path,
            repo_owner=args.repo_owner,
            repo_name=args.repo_name,
            project_number=args.project_number,
        )
        print(f"✓ Project initialized at {args.path}")
        return 0
    except Exception as e:
        print(f"✗ Failed to initialize project: {e}", file=sys.stderr)
        return 1


def _cmd_import_roadmap(args: argparse.Namespace) -> int:
    """Handler for import-roadmap command."""
    try:
        # Load project config
        config = load_project_config(args.project)
        paths = config.get("paths", {})

        roadmap_path = _resolve_project_path(
            args.project, paths.get("roadmap", "roadmap/roadmap.md")
        )
        outputs_dir = _resolve_project_path(
            args.project, paths.get("outputs", "outputs")
        )

        if not os.path.exists(roadmap_path):
            print(f"✗ Roadmap not found: {roadmap_path}", file=sys.stderr)
            return 1

        # GitHub config from file or environment
        github_config = config.get("github", {})
        repo_owner = (
            args.repo_owner
            or github_config.get("repo_owner")
            or os.getenv("REPO_OWNER")
        )
        repo_name = (
            args.repo_name
            or github_config.get("repo_name")
            or os.getenv("REPO_NAME")
        )
        project_number = (
            args.project_number
            or github_config.get("project_number")
            or os.getenv("PROJECT_NUMBER")
        )
        default_status = args.default_status or os.getenv("DEFAULT_STATUS", "Backlog")

        output_json = os.path.join(outputs_dir, "import.json")
        manifest_json = os.path.join(outputs_dir, "manifest.json")

        # Run import pipeline
        project, results, import_run = import_roadmap(
            input_path=roadmap_path,
            output_json=output_json,
            manifest_json=manifest_json,
            previous_manifest=args.previous_manifest,
            dedupe_policy=args.dedupe_policy,
            publish_to_github=False,  # CLI handles publishing
            repo_owner=repo_owner,
            repo_name=repo_name,
            default_status=default_status,
            dry_run=args.dry_run,
        )

        # Display preview
        print(render_preview(project))

        # Summary
        print(f"✓ Import completed")
        print(f"  Normalized JSON: {output_json}")
        print(f"  Manifest: {manifest_json}")
        print(f"  Results: {len(results)} decisions")

        return 0

    except Exception as e:
        print(f"✗ Import failed: {e}", file=sys.stderr)
        return 1


def _cmd_bootstrap_github(args: argparse.Namespace) -> int:
    """Handler for bootstrap-github command."""
    try:
        config = load_project_config(args.project)
        github_config = config.get("github", {})

        repo_owner = (
            args.repo_owner
            or github_config.get("repo_owner")
            or os.getenv("REPO_OWNER")
        )
        repo_name = (
            args.repo_name
            or github_config.get("repo_name")
            or os.getenv("REPO_NAME")
        )
        token = args.token or os.getenv("GITHUB_TOKEN")

        if not repo_owner or not repo_name or not token:
            print(
                "✗ Missing repo_owner, repo_name, or GITHUB_TOKEN", file=sys.stderr
            )
            return 1

        bootstrap_github(
            token=token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            create_labels=args.labels,
        )

        print(f"✓ GitHub bootstrap completed for {repo_owner}/{repo_name}")
        return 0

    except Exception as e:
        print(f"✗ Bootstrap failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Taskboard Importer - Markdown to GitHub Tasks"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init-project
    init_parser = subparsers.add_parser(
        "init-project", help="Initialize new project workspace"
    )
    init_parser.add_argument("--path", required=True, help="Project path")
    init_parser.add_argument("--title", required=True, help="Project title")
    init_parser.add_argument(
        "--template-path", default=None, help="Template directory to copy"
    )
    init_parser.add_argument("--repo-owner", default=None, help="GitHub repo owner")
    init_parser.add_argument("--repo-name", default=None, help="GitHub repo name")
    init_parser.add_argument("--project-number", type=int, default=None, help="GitHub project number")
    init_parser.set_defaults(func=_cmd_init_project)

    # import-roadmap
    import_parser = subparsers.add_parser(
        "import-roadmap", help="Import roadmap Markdown file"
    )
    import_parser.add_argument("--project", required=True, help="Project path")
    import_parser.add_argument(
        "--previous-manifest", default=None, help="Previous manifest for deduplication"
    )
    import_parser.add_argument(
        "--dedupe-policy",
        default="skip",
        choices=["skip", "create", "update"],
        help="Deduplication policy",
    )
    import_parser.add_argument("--repo-owner", default=None, help="GitHub repo owner")
    import_parser.add_argument("--repo-name", default=None, help="GitHub repo name")
    import_parser.add_argument(
        "--default-status", default=None, help="Default task status"
    )
    import_parser.add_argument(
        "--dry-run", action="store_true", help="Preview only, don't publish"
    )
    import_parser.set_defaults(func=_cmd_import_roadmap)

    # bootstrap-github
    bootstrap_parser = subparsers.add_parser(
        "bootstrap-github", help="Bootstrap GitHub repository"
    )
    bootstrap_parser.add_argument("--project", required=True, help="Project path")
    bootstrap_parser.add_argument("--repo-owner", default=None, help="GitHub repo owner")
    bootstrap_parser.add_argument("--repo-name", default=None, help="GitHub repo name")
    bootstrap_parser.add_argument("--token", default=None, help="GitHub token")
    bootstrap_parser.add_argument(
        "--labels", nargs="*", default=None, help="Labels to create"
    )
    bootstrap_parser.set_defaults(func=_cmd_bootstrap_github)

    # Parse args
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
