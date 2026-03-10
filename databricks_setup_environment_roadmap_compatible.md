# Roadmap operativa — Setup Environment Databricks

## Scopo del documento
Questa roadmap descrive **tutte le attività e sottoattività** necessarie per portare il setup environment Databricks da **0 a concluso**, con una struttura pensata per:
- avere sempre visibilità sullo **stato reale di avanzamento**;
- sapere cosa è **già stato fatto**, cosa è **in corso** e cosa **manca**;
- produrre per ogni step un **output verificabile**;
- usare il file come checklist viva dentro la cartella di progetto.

---

## Come usare questa roadmap
Per ogni sottoattività compila questi campi:
- **Status**: `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED`
- **Owner**: chi la esegue
- **Data**: quando è stata eseguita
- **Evidenza**: notebook, screenshot, output comando, link repo, path file, job run, ecc.
- **Note/Rischi**: eventuali problemi o decisioni prese

### Convenzione avanzamento
- **0%**: nessuna attività iniziata
- **25%**: accessi e strumenti base pronti
- **50%**: repo/package e compute funzionanti
- **75%**: sample run end-to-end stabile
- **100%**: ambiente documentato, ripetibile, pronto per sviluppo e demo portfolio

---

# 1. Definizione perimetro setup

## 1.1 Obiettivo del setup
**Attività**
- Definire con chiarezza cosa significa “environment concluso”.
- Stabilire se il focus è:
  - sviluppo notebook;
  - sviluppo package Python;
  - esecuzione batch/job;
  - gestione repo Git;
  - test con dati sample in Volume/DBFS.

**Output atteso**
- Mini definizione di done del setup.

**Done quando**
- Esiste una frase chiara del tipo:  
  `L'environment è concluso quando posso eseguire il progetto da repo versionata su Databricks, importare il package senza workaround fragili, lanciare un test sample end-to-end e produrre un output verificabile.`

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 1.2 Inventario iniziale
**Attività**
- Elencare gli asset disponibili:
  - account Databricks;
  - workspace;
  - compute/cluster/serverless;
  - repo GitHub/GitLab;
  - progetto locale;
  - sample data;
  - config file;
  - Volumes / Unity Catalog / Catalog / Schema.

**Output atteso**
- Tabella inventario iniziale.

**Done quando**
- È chiaro cosa esiste già e cosa manca.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 2. Accesso e prerequisiti di base

## 2.1 Accesso al workspace Databricks
**Attività**
- Verificare login al workspace.
- Verificare quale workspace si sta usando.
- Annotare host workspace.

**Verifica**
- Accesso UI riuscito.
- Host disponibile e corretto.

**Output atteso**
- Host Databricks documentato.

**Done quando**
- L’utente entra stabilmente nel workspace corretto.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 2.2 Permessi minimi
**Attività**
- Verificare permessi su:
  - workspace folders;
  - repo;
  - compute;
  - catalog/schema/volume;
  - jobs/workflows, se previsti.

**Verifica**
- Riesci ad aprire notebook, collegare repo, leggere/scrivere nel path di test.

**Output atteso**
- Lista permessi effettivi disponibili.

**Done quando**
- Non ci sono blocchi autorizzativi per sviluppo e test.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 2.3 Tool locale di supporto
**Attività**
- Verificare installazione di:
  - Python;
  - Git;
  - VS Code;
  - Databricks CLI / extension VS Code, se adottata.
- Annotare versioni.

**Verifica**
- Comandi base disponibili da terminale.

**Output atteso**
- Lista versioni tool.

**Done quando**
- Gli strumenti locali minimi sono installati e riconosciuti.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 3. Connessione locale ↔ Databricks

## 3.1 Configurazione autenticazione
**Attività**
- Configurare il profilo Databricks locale.
- Associare host corretto.
- Verificare metodo di autenticazione in uso.

**Verifica**
- Login CLI riuscito.
- Profilo salvato correttamente.

**Output atteso**
- Profilo locale funzionante.

**Done quando**
- Da locale è possibile autenticarsi al workspace senza errori.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 3.2 Test connessione operativa
**Attività**
- Eseguire un comando di verifica verso il workspace.
- Confermare che il profilo punti al tenant corretto.

**Verifica**
- La CLI/estensione risponde senza errori di host o auth.

**Output atteso**
- Test connessione riuscito.

