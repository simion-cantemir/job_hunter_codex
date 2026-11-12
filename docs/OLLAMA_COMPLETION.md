# Finalizarea răspunsurilor Ollama

Actualizare: 2026-11-12.

## Corecție ulterioară — ambele etape și citate din sursă

Utilizatorul a raportat explicit atingerea limitei de 1024 tokens. Corecția precedentă ajustase matching-ul, dar extragerea și matching-ul pentru puține cerințe puteau încă folosi 1024. Ambele rute ale analizei folosesc acum minimum 2048, maximum 4096:

- Extragere: `requirements-output-budget-1`, `min(4096, max(2048, 1024 + lungime_sursă))`.
- Matching: `matching-output-budget-2`, `min(4096, max(2048, 256 + 384 * număr_cerințe))`.

Sunt euristici de capacitate, nu estimări exacte de tokenizare sau garanții de finalizare. `chat_local()` direct păstrează implicit 1024; orchestratoarele transmit explicit bugetele. Erorile indică etapa: extragerea din job sau comparația cu fragmentele CV-ului. Tipul erorii și metadatele sigure sunt păstrate.

UI activează explicit `requirements-source-spans-1`: schema enumeră citate existente, evitând reformularea. Rândurile cu bullet și continuările lor sunt păstrate împreună; titlurile terminate cu `:` nu sunt candidați. Vezi [limitele și metoda](LOCAL_EXTRACTION.md). Backend-ul implicit păstrează promptul requirements-1 pentru comparațiile istorice; nu promovăm matching-2.

180 teste trecute. Testul real automat fără schema ancorată a finalizat generarea la 2048, dar validatorul a respins un citat: [rezultat păstrat](evaluations/completion_002.automatic.current.json). Testul cu schema ancorată a ajuns la pending semantic review cu două apeluri complete (297/508 tokens în prima rulare; rezultatul final detaliat este în artefactul următor), fără decizie aplicată. După excluderea titlurilor, [rularea detaliată](evaluations/completion_003.grounded.current.json) a produs șapte rezultate, incluzând incorect fraza introductivă ca mandatory, față de șase cerințe așteptate. A folosit 277 tokens pentru extragere și 507 pentru matching; două rezultate de matching au necesitat recuperare conservatoare. `expected_requirements_match=false`, iar scriptul întoarce exit code 1 pentru diferența semantică. Nu prezentăm acest rezultat ca validare semantică reușită sau reproducere a trunchierii private.

```powershell
.\.venv\Scripts\python.exe -m jobhunter.completion_smoke --automatic
```

Nu au fost accesate date private. Repornește Streamlit și reia analiza cu profilul salvat. Dacă limita maximă este atinsă, analiza rămâne oprită; nu există retry automat sau aplicare de output trunchiat.

## Istoric — prima ajustare a matching-ului

Mesajul vechi grupa răspuns neterminat, limită de generare și model diferit. Raportarea lui de către utilizator nu permite stabilirea retrospectivă a cauzei exacte; nu au fost inspectate răspunsul privat, CV-ul sau baza locală.

## Comportament verificat

`chat_local()` separă acum erorile `output_limit` (`done_reason=length`), `incomplete` (`done` diferit de true), `unexpected_model` și `unexpected_stop`. Mesajele sunt în română, fără textul modelului sau nume externe neverificate. Excepția păstrează doar codul, limita cerută și numărul de tokens raportați când este un întreg valid. Nici JSON aparent complet nu este acceptat dacă serverul indică trunchiere.

API-ul permite un buget pe apel de 128–4096 tokens, validat înaintea transportului. Prima ajustare lăsase extragerea la 1024 și folosea politica `matching-output-budget-1`: `min(4096, max(1024, 256 + 384 * număr_cerințe))`. Aceste valori istorice sunt înlocuite de regulile de mai sus. Bugetele și politicile intră în raportul nou, fără rescrierea rapoartelor vechi. Setările globale nu sunt mutate.

Este o capacitate suplimentară, nu o garanție că orice răspuns se termină în limită sau că interpretarea este corectă. Contextul configurat rămâne 8192, timeoutul implicit 60 secunde per apel. Nu există retry automat, schimbare de model, descărcare sau serviciu cloud. Modelul și validarea `done_reason=stop` rămân obligatorii; nimic nu este aplicat automat.

## Verificări

- 174 teste trecute, șase noi pentru limite per apel, opțiuni nemodificate, categorii separate, respingerea trunchierii și UI fără rezultat/persistență implicită.
- Două apeluri reale la Ollama pe jobul fictiv în română cu șase cerințe și profilul `profile_001.json`, exclusiv sintetic. Cerințele au fost selectate determinist pentru acest smoke check; nu este aprobare reală.
- Limita veche 1024 și limita nouă 2560 au produs fiecare `done=true`, `done_reason=stop`, modelul așteptat, 428 tokens și șase rezultate valide structural. Incidentul privat nu a fost reprodus și nu demonstrăm un câștig de precizie sau o remediere confirmată pe datele utilizatorului.
- Rezumate fără textul răspunsului: [baseline](evaluations/completion_001.baseline.json) și [current](evaluations/completion_001.current.json). Ambele rămân pending semantic review, fără decizie aplicată. Fără inspecție vizuală nouă în browser.

Reproducere numai pe date fictive:

```powershell
.\.venv\Scripts\python.exe -m jobhunter.completion_smoke --baseline
.\.venv\Scripts\python.exe -m jobhunter.completion_smoke
```

Pentru aplicație, repornește Streamlit și reia analiza cu profilul salvat; nu reimporta CV-ul pentru această modificare.

Surse primare consultate: [Ollama chat: done, done_reason, eval_count și options](https://docs.ollama.com/api/chat), [parametrii de generare](https://docs.ollama.com/modelfile#valid-parameters-and-values). Bugetul ales este o regulă a proiectului, nu o recomandare oficială Ollama.
