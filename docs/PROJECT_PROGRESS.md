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

## Nu este implementat sau validat

Nu există încă integrare LLM, inference, UI, scoring sau sursă de joburi. Componenta de stocare este testată; analiza AI end-to-end nu este implementată. Lipsesc CV-ul real și benchmark-ul. Modelul instalat nu este încă recomandat pentru producție. Nicio comparație local/cloud măsurată.

## Pasul următor propus

Faza 1, task mic: contractul de date pentru cerințe și un golden example sintetic revizuit împreună. Definim mandatory/optional/unknown, citatul sursă și dovezile din profil înainte de integrarea modelului. Acceptance criteria: exemplu coerent și validare care respinge cerințe fără dovezi verificabile. Nu extragem automat încă.

## Continuitate

Pentru reluare citește AGENTS.md, acest fișier și ROADMAP.md; apoi doar documentele taskului. Propunerile tehnice sunt în docs/DECISIONS.md, nu presupune acceptare explicită din partea utilizatorului. Întrebarea lecției 2 din jurnal așteaptă răspuns. PowerShell sandbox nu a putut porni (setup refresh error); operațiile shell au fost executate cu escaladare aprobată. Git poate necesita `-c safe.directory=C:/Projects/JobHunterAI` din cauza conturilor locale diferite; nu schimba configurația globală.