**Done quando**
- La connessione è utilizzabile per operazioni reali.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 4. Setup repository di progetto

## 4.1 Creazione o collegamento repo remota
**Attività**
- Verificare se il progetto vive su GitHub o GitLab.
- Creare repo se assente oppure collegare quella esistente.
- Definire branch principale (`main` o `master`) e, se serve, branch di sviluppo.

**Verifica**
- Repo remota accessibile.

**Output atteso**
- URL repo e branch strategy minima documentate.

**Done quando**
- Esiste una repo remota usabile come source of truth.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 4.2 Allineamento repo locale
**Attività**
- Verificare struttura locale del progetto.
- Eseguire commit iniziale se necessario.
- Push verso repo remota.

**Verifica**
- La repo remota contiene i file attesi.

**Output atteso**
- Primo stato versionato del progetto.

**Done quando**
- Il codice locale è allineato alla repo remota.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 4.3 Collegamento repo in Databricks
**Attività**
- Collegare la repo al workspace Databricks oppure clonarla nell’area repo del workspace.
- Verificare branch attiva.
- Verificare che i file siano visibili nel workspace.

**Verifica**
- Apri i file del progetto da Databricks.

**Output atteso**
- Repo disponibile nel workspace.

**Done quando**
- Il progetto è apribile e modificabile da Databricks.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 4.4 Regole di sync Git
**Attività**
- Definire regola operativa minima:
  - modifiche locali → commit → push → pull/sync in Databricks;
  - evitare modifiche concorrenti sullo stesso file in locale e in workspace;
  - gestire conflitti in modo esplicito.

**Verifica**
- Simulare una modifica locale e sincronizzarla in Databricks.

**Output atteso**
- Mini procedura Git di team/personale.

**Done quando**
- È chiaro come evitare perdita di modifiche e conflitti opachi.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 5. Setup compute e runtime

## 5.1 Scelta compute
**Attività**
- Identificare il compute da usare per sviluppo:
  - cluster classico;
  - all-purpose;
  - serverless notebook, se disponibile e compatibile.
- Scegliere una sola opzione consigliata per il progetto.

**Opzione consigliata**
- **All-purpose cluster dedicato di sviluppo** per debugging più controllabile.

**Alternativa**
- **Serverless** se già abilitato e compatibile, con meno overhead ma minore controllo su alcuni casi.

**Verifica**
- Compute selezionato visibile e avviabile.

**Output atteso**
- Nome compute di riferimento documentato.

**Done quando**
- Esiste un compute standard ufficiale per i test del progetto.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 5.2 Attach notebook al compute corretto
**Attività**
- Aprire il notebook di test.
- Verificare a quale compute è attaccato.
- Se necessario fare detach/reattach sul compute standard.

**Verifica**
- Il notebook risulta attached al compute corretto.

**Output atteso**
- Notebook agganciato correttamente.

**Done quando**
- Tutti i test sono eseguiti sul compute deciso come standard.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 5.3 Sanity check runtime
**Attività**
- Verificare versione runtime Python/Databricks.
- Verificare disponibilità librerie chiave.
- Annotare eventuali incompatibilità.

**Verifica**
- Una cella stampa versioni Python e librerie.

**Output atteso**
- Snapshot ambiente runtime.

**Done quando**
- Sai esattamente su quale runtime stai lavorando.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 6. Setup package e dipendenze del progetto

## 6.1 Verifica struttura package
**Attività**
- Controllare presenza di:
  - `pyproject.toml`;
  - cartella `src/`;
  - package con `__init__.py`;
  - eventuali script di build/test.

**Verifica**
- Path repo e package esistono realmente.

**Output atteso**
- Struttura package validata.

**Done quando**
- Il progetto ha struttura coerente per install/import.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 6.2 Strategia di import/install
**Attività**
- Scegliere come usare il progetto in Databricks:
  - `sys.path` temporaneo per debug rapido;
  - installazione editable / package installato per uso più pulito.

**Opzione consigliata**
- **Installazione del package** come approccio target.

**Alternativa**
- **`sys.path`** solo per sblocco rapido iniziale.

**Verifica**
- Definire approccio target e workaround temporanei.

**Output atteso**
- Strategia di import documentata.

**Done quando**
- È chiaro qual è la soluzione temporanea e qual è quella definitiva.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 6.3 Test import package
**Attività**
- Eseguire import del package nel notebook.
- Stampare `__file__` del modulo importato.
- Confermare che il modulo caricato sia quello giusto.

