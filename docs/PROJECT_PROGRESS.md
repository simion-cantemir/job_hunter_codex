# Project progress

Data ultimei actualizări: 2026-11-11, Europe/Bucharest. Checkpointurile anterioare sunt păstrate ca istoric.

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

UI locală este implementată și testată cu AppTest și HTTP. Utilizatorul a parcurs și confirmat primul exemplu fictiv, inclusiv corecția R2 și mesajul de salvare cu audit. Nu există reviewer autentificat sau sursă automată de joburi. Fluxul AI continuă să producă drafturi până la confirmarea explicită din UI. Ponderile nu sunt calibrate pe joburi reale. Lipsesc CV-ul real și benchmark-ul reprezentativ. Modelul nu este încă recomandat pentru producție. Nicio comparație local/cloud măsurată.

## Pasul următor propus

Set mic de cazuri suplimentare (limbă obligatorie/opțională/alternative, informații lipsă și prompt injection) pentru evaluarea semantică și stabilirea limitelor MVP. Primul walkthrough pe exemplul fictiv este încheiat, fără a echivala un singur caz cu validarea generală. CV-ul real numai după ce utilizatorul îl furnizează. Aprobarea acestui exemplu nu se extinde asupra altor analize.

## Acceptance walkthrough confirmat de utilizator

- Utilizatorul a deschis UI și a comparat R2 cu P2; a identificat schimbarea nejustificată de sens despre cursurile de engleză.
- Ghidat prin conversație, a corectat explicația și a confirmat că scorul rămâne 60% și eligibilitatea De clarificat.
- A confirmat R3: opțională, lipsă confirmată, P3; R4: prioritate și matching necunoscute, fără dovezi; R1: obligatorie, susținută, P1 (4 ani față de minimum 3).
- După indicațiile pentru completarea reviewerului/notei și confirmare, utilizatorul a raportat că analiza a fost salvată și a apărut mesajul de succes cu audit.
- Dovezi: confirmări explicite ale utilizatorului în conversație. Agentul nu a inspectat direct browserul sau baza privată și nu pretinde o verificare independentă a persistenței ori a conținutului notei.
- Walkthrough-ul este o revizuire umană a unui exemplu fictiv, nu aprobare pentru joburi reale și nu un benchmark. Nu s-au trimis aplicații sau mesaje. În acest pas au fost actualizate numai documentele; testele de cod nu au fost rerulate.

## Ultimul checkpoint — UI locală, 2026-11-11

- Utilizatorul a răspuns corect că modificarea profilului invalidează aprobarea veche. Istoricul rămâne legat de snapshotul aprobat anterior; nu ștergem retroactiv deciziile.
- Implementate `app.py`, `.streamlit/config.toml` și `jobhunter/ui_session.py`: import text, profil fictiv editabil, încărcare analiză salvată, apel local AI, surse vizibile, corecții cu motiv, raport descărcabil, confirmare și istoric în SQLite.
- Streamlit 1.67.0 și dependențele instalate numai în `.venv`. `requirements.txt` fixează dependența directă; requirements-lock.txt păstrează versiunile testate pe Windows/Python 3.13. `pip check` a trecut. Server loopback și telemetry dezactivată, fără publicare.
- 94 de teste trecute, inclusiv 11 AppTest pentru interacțiuni UI. Testele de confirmare folosesc reviewer fictiv și baze temporare, fără aprobări atribuite utilizatorului. Transportul AI este mock; modelul real nu a fost apelat din nou în acest pas.
- Testul fluxului AI complet a găsit o incompatibilitate tuple Python/listă JSON la integrarea cu review. Conversia la contractul JSON a fost corectată, apoi suita a trecut.
- Server pornit pentru verificare pe 127.0.0.1:8501: pagină HTTP 200, health ok. Serverul de verificare a fost oprit. Nu avem screenshot sau test vizual într-un browser; AppTest simulează UI fără browser.
- Baza UI implicită: data/private/jobhunter-demo.sqlite3, ignorată de Git. În acest pas doar testele au simulat aplicări în baze temporare. Profilul real/CV-ul nu este integrat, deduplicarea între sesiuni și dashboard-ul complet rămân neimplementate.
- Pornire: `.\.venv\Scripts\python.exe -m streamlit run app.py`. Detalii și limite în docs/LOCAL_UI.md.

## Ultimul checkpoint — aprobare backend și aplicare auditată

