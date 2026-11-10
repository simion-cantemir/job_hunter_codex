# Matching cu dovezi — versiunea 1

Implementare: `jobhunter/matching.py`. Validează comparații propuse; nu generează automat comparații și nu apelează un LLM.

## Intrări și trasabilitate

Profilul are o versiune și o listă de fapte cu ID unic, text și tip: `experience` sau `confirmed_gap`. Un `confirmed_gap` trebuie să provină dintr-o declarație explicită, nu din absența unei informații. Profilul real va necesita revizuire față de CV-ul master; validarea structurii nu confirmă adevărul biografic. În acest pas folosim numai profilul fictiv din `tests/fixtures/profile_001.json`.

Rezultatul de matching conține `schema_version: "1"`, `profile_version` și `matches`. Pentru fiecare cerință validată trebuie să existe exact un rezultat cu `requirement_id`, `status`, `evidence_ids` și `explanation`. Explicația este obligatorie. Versiunea profilului trebuie să corespundă, pentru a evita folosirea accidentală a unei evaluări pentru alt profil.

| Status | Regula de dovezi | Exemplu sintetic |
|---|---|---|
| supported | Cel puțin un fapt de tip experience | 4 ani de leadership pentru minimum 3 ani ceruți |
| partial | Cel puțin un fapt de tip experience; limitarea explicată | Engleză B1, fără confirmarea nivelului profesional cerut |
| confirmed_missing | Cel puțin un fapt de tip confirmed_gap | Declarație explicită că nu există experiență în AI adoption |
| unknown | Fără dovadă concludentă; lista evidence_ids este goală în v1 | Profilul nu menționează integrări cu furnizori |

Faptele sunt păstrate o singură dată în profil, iar matching-ul le citează prin ID, evitând duplicarea și rescrierea lor. Această trasabilitate explicită este mai ușor de verificat decât un paragraf liber. La introducerea CV-ului real vom avea nevoie și de legătura dintre fiecare fapt și sursa sa din document.

## Limite

Validatorul respinge ID-uri inventate sau duplicate, cerințe omise, versiuni diferite și concluzii fără tipul de dovadă cerut. Nu poate confirma că dovada este relevantă semantic: un fapt despre leadership nu poate demonstra engleza doar fiindcă are un ID valid. Corectitudinea sensului necesită revizuire și evaluări separate. Contradicțiile și dovezile neconcludente necesită revizuire umană; schema v1 nu implementează soluționarea automată a contradicțiilor.

`partial` este o etichetă propusă pentru exemplul de engleză, nu o echivalare universală între B1 și cerințele angajatorilor. Exemplul este redactat de agent și nu este încă revizuit de utilizator. Prioritatea jobului (`mandatory/optional/unknown`) și potrivirea profilului sunt două dimensiuni diferite.

Scoring-ul, persistarea analizelor și asocierea lor cu versiunea jobului nu sunt implementate încă. Înainte de persistarea rapoartelor vom adăuga legătura cu jobul și versiunea textului-sursă.
