# Interfața locală Streamlit

Data verificării: 2026-11-11.

## Pornire și utilizare

Din rădăcina proiectului:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Deschide `http://127.0.0.1:8501`. Oprește procesul din terminal cu Ctrl+C. Configurația din `.streamlit/config.toml` limitează serverul la loopback și dezactivează telemetry. Nu publica acest prototip și nu îl expune pe rețea: reviewerul este declarat de utilizator, fără autentificare.

1. Citește jobul fictiv precompletat sau introdu manual un text de test.
2. Profilul fictiv poate fi inspectat și modificat în secțiunea sa. CV-ul real nu este încă integrat.
3. „Încarcă analiza fictivă salvată” funcționează numai cu sursele inițiale exacte, fără inference. „Analizează cu Ollama local” apelează modelul deja instalat, după validarea profilului. Eșecul nu păstrează vechea analiză drept rezultat curent.
4. Fiecare cerință afișează citatul jobului, explicația originală și textul exact al dovezilor. Poți corecta prioritatea, statusul, dovezile și explicația. O corecție necesită motiv și revalidare; nu modifică citatul original.
5. Rezultatul și scorul sunt recalculate. Cerințele cu prioritate necunoscută rămân în afara scorului, cu contor vizibil; un scor mare nu compensează un blocaj obligatoriu confirmat.
6. Completează numele reviewerului, nota, bifează confirmarea materialului afișat și apasă butonul de aplicare. Nicio bifă sau simplă editare nu aplică o decizie.
7. Jobul, decizia și auditul se salvează local. Istoricul include și respingerile; nu se trimit aplicații, emailuri sau mesaje.

## Stare și date

`jobhunter/ui_session.py` păstrează în sesiunea browserului analiza curentă, corecțiile și înregistrarea aprobării. Inputul include întregul profil, nu doar numărul versiunii. Schimbarea titlului, jobului sau profilului invalidează analiza și confirmarea curente. Modificarea corecțiilor cere confirmare nouă, inclusiv când revii ulterior la o valoare anterioară. Reîncărcarea unei analize cere și ea confirmare nouă.

Rerun-urile obișnuite nu apelează modelul și nu aplică decizii. Repetarea aceleiași aplicări în aceeași sesiune folosește înregistrarea existentă, fără duplicate. O revizuire nouă a aceleiași analize poate adăuga o nouă decizie auditată pentru jobul deja salvat în sesiune.

Baza implicită este `data/private/jobhunter-demo.sqlite3`, ignorată de Git. `JOBHUNTER_DB_PATH` poate selecta o altă bază numai în directorul proiectului; testele folosesc baze temporare separate. UI nu deține o bază cloud și nu păstrează CV-uri. Datele introduse nu trebuie considerate protejate prin autentificare: rulează doar local.

Schimbarea profilului invalidează analiza/aprobarea activă din sesiune, dar nu șterge sau revocă retroactiv deciziile istorice. Acestea rămân asociate snapshoturilor revizuite atunci. Reevaluarea pe noul profil trebuie generată și aprobată separat. Deduplicarea între sesiuni și evaluarea automată a vechilor joburi nu sunt încă implementate.

## Instalare reproductibilă

Streamlit 1.67.0 și dependențele au fost instalate numai în `.venv`. Pentru refacerea mediului:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

`requirements.txt` fixează dependența directă; `requirements-lock.txt` păstrează toate versiunile instalate și verificate pe Windows/Python 3.13. Nu este un lock universal pentru orice sistem. `pip check` a trecut.

## Verificări și limite

- 94 de teste trecute, dintre care 11 noi folosesc Streamlit AppTest. Simulează încărcarea, fluxul complet AI cu transport mock, corecțiile, confirmarea, aplicarea auditată, rerun-uri, schimbarea sursei/profilului, erorile de inference, dovezile invalide și respingerea pentru o cerință obligatorie.
- Aprobarile din teste sunt declarate fictive și folosesc baze temporare. Raportul utilizatorului nu a fost aprobat de agent.
- Serverul a pornit pe 127.0.0.1:8501; pagina a returnat HTTP 200 și endpointul health `ok`. Serverul de verificare a fost oprit.
- AppTest verifică interacțiunile fără browser. Nu s-a efectuat inspecție vizuală într-un browser sau screenshot; nu s-a repetat inference real în testele UI. Backend-ul Ollama fusese verificat separat pe date fictive.
- Primul test al fluxului AI complet a găsit tuple Python în raport, unde validatorul cere liste JSON. Conversia a fost corectată la granița UI/backend; întreaga suită a trecut ulterior.
- Profilul și corecțiile suportă doar structura de bază existentă. Nu avem upload CV, editarea listei de cerințe omise, dashboard complet, surse automate, deduplicare globală, conturi sau validare de calitate reprezentativă.

Documentație oficială consultată: [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [widget behavior](https://docs.streamlit.io/develop/concepts/architecture/widget-behavior), [forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form). Am ales widgeturi reactive și identități distincte pentru confirmare, astfel încât editările să invalideze imediat aprobarea curentă; nu ascundem editările nesalvate într-un formular de confirmare.
