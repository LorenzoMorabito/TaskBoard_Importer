# Contributing to TaskBoard Importer

## Project Structure (New Modular Architecture)

TaskBoard Importer is organized in 7 clean domains:

```
src/taskboard_importer/

├── domain/                 Core business entities and validation
│   ├── project_spec.py    Task, Phase, ProjectImport models
│   ├── import_run.py      ImportRun, PublishResult models
│   ├── validation.py      Business rule validation
│   └── identifiers.py     ID generation utilities

├── parsing/               Parse Markdown → Domain models
│   ├── markdown_reader.py File I/O and hashing
│   ├── roadmap_parser.py  Markdown → ProjectImport
│   └── source_mapping.py  Line-level source traceability

├── policies/              Task classification and publish rules
│   ├── classification.py  Determine task_type and publish_policy
│   └── publish_rules.py   Policy enum and utility functions

├── sync/                  Deduplication and manifest management
│   ├── fingerprints.py    SHA256 content hashing
│   ├── manifest_store.py  Load/save manifest JSON
│   ├── sync_planner.py    Dedupe planning (skip/create/update)
│   └── drift_report.py    Version comparison and drift detection

├── infrastructure/        External integrations
│   ├── github/           GitHub API clients
│   │   ├── client.py     Base HTTP client
│   │   ├── issues.py     Issues API
│   │   ├── labels.py     Labels API
│   │   └── projects_v2.py Projects GraphQL
│   │
│   └── workspace/        Project filesystem management
│       ├── scaffold.py   Create project structure
│       ├── project_config.py Load project config
│       └── template_loader.py Template management

├── application/           Complete pipelines
│   ├── import_roadmap.py Full pipeline orchestrator
│   ├── init_workspace.py Workspace initialization
│   └── bootstrap_github.py GitHub setup

├── presentation/          CLI and UX
│   ├── cli.py            Command-line interface
│   └── preview.py        Terminal preview rendering

└── __init__.py            Public API exports
```

## Development Guidelines

### 1. Adding a Feature

**Step 1: Define in Domain Layer**
```python
# domain/project_spec.py or helpers
@dataclass
class MyEntity:
    """Your new entity."""
    field1: str
    field2: Optional[int] = None
```

**Step 2: Implement Logic in Appropriate Layer**
- **Parsing:** If reading from Markdown → parsing module
- **Transformation:** If transforming/classifying → policies module
- **Persistence:** If storing/loading → sync module
- **GitHub:** If integrating with GitHub → infrastructure/github

**Step 3: Expose in Application Orchestrator**
```python
# application/import_roadmap.py
def import_roadmap(...):
    # Use your new feature
    result = my_new_feature(project)
```

**Step 4: Add Tests**
- Unit tests: `tests/test_<module>.py`
- Integration: `tests/test_<concern>.py`

**Step 5: Update __init__.py if Public**
```python
# __init__.py
from .policies import my_new_feature
__all__ = [..., "my_new_feature"]
```

### 2. Modifying an Existing Module

1. **Always check reverse-dependencies** before changing function signatures
2. **Run full test suite:**
   ```bash
   pytest tests/ -v
   ```
3. **Update affected imports** in application orchestrators
4. **Update tests** if behavior changes
5. **Update docstrings** and comments

### 3. Adding Tests

New tests should:
- Be placed in `tests/test_<module>.py`
- Follow the existing pattern (class-based grouping)
- Test one concern per test
- Use fixtures from `conftest.py`
- Have descriptive names

Example:
```python
import pytest
from taskboard_importer.parsing import parse_markdown

class TestMyFeature:
    def test_basic_case(self):
        # Arrange
        # Act
        # Assert
        pass
    
    def test_edge_case(self):
        pass
```

### 4. Code Style

- **Python:** PEP 8 (handled by autopep8 / black)
- **Docstrings:** Google-style
- **Type hints:** Use where beneficial
- **Imports:** `from module import X` (avoid wildcards)

### 5. Common Tasks

#### Run all tests
```bash
pytest tests/ -v
```

#### Run specific test module
```bash
pytest tests/test_parsing.py -v
```

#### Run with coverage
```bash
pytest tests/ --cov=src/taskboard_importer --cov-report=html
```

#### Test a real roadmap locally
```bash
python -c "
from taskboard_importer.application import import_roadmap

project, results, run = import_roadmap(
    input_path='path/to/roadmap.md',
    output_json='outputs/test_import.json',
    manifest_json='outputs/test_manifest.json',
    dry_run=True
)
print(f'Processed {sum(len(p.tasks) for p in project.phases)} tasks')
"
```

### 6. Before Submitting a PR

1. ✅ Run `pytest tests/ -v` - all tests pass
2. ✅ No imports from legacy modules (cli, schema, dedupe, etc.)
3. ✅ Docstrings updated
4. ✅ `__init__.py` exports updated (if public)
5. ✅ No circular dependencies
6. ✅ Commit message describes intent

## Architecture Decision Records

See `docs/decisions.md` for past decisions.

When proposing architectural changes:
1. **Document the decision** in a new ADR
2. **Explain rationale** (why, not just what)
3. **Note trade-offs** (pros/cons)
4. **Link to related decisions**
5. **Get team feedback** before implementation

## Module Boundaries

### domain ↔ Other
- **Can be imported by:** All other modules
- **Should import from:** Nothing (foundational)
- **Responsibility:** Define entities, validation, ID generation

### parsing ↔ Other
- **Can import from:** domain
- **Should NOT import from:** policies, sync, infrastructure, application, presentation
- **Responsibility:** Read files, extract structure, map to domain

### policies ↔ Other
- **Can import from:** domain, parsing (for analysis)
- **Should NOT import from:** sync, infrastructure, application
- **Responsibility:** Classify content, assign policies

### sync ↔ Other
- **Can import from:** domain, policies
- **Should NOT import from:** parsing, infrastructure, application
- **Responsibility:** Hash, fingerprint, dedupe, manifest I/O

### infrastructure ↔ Other
- **Can import from:** domain
- **Should NOT import from:** parsing, policies, sync (except for reference)
- **Responsibility:** External APIs and filesystem

### application ↔ Other
- **Can import from:** All modules
- **Should NOT be imported from:** Anywhere except CLI/tests
- **Responsibility:** Orchestrate complete workflows

### presentation ↔ Other
- **Can import from:** All modules (for UI rendering)
- **Entry point** for CLI

---

## Questions?

- Check existing code in the module for patterns
- Look at existing tests for examples
- Review `docs/MIGRATION.md` for legacy→modern mappings
- Check `docs/architecture.md` for detailed module descriptions
