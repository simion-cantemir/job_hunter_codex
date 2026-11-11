# Evaluarea cerințelor de limbă

## Cazuri și așteptări

Setul `tests/fixtures/language_cases.json` conține un profil exclusiv fictiv: engleză profesională declarată și lipsa explicită a cunoștințelor de germană. Nu reprezintă CV-ul sau nivelurile reale ale utilizatorului.

| Caz | Interpretare așteptată | Eligibilitate propusă |
|---|---|---|
| Engleză și germană obligatorii | Engleza susținută, germana lipsă confirmată | rejected |
| Engleză obligatorie, germana avantaj | Engleza susținută, lipsa germană rămâne opțională | eligible |
| Engleză SAU germană obligatorie | O singură cerință alternativă, satisfăcută prin engleză | eligible |

`eligible` înseamnă că nu există un blocaj în cerințele evaluate; nu înseamnă că se trimite o aplicație. Scorurile deterministe ale referințelor sunt 50%, aproximativ 66,7% și 100%, dar rezultatele diferite de eligibilitate depind de criteriile eliminatorii, nu doar de medie.

## Rulare și separarea verificărilor

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m jobhunter.evaluate_languages
```

Prima comandă rulează teste deterministe, fără inference real. A doua face până la șase apeluri locale (extragere și matching pentru fiecare caz), folosind modelul deja instalat `llama3.2:3b` și parametrii din adaptor. Nu apelează backend-ul SQLite sau funcțiile de aprobare. Jobul salvat de utilizator rămâne neatins.

Runnerul validează mai întâi referințele și consistența lor cu politica. Modelul primește numai textul-sursă și profilul, nu etichetele așteptate. Comparația este făcută ulterior în Python, prin citat și prioritate, apoi status și ID-uri de dovezi, independent de ordinea sau ID-urile cerințelor generate.

Se verifică separat:

- Extragerea exactă a citatelor și priorităților, inclusiv păstrarea alternativei OR într-o singură cerință.
- Concordanța statusurilor și seturilor de ID-uri cu referința.
- Eligibilitatea propusă și păstrarea rezultatului ca draft, fără decizie aplicată.

Explicațiile sunt păstrate integral pentru revizuire, dar nu primesc aprobare semantică automată. Un scor de concordanță mare nu înseamnă că toate reformulările sunt fidele. Validitatea citatelor și ID-urilor continuă să fie verificată înainte ca runnerul să primească draftul.

Baseline-ul inițial este păstrat în `docs/evaluations/language_eval_001.*`. Runnerul actual scrie implicit `language_eval_current.*` și refuză suprascrierea numelui baseline-ului; poți selecta `--output-name`, `--suite baseline|new` și `--matching-prompt matching-1|matching-2`. Un caz eșuat este înregistrat, fără retry automat, iar celelalte continuă. Exit code este 1 dacă există eșec sau diferențe măsurate, nu doar pentru erori de transport. O nouă execuție cu același nume curent reface acele fișiere.

## Limite

Cele trei cazuri sunt redactate de agent și nu formează un benchmark reprezentativ. Aprobarea utilizatorului pentru primul walkthrough nu se extinde asupra lor. Nu am schimbat prompturile pentru această primă evaluare. Nu generalizăm de aici calitatea pentru toate limbile, formulările, nivelurile, explicațiile sau joburile reale.

Unit tests validează mecanismul și referințele, nu performanța unui model real. Raportul de inference trebuie interpretat separat, iar profilul real se integrează numai după furnizarea CV-ului.

## Baseline observat — 2026-11-11

Rularea reală a executat cele șase apeluri, fără retry și fără schimbarea prompturilor:

| Caz | Extragere | Matching față de referință | Eligibilitate propusă |
|---|---|---|---|
| Germană obligatorie | Corectă în criteriile exacte | supported / confirmed_missing, dovezi corecte | rejected, așteptat |
| Germană opțională | Corectă în criteriile exacte | Germană unknown în loc de confirmed_missing | eligible, așteptat |
| Engleză OR germană | O singură cerință alternativă | supported, dovada P_EN | eligible, așteptat |

Concordanță pe toate criteriile măsurate: **2/3 cazuri**. Extragere: 3/3; eligibilitate propusă: 3/3. Aceste numere se referă numai la setul mic de aici și nu reprezintă o estimare de precizie generală.

Eroarea din cazul opțional: modelul afirmă că nu există dovezi concludente despre germană, ignorând declarația explicită P_DE. Validatorul structural permite unknown fără dovezi; nu poate detecta singur omisiunea semantică. Eligibilitatea nu este afectată aici, dar intervalul scorului devine inutil de larg (aproximativ 66,7–100%, în loc de 66,7% pentru referința evaluată complet).

La inspectarea outputului, explicațiile sunt în engleză, deși promptul matching-1 cere română. Limba și fidelitatea explicațiilor nu au fost incluse în verdictul automat; cele două cazuri trecute nu constituie aprobare a tuturor aspectelor outputului. Nu corectăm tacit raportul brut.

Extragere/matching, în secunde observate: 33,492/3,196 pentru mandatory; 2,585/3,087 pentru optional; 2,392/2,650 pentru OR. Nu comparăm performanța fără controlul încărcării modelului/cache-ului. Cele **101 teste locale au trecut**, separat de această evaluare care a încheiat cu exit code 1 pentru diferența găsită.

Ulterior a fost testat [matching-2](MATCHING_V2.md): rezolvă cele trei cazuri inițiale, dar trece numai 3/5 cazuri noi și propune o respingere greșită pentru spaniolă nemenționată. Candidatul rămâne experimental. Sunt necesare dovezi asociate explicit limbilor și reguli verificabile, nu doar un prompt mai detaliat.
