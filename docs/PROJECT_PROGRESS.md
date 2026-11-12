# Project progress

Data ultimei actualizări: 2026-11-12, Europe/Bucharest. Checkpointurile anterioare sunt păstrate ca istoric.

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

UI și profilul master sunt implementate și testate pe documente fictive, cu AppTest și HTTP. Utilizatorul raportează adăugarea CV-ului și extragerea textului; agentul nu a inspectat CV-ul, salvarea sau aprobarea profilului privat. Nu există reviewer autentificat, surse automate de joburi, CV tailoring/export sau benchmark reprezentativ. Fluxul AI produce drafturi până la confirmare. Ponderile și calitatea generală pe date reale nu sunt validate; modelul nu este recomandat pentru producție autonomă.

## Pasul următor propus

Utilizatorul reia analiza după repornirea Streamlit, cu profilul salvat și diagnosticele Ollama separate. Pentru jobul fictiv poate selecta manual cele șase cerințe, apoi revizui matching-ul. Nu pretindem remedierea confirmată a incidentului privat; calitatea extragerii și interpretării necesită evaluare separată. Preferință: etape cap-coadă, explicație la final.

## Ultimul checkpoint — finalizare Ollama și buget de matching

- Utilizatorul a raportat eroarea generică incomplete/truncated/unexpected model. Cauza privată rămâne neconfirmată; răspunsul și datele private nu au fost inspectate.
- Diagnostice distincte în română pentru limită, neterminat, model diferit și motiv de oprire neașteptat. Validarea completitudinii rămâne strictă, inclusiv când JSON-ul pare valid; fără retry automat sau date parțiale aplicate.
- Buget de matching versionat și proporțional cu numărul cerințelor: minimum 1024, maximum 4096, 2560 pentru șase cerințe. `chat_local` validează opțiunea per apel fără mutarea setărilor globale. Extragerea rămâne implicit la 1024.
- 174 teste trecute, șase noi. Test real local înainte/după pe șase cerințe și profil fictiv: ambele limite au reușit, câte 428 tokens, șase rezultate valide structural, fără decizie aplicată. Incidentul nu este reprodus; nu este benchmark semantic. Artefacte: docs/evaluations/completion_001.baseline.json și completion_001.current.json.
- Ghid și limite: docs/OLLAMA_COMPLETION.md. Nicio instalare, schimbare de model, acces la CV sau baza privată. Pentru utilizare trebuie repornit Streamlit.

## Ultimul checkpoint — citat AI invalid și selecție manuală a cerințelor

- Utilizatorul a raportat `Model quote does not occur verbatim in the source` la testare. Cauza exactă a diferenței de text nu este observată; nu s-a inspectat răspunsul privat și nu pretindem reproducerea incidentului.
- Eroarea de citat are tip distinct și mesaj în română. Validatorul rămâne strict, fără fuzzy matching sau repararea automată a citatului. O extragere eșuată nu produce matching ori rezultat parțial reutilizat.
- UI oferă explicit „Selectează manual din anunț”: rânduri exacte plus prioritate declarată de utilizator. `analyze_draft(selected_requirements=...)` revalidează sursa și apelează doar matching-ul; raportul marchează originea manuală. Schimbarea modului/selecției/priorității invalidează analiza și confirmarea.
- 168 teste trecute, 8 noi; teste UI cu transport simulat, fără apel real Ollama sau inspecție vizuală nouă. Nu au fost accesate CV-ul sau baza privată. Ghid: docs/LOCAL_EXTRACTION.md.
- Limite: selecție pe rânduri, completitudine și condiții OR/AND de verificat manual; extragerea automată poate încă eșua. Repornește Streamlit și folosește profilul salvat pentru reluare.

## Ultimul checkpoint — flux CV → fragmente → job

- Cerință a utilizatorului: încărcare CV, alegere blocuri prin selecție/copy-paste, comparație cu cerințele jobului. Implementate copy-paste exact cu citate la nivel de fragment (inclusiv sub-bloc/pagină), mai multe casete, eliminare prin golire și alegere explicită a contextului pentru text repetat.
- CV-ul este primul pas implicit, textul se citește automat, iar jobul apare după salvarea fragmentelor. Denumirile sunt simplificate; opțiunea confirmed_gap este avansată. Confirmarea sursei rămâne explicită, iar schimbările, inclusiv text invalid/restaurat, invalidează bifa veche.
- Originalul salvat poate fi refolosit prin „Alege alte fragmente din acest CV”. Selecțiile vechi și profilurile pe blocuri complete rămân compatibile. Nu se rescriu profiluri aprobate și nu sunt accesate date private pentru dezvoltare/testare.
- 160 teste trecute, 8 noi pentru fragmente și AppTest. Primul test cu mai multe fragmente a detectat capturarea greșită a contextului repetat; corectată înainte de rerularea reușită. Transportul AI este simulat în testele UI; nicio nouă evaluare a calității modelului.
- Limite: copy-paste din textul citit, fără selecție vizuală direct pe PDF sau capturare automată a textului evidențiat. Browserul nu a fost inspectat vizual. Repornește Streamlit; ghid actualizat în docs/MASTER_PROFILE.md.

