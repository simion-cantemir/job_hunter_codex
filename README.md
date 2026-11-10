# Job Hunter AI

Asistent local de căutare a joburilor și proiect practic de AI Engineering, AI Product și Technical Delivery Management.

## Status

2026-11-10: Faza 1 — stocare SQLite, contracte, scoring, eligibilitate și flux local de extragere + matching pe date fictive verificate. Rapoartele AI sunt propuneri pentru revizuire, fără decizii aplicate automat. Nu există încă interfață. Directorul inițial era gol; niciun prototip anterior nu a fost găsit aici. Nu am căutat în afara directorului furnizat.

## Mediu verificat

| Componentă | Rezultat |
|---|---|
| OS | Windows 11 Pro, 64-bit, 10.0.26300 |
| Model sistem | Lenovo, identificator raportat 83F0 |
| RAM | 31,4 GiB raportați de sistem |
| GPU | NVIDIA GeForce RTX 5070 Laptop GPU |
| VRAM | 8151 MiB; separată de RAM |
| Driver NVIDIA | 581.15 |
| Spațiu liber C: | 505,5 GiB la diagnostic |
| Python | `python`: 3.13.17; `py -0p` nu identifică instalări |
| SQLite | 3.50.4 prin biblioteca standard Python |
| Git | 2.56.0.windows.4 |
| Ollama | 0.40.11; `ollama list` funcționează |
| Model instalat | `llama3.2:3b`, 2,0 GB pe disc; prima inference verificată pe job fictiv |
| Pachete Python | streamlit, pytest, python-docx, pydantic, requests nu sunt disponibile în interpreterul verificat |

WMI a necesitat acces aprobat în afara sandbox-ului. Rezultatul inițial Get-PSDrive cu zero spațiu liber nu a fost considerat valid; spațiul a fost verificat prin Win32_LogicalDisk. Nu s-au instalat programe sau modele.

## Instalare și utilizare

Din rădăcina proiectului, în PowerShell:

```powershell
python -m venv .venv --without-pip
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Crearea mediului este necesară doar prima dată. Deocamdată folosim exclusiv biblioteca standard; nu avem nevoie de pip sau downloaduri. Interpreterul se apelează direct, fără activare sau modificări ExecutionPolicy. Folosim `python`, nu presupunem funcționarea launcherului `py`.

Testele folosesc joburi sintetice și baze temporare în proiect, închise și eliminate automat după verificare. `jobhunter/storage.py` păstrează textul original prin interogări parametrizate. Nu execută analiza jobului și nu accesează Ollama. Instrucțiunile Streamlit vor fi adăugate după implementare și verificare.

Prima componentă din Faza 1 este [contractul cerințelor](docs/REQUIREMENTS_CONTRACT.md): validator Python și un exemplu sintetic de extragere așteptată. Verifică structura și proveniența citatelor; nu reprezintă încă analiză AI sau validare semantică.

Am adăugat și [contractul de matching](docs/MATCHING_CONTRACT.md): profil fictiv versionat, dovezi referite prin ID și stările supported/partial/confirmed_missing/unknown. [Scoring-ul determinist](docs/SCORING.md) produce contribuții explicite, intervale și avertizări. [Eligibilitatea](docs/ELIGIBILITY.md) exclude joburile cu cerințe obligatorii confirmate ca neîndeplinite pe date revizuite, cu motive și istoric în SQLite. Există 69 de teste trecute în total. Fluxul AI nou produce numai propuneri și nu aplică această excludere.

## Revizuire fără un nou apel AI

```powershell
.\.venv\Scripts\python.exe -m jobhunter.review_demo
```

Deschide [raportul lizibil](docs/evaluations/review_001.md). Sunt afișate sursele, explicația originală și corecția propusă de agent pentru engleză, fără aprobare implicită. [Mecanismul de revizuire](docs/REVIEW.md) leagă modificările de analiza exactă și păstrează originalul. Nu există încă acțiune de aprobare/aplicare.

## Extragere locală demonstrabilă

Cu Ollama pornit și modelul `llama3.2:3b` deja instalat:

```powershell
.\.venv\Scripts\python.exe -m jobhunter.extract_demo
```

Comanda analizează doar exemplul fictiv și afișează JSON în terminal, fără modificarea bazei de date. Prima rulare reală: 4/4 citate și priorități identice cu referința, aproximativ 37,4 secunde. Un singur caz nu demonstrează precizia generală. Vezi [integrarea și limitele](docs/LOCAL_EXTRACTION.md) și [rezultatul observat](docs/evaluations/ollama_job_001_run_001.json). Testele obișnuite simulează transportul și nu pornesc inference.

## Arhitectură și progres

Pentru [analiza combinată pe profil fictiv](docs/LOCAL_MATCHING.md):

```powershell
.\.venv\Scripts\python.exe -m jobhunter.analyze_demo
```

Prima rulare: 4/4 statusuri și referințe la dovezi identice cu referința; scor provizoriu 60%, eligibilitate propusă needs_review, fără modificări SQLite. Explicația modelului despre engleză conține o eroare de reformulare, documentată în raport; acest rezultat nu este o validare semantică completă.

MVP propus: Streamlit → servicii Python → SQLite; adaptor LLM local pentru extragere, validare și scoring în Python. Vezi [arhitectura](docs/ARCHITECTURE.md), [planul](ROADMAP.md), [progresul](docs/PROJECT_PROGRESS.md) și [jurnalul educațional](docs/LEARNING_JOURNAL.md).
