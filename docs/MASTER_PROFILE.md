# CV master: import local, surse și profil revizuit

## Ce este implementat

Import TXT UTF-8, DOCX și PDF cu text, plus text lipit manual. Poți alege blocuri întregi sau copia fragmente de orice dimensiune din textul afișat. Nu sunt reformulate, completate sau clasificate de un LLM în această etapă. Fișierul original și textul integral sunt păstrate local, inclusiv istoricul QA și rolurile care nu au fost selectate ca fragmente.

Originalul este sursă de revizuire, nu o garanție automată că textul extras este complet sau că afirmațiile sunt adevărate. Utilizatorul verifică extracția și selectează faptele înaintea confirmării.

## Utilizare

Repornește aplicația pentru noile module:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

1. **Încarcă CV-ul.** Modul „Profil master din CV” este implicit. Încarcă fișierul sau lipește textul integral; textul este citit automat. Verifică datele, caracterele și ordinea secțiunilor.
2. **Alege fragmentele.** În stânga vezi CV-ul, în dreapta lipești câte un fragment în fiecare casetă. „Adaugă încă un fragment” creează o casetă nouă; golește o casetă pentru a elimina fragmentul. Poți opta și pentru selecția blocurilor întregi.
3. Fiecare fragment trebuie să existe exact în textul afișat. Spațiile de la început/sfârșit sunt ignorate, textul interior nu este rescris. Dacă fragmentul apare de mai multe ori, alegi apariția după context. Include rolul/perioada când sunt relevante; o frază izolată poate pierde contextul.
4. Completează numele, verifică nota și bifează că textul și fragmentele sunt corecte. Apasă **„Salvează fragmentele și continuă la job”**. Se păstrează versiunea selecției și sursa; modificările cer confirmare nouă.
5. **Compară cu un job.** Completează titlul și descrierea jobului, apoi apasă „Analizează cu Ollama local”. Modelul extrage cerințele și le compară cu fragmentele alese. Verifică propunerea și sursele înainte de aplicare.

Dacă ai deja un profil salvat, apasă **„Alege alte fragmente din acest CV”** pentru a refolosi originalul, fără reîncărcare. O nouă selecție produce o versiune separată. Opțiunea avansată „Lipsă declarată explicit” se folosește numai dacă sursa afirmă lipsa unei competențe; o omisiune din CV nu este dovadă de lipsă. Modul fictiv rămâne separat.

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
- Blocurile pot conține date de contact; selectează pentru matching doar ce este necesar. PDF poate produce blocuri la nivel de pagină; copy-paste permite alegerea unui fragment mai mic. Nu există încă selecție vizuală a coordonatelor direct pe pagina PDF sau buton care capturează automat textul evidențiat cu mouse-ul: folosește Ctrl+C/Ctrl+V ori selecția blocurilor.
- Matcherul are încă limita inițială de input de 12.000 de caractere. Un profil mare poate necesita o selecție mai concentrată de fapte; originalul integral rămâne păstrat. Nu se generează încă un CV personalizat.

## Verificări

**160 teste trecute** în suita curentă (2026-11-12). Etapa importului inițial a adăugat 19 teste; simplificarea cu fragmente parțiale adaugă 8 teste pentru citate exacte, text repetat, poziții invalide, salvare/reîncărcare, compatibilitatea versiunilor vechi, mai multe casete și invalidarea confirmării chiar după restaurarea textului.

AppTest a verificat importul prin text lipit, revizuirea și salvarea cu reviewer fictiv, selecția versiunii într-o sesiune nouă, analiza cu transport AI simulat și includerea provenienței în audit. Parserele TXT/DOCX/PDF au fost testate separat. Uploadul și selecția cu mouse-ul într-un browser nu au fost testate vizual. Utilizatorul raportează că a încărcat CV-ul; agentul nu a inspectat conținutul privat.

```powershell
.\.venv\Scripts\python.exe -m jobhunter.master_profile_demo
```

Demonstrația folosește exclusiv `tests/fixtures/master_cv_synthetic.txt` și o bază temporară eliminată la final. Rezumat: 5 fapte, citate exacte, bytes originali identici și istoric QA păstrat, fără apel AI sau decizie de job aplicată. Artefact: `docs/evaluations/master_profile_001.demo.json`, cu real_user_approval=false.

pypdf 7.0.1 este instalat numai în `.venv`; `pip check` a trecut și lockul dependențelor a fost actualizat. Serverul temporar pe 8502 a returnat HTTP 200 / health ok și a fost oprit. Sesiunea utilizatorului de pe 8501 nu a fost oprită.

Surse tehnice consultate: [extragerea PDF și limitele ei](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), [structura WordprocessingML](https://learn.microsoft.com/en-us/office/open-xml/word/structure-of-a-wordprocessingml-document), [upload Streamlit](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader).
