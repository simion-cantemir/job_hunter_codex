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

Nu există încă integrare LLM, inference, UI, matching automat cu profilul, scoring sau sursă de joburi. Stocarea și validarea contractelor sunt testate; analiza AI end-to-end nu este implementată. Un citat sau ID valid nu certifică relevanța, prioritatea sau completitudinea interpretării. Lipsesc CV-ul real și benchmark-ul. Modelul instalat nu este încă recomandat pentru producție. Nicio comparație local/cloud măsurată.

## Pasul următor propus

Implementăm scoring determinist pe rezultatele validate: contribuții explicite, interval pentru necunoscute și avertizări pentru cerințe obligatorii. Înainte trebuie definit tratamentul priorității unknown, care nu primește automat greutatea unei cerințe obligatorii. Acceptance criteria: calcul repetabil și teste pentru unknown, cerințe lipsă și listă goală. Integrarea Ollama urmează separat. Exemplele sintetice rămân propuneri pentru revizuirea utilizatorului.

## Continuitate

Pentru reluare citește AGENTS.md, acest fișier și ROADMAP.md; apoi doar documentele taskului. Propunerile tehnice sunt în docs/DECISIONS.md, nu presupune acceptare explicită din partea utilizatorului. Utilizatorul preferă acum răspunsurile de interviu în română; engleza doar la cerere. PowerShell sandbox nu a putut porni (setup refresh error); operațiile shell au fost executate cu escaladare aprobată. Git poate necesita `-c safe.directory=C:/Projects/JobHunterAI` din cauza conturilor locale diferite; nu schimba configurația globală.

## Ultimul checkpoint de lucru — matching

- Implementat validatorul de profil și matching în `jobhunter/matching.py`, cu date exclusiv fictive, fără informațiile reale ale utilizatorului.
- `tests/fixtures/profile_001.json` și `matches_001.expected.json`: un caz pentru fiecare status, cu explicații în română. Nu sunt rezultate LLM și nu au încă validare umană a sensului.
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 18 teste trecute, dintre care 9 noi pentru matching. Confirmate respingerea dovezilor inventate, a cerințelor omise, a versiunii greșite și a lipsei afirmate fără dovadă explicită.
- Actualizată preferința persistentă de limbă pentru interviu în AGENTS.md. Lecția 4 introdusă; distincția lipsă/necunoscut nu este încă verificată prin răspunsul utilizatorului.