- Implementat `jobhunter/approval.py`: confirmare explicită, reviewer declarat, notă, timestamp UTC, snapshoturi și rezultat calculat. Hashul materialului de revizuire este diferit de hashul analizei originale și include corecțiile plus rezultatul rubricii/politicii. Schimbarea lor invalidează aprobarea.
- `apply_approved_review()` păstrează decizia și auditul în aceeași tranzacție SQLite; replay-ul identic nu dublează datele. `review_approvals` este o tabelă nouă, fără rescrierea datelor existente. `approval_history()` oferă snapshotul complet.
- 83 de teste trecute: 14 noi pentru aprobări, date schimbate, istoric corecții, sursă greșită, idempotency și rollback la eșecul auditului. Testul de lipsă obligatorie aprobată fictiv exclude jobul, fără ștergere.
- Rulat `.\.venv\Scripts\python.exe -m jobhunter.approval_demo`: reviewer explicit fictiv, bază temporară eliminată la final, 1 decizie și 1 aprobare simulate, status needs_review, scor 60%, fără duplicate. Rezumat în docs/evaluations/approval_001.demo.json cu real_user_approval=false.
- Nicio nouă inference, dependență, bază persistentă sau aprobare atribuită utilizatorului. Review-ul real rămâne pending. Numele reviewerului nu este autentificat și hashurile nu sunt semnături.

## Ultimul checkpoint — raport lizibil și corecții propuse

- Implementate `jobhunter/review.py` și `.\.venv\Scripts\python.exe -m jobhunter.review_demo`. Citim analiza deja salvată; fără inference, rețea sau modificări SQLite.
- Generate docs/evaluations/review_001.md și review_001.proposal.json: citate, dovezi exacte, text integral al jobului/profilului, explicații originale și corecția R2 propusă de agent, neaprobată.
- Snapshoturile original/revizuit și nota corecției sunt păstrate separat; fingerprintul leagă corecțiile de raport, sursă și profilul furnizat. Nu reprezintă semnătură sau aprobare umană. Raportul istoric nu avea hashul profilului, deci identitatea lui nu este certificată retroactiv.
- 69 de teste trecute (9 noi pentru review). Demo executat și output inspectat textual. Prima execuție a demo-ului a identificat eroarea de afișare a diacriticelor în terminalul Windows; mesajele terminalului sunt acum ASCII, fișierele rămân UTF-8. Demo-ul a fost rerulat cu succes.
- Corecțiile pot modifica numai cerințe existente și sunt revalidate; scorul și eligibilitatea sunt recalculate. Nicio corecție nu autorizează automat o decizie.

## Ultimul checkpoint — matching local și analiză provizorie

- Utilizatorul a explicat corect diferența dintre JSON valid și interpretare corectă; am precizat că formatul JSON este cerut explicit de aplicație.
- Reutilizat transportul prin `chat_local()`; adăugat `jobhunter/ai_matching.py` cu prompt matching-1 și validarea dovezilor/versiunii. `jobhunter/analysis.py` orchestrează extragere, matching, scoring și eligibilitate, numai ca AnalysisDraft.
- Demo nou: `.\.venv\Scripts\python.exe -m jobhunter.analyze_demo`. Nu scrie în SQLite; `review_status=pending_semantic_review`, `decision_applied=false`, inclusiv când eligibilitatea propusă este rejected.
- 60 de teste trecute în suita locală, 9 noi pentru matching asistat și orchestrare. Verificate dovezi inventate/lipsă, eroare transport fără fallback, intrare invalidă înainte de inference, revalidare la granița workflow-ului și menținerea draftului pending chiar la respingere propusă.
- Rulare reală combinată pe job/profil fictive: extragere 2,817 secunde (396/102 tokens), matching 4,870 secunde (692/318 tokens). Statusuri și ID-uri de dovezi: 4/4 identice cu referința redactată de agent. Scor provizoriu 60%, eligibilitate propusă needs_review. Raport în docs/evaluations/ollama_analysis_001_run_001.json.
- Problemă observată: explicația despre engleză este nefirească și schimbă faptul „participă la cursuri” în „în curs de înscriere”. Raportul păstrează outputul brut; 4/4 nu validează explicațiile. Nu am optimizat promptul pe acest singur rezultat și nu îl declarăm benchmark.
- Nicio nouă dependență, model sau serviciu plătit. Date exclusiv fictive; GPU și efectele cache-ului nu au fost măsurate.

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
