# Job Hunter AI

Asistent local de căutare a joburilor și proiect practic de AI Engineering, AI Product și Technical Delivery Management.

## Status

2026-11-12: flux simplificat **CV → fragmente alese prin copy-paste sau selecție → comparație cu jobul**. 180 teste trecute. Ambele etape AI au minimum 2048 tokens; UI constrânge citatele la sursă. [Testul automat ajunge la revizuire, dar include o frază introductivă în plus](docs/OLLAMA_COMPLETION.md); interpretarea nu este validată automat. Poți [selecta manual cerințele](docs/LOCAL_EXTRACTION.md). CV-urile salvate pot fi refolosite; conținutul privat nu a fost inspectat de agent.

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
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mediul `.venv` este deja pregătit pe acest laptop; pentru utilizare ai nevoie doar de ultima comandă. Deschide `http://127.0.0.1:8501`. Pentru primul tur, folosește butonul „Încarcă analiza fictivă salvată”, fără apel AI. Detalii și limite în [LOCAL_UI.md](docs/LOCAL_UI.md). Oprire: Ctrl+C în terminal.

Pentru verificări:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Crearea mediului și instalarea sunt necesare doar la setup/refacere. Streamlit 1.67.0 și pypdf 7.0.1 sunt instalate local în `.venv`; celelalte componente backend folosesc biblioteca standard. Interpreterul se apelează direct, fără activare sau modificări ExecutionPolicy. Folosim `python`, nu presupunem funcționarea launcherului `py`.

Testele folosesc joburi sintetice și baze temporare în proiect, închise și eliminate automat după verificare. `jobhunter/storage.py` păstrează textul original prin interogări parametrizate. Testele UI simulează transportul AI, fără inference real. Baza UI este locală în `data/private/`, ignorată de Git.

Prima componentă din Faza 1 este [contractul cerințelor](docs/REQUIREMENTS_CONTRACT.md): validator Python și un exemplu sintetic de extragere așteptată. Verifică structura și proveniența citatelor; nu reprezintă încă analiză AI sau validare semantică.

Am adăugat și [contractul de matching](docs/MATCHING_CONTRACT.md): profil versionat, dovezi referite prin ID și stările supported/partial/confirmed_missing/unknown. [Scoring-ul determinist](docs/SCORING.md) produce contribuții explicite, intervale și avertizări. [Eligibilitatea](docs/ELIGIBILITY.md) exclude joburile cu cerințe obligatorii confirmate ca neîndeplinite pe date revizuite, cu motive și istoric în SQLite. Există 180 teste de cod trecute. Fluxul AI produce propuneri; aplicarea necesită aprobare.

## CV master și profil verificat

Repornește Streamlit. Modul implicit este **„Profil master din CV”**: încarci TXT/DOCX/PDF cu text sau lipești CV-ul integral, apoi copiezi fragmentele dorite în casete separate ori selectezi blocuri întregi. Textul se citește automat, iar fiecare fragment este verificat în sursă. Apeși **„Salvează fragmentele și continuă la job”**, completezi jobul și pornești comparația. Pentru un CV salvat poți folosi **„Alege alte fragmente din acest CV”**. Originalul și istoricul QA/rolurile vechi rămân păstrate local. PDF-urile scanate nu au încă OCR.

[Ghid și limite](docs/MASTER_PROFILE.md). Nu este necesar să trimiți CV-ul în chat pentru importul din aplicație. Nu există încă generare de CV-uri personalizate.

## Evaluarea cerințelor de limbă

```powershell
.\.venv\Scripts\python.exe -m jobhunter.evaluate_languages
```

Trei cazuri fictive, cu până la șase apeluri locale, fără modificarea bazei private. [Raportul primei rulări](docs/evaluations/language_eval_001.md) păstrează eroarea observată la matching-ul germană opțională. Exit code 1 semnalează diferențe, chiar dacă unit tests trec. Vezi [metoda și limitele](docs/LANGUAGE_EVALUATION.md).

[Comparația prompturilor](docs/evaluations/matching_v2_comparison.md) arată de ce matching-2 nu a fost activat implicit. [Protocolul](docs/MATCHING_V2.md) include comenzile pentru selectarea explicită a candidatului și a setului nou, păstrând baseline-ul original.

Pentru soluția verificabilă, vezi [limbile structurate](docs/STRUCTURED_LANGUAGES.md). În UI, după încărcarea analizei, poți activa „Evaluează limbile pe date structurate”, selecta nivelul, dovezile și operatorul și revizui calculul înainte de confirmare. Nu sunt deduse automat competențe din CV. Repornește serverul existent pentru a încărca noua versiune.

```powershell
.\.venv\Scripts\python.exe -m jobhunter.evaluate_structured_languages
```

[Raportul 8/8](docs/evaluations/structured_languages_001.md) folosește outputuri deja salvate și adnotări fictive explicite, fără inference sau modificări în baza privată.

## Revizuire fără un nou apel AI

```powershell
.\.venv\Scripts\python.exe -m jobhunter.review_demo
```

Deschide [raportul lizibil](docs/evaluations/review_001.md). Sunt afișate sursele, explicația originală și corecția propusă de agent pentru engleză, fără aprobare implicită. [Mecanismul de revizuire](docs/REVIEW.md) leagă modificările de analiza exactă și păstrează originalul. [Aprobarea backend](docs/APPROVAL.md) poate fi folosită acum din UI locală, cu nume, notă și confirmare explicită. Agentul nu a aprobat analiza în numele utilizatorului.

Simulare tehnică de aprobare, cu reviewer fictiv și bază temporară:

```powershell
.\.venv\Scripts\python.exe -m jobhunter.approval_demo
```

Această comandă nu înregistrează o aprobare reală din partea ta și nu modifică o bază persistentă.

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
