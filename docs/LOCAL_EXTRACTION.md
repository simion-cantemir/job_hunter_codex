# Prima integrare Ollama

## Schema cu citate din sursă și limitele ambelor etape — 2026-11-12

UI folosește explicit `grounded_extraction=True` în `analyze_draft`, respectiv `grounded=True` în `extract_requirements`. Schema `requirements-source-spans-1` enumeră citate exacte existente în anunț: rânduri simple sau bullets cu continuările lor. Modelul alege citatul și prioritatea, iar Python verifică în continuare existența exactă, unicitatea și pozițiile. Schema și promptul baseline `requirements-1` rămân disponibile implicit în backend/evaluările vechi; schema comună nu este mutată.

Rândurile terminate cu `:` sunt tratate ca titluri, disponibile în sursa trimisă modelului pentru context, dar excluse dintre citate. Este o euristică de layout, nu parser universal: o cerință cu structură atipică poate fi omisă, o frază introductivă poate fi aleasă greșit, iar paragrafele/alternativele fără bullets pot necesita selecție manuală. Revizuiește relevanța, completitudinea și OR/AND. Nu echivala respectarea schemei cu interpretare corectă.

Bugetul extragerii este acum minimum 2048, maximum 4096, proporțional cu lungimea sursei; matching-ul are tot minimum 2048. Erorile indică etapa și rămân blocante la trunchiere. Politici, teste și rezultatul automat cu o cerință introductivă în plus: [OLLAMA_COMPLETION.md](OLLAMA_COMPLETION.md). 180 teste trecute, fără acces la date private; testul semantic fictiv detaliat nu a trecut comparația 6/6. UI ajunge la revizuire, fără aprobare automată.

## Continuare când citatul AI nu corespunde sursei — 2026-11-12

Eroarea `Model quote does not occur verbatim in the source` înseamnă că cel puțin un citat returnat nu există exact în textul primit. Mesajul singur nu identifică diferența sau cauza ei; nu presupunem că rularea privată a fost reprodusă. Acum mesajul este în română, iar UI indică ruta manuală. Nu acceptăm parafraze ca citate și nu reutilizăm o extragere parțială.

După repornirea Streamlit, la **„Cum alegi cerințele jobului?”** poți alege **„Selectează manual din anunț”**. Selectezi rândurile cu cerințe și alegi pentru fiecare **Obligatorie / Opțională / Necunoscută**, după anunț. Nu selecta titluri sau date despre companie. Prioritatea implicită este Necunoscută; nu o deducem din poziția rândului. Pentru jobul fictiv Engineering Manager — Quality & Delivery din conversație, primele patru cerințe sunt obligatorii și ultimele două opționale.

La apăsarea analizei, Python calculează pozițiile exacte și validează citatele; modelul este apelat numai pentru matching. Raportul marchează extragerea `model=manual`, `prompt_version=requirements-manual-1`, fără a o atribui AI-ului. Review-ul și confirmarea finală rămân obligatorii. Schimbarea modului, rândurilor sau priorităților invalidează analiza și aprobarea curentă. CV-ul și profilurile salvate nu sunt rescrise.

Limite: alegerea este la nivel de rând, nu un parser de propoziții. O cerință împărțită pe rânduri (mai ales OR/AND) poate necesita clarificare; nu transforma alternativele în obligații separate. Selecția manuală nu garantează completitudinea sau relevanța și nu repară extragerea automată. API-ul păstrează validarea strictă; noul parametru opțional `selected_requirements` din `analyze_draft` este revalidat înaintea oricărui apel de matching.

168 teste trecute, inclusiv 8 noi pentru citate reformulate, Unicode/CRLF, rânduri repetate, selecții invalide, bypassul exclusiv al extragerii, invalidarea analizei și continuarea din UI fără salvare implicită. Transportul este simulat; nu s-a executat o nouă inference reală sau inspecție vizuală de browser pentru această etapă. Nu am accesat CV-ul ori baza privată.

`jobhunter/ollama.py` folosește biblioteca standard Python pentru POST la `http://127.0.0.1:11434/api/chat`. Modelul este fixat la `llama3.2:3b`, deja instalat; adaptorul nu descarcă modele și nu configurează cloud. Proxy-urile sistemului sunt ignorate și redirecturile sunt refuzate pentru acest apel.

## Flux și utilizare

```powershell
.\.venv\Scripts\python.exe -m jobhunter.extract_demo
```

Comanda citește exclusiv jobul fictiv din `tests/fixtures/job_001.txt`, afișează rezultatul și comparația cu exemplul așteptat. Nu modifică SQLite și nu face matching cu profilul. Comparația folosește perechi citat/prioritate, fără a pretinde că un singur exemplu este un benchmark reprezentativ. Rezultatul de referință a fost propus de agent și nu este încă revizuit de utilizator.

Python trimite instrucțiuni în mesajul system și jobul ca date JSON în mesajul user. Modelul returnează doar prioritatea și citatul. Python calculează ID-urile și pozițiile în sursă și apelează validatorul existent. Citările inexistente, ambigue (apar de mai multe ori) sau duplicate sunt respinse. Nu reparăm automat citate și nu extragem procente de compatibilitate din răspuns.

Ollama primește schema JSON prin `format` și `stream: false`, conform [API chat](https://docs.ollama.com/api/chat) și [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), consultate la 2026-11-10. Schema constrânge forma răspunsului; validarea sursei și evaluarea sensului rămân responsabilități separate.

## Limite și erori

- Prompt version `requirements-1`; temperature 0, seed 42, context 8192 tokens, maximum 1024 tokens generați. Temperatura mică reduce variația, fără garanție de reproducibilitate absolută.
- Maximum 8000 caractere de sursă în acest experiment, fără trunchiere automată. Limita în caractere nu garantează încadrarea oricărui text în contextul exprimat în tokens; tokenizarea și calibrarea pentru joburi lungi rămân de realizat.
- Timeout de conexiune/citire de 60 secunde implicit, configurabil până la 120 secunde; nu este un deadline absolut pentru toate operațiile de transport. Răspuns de maximum 256000 bytes. Fără retry automat. Un timeout al clientului nu garantează anularea imediată a inference pe server.
- Erorile HTTP, lipsa serviciului/modelului, JSON invalid, output neterminat sau limita de tokens atinsă produc `ExtractionError`, fără folosirea unui rezultat parțial. Mesajele de eroare nu includ textul jobului sau corpul răspunsului HTTP.
- `keep_alive: "0"` solicită eliberarea modelului după răspuns; nu schimbă configurația persistentă Ollama. Testul real poate încărca modelul și utiliza CPU/GPU/RAM/VRAM.
- Promptul tratează anunțul ca date neîncredere și nu oferă tools. Această delimitare nu garantează imunitate la prompt injection sau corectitudine semantică. Un citat real poate fi totuși clasificat greșit ori unele cerințe pot lipsi.
- Golul de cerințe rămâne gol; politica de eligibilitate existentă cere revizuire, nu declară automat potrivire.

Testele unitare folosesc transport simulat; rularea reală este separată și trebuie raportată distinct. Nu s-au transmis date personale sau CV-uri în acest pas.

## Rezultat observat

Prima rulare locală a reușit: 4 cerințe, toate cu citat și prioritate identice cu exemplul așteptat. Timp observat: 37,449 secunde, 396 tokens de prompt și 102 tokens generați conform răspunsului Ollama. Datele sunt salvate în `docs/evaluations/ollama_job_001_run_001.json`. Nu am măsurat utilizarea GPU, separarea timpului de încărcare sau distribuția latenței pe rulări repetate. Cele 51 de teste locale au trecut, independent de această rulare reală.
