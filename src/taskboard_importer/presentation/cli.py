"""Command-line interface for TaskBoard Importer.

Delegates to application layer orchestrators.
"""

import argparse
import sys
from pathlib import Path

from taskboard_importer.application import (
    bootstrap_github,
    import_roadmap,
    init_workspace,
)
from taskboard_importer.infrastructure.workspace import load_project_config


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="TaskBoard Importer - Markdown roadmap to GitHub Tasks",
        prog="taskboard",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init-project command
    init_parser = subparsers.add_parser(
        "init-project", help="Initialize a new project workspace"
    )
    init_parser.add_argument("--path", required=True, help="Project path")
    init_parser.add_argument("--title", required=True, help="Project title")
    init_parser.add_argument(
        "--repo-owner", required=True, help="GitHub repository owner"
    )
    init_parser.add_argument(
        "--repo-name", required=True, help="GitHub repository name"
    )

    # import-roadmap command
    import_parser = subparsers.add_parser(
        "import-roadmap", help="Import roadmap Markdown to tasks"
    )
    import_parser.add_argument("--project", required=True, help="Project path")
    import_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    import_parser.add_argument(
        "--dedupe-policy",
        choices=["skip", "create", "update"],
        default="skip",
        help="Deduplication policy",
    )
    import_parser.add_argument(
        "--previous-manifest", help="Path to previous manifest.json"
    )

    # bootstrap-github command
    bootstrap_parser = subparsers.add_parser(
        "bootstrap-github", help="Bootstrap GitHub project"
    )
    bootstrap_parser.add_argument("--project", required=True, help="Project path")
    bootstrap_parser.add_argument(
        "--repo-owner", required=True, help="GitHub repository owner"
    )
    bootstrap_parser.add_argument(
        "--repo-name", required=True, help="GitHub repository name"
    )
    bootstrap_parser.add_argument("--token", help="GitHub token")
    bootstrap_parser.add_argument(
        "--project-number", type=int, help="GitHub project number"
    )

    args = parser.parse_args()

    if args.command == "init-project":
        return _cmd_init_project(args)
    elif args.command == "import-roadmap":
        return _cmd_import_roadmap(args)
    elif args.command == "bootstrap-github":
        return _cmd_bootstrap_github(args)
    else:
        parser.print_help()
        return 1


def _cmd_init_project(args):
    """Handle init-project command."""
    try:
        init_workspace(
            path=args.path,
            title=args.title,
            repo_owner=args.repo_owner,
            repo_name=args.repo_name,
        )
        print(f"✅ Project initialized at {args.path}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def _cmd_import_roadmap(args):
    """Handle import-roadmap command."""
    try:
        # Load project config
        config = load_project_config(args.project)

        # Prepare roadmap path
        roadmap_path = Path(args.project) / "roadmap" / "roadmap.md"
        if not roadmap_path.exists():
            print(f"❌ Roadmap file not found: {roadmap_path}", file=sys.stderr)
            return 1

        # Prepare output paths
        output_dir = Path(args.project) / "outputs"
        output_dir.mkdir(exist_ok=True)

        import_json = output_dir / "import.json"
        manifest_json = output_dir / "manifest.json"

        # Run import orchestrator
        project, results, run = import_roadmap(
            input_path=str(roadmap_path),
            output_json=str(import_json),
            manifest_json=str(manifest_json),
            previous_manifest=args.previous_manifest,
            dedupe_policy=args.dedupe_policy,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            print(f"✅ [DRY-RUN] Import complete: {len(results)} tasks processed")
        else:
            print(
                f"✅ Import complete: {len(results)} tasks published to GitHub"
            )
        print(f"📊 Imported: {import_json}")
        print(f"📋 Manifest: {manifest_json}")

        return 0
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Import failed: {e}", file=sys.stderr)
        return 1


def _cmd_bootstrap_github(args):
    """Handle bootstrap-github command."""
    try:
        # Load project config
        config = load_project_config(args.project)

        # Extract labels from config or use defaults
        labels = config.get("labels", [])
        if not labels:
            labels = ["Documentation", "Phase 1", "Phase 2"]

        # Run bootstrap
        bootstrap_github(
            repo_owner=args.repo_owner,
            repo_name=args.repo_name,
            labels=labels,
            token=args.token,
            project_number=args.project_number,
        )

        print(f"✅ GitHub project bootstrapped")
        return 0
    except Exception as e:
        print(f"❌ Bootstrap failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
