# Matching-2 — modificare controlată de prompt

## Problema și schimbarea

Baseline-ul matching-1 a ignorat lipsa explicită de germană în cazul opțional, producând unknown. Eligibilitatea finală era corectă, dar intervalul scorului era nejustificat de larg. Explicațiile erau și în engleză, deși se solicitase română.

În `jobhunter/ai_matching.py`, matching-2:

- Separă explicit capacitatea candidatului de prioritatea cerinței: o lipsă declarată rămâne confirmed_missing chiar pentru un avantaj opțional.
- Cere verificarea sensului integral pentru OR și AND, fără a transforma lipsa unei alternative în lipsa tuturor alternativelor.
- Păstrează unknown pentru absența informațiilor și evită folosirea unui gap despre altă competență.
- Dă instrucțiunile în principal în română și descrie în schema JSON limba explicației.
- Cere fidelitate față de sursă, fără a transforma participarea la cursuri în înscriere viitoare.

Nu am schimbat modelul, parametrii de inference, rubricile de scoring sau politica de eligibilitate. Nu am introdus reguli care să rescrie automat concluziile modelului. Validatorii și revizuirea umană rămân necesare; promptul nu garantează singur corectitudinea.

## Protocolul acestei verificări

1. Păstrăm baseline-ul original în `language_eval_001.json` și `.md`; CLI refuză suprascrierea acestui nume.
2. Definim cinci cazuri suplimentare în `tests/fixtures/language_checks_new.json`, cu așteptări înainte de execuție: franceză opțională, franceză obligatorie, spaniolă nemenționată, OR în ordine inversă, condiție combinată AND.
3. Modificăm promptul o singură dată pentru această verificare, apoi rulăm cele trei cazuri existente și setul nou. Nu ajustăm versiunea după inspectarea rezultatului setului nou.
4. Modelul primește numai jobul și profilul fiecărui set. Referințele sunt comparate în Python, nu incluse în prompt.

```powershell
.\.venv\Scripts\python.exe -m jobhunter.evaluate_languages --suite baseline --matching-prompt matching-2 --output-name language_eval_v2_baseline
.\.venv\Scripts\python.exe -m jobhunter.evaluate_languages --suite new --matching-prompt matching-2 --output-name language_eval_v2_new
```

Cele cinci cazuri noi sunt redactate de același agent, nu constituie un test independent creat de o altă persoană sau un benchmark reprezentativ. Sunt o verificare suplimentară pe formulări diferite, nu o estimare statistică a preciziei generale. Fidelitatea și limba explicațiilor nu sunt certificate automat prin concordanța etichetelor.

## Rezultate și decizie

| Set | matching-1 | matching-2 |
|---|---|---|
| Trei cazuri inițiale | 2/3 criterii complete, 3/3 eligibilitate | 3/3 criterii complete, 3/3 eligibilitate |
| Cinci cazuri noi | 2/5 criterii complete, 3/5 eligibilitate | 3/5 criterii complete, 4/5 eligibilitate |

Matching-1 pe setul nou a fost rulat o dată după evaluarea candidatului, pentru a evita compararea unor seturi diferite. Nu am modificat prompturile după inspectarea cazurilor noi și nu am repetat apelurile pentru a selecta rezultate convenabile.

Probleme importante:

- Matching-2 corectează gap-ul opțional inițial și îl transferă la franceză opțională. Recunoaște și franceza obligatorie lipsă.
- La spaniolă nemenționată, matching-2 folosește greșit lipsurile de germană și franceză pentru a propune rejected. Așteptarea este unknown / needs_review.
- La AND, matching-2 propune statusul și respingerea corecte, dar citează suplimentar și irelevant lipsa francezei. Matching-1 avea aici dovezile corecte: regresie de trasabilitate în setul nou.
- Matching-1 propune greșit eligible pentru franceză obligatorie și spaniolă nemenționată, folosind dovada despre engleză. Nu îl declarăm sigur doar fiindcă nu activăm candidatul.
- Explicațiile matching-2 folosesc română, dar conțin formulări deformate și uneori afirmații false; de exemplu, sugerează că persoana nu vorbește niciun alt limbaj, deși profilul confirmă engleza. Nu este rezolvată calitatea explicațiilor.

**Decizie: matching-2 nu este promovat ca implicit.** Rămâne selectabil explicit pentru evaluări prin `--matching-prompt matching-2`. `propose_matches()` și UI folosesc în continuare matching-1. Niciuna dintre variante nu este validată pentru filtrare autonomă, iar toate propunerile cer în continuare revizuire umană. Rolul defaultului vechi este continuitatea implementării, nu o afirmație că ar fi superior ori suficient de sigur.

Au trecut **104 teste de cod**, inclusiv selecția explicită a versiunii experimentale, protejarea baseline-ului și consistența celor cinci referințe noi. Rulările de inference cu diferențe au returnat exit code 1; unit tests nu validează automat sensul outputului.

Artefacte:

- `docs/evaluations/language_eval_001.*`: baseline original, nemodificat.
- `docs/evaluations/language_eval_v2_baseline.*`: candidatul pe setul inițial.
- `docs/evaluations/language_eval_v2_new.*`: prima verificare a candidatului pe setul nou.
- `docs/evaluations/language_eval_v1_new.*`: comparație matching-1 pe același set nou.

Următorul pas propus: reprezentarea limbilor din profil și a condițiilor OR/AND prin date explicite, cu revizuire și reguli Python pentru evaluare. Un ID de tip experience/confirmed_gap nu garantează relevanța pentru limba cerută; avem nevoie de o asociere verificabilă între competență și dovadă. Nu implementăm un regex fragil care să pretindă că rezolvă orice formulare de job și nu adăugăm agenți sau modele plătite pentru a masca rezultatul.
