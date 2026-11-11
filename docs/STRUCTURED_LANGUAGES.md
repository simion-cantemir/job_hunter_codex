# Limbi de lucru: date explicite și reguli Python

## Rezultatul etapei

`jobhunter/languages.py` evaluează limbile din adnotări explicite, fără să solicite unui LLM verdictul. Adnotările, dovezile și condițiile trebuie revizuite de persoana care aprobă analiza. Nu am construit un parser universal și nu am declarat modelul mai precis.

Sunt reprezentate separat:

- **Limba din profil:** cod, nivel declarat și ID-urile faptelor care susțin nivelul.
- **Condiția jobului:** ID-ul cerinței, limbile, operatorul all/any/unclear și nivelul minim cerut.
- **Importanța cerinței:** mandatory/optional/unknown din raportul revizuit; nu schimbă capacitatea demonstrată a candidatului.

Nivelurile unknown/none/basic/professional/fluent sunt o rubrică simplă a prototipului, nu o scală oficială sau o conversie CEFR. Nu transformăm automat B1 în alt nivel. Basic/professional/fluent au o ordine definită în cod, iar alegerea nivelului trebuie confirmată față de sursă.

## Reguli

| Situație | Matching |
|---|---|
| O alternativă OR este satisfăcută | supported, cu dovada alternativei suficiente |
| OR nu are alternativă satisfăcută și una este necunoscută | unknown |
| Toate alternativele OR au lipsă explicită | confirmed_missing, cu dovezile relevante |
| AND are o condiție lipsă explicit | confirmed_missing, fără a cita lipsuri din alte limbi |
| AND nu are lipsă explicită, dar are informație necunoscută | unknown |
| Capacitate cunoscută, dar sub nivelul cerut | partial, nu lipsă explicită |
| Operator/nivel minim neclar | unknown, fără respingere bazată pe presupuneri |

O lipsă confirmată optional rămâne lipsă în matching, dar nu respinge jobul. O lipsă obligatorie confirmată respinge numai la aplicarea unei analize revizuite și aprobate. Un necunoscut obligatoriu rămâne de clarificat.

## Asocierea dovezilor

Pentru un nivel pozitiv sunt necesare fapte experience; pentru none, fapte confirmed_gap. Un control lexical limitat cere ca textul dovezii să numească limba evaluată. De exemplu, o dovadă care numește doar germana/franceza nu poate fi atribuită spaniolei. Listele de limbi dintr-o regulă nu pot omite o limbă recunoscută în citat și operatorii OR/AND expliciți nu pot fi inversați.

Acest control nu demonstrează adevărul sau sensul unei declarații. Un text contradictoriu, o negație complexă ori o asociere manuală greșită necesită revizuire. Limitele vocabularului sunt engleză, germană, franceză, spaniolă, română și italiană, cu formele EN/RO implementate. Limbile nerecunoscute și expresiile mixte/nestate nu sunt rezolvate automat. Nu folosim reguli de limbă pentru celelalte competențe.

## Interfață

Repornește serverul pentru a încărca noile module:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

După încărcarea unei analize, deschide **„Limbi de lucru — reguli explicite în Python”** și activează **„Evaluează limbile pe date structurate”**. Modulul este opt-in; rezultatele LLM originale rămân păstrate.

Pentru fiecare cerință recunoscută verifici operatorul și nivelul minim. Pentru fiecare limbă alegi nivelul din profil și dovezile filtrate la limba și tipul corespunzătoare. Valoarea implicită a nivelului este necunoscută; nu completăm competențe în numele utilizatorului. Un nivel pozitiv fără dovadă blochează aplicarea până la corectare.

Regulile recalculează propunerea înaintea confirmării finale. Dacă există și o corecție manuală la aceeași cerință, rezultatul calculat din adnotările de limbă are prioritate; nota manuală și explicația originală sunt păstrate. Pentru evaluarea manuală poți dezactiva modulul, ceea ce cere confirmare nouă.

## Audit și compatibilitate

`ReviewMaterial.language_review` păstrează adnotările în snapshot. Înainte de aprobare, rezultatul este recalculat din reguli și comparat cu matching-ul revizuit; nici măcar un istoric de corecții aparent consistent nu poate ascunde o concluzie diferită de regulile atașate.

Modificarea adnotărilor invalidează confirmarea din UI și înregistrarea aprobării, chiar dacă scorul rămâne identic. SQLite păstrează configurația împreună cu originalul și rezultatul revizuit. Nu există migrare distructivă de tabel.

Pentru analizele fără adnotări, snapshotul canonic omite noul câmp null. Testul de regresie confirmă păstrarea fingerprintului unei aprobări vechi din demonstrație. Nu am rescris aprobări sau joburi din baza privată.

## Verificare

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m jobhunter.evaluate_structured_languages
```

- **123 teste trecute**, inclusiv regulile OR/AND, nivelurile parțiale, lipsa informației, dovezile irelevante, sursele românești, operatorii greșiți, condițiile mixte, auditul și invalidarea confirmării din UI.
- **8/8 cazuri salvate** satisfac criteriile măsurate după adnotări structurate redactate de agent. Aceasta validează regulile pe acele intrări, nu extracția automată, o aprobare a utilizatorului sau precizia unui LLM. Nu sunt exemple independente nefolosite în dezvoltare.
- Raport: [structured_languages_001.md](evaluations/structured_languages_001.md), cu output brut în JSON. Zero apeluri noi la model și zero decizii aplicate în evaluare.
- Spaniola nemenționată este corectată din rejected în needs_review; AND elimină dovada franceză irelevantă; lipsurile opționale rămân vizibile fără respingere.
- Serverul temporar de verificare pe portul 8502 a returnat HTTP 200 și health ok și a fost oprit. Nu am oprit serverul utilizatorului de pe 8501. UI a fost testată prin AppTest; nu s-a făcut inspecție vizuală într-un browser.

## Ce rămâne în afara etapei

Nu există încă profil master din CV, normalizare automată sigură a limbilor sau interpretare universală a condițiilor complexe. Extragerea cerințelor și celelalte competențe continuă să necesite revizuire. Nu au fost cumpărate servicii, instalate modele sau modificate joburile utilizatorului.