**Verifica**
- `import` riuscito e path corretto.

**Output atteso**
- Evidenza di import OK.

**Done quando**
- L’import del package funziona in modo ripetibile.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 6.4 Gestione dipendenze
**Attività**
- Elencare dipendenze del progetto.
- Verificare che siano disponibili sul compute.
- Risolvere eventuali mismatch di versione.

**Verifica**
- Import di tutte le librerie critiche riuscito.

**Output atteso**
- Dipendenze core validate.

**Done quando**
- Nessuna dipendenza critica blocca i test.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 7. Setup storage, path e dati di test

## 7.1 Definizione path standard
**Attività**
- Definire i path standard per:
  - repo sorgente;
  - config;
  - sample input;
  - output;
  - eventuali volumi/catalog/schema.

**Verifica**
- Tutti i path esistono o sono creabili.

**Output atteso**
- Tabella dei path standard di progetto.

**Done quando**
- I path usati nei test non sono “sparsi” o ambigui.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 7.2 Verifica accesso a sample data
**Attività**
- Controllare presenza del file sample.
- Controllare accessibilità del config sample.
- Verificare che l’output path sia scrivibile.

**Verifica**
- `exists = True` per input e config.
- Test di scrittura directory/file riuscito.

**Output atteso**
- Evidenza accesso dati di test.

**Done quando**
- Il sample può essere letto e l’output può essere scritto.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 7.3 Controllo configurazione sample
**Attività**
- Aprire il file di configurazione sample.
- Verificare coerenza dei path relativi/assoluti.
- Verificare parametri minimi richiesti dall’applicazione.

**Verifica**
- La config è leggibile e semanticamente coerente.

**Output atteso**
- Config sample validata.

**Done quando**
- La config può essere usata in run senza ambiguità sui path.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 8. Test tecnico di bootstrap

## 8.1 Notebook di diagnostica ambiente
**Attività**
- Creare o aggiornare un notebook di test che esegua in sequenza:
  - stampa compute/runtime;
  - verifica path repo;
  - verifica import package;
  - verifica config;
  - verifica sample file;
  - verifica scrittura output path.

**Verifica**
- Tutti i check restituiscono stato chiaro.

**Output atteso**
- Notebook di bootstrap riusabile.

**Done quando**
- Esiste un unico notebook per diagnosticare rapidamente l’environment.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 8.2 Classificazione errori ambiente
**Attività**
- Raccogliere gli errori incontrati.
- Classificarli per categoria:
  - auth/permessi;
  - compute attach;
  - import/package;
  - I/O path;
  - dipendenze;
  - runtime metadata/sessione Spark.

**Verifica**
- Ogni errore noto ha una causa probabile e una contromisura.

**Output atteso**
- Registro problemi environment.

**Done quando**
- Gli errori non sono più “casuali”, ma tracciati e spiegati.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 9. Esecuzione sample end-to-end

## 9.1 Avvio run reale
**Attività**
- Lanciare il progetto sul sample data usando il config validato.
- Evitare workaround non documentati.

**Verifica**
- La run parte senza errori bloccanti di environment.

**Output atteso**
- Esecuzione reale del parser/processo.

**Done quando**
- La run raggiunge il punto finale previsto dal flusso.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 9.2 Validazione output
**Attività**
- Verificare che l’output finale venga creato.
- Aprire o ispezionare il contenuto generato.
- Confermare che non sia solo “file creato”, ma file sensato.

**Verifica**
- Output leggibile e coerente con il sample.

**Output atteso**
- File o tabella finale verificata.

**Done quando**
- L’utente può mostrare un risultato concreto del test.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 9.3 Ripetibilità della run
**Attività**
- Rieseguire il test una seconda volta in modo pulito.
- Verificare che il risultato sia stabile.

**Verifica**
- Due esecuzioni consecutive non presentano comportamenti casuali.

**Output atteso**
- Evidenza di run ripetibile.

**Done quando**
- Il test non dipende dal caso o da uno stato sporco del notebook.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 10. Stabilizzazione e hardening minimo

## 10.1 Pulizia workaround temporanei
**Attività**
- Identificare workaround usati per sbloccare i test.
- Decidere quali mantenere e quali rimuovere.
- Portare il setup verso una modalità più pulita.

**Verifica**
- Il notebook non dipende da hack fragili non documentati.

