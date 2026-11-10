# Scoring determinist — rubrica 1

Implementare: `jobhunter/scoring.py`. Primește cerințe și matching deja validate; nu interpretează singur CV-ul și nu validează semantic dovezile. Funcția verifică și corespondența exactă între cerințe și rezultate, categoriile și configurația numerică.

## Reguli inițiale

| Element | Valoare implicită |
|---|---|
| Cerință mandatory | Pondere 2 |
| Cerință optional | Pondere 1 |
| Prioritate unknown | Exclusă explicit, cu ID și avertizare |
| Matching supported | Contribuție 1 × pondere |
| Matching partial | Contribuție 0,5 × pondere |
| Matching confirmed_missing | Contribuție 0 |
| Matching unknown | Contribuție între 0 și pondere |

Minimum = suma contribuțiilor minime / suma ponderilor incluse × 100. Maximum folosește contribuțiile maxime. Acesta este un interval aritmetic, nu un interval statistic de încredere.

Acoperirea = ponderea cerințelor cu matching diferit de unknown / suma ponderilor incluse × 100. Acoperire 100% nu înseamnă compatibilitate 100%, nici CV complet: include și evaluări parțiale sau lipsuri confirmate și se referă numai la subsetul cu prioritate cunoscută. Cerințele excluse sunt întotdeauna raportate separat.

Lista goală sau lipsa tuturor priorităților produce scor și acoperire indisponibile (`None`), nu zero. Pentru o cerință obligatorie cu matching partial, confirmed_missing sau unknown, raportul păstrează o avertizare distinctă indiferent de medie. [Politica separată de eligibilitate](ELIGIBILITY.md), acceptată ulterior de utilizator, respinge jobul pentru mandatory confirmed_missing; scorul nu poate anula acest filtru.

Configurația numerică este parametrizabilă în Python; raportul include întreaga rubrică, versiunea și contribuțiile individuale. Schimbarea parametrilor poate schimba rezultatul; de aceea versiunea singură nu înlocuiește salvarea configurației complete. Interfața configurabilă și persistarea raportului nu sunt implementate încă.

## Exemplul fictiv

| Cerință | Pondere | Contribuție |
|---|---|---|
| Leadership: supported | 2 | 2 |
| Engleză: partial | 2 | 1 |
| AI adoption: confirmed_missing, optional | 1 | 0 |
| Furnizori: prioritate unknown | Exclusă | Indisponibilă |

Scor: (2 + 1 + 0) / 5 = 60%, pentru cele trei cerințe incluse. Acoperirea subsetului: 100%. Avertizări: engleză obligatorie parțial susținută și furnizori excluși din calcul din cauza priorității necunoscute.

Dacă matching-ul pentru engleză devine unknown, minimul este 2/5 = 40%, maximul este (2+2)/5 = 80%, iar acoperirea subsetului este 3/5 = 60%.

## Limite și alegerea soluției

Ponderile sunt o propunere de produs, necalibrată pe un set reprezentativ și nerevizuită încă explicit de utilizator. Excluderea priorităților necunoscute poate face scorul subsetului optimist sau pesimist față de toate cerințele; avertizarea și lista de excluderi trebuie afișate împreună cu scorul. Nu comparăm mecanic joburi cu acoperire și excluderi diferite.

Un scor produs direct de LLM ar fi mai greu de reprodus și auditat. Codul determinist permite verificarea aritmeticii, dar calitatea finală depinde în continuare de extragere și matching. Nu estimăm probabilitatea angajării și nu pretindem încă relevanță demonstrată pentru joburi reale.
