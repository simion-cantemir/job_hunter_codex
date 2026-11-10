# Contractul cerințelor — versiunea 1

Implementat în `jobhunter/requirements.py`; nu este încă un extractor LLM.

## Date acceptate

Obiect JSON cu exact `schema_version` (string `"1"`) și `requirements` (listă). Fiecare cerință conține exact:

| Câmp | Sens |
|---|---|
| id | Identificator text nevid, unic în extragere |
| priority | `mandatory`, `optional` sau `unknown` |
| quote | Citat exact, nevid, din textul jobului |
| start / end | Poziții în caractere Unicode Python; start inclusiv, end exclusiv |

Nu generăm reformulări în acest prim contract: citatul păstrează cerința originală. `unknown` înseamnă că obligativitatea nu este clară; nu indică dacă profilul candidatului satisface cerința. Matching-ul va avea un contract separat.

Validarea verifică tipurile, câmpurile, identificatorii și egalitatea `source[start:end] == quote`. Datele invalide produc `ValueError`, fără corecții sau presupuneri automate. O listă goală este acceptată, dar nu demonstrează că jobul nu conține cerințe; completitudinea va fi evaluată separat. Folosim exact textul sursă primit de validator, fără normalizări ulterioare. În adaptorul viitor vom putea calcula pozițiile în cod din citate, cu tratarea explicită a citatelor repetate, fără a cere modelului să numere caractere.

## Primul golden example, propus de agent

Sursa este `tests/fixtures/job_001.txt`; rezultatul așteptat este `tests/fixtures/job_001.expected.json`. Compania și jobul sunt fictive. Acesta este un singur caz de referință, nu un benchmark reprezentativ și nu a fost încă revizuit de utilizator.

| Cerință | Prioritate așteptată | Justificare |
|---|---|---|
| At least 3 years of engineering team leadership. | mandatory | Apare în secțiunea Required |
| Professional working proficiency in English. | mandatory | Apare în secțiunea Required |
| Experience with AI adoption initiatives. | optional | Apare în secțiunea Nice to have |
| Experience with vendor integrations. | unknown | Sursa declară că prioritatea nu este specificată |

Salariul nu este menționat: rămâne necunoscut, fără valoare inventată. Contractul curent nu extrage metadate de job sau dovezi din CV. Nu folosește informațiile autobiografice ale utilizatorului drept profil verificat.

## Ce garantează și ce nu

Un citat valid dovedește prezența textului în sursă. Nu dovedește că este cerință, că prioritatea este corectă sau că instrucțiunile malițioase dintr-un job sunt sigure. Prioritatea, relevanța și completitudinea necesită evaluări semantice separate. Datele extrase nu autorizează acțiuni externe.
