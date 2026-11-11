# Rezumatul comparației matching-1 / matching-2

Model local: llama3.2:3b; parametrii de inference au rămas aceiași. Fiecare combinație versiune/set a avut o singură rulare, fără retry selectiv. Referințele sunt fictive și redactate de agent.

| Caz nou | matching-1 | matching-2 |
|---|---|---|
| Franceză opțională, lipsă explicită | unknown greșit; eligible corect | confirmed_missing și eligible, dovezi corecte |
| Franceză obligatorie, lipsă explicită | supported / eligible greșit, citează engleza | confirmed_missing / rejected corect; explicație cu afirmație nejustificată |
| Spaniolă obligatorie, nemenționată | supported / eligible greșit, citează engleza | confirmed_missing / rejected greșit, citează lipsa altor limbi |
| Germană OR engleză | supported / eligible corect | supported / eligible corect |
| Engleză AND germană | confirmed_missing / rejected corect | același status, dar include dovadă franceză irelevantă |

Set inițial: criterii complete 2/3 → 3/3. Set nou: 2/5 → 3/5. Acesta nu este un rezultat suficient pentru activarea automată a candidatului sau pentru o estimare de precizie generală.

**matching-2 rămâne experimental; defaultul nu se schimbă.** Ambele versiuni necesită revizuire. Nicio decizie nu a fost aplicată, niciun job salvat de utilizator nu a fost modificat și nicio aprobare existentă nu a fost rescrisă.

Rapoartele complete păstrează explicațiile brute: [matching-2 inițial](language_eval_v2_baseline.md), [matching-2 nou](language_eval_v2_new.md), [matching-1 nou](language_eval_v1_new.md). Explicațiile nu sunt aprobate automat de scorul de concordanță.
