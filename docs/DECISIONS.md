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

Nicio propunere din acest tabel nu reprezintă o decizie tehnică deja confirmată de utilizator.
