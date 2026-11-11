# Decizii și propuneri — 2026-11-10

| ID | Status | Alegere și motiv |
|---|---|---|
| D01 | Cerință utilizator | Pași mici, practică și învățare; fără implementarea întregului produs la START. |
| D02 | Propunere agent | Python + SQLite + Streamlit: complexitate mică pentru produs personal. Nicio instalare încă. |
| D03 | Propunere agent | LLM pentru extragere, cod pentru scoring; dovezi și necunoscute explicite. |
| D04 | Propunere agent | Fără RAG/multi-agent în MVP; experiment separat ulterior. |
| D05 | Cerință utilizator | Fără servicii plătite sau acțiuni externe fără aprobare explicită. |
| D06 | Propunere agent | Evaluăm întâi modelul deja instalat, fără a-l declara potrivit înainte de benchmark. |
| D07 | Cerință utilizator | Date sintetice până la CV; istoric profesional păstrat integral și afirmații trasabile. |
| D08 | Propunere agent, implementată pentru experiment | Scoring determinist cu ponderi 2/1, credit parțial 0,5, interval pentru matching unknown și excludere explicită a priorităților unknown; fără calibrare pe joburi reale încă. |
| D09 | Preferință actualizată de utilizator | Răspunsuri de interviu în română; engleză doar la cerere. |
| D10 | Acceptată explicit de utilizator | Mandatory confirmed_missing → job respins din oportunități indiferent de scor, cu motiv și înregistrare păstrate. Mandatory partial/unknown → clarificare. Limba de lucru este determinantă. Implementată și testată pe date fictive. |
| D11 | Implementată și verificată de agent în pasul autorizat | Ollama local prin HTTP standard-library, modelul deja instalat llama3.2:3b, output cu schemă; citate validate și poziții calculate în Python. Fără tools sau schimbări ale configurației persistente. O singură inference pe date fictive; calitatea generală rămâne de evaluat. |
| D12 | Implementată de agent pentru controlul calității | Matching-ul AI și eligibilitatea rezultată sunt propuneri pending semantic review. Fluxul de analiză nu apelează stocarea deciziilor. Nu confundăm ID-uri valide cu explicații corecte; prima rulare a arătat o reformulare greșită chiar cu 4/4 statusuri și dovezi așteptate. |
| D13 | Implementată de agent în pasul autorizat | Raport Markdown local și snapshot de revizuire, fără noi dependențe sau inference. Corecțiile sunt legate de datele exacte prin fingerprint și rămân propuneri; aprobarea/aplicarea sunt un pas distinct, încă neimplementat. |
| D14 | Implementată și testată de agent în pasul următor autorizat | Aprobare backend cu reviewer declarat, notă, timestamp UTC și snapshot exact, incluzând rezultatul rubricii/politicii; aplicare atomică și idempotentă în SQLite. Simulare exclusiv fictivă; nu există aprobare semantică a raportului de către utilizator sau autentificare. |
| D15 | Implementată și testată de agent la 2026-11-11 | UI Streamlit 1.67.0 instalată în `.venv`, server doar loopback, fără telemetry. Widgeturi reactive și confirmare legată de versiunea materialului, fără aplicare la rerun. AppTest și HTTP verificate; inspecție vizuală în browser neexecutată. |
| D16 | Candidat evaluat, nepromovat | Matching-2 rezolvă cazurile inițiale, dar eșuează pe spaniolă nemenționată și citează o dovadă irelevantă la AND. Rămâne opt-in pentru evaluări; defaultul matching-1 și revizuirea obligatorie se păstrează. Niciuna dintre variante nu este validată pentru filtrare autonomă. Urmează modelarea explicită a limbilor. |
| D17 | Implementată și verificată de agent | Limbile adnotate explicit sunt evaluate prin reguli Python pentru OR/AND, niveluri și dovezi. Modul opt-in în UI, audit al adnotărilor, compatibilitate cu snapshoturile vechi. 8/8 pe intrări fictive structurate; nu este îmbunătățire măsurată a extracției LLM și nu autorizează decizii fără revizuire. |
| D18 | Implementată și verificată pe documente fictive | Import CV local TXT/DOCX/PDF cu text, fără LLM, cu limite și revizuire explicită. Fapte ca excerpts exacte, citate, sursă integrală și versiuni; proveniența rămâne în audit, nu în prompt. pypdf 7.0.1 este dependență locală; fără OCR sau export/tailoring încă. |

Nicio propunere din acest tabel nu reprezintă o decizie tehnică deja confirmată de utilizator.