## Ultimul checkpoint — diagnostic matching și recuperare conservatoare

- Utilizatorul a raportat eroarea generică de validare. Cauza exactă a acelei rulări rămâne necunoscută; nu am inspectat CV-ul, outputul privat sau baza locală.
- Validatorul strict produce categorii explicite. Schema matching-schema-2 restrânge dovezile la ID-urile reale și numărul rezultatelor. Promptul implicit rămâne matching-1; candidatul matching-2 nu a fost promovat.
- UI recuperează explicit rezultatele invalide ca unknown, fără dovezi, cu avertizare și revizuire obligatorie. Nu inventează lipsuri și nu salvează/aplică automat o decizie. Timeouturile/erorile de transport rămân erori. API/CLI rămân stricte implicit.
- 152 teste trecute, 10 noi, inclusiv AppTest fără persistență/aprobare implicită. Smoke check real prin Ollama pe profil master și job fictive: 4/4 rezultate valide structural, needs_review, nicio decizie aplicată. Nu este benchmark semantic sau reproducerea incidentului privat.
- Ghid: docs/MATCHING_DIAGNOSTICS.md; rezumat sintetic: docs/evaluations/matching_recovery_001.smoke.json. Pentru utilizare trebuie repornit Streamlit; profilul deja salvat nu necesită reimportare.

## Ultimul checkpoint — import CV și profil master

- Implementate cv_import.py, master_profile.py și profile_ui.py: TXT UTF-8, DOCX și PDF cu text, import manual, text integral, blocuri cu poziții/etichete, selecție de fapte exacte și confirmare explicită.
- Originalul este păstrat ca bytes plus text integral în tabele noi locale master_documents/master_profiles; fără ștergere sau migrare distructivă. Sursele QA/roluri vechi sunt păstrate inclusiv când nu sunt selectate ca fapte pentru matching.
- Profilul master are versiune bazată pe conținut și proveniență per fapt. Modificările invalidează versiunea/confirmarea; reîncărcarea revalidează sursa și citatele. Faptele rămân compatibile cu motorul existent. Metadatele reviewerului și fișierul CV sunt excluse din prompt; numai faptele selectate merg la matching local la cerere.
- UI: selecție separată Profil fictiv / Profil master din CV; un draft neaprobat blochează analiza. Salvarea și reîncărcarea profilului, folosirea la matching și auditul jobului au teste AppTest cu date fictive.
- 142 teste trecute, 19 noi. Parserele au teste sintetice TXT/DOCX/PDF, iar uploadul dintr-un browser nu a fost inspectat vizual. Testul UI folosește text lipit; transportul AI este simulat. Niciun CV real sau aprobare atribuită utilizatorului.
- master_profile_demo: 5 fapte, citate exacte, original identic și QA/roluri vechi păstrate, în bază temporară eliminată. Zero apeluri model/decizii de job. Rezumat în docs/evaluations/master_profile_001.demo.json, real_user_approval=false.
- pypdf 7.0.1 instalat numai în .venv; requirements și lock actualizate, pip check trecut. Server temporar 8502 verificat HTTP 200 / health ok și oprit; sesiunea utilizatorului de pe 8501 nu a fost oprită. Repornește pentru noile module.
- PDF scanat necesită OCR/import manual; PDF criptat și DOCX text boxes sunt respinse. Extragerea layoutului/ordinii are limite și necesită revizuire. Ghid și limite în docs/MASTER_PROFILE.md. Nu există încă CV tailoring sau export DOCX/PDF generat.

## Ultimul checkpoint — reguli structurate pentru limbi, etapă finalizată

- Implementat `jobhunter/languages.py`: limbă/nivel/dovezi în profil, condiții explicite all/any/unclear, nivel minim, logică deterministă pentru supported/partial/confirmed_missing/unknown. Control lexical limitat EN/RO pentru șase limbi, fără pretenție de parser semantic universal sau conversie CEFR.
- Adăugat `ReviewMaterial.language_review`, recalculare obligatorie înaintea aprobării, snapshoturi cu configurația și invalidare după modificări. Materialele fără adnotări păstrează serializarea/fingerprintul vechi; regresia este testată. Nu au fost migrate sau rescrise date private.
- UI: secțiunea opt-in „Limbi de lucru — reguli explicite în Python”, cu operator/nivel/dovezi, rezultate recalculate și confirmare nouă după editări. Nu se presupun competențe și nu se aprobă adnotări în numele utilizatorului. Corecțiile manuale și originalele sunt păstrate; regulile au prioritate pentru cerințele configurate.
- 123 de teste trecute (19 noi), inclusiv spaniolă fără informație, OR/AND, nivel parțial, dovezi despre alte limbi, operator greșit, condiții mixte, snapshot/aprobare veche, audit și invalidarea confirmării din UI.
- `python -m jobhunter.evaluate_structured_languages`: 8/8 pe outputurile salvate și adnotările explicite redactate de agent. Zero apeluri noi la model, zero aprobări/decizii aplicate. Este verificarea logicii pe intrări curate, nu precizie LLM sau adnotări aprobate de utilizator.
- Raport în docs/evaluations/structured_languages_001.md și JSON; toate baseline-urile LLM rămân intacte. Ghid în docs/STRUCTURED_LANGUAGES.md.
- Server temporar verificat pe 127.0.0.1:8502 (HTTP 200, health ok), apoi oprit. Serverul utilizatorului de pe 8501 nu a fost oprit. Nu s-a făcut inspecție vizuală în browser; testele UI sunt AppTest. Pentru modulele noi, utilizatorul trebuie să repornească propriul server.
- Nicio instalare, serviciu plătit, model nou sau acces la baza privată. Etapa limbilor este completă în limitele declarate; CV-ul real și extragerea semantică generală rămân neimplementate/nevalidate.