**Output atteso**
- Elenco workaround rimossi o accettati temporaneamente.

**Done quando**
- L’ambiente è sufficientemente pulito per sviluppo continuativo.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 10.2 Struttura standard dei notebook di test
**Attività**
- Separare:
  - notebook diagnostico ambiente;
  - notebook smoke test;
  - notebook run sample.

**Verifica**
- Ogni notebook ha uno scopo chiaro.

**Output atteso**
- Cartella notebook ordinata.

**Done quando**
- Chiunque capisce dove lanciare check, smoke test e run reale.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 10.3 Logging minimo
**Attività**
- Far stampare al run almeno:
  - compute usato;
  - config usato;
  - input file;
  - output path;
  - esito finale.

**Verifica**
- L’output di run è leggibile e auditabile.

**Output atteso**
- Run log minimo standard.

**Done quando**
- Ogni esecuzione lascia evidenze utili per debug.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 11. Industrializzazione minima dell’environment

## 11.1 Parametrizzazione del run
**Attività**
- Definire i parametri minimi necessari:
  - config path;
  - input path;
  - output path;
  - eventuale mode/test flag.

**Verifica**
- Il run non dipende da valori hardcoded sparsi.

**Output atteso**
- Parametri di esecuzione documentati.

**Done quando**
- Il flusso può essere rilanciato cambiando pochi parametri chiari.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 11.2 Predisposizione a job/workflow
**Attività**
- Valutare se il notebook/script può essere lanciato come job.
- Identificare input/output e dipendenze minime.

**Verifica**
- Esiste una bozza di esecuzione schedulabile.

**Output atteso**
- Ready for Jobs: sì/no + motivazione.

**Done quando**
- È chiaro se l’ambiente è pronto anche per orchestrazione base.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 12. Documentazione finale del setup

## 12.1 README environment setup
**Attività**
- Scrivere una guida breve con:
  - prerequisiti;
  - repo da aprire;
  - compute da usare;
  - notebook da lanciare;
  - sample config;
  - output atteso;
  - errori comuni.

**Verifica**
- Una persona esterna capisce come riprodurre il setup.

**Output atteso**
- Documento README o sezione dedicata nella repo.

**Done quando**
- Il setup è riproducibile senza ricostruirlo “a memoria”.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 12.2 Stato finale e checklist di chiusura
**Attività**
- Compilare la checklist finale di chiusura.

### Checklist di chiusura
- [ ] Accesso workspace verificato
- [ ] Permessi minimi verificati
- [ ] Tool locali configurati
- [ ] Profilo Databricks locale funzionante
- [ ] Repo remota configurata
- [ ] Repo disponibile in Databricks
- [ ] Regole Git minime definite
- [ ] Compute standard scelto
- [ ] Notebook attached al compute corretto
- [ ] Runtime validato
- [ ] Package structure validata
- [ ] Import package riuscito
- [ ] Dipendenze core verificate
- [ ] Path standard documentati
- [ ] Sample config verificata
- [ ] Input sample accessibile
- [ ] Output path scrivibile
- [ ] Notebook diagnostico pronto
- [ ] Run sample end-to-end eseguita
- [ ] Output finale validato
- [ ] Run ripetibile verificata
- [ ] Workaround critici ridotti
- [ ] Parametri run documentati
- [ ] README setup scritto

**Output atteso**
- Stato finale compilato.

**Done quando**
- Tutti i punti sopra sono chiusi oppure i blocchi residui sono esplicitati.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 13. Registro avanzamento sintetico

## Tabella stato avanzamento
| ID | Macrofase | Stato | % fase | Dipendenze | Evidenza | Note |
|---|---|---:|---:|---|---|---|
| 1 | Definizione perimetro | TODO | 0 | - | - | - |
| 2 | Accessi e prerequisiti | TODO | 0 | 1 | - | - |
| 3 | Connessione locale ↔ Databricks | TODO | 0 | 2 | - | - |
| 4 | Setup repository | TODO | 0 | 2,3 | - | - |
| 5 | Setup compute e runtime | TODO | 0 | 2 | - | - |
| 6 | Setup package e dipendenze | TODO | 0 | 4,5 | - | - |
| 7 | Storage, path e sample data | TODO | 0 | 2,5 | - | - |
| 8 | Diagnostica ambiente | TODO | 0 | 5,6,7 | - | - |
| 9 | Run sample end-to-end | TODO | 0 | 6,7,8 | - | - |
| 10 | Stabilizzazione | TODO | 0 | 9 | - | - |
| 11 | Industrializzazione minima | TODO | 0 | 10 | - | - |
| 12 | Documentazione finale | TODO | 0 | 11 | - | - |

