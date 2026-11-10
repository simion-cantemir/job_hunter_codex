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

Nu există încă integrare LLM, inference, UI, matching cu profilul, scoring sau sursă de joburi. Stocarea și validarea contractului sunt testate; analiza AI end-to-end nu este implementată. Un citat valid nu certifică relevanța, prioritatea sau completitudinea extragerii. Lipsesc CV-ul real și benchmark-ul. Modelul instalat nu este încă recomandat pentru producție. Nicio comparație local/cloud măsurată.

## Pasul următor propus

Revizuim primul golden example cu utilizatorul, apoi definim un profil exclusiv sintetic și dovezile de matching pentru fiecare cerință. Acceptance criteria: diferențiem susținut/parțial/lipsă confirmată/necunoscut, fără a deduce o lipsă din simpla absență a unei informații. După acest pas putem conecta extracția locală prin Ollama și compara răspunsul cu exemplul de referință.

## Continuitate

Pentru reluare citește AGENTS.md, acest fișier și ROADMAP.md; apoi doar documentele taskului. Propunerile tehnice sunt în docs/DECISIONS.md, nu presupune acceptare explicită din partea utilizatorului. Întrebarea lecției 3 din jurnal așteaptă răspuns. PowerShell sandbox nu a putut porni (setup refresh error); operațiile shell au fost executate cu escaladare aprobată. Git poate necesita `-c safe.directory=C:/Projects/JobHunterAI` din cauza conturilor locale diferite; nu schimba configurația globală.
