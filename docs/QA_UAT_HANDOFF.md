# QA/UAT Handoff

Questo documento definisce il gate minimo per promuovere una build di
TaskBoard Importer verso QA tecnico, UAT controllato e pilot users.

## Build Candidata

- Branch: `main`
- Commit SHA: aggiornare con la build candidata
- Entry point ufficiale: `taskboard`
- Entry point alternativo per sviluppo locale:
  `python -m taskboard_importer.presentation.cli`

## Evidenze Minime Richieste

1. Installazione del package con `pip install -e .`
2. Esecuzione della CLI ufficiale con `taskboard --help`
3. Esecuzione della test suite
4. Report coverage aggiornato
5. Smoke test locale in `--dry-run`
6. Integration test controllato su GitHub reale
7. Elenco limitazioni residue note

## Gate Tecnici

- Nessun riferimento operativo a entrypoint legacy
- Test suite allineata alla tassonomia modulare
- Publish GitHub validato almeno su create e update
- `manifest.json` verificato come sorgente di stato per l'update
- Documentazione allineata ai comandi canonici

## Integration Test GitHub Reale

L'integration test minimo deve coprire:

1. `bootstrap-github` con token reale
2. `import-roadmap` con publish reale e creazione issue
3. modifica controllata della roadmap
4. `import-roadmap` con `--dedupe-policy update`
5. verifica del riuso di `manifest.json`
6. sync su Project V2, se incluso nello scope

## Limitazioni Note

- `publish_as_doc_issue` e' deferred nel manifest, non viene pubblicato come issue attiva
- l'integrazione live GitHub/Project V2 richiede ancora evidenza ambiente reale

## Deliverable per QA

- SHA validato
- log test suite
- log coverage
- output smoke test
- report integration test
- eventuali issue aperte / limitazioni residue
