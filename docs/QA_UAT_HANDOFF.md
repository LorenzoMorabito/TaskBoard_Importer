# QA/UAT Handoff

Questo documento definisce lo stato di handoff verso QA/UAT e il perimetro di
supporto dopo il superamento del gate finale di integrazione.

## Build Validata

- Branch: `main`
- Baseline tag: `qa-ready-001`
- Baseline commit SHA: `1bd7f3be9c6690a3dab572f9eac79c91e3c19a4d`
- Evidence commit SHA: `1209868`
- Stato: gate finale superato, pronto per QA tecnico esteso e UAT controllato
- Entry point ufficiale: `taskboard`
- Entry point alternativo per sviluppo locale:
  `python -m taskboard_importer.presentation.cli`

## Evidenze Disponibili

1. Installazione del package con `pip install -e .`
2. Esecuzione della CLI ufficiale
3. Test suite e coverage
4. Smoke test locale in `--dry-run`
5. Integration test controllato su GitHub reale
6. Report finale di integrazione
7. Elenco limitazioni residue note

## Gate Tecnici Validati

- Nessun riferimento operativo a entrypoint legacy
- Test suite allineata alla tassonomia modulare
- Publish GitHub validato almeno su create e update
- `manifest.json` verificato come sorgente di stato per l'update
- Documentazione allineata ai comandi canonici
- Sync su GitHub Project V2 validato su ambiente sandbox

## Evidenze Repo

- Report di integrazione:
  `outputs/qa-ready-001-session/INTEGRATION_TEST_REPORT.md`
- Workspace di sessione:
  `outputs/qa-ready-001-session/`
- Manifest finale:
  `outputs/qa-ready-001-session/outputs/manifest.json`

## Limitazioni Note / Follow-up

- `publish_as_doc_issue` e' deferred nel manifest, non viene pubblicato come issue attiva
- bug residuo Windows Unicode/emoji tracciato in `docs/KNOWN_ISSUES.md` e nell'issue repo `#1`

## Regola Operativa Post-Gate

Da questo punto in avanti il supporto al progetto e' limitato a:

1. bug reali emersi in QA tecnico esteso
2. bug reali emersi in UAT controllato
3. chiarimenti operativi o di handoff

Non sono pianificati ulteriori refactor preventivi o sviluppi strutturali fuori
da defect fixing o richieste formalizzate di change scope.
