# Integration Test Report

## Build

- Branch: `main`
- Commit SHA: `1bd7f3be9c6690a3dab572f9eac79c91e3c19a4d`
- Tag: `qa-ready-001`
- Date: `2026-03-16`
- Target repository: `LorenzoMorabito/TaskBoard_Importer_Sandbox`
- Target Project V2: `https://github.com/users/LorenzoMorabito/projects/2`

## Session Scope

Validated in sequence:

1. package installation
2. CLI verification
3. `init-project`
4. `import-roadmap --dry-run`
5. local output verification (`import.json`, `manifest.json`)
6. live publish with issue creation
7. controlled roadmap modification
8. rerun with previous manifest and `--dedupe-policy update`
9. issue update verification without unwanted duplication
10. Project V2 synchronization verification

## Commands Executed

```powershell
.\.venv\Scripts\python -m pip install -e .
```

```powershell
python -m taskboard_importer.presentation.cli --help
.\.venv\Scripts\taskboard.exe --help
```

```powershell
python -m taskboard_importer.presentation.cli init-project --path "outputs/qa-ready-001-session" --title "QA Ready Session" --repo-owner LorenzoMorabito --repo-name TaskBoard_Importer_Sandbox
```

```powershell
python -m taskboard_importer.presentation.cli import-roadmap --project "outputs/qa-ready-001-session" --dry-run
```

```powershell
.\.venv\Scripts\taskboard.exe bootstrap-github --project "outputs/qa-ready-001-session" --repo-owner LorenzoMorabito --repo-name TaskBoard_Importer_Sandbox --token $env:GITHUB_TOKEN --project-number 2
```

```powershell
.\.venv\Scripts\taskboard.exe import-roadmap --project "outputs/qa-ready-001-session" --repo-owner LorenzoMorabito --repo-name TaskBoard_Importer_Sandbox --token $env:GITHUB_TOKEN --project-number 2 --dedupe-policy create
```

```powershell
.\.venv\Scripts\taskboard.exe import-roadmap --project "outputs/qa-ready-001-session" --repo-owner LorenzoMorabito --repo-name TaskBoard_Importer_Sandbox --token $env:GITHUB_TOKEN --project-number 2 --dedupe-policy update --previous-manifest "outputs/qa-ready-001-session/outputs/manifest.json"
```

## Results

### Local Validation

- Package installation: PASSED
- CLI verification: PASSED
- Workspace initialization: PASSED
- Dry-run import: PASSED
- `import.json` generated: PASSED
- `manifest.json` generated: PASSED

Local dry-run summary:

- phases parsed: `16`
- tasks parsed: `37`
- `publish_as_issue`: `32`
- `publish_as_doc_issue`: `1`
- `publish_as_note`: `4`

### Live Publish Validation

Initial live publish (`--dedupe-policy create`):

- issues created: `32`
- deferred manifest-only doc issue: `1`
- manifest-only notes: `4`
- Project V2 synced items: `32`

Sample created issues:

- `#1` `[1.1] 1.1 Obiettivo del setup`
- `#2` `[1.2] 1.2 Inventario iniziale`
- `#3` `[2.1] 2.1 Accesso al workspace Databricks`

GitHub repository evidence:

- live issue count in sandbox repository: `32`

### Update Validation

Controlled change applied to roadmap:

- task `1.1`
- `Output atteso` changed from `Mini definizione di done del setup.` to `Mini definizione di done del setup con criteri operativi verificabili.`

Update rerun result:

- decisions: `1 update`, `36 skip`, `0 create`
- updated issue number: `#1`
- duplicate issue created: `NO`
- updated issue kept same Project V2 item id: `PVTI_lAHOB-5RC84BR4mWzgnicKQ`

Live verification:

- issue `#1` contains updated text: `YES`
- issue `#1` label preserved: `operational_task`

### Project V2 Validation

- project title: `TaskBoard Importer - QA Sandbox`
- issue items found in Project V2: `32`
- issue `#1` present in Project V2: `YES`
- Project V2 item id for issue `#1`: `PVTI_lAHOB-5RC84BR4mWzgnicKQ`

## Bugs / Notes

### Bug 1: CLI Unicode output on Windows shell

- Severity: medium
- Status: open
- Description: CLI output with emoji fails on some Windows console encodings unless `PYTHONIOENCODING=utf-8` is set.
- Impact: command execution succeeds, but standard console output can fail before normal completion in non-UTF-8 shells.

### Note 1: `taskboard` entrypoint availability

- Severity: low
- Status: expected environment behavior
- Description: `taskboard` is available through the virtual environment executable path (`.\.venv\Scripts\taskboard.exe`) after installation. It is not globally available unless the virtual environment is activated or its Scripts path is on `PATH`.

### Note 2: `publish_as_doc_issue`

- Severity: informational
- Status: known limitation
- Description: `publish_as_doc_issue` remains deferred in the manifest and is not published as an active GitHub issue.

## Final Assessment

Gate result: `PASSED WITH MINOR KNOWN ISSUES`

The integration gate validated successfully for:

- package installation
- canonical CLI
- workspace initialization
- dry-run generation
- live issue creation
- live issue update without unwanted duplication
- manifest reuse
- Project V2 synchronization

Recommended disposition:

- ready for QA/UAT progression
- track the Windows console Unicode output issue as a follow-up defect
