# Finalizarea răspunsurilor Ollama

Actualizare: 2026-11-12.

Mesajul vechi grupa răspuns neterminat, limită de generare și model diferit. Raportarea lui de către utilizator nu permite stabilirea retrospectivă a cauzei exacte; nu au fost inspectate răspunsul privat, CV-ul sau baza locală.

## Comportament verificat

`chat_local()` separă acum erorile `output_limit` (`done_reason=length`), `incomplete` (`done` diferit de true), `unexpected_model` și `unexpected_stop`. Mesajele sunt în română, fără textul modelului sau nume externe neverificate. Excepția păstrează doar codul, limita cerută și numărul de tokens raportați când este un întreg valid. Nici JSON aparent complet nu este acceptat dacă serverul indică trunchiere.

API-ul permite un buget pe apel de 128–4096 tokens, validat înaintea transportului; implicit rămâne 1024 pentru extragere. Matching-ul folosește politica versionată `matching-output-budget-1`: `min(4096, max(1024, 256 + 384 * număr_cerințe))`. Pentru șase cerințe rezultă 2560. Bugetul efectiv și politica intră în raportul nou, fără rescrierea rapoartelor vechi. Setările globale nu sunt mutate.

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
