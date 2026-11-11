# CV master: import local, surse și profil revizuit

## Ce este implementat

Import TXT UTF-8, DOCX și PDF cu text, plus text lipit manual. Selectarea unor blocuri exacte din document creează fapte pentru matching. Nu sunt reformulate, completate sau clasificate de un LLM în această etapă. Fișierul original și textul integral sunt păstrate local, inclusiv istoricul QA și rolurile care nu au fost selectate ca fapte.

Originalul este sursă de revizuire, nu o garanție automată că textul extras este complet sau că afirmațiile sunt adevărate. Utilizatorul verifică extracția și selectează faptele înaintea confirmării.

## Utilizare

Repornește aplicația pentru noile module:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

1. La „Profil pentru analiză” alege **„Profil master din CV”**.
2. Alege **„Importă și revizuiește un CV”**, apoi un fișier sau textul integral.
3. Apasă „Extrage textul CV-ului” și verifică toate secțiunile, datele, caracterele și ordinea. Pentru documente pe coloane poate fi nevoie de o variantă mai simplă sau text manual.
4. Selectează blocurile fidele sursei. „Lipsă declarată explicit” se folosește numai dacă sursa chiar afirmă lipsa unei competențe; lipsa mențiunii nu este dovadă.
5. Completează reviewerul și nota, bifează verificarea și salvează profilul. Schimbarea documentului/selecției cere confirmare nouă.
6. Folosește o versiune salvată pentru analiza joburilor. Modul fictiv este separat, iar analiza fictivă precalculată nu poate fi combinată cu un profil master real.

În modul master poți vedea faptele/citatele și descărca originalul din stocarea locală. Modificarea profilului se face printr-o nouă revizuire/import, nu prin rescrierea tacită a unei versiuni aprobate. Reimportul identic, cu aceeași selecție, păstrează prima înregistrare de revizuire pentru acel conținut.

## Trasabilitate

`jobhunter/cv_import.py` produce hashul fișierului, hashul textului extras, blocuri cu poziții exacte și etichete de pagină/paragraf. Pozițiile sunt în textul normalizat afișat, nu offseturi în bytes PDF/DOCX și nici coordonate vizuale.

`jobhunter/master_profile.py` generează versiunea profilului din sursă, fapte, tipuri și citate. Fiecare fapt este un excerpt exact. Aprobarea include reviewerul declarat, nota și timpul UTC; numele nu este autentificat și hashurile nu sunt semnături digitale.

`master_documents` și `master_profiles` sunt tabele noi, în aceeași bază locală privată selectată pentru UI. La salvare revalidăm originalul și citatele. La încărcare verificăm amprentele și concordanța sursei. Profilul are `provenance`, inclusă în snapshotul analizei și auditul aprobării jobului. Profilele fictive vechi rămân compatibile.

Apelul de matching primește numai versiunea și faptele selectate. Nu primește bytes-ul fișierului, documentul integral separat, numele reviewerului sau metadatele de audit. Faptele sunt tot date din CV și ajung la modelul local numai când apeși analiza. Nu există apel cloud în acest flux.

## Păstrarea datelor și limite

- Importul și revizuirea inițială rămân în memorie până la confirmare; un draft nu este profil activ pentru analiză.
- Salvarea este în `data/private/`, ignorat de Git. Nu este stocare criptată sau multi-user; confidențialitatea depinde și de accesul la laptop. Nu expune serverul în rețea.
- Maximum fișier 10 MiB, text extras 100.000 caractere, PDF 50 pagini, 100 blocuri selectate. Fără trunchiere tacită. Acestea nu garantează consum fix de memorie pentru orice fișier corupt.
- PDF nu are OCR. Fișierele fără text și cele criptate sunt respinse. Sunt semnalate paginile fără text și riscul pierderii ordinii pe coloane. Streamurile mari sunt verificate, dar decomprimarea lor poate necesita resurse înainte de verificare.
- DOCX: paragrafe/tabele din corp plus antete/subsoluri/note. Nu deschidem Word, nu executăm macro-uri și nu extragem arhiva pe disc. DOCM, macro-urile și declarațiile de entități XML sunt respinse; text boxes cer alt format/import manual. Layoutul, imaginile și fidelitatea vizuală nu sunt reconstruite.
- Blocurile pot conține date de contact; selectează pentru matching doar ce este necesar. PDF poate produce blocuri la nivel de pagină, care necesită atenție suplimentară la selecție.
- Matcherul are încă limita inițială de input de 12.000 de caractere. Un profil mare poate necesita o selecție mai concentrată de fapte; originalul integral rămâne păstrat. Nu se generează încă un CV personalizat.

## Verificări

**142 teste trecute**, dintre care 19 noi pentru această etapă: importuri sintetice în trei formate, diacritice, citate, QA/roluri vechi, fișiere invalide/criptate, XML neacceptat, confirmare, versiuni, modificarea sursei, metadata exclusă din prompt și integrarea UI.

AppTest a verificat importul prin text lipit, revizuirea și salvarea cu reviewer fictiv, selecția versiunii într-o sesiune nouă, analiza cu transport AI simulat și includerea provenienței în audit. Parserele TXT/DOCX/PDF au fost testate separat. Uploadul dintr-un browser nu a fost testat vizual; niciun CV real nu a fost furnizat.

```powershell
.\.venv\Scripts\python.exe -m jobhunter.master_profile_demo
```

Demonstrația folosește exclusiv `tests/fixtures/master_cv_synthetic.txt` și o bază temporară eliminată la final. Rezumat: 5 fapte, citate exacte, bytes originali identici și istoric QA păstrat, fără apel AI sau decizie de job aplicată. Artefact: `docs/evaluations/master_profile_001.demo.json`, cu real_user_approval=false.

pypdf 7.0.1 este instalat numai în `.venv`; `pip check` a trecut și lockul dependențelor a fost actualizat. Serverul temporar pe 8502 a returnat HTTP 200 / health ok și a fost oprit. Sesiunea utilizatorului de pe 8501 nu a fost oprită.

Surse tehnice consultate: [extragerea PDF și limitele ei](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), [structura WordprocessingML](https://learn.microsoft.com/en-us/office/open-xml/word/structure-of-a-wordprocessingml-document), [upload Streamlit](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader).