---

# 14. Best practice operative

## Da fare sempre
- Tenere **un solo compute standard** per i test iniziali.
- Usare **path documentati** e non improvvisati cella per cella.
- Distinguere chiaramente **workaround temporanei** da **soluzioni definitive**.
- Salvare sempre una **evidenza verificabile** per ogni step chiuso.
- Fare sync Git in modo disciplinato, evitando modifiche parallele sullo stesso file.
- Testare prima un **sample piccolo e ripetibile**.

## Errori comuni da evitare
- Considerare “setup concluso” solo perché l’`import` funziona.
- Mescolare problemi di codice con problemi di environment.
- Cambiare continuamente compute senza tracciare gli effetti.
- Usare notebook sporchi come unica fonte di verità.
- Non annotare quale config/path/output è stato usato in una run.

---

# 15. Criterio finale di completamento

## 15.1 Verifica checklist di completamento finale
**Attività**
- Verificare che il workspace sia accessibile e che il compute standard sia definito.
- Verificare che la repo sia sincronizzata e che il progetto sia apribile da Databricks.
- Verificare che package/import siano stabili e documentati.
- Verificare che sample config e sample input siano accessibili.
- Verificare che il run end-to-end produca un output verificabile.
- Verificare che il test sia ripetibile.
- Verificare che esista una documentazione minima sufficiente a rifare il setup senza dipendere dalla memoria.

**Verifica**
- Tutte le condizioni finali risultano confermate con evidenze puntuali.
- Eventuali gap residui sono esplicitati e classificati come blocker o attività residue.

**Output atteso**
- Checklist finale di completamento compilata con esito per ogni criterio.

**Done quando**
- Tutti i criteri finali sono marcati come soddisfatti oppure i blocchi residui sono formalizzati con owner e prossimo step.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 15.2 Chiusura formale del setup environment
**Attività**
- Consolidare l’esito finale del setup.
- Riportare percentuale complessiva di avanzamento reale.
- Dichiarare se l’environment è pronto per sviluppo continuativo, demo portfolio e run ripetibili.
- Annotare eventuali limiti residui accettati.

**Verifica**
- Esiste una dichiarazione finale chiara sullo stato dell’environment.
- La decisione finale è coerente con le evidenze raccolte nelle fasi precedenti.

**Output atteso**
- Stato finale del setup formalizzato e pronto da condividere.

**Done quando**
- È disponibile una chiusura formale del tipo:  
  `Environment concluso / non concluso`, con motivazione, data e riferimenti alle evidenze.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

# 16. Prossimo aggiornamento consigliato

## 16.1 Aggiornamento stato attuale reale
**Attività**
- Compilare la sintesi finale dello stato attuale reale.
- Aggiornare i campi:
  - Percentuale complessiva;
  - Completato;
  - In corso;
  - Bloccato;
  - Prossimo step operativo;
  - Rischio principale;
  - Decisione richiesta.
- Allineare la sintesi con la tabella stato avanzamento e con l’ultima evidenza disponibile.

**Verifica**
- La sintesi finale è coerente con il reale avanzamento del progetto.
- Non ci sono discrepanze tra stato dichiarato e prove raccolte.

**Output atteso**
- Sezione “Stato attuale reale” compilata e aggiornata.

**Done quando**
- La roadmap termina con una fotografia sintetica, leggibile e aggiornata del progetto.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

---

## 16.2 Pianificazione del prossimo step operativo
**Attività**
- Identificare il prossimo step operativo a maggior valore.
- Esplicitare eventuali dipendenze, decisioni richieste e rischi principali.
- Definire chi deve fare cosa nel prossimo aggiornamento della roadmap.

**Verifica**
- Il prossimo step è specifico, eseguibile e assegnabile.
- Esiste chiarezza su eventuali blocker da risolvere prima del passo successivo.

**Output atteso**
- Piano di prosecuzione immediata documentato.

**Done quando**
- È disponibile un prossimo step chiaro con owner, obiettivo e criterio di completamento.

**Tracking**
- Status:
- Owner:
- Data:
- Evidenza:
- Note/Rischi:

