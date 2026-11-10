# Project progress

Data: 2026-11-10, Europe/Bucharest.

## Finalizat

- Cerințele START citite; directorul C:\Projects\JobHunterAI era gol, fără repository Git sau prototip.
- Diagnostic verificat și limitări documentate în README.md.
- Create documentele cerute, reguli persistente, arhitectură propusă, roadmap și prima lecție.
- Creat `.venv` cu Python 3.13.17, fără pip, downloaduri sau pachete externe; confirmat interpreterul din proiect și izolarea față de interpreterul de bază.
- Implementat `jobhunter/storage.py`: salvare/recitire job, validare câmpuri obligatorii și interogări parametrizate.
- Rulat `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 2 teste trecute. Verificate persistența prin redeschidere, păstrarea exactă a textului cu diacritice/conținut SQL, ID absent și respingerea câmpurilor goale. Bazele de test sunt temporare, exclusiv sintetice.
- Utilizatorul a răspuns corect la întrebarea despre LLM-ul local; clarificată orchestrarea Python/Ollama.
- Utilizatorul a confirmat corect că joburile persistă în SQLite la oprirea Ollama.
- F1 începută: contract versiunea 1 în `jobhunter/requirements.py`, cu mandatory/optional/unknown, citate și poziții în sursă; primul golden example sintetic în `tests/fixtures/`, documentat în `docs/REQUIREMENTS_CONTRACT.md`. Exemplul este propus de agent și nu este încă revizuit de utilizator.
- Suita actuală: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`, 9 teste trecute (7 pentru contract, 2 pentru SQLite). Acoperă output invalid, citate inexistente, poziții greșite, Unicode, câmpuri lipsă/extra și ID duplicat. Prima rulare a detectat poziții introduse manual greșit în fixture; acestea au fost corectate, apoi întreaga suită a trecut.

## Nu este implementat sau validat

Nu există încă UI, matching automat cu profilul sau sursă de joburi. Extragerea LLM locală a fost executată pe un job fictiv, dar analiza end-to-end cu matching automat nu este implementată. Stocarea, validarea contractelor și calculul scorului sunt testate. Un citat sau ID valid nu certifică relevanța, prioritatea sau completitudinea interpretării. Ponderile de scoring nu sunt calibrate pe joburi reale. Lipsesc CV-ul real și benchmark-ul reprezentativ. Modelul instalat nu este încă recomandat pentru producție. Nicio comparație local/cloud măsurată.

## Pasul următor propus

Matching asistat de model pe profilul fictiv, cu dovezi validate și raport combinat de scoring/eligibilitate. Acceptance criteria: niciun ID de dovadă inventat, unknown pentru informația absentă, fără respingere bazată pe o concluzie LLM nerevizuită. Înainte de folosirea deciziilor automate vom introduce o etapă explicită de revizuire semantică. Exemplele sintetice și ponderile rămân propuneri pentru revizuirea utilizatorului.

## Ultimul checkpoint — extragere locală Ollama

- Consultate documentația oficială Ollama chat și structured outputs; linkuri în docs/LOCAL_EXTRACTION.md.
- Implementate adaptorul standard-library `jobhunter/ollama.py` și demo-ul `python -m jobhunter.extract_demo`, exclusiv pe jobul fictiv. Endpoint fix local, proxy dezactivat, redirecturi refuzate, fără tools, retry sau downloaduri. Citatele sunt validate; ID-urile și pozițiile sunt calculate în cod.
- Suita: 51 de teste trecute (10 noi, transport simulat), inclusiv conexiune indisponibilă/timeout, HTTP error, JSON invalid, răspuns trunchiat, citate inexistente/ambigue/duplicate și intrări prea lungi. Nicio nouă dependență instalată.
- Rulare reală separată: llama3.2:3b, ID local scurt a80c4f17acd5; 37,449 secunde, 396 prompt tokens și 102 output tokens. Toate cele 4 citate/priorități corespund referinței. Rezultat observat salvat în docs/evaluations/ollama_job_001_run_001.json.
- Este un singur exemplu redactat de agent, nu benchmark reprezentativ sau revizuire umană. Nu s-au folosit CV/date personale și nu s-a modificat SQLite. Nu am măsurat utilizarea GPU sau latențe repetate.

## Ultimul checkpoint — eligibilitate și limba de lucru

- Utilizatorul a acceptat explicit respingerea din oportunități pentru mandatory confirmed_missing, cu păstrarea istoricului. Limba de lucru este determinantă. Cerința lipsă rămâne cu zero în scor; respingerea este o decizie separată.
- Implementat `jobhunter/eligibility.py`: validarea intrărilor, rejected/needs_review/eligible și motive trasabile. Datele parțiale/necunoscute nu produc respingere.
- Extins SQLite prin tabela nouă `job_decisions`, fără ștergere de date: timestamp UTC, motive, versiuni, hash al textului sursă. Listarea exclude ultima decizie rejected. Reevaluarea explicită păstrează istoricul.
- Rulat `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 41 de teste trecute (12 noi). Verificate cazuri de limbă obligatorie/opțională/necunoscută, scor >90% cu blocaj, redeschidere DB, istoricul reevaluării, asociere cu textul corect și compatibilitate cu schema veche.
- Prima execuție a identificat o conexiune de test neînchisă la curățarea SQLite pe Windows; am corectat închiderea explicită și suita a trecut. Nicio bază cu date reale nu a fost modificată.
- Nu există încă UI, deduplicare a reimporturilor, runtime LLM sau evaluare semantică. Profilurile și versiunile analizelor nu sunt încă persistate complet pentru auditul pe date reale. Stocarea respingerii nu înseamnă că evitarea reanalizării la reimport este implementată.

## Continuitate

Pentru reluare citește AGENTS.md, acest fișier și ROADMAP.md; apoi doar documentele taskului. Propunerile tehnice sunt în docs/DECISIONS.md, nu presupune acceptare explicită din partea utilizatorului. Utilizatorul preferă acum răspunsurile de interviu în română; engleza doar la cerere. PowerShell sandbox nu a putut porni (setup refresh error); operațiile shell au fost executate cu escaladare aprobată. Git poate necesita `-c safe.directory=C:/Projects/JobHunterAI` din cauza conturilor locale diferite; nu schimba configurația globală.

## Ultimul checkpoint de lucru — matching

- Implementat validatorul de profil și matching în `jobhunter/matching.py`, cu date exclusiv fictive, fără informațiile reale ale utilizatorului.
- `tests/fixtures/profile_001.json` și `matches_001.expected.json`: un caz pentru fiecare status, cu explicații în română. Nu sunt rezultate LLM și nu au încă validare umană a sensului.
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 18 teste trecute, dintre care 9 noi pentru matching. Confirmate respingerea dovezilor inventate, a cerințelor omise, a versiunii greșite și a lipsei afirmate fără dovadă explicită.
- Actualizată preferința persistentă de limbă pentru interviu în AGENTS.md. Utilizatorul a răspuns ulterior corect la întrebarea lecției 4: lipsa mențiunii în CV nu demonstrează lipsa experienței.

## Ultimul checkpoint de lucru — scoring

- Implementat `jobhunter/scoring.py`: rubrică versionată și parametrizabilă, contribuții per cerință, interval min/max, acoperire a subsetului evaluabil, avertizări obligatorii și excluderi explicite pentru prioritate unknown.
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 29 de teste trecute, dintre care 11 noi pentru scoring. Verificate cazurile necunoscute, liste goale, rezultate lipsă/duplicate, configurație invalidă și avertizări la medie mare.
- Exemplul fictiv: 60–60%, acoperire 100% numai pentru cele trei cerințe cu prioritate cunoscută, R4 exclusă. Varianta cu engleză unknown: 40–80%, acoperire 60% pe același subset.
- Lecția 5 introdusă; întrebarea despre avertizarea obligatorie așteaptă răspuns. Nu există încă probabilități de angajare, ranking validat sau rezultate de inference.