## Ultimul checkpoint — candidat matching-2, nepromovat

- Adăugate cinci cazuri noi (franceză optional/mandatory, spaniolă fără informație, reverse OR, AND) înainte de execuția lor. Au fost folosite o singură dată pentru verificarea candidatului, fără retuning după inspectarea rezultatelor.
- Matching-2 separă prioritatea de capacitate și cere explicit tratarea OR/AND și explicații în română. Modelul, opțiunile, scoring-ul și politica nu au fost schimbate. Schema include pentru candidat o descriere a limbii explicației.
- Candidat pe set inițial: 3/3 criterii complete, față de 2/3 în baseline. Pe set nou: 3/5 criterii complete și 4/5 eligibilitate. Eroare critică: spaniola nemenționată este dedusă ca lipsă din gap-uri germană/franceză; AND citează și franceza irelevantă.
- Comparație cu matching-1 pe același set nou: 2/5 criterii complete și 3/5 eligibilitate. Propune greșit eligible pentru franceză obligatorie și spaniolă nemenționată, folosind dovada de engleză. Nici vechea variantă nu este suficient de sigură autonom.
- Matching-2 nu este activat implicit: registry de prompturi în ai_matching.py, opt-in prin parametrul prompt_version și CLI --matching-prompt. Defaultul UI/backend rămâne matching-1, fără a afirma superioritate sau siguranță. Revizuirea continuă să fie obligatorie.
- 104 teste de cod trecute. Baseline-ul original nu a fost rescris. Rapoarte noi: language_eval_v2_baseline.*, language_eval_v2_new.*, language_eval_v1_new.*, plus matching_v2_comparison.md. Rulările cu diferențe au returnat exit code 1, fără retry selectiv.
- Explicațiile matching-2 au fragmente românești deformate și afirmații nejustificate; corectitudinea lor nu este certificată de concordanța statusurilor. Nu au fost aprobate semantic de utilizator.
- Nicio accesare/modificare a jobului sau bazei private, nicio aprobare/decizie aplicată, nicio instalare sau model nou. Protocol și limite în docs/MATCHING_V2.md.

## Ultimul checkpoint — evaluarea reală a limbilor

- Utilizatorul a confirmat că, după reîncărcarea UI, jobul și decizia De clarificat rămân vizibile și decizia apare o singură dată. Dovada este confirmarea din conversație, nu o inspecție independentă a bazei de către agent.
- Adăugat setul tests/fixtures/language_cases.json și runnerul `python -m jobhunter.evaluate_languages`, fără acces la stocarea joburilor/aprobărilor. Profil exclusiv fictiv: engleză profesională, lipsă explicită de germană.
- 101 teste locale trecute, inclusiv 7 noi pentru referințe, aritmetică, comparație pe citate, erori fără retry și lipsa transmiterii etichetelor așteptate către model.
- Rulare reală separată, 6 apeluri la llama3.2:3b, prompturi requirements-1/matching-1 nemodificate: criterii măsurate complete 2/3; extragere 3/3; eligibilitate propusă 3/3. Cazurile mandatory și OR au trecut criteriile; optional a ignorat P_DE și a produs unknown în loc de confirmed_missing.
- Explicațiile brute sunt în engleză, deși cerem română. Nu primesc verdict semantic automat. Eroarea optional nu schimbă eligibilitatea în exemplu, dar lărgește incertitudinea scorului la aproximativ 66,7–100%.
- Baseline complet în docs/evaluations/language_eval_001.json și raport lizibil language_eval_001.md. Evaluarea a returnat exit code 1 pentru diferență; aceasta nu este o eroare a unit tests și nu a fost ascunsă prin retry sau ajustarea promptului.
- Jobul revizuit de utilizator și baza privată nu au fost accesate/modificate. Nicio aprobare sau decizie aplicată. Rezultatele sunt drafturi pentru revizuire, nu joburi recomandate automat. Instrucțiuni și limite în docs/LANGUAGE_EVALUATION.md.

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
