# Taskboard Importer

Sistema deterministico per trasformare roadmap Markdown strutturate in task normalizzati e pubblicarli su GitHub Issues + Projects.

## Funzionalita
- Parsing robusto di file Markdown strutturati
- Normalizzazione in JSON con schema stabile
- Preview e conferma human-in-the-loop
- Dry-run con output JSON e manifest
- Publish su GitHub Issues e, opzionalmente, Project V2
- Deduplica basata su `section_ref` + hash contenuti

## Struttura
- `src/taskboard_importer/`: core del sistema
- `tests/`: test e fixture
- `outputs/`: esempi di output
- `docs/`: note di architettura

## Esecuzione rapida
```bash
python -m taskboard_importer.run_import --input tests/fixtures/databricks_setup_environment_roadmap.md --dry-run
```

## Dedupe policy
- `skip`: salta task invariati rispetto al manifest precedente
- `create`: crea sempre nuove issue
- `update`: aggiorna issue esistenti se il contenuto e' cambiato

Esempio con update:
```bash
python -m taskboard_importer.run_import \
  --input tests/fixtures/databricks_setup_environment_roadmap.md \
  --previous-manifest outputs/sample_manifest.json \
  --dedupe-policy update
```

## Telemetria manifest
Il `result_summary` include anche i conteggi di sync Project V2:
- `project_sync_found`
- `project_sync_recovered`
- `project_sync_missing`
- `project_sync_failed`
- `project_sync_skipped`

## Pubblicazione su GitHub
Imposta le variabili ambiente o passa i parametri CLI:
- `GITHUB_TOKEN`
- `REPO_OWNER`
- `REPO_NAME`
- `PROJECT_NUMBER` (opzionale)
- `DEFAULT_STATUS` (opzionale)

Esempio:
```bash
python -m taskboard_importer.run_import \
  --input tests/fixtures/databricks_setup_environment_roadmap.md \
  --repo-owner <owner> --repo-name <repo> --project-number 1 \
  --default-status "Todo" --yes
```

## Note
- In assenza di `--yes` viene richiesta conferma prima del publish.
- Se `--dry-run` e' attivo, non vengono effettuate chiamate API.
