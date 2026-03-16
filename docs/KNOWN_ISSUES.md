# Known Issues

Questo documento traccia i bug e le limitazioni note rilevate dopo il
superamento del gate finale di integrazione.

## BUG-001 - CLI Unicode output on Windows shell

- Status: open
- Severity: medium
- Area: `presentation/cli.py`
- Detected during: integration gate `qa-ready-001`
- Evidence: `outputs/qa-ready-001-session/INTEGRATION_TEST_REPORT.md`

### Description

Su alcune shell Windows con encoding non UTF-8 l'output della CLI puo' fallire
quando stampa emoji (`✅`, `❌`, `📊`, `📋`), anche se il comando sottostante e'
stato eseguito correttamente.

### Impact

- il workflow applicativo non fallisce per logica di business
- l'esecuzione operativa da shell Windows puo' interrompersi prima del normale
  completamento dell'output

### Current Workaround

Impostare prima dell'esecuzione:

```powershell
$env:PYTHONIOENCODING='utf-8'
```

oppure usare una shell/terminale con encoding UTF-8.

### Proposed Resolution

- rimuovere emoji dall'output CLI oppure
- introdurre un fallback ASCII quando l'encoding della console non supporta i
  caratteri Unicode richiesti

## LIM-001 - `publish_as_doc_issue`

- Status: known limitation
- Severity: informational

### Description

I task classificati come `publish_as_doc_issue` restano deferred nel
`manifest.json` e non vengono pubblicati come issue GitHub attive.

### Scope Decision

Fuori scope per la baseline `qa-ready-001`. Non blocca il passaggio a QA/UAT.
