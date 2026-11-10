# Roadmap și sesiuni

Sesiuni propuse de 2–3 ore, 4 pe săptămână la disponibilitatea de 10–12 ore. Estimări de planificare, ajustabile după fiecare demonstrație; fără termen garantat.

| Sesiuni / fază | Livrare și învățare | Acceptance criteria |
|---|---|---|
| 1 / F0, finalizată | Diagnostic, arhitectură, lecția LLM/Codex | Specificații verificate, limite notate, documente persistente create. |
| 2 / F0 | Mediu virtual, structură minimă, SQLite; backend și state | Un exemplu sintetic poate fi salvat și recitit într-un test temporar; fără date personale și fără servicii externe. |
| 3–4 / F1 | Profil sintetic, job de test, schema cerințelor; prompts și hallucinations | Cerințe cu citate din sursă, mandatory/optional/unknown; output invalid respins, nu reparat prin presupuneri. |
| 5–6 / F1 | Matching și scoring; unit tests, golden examples | Calcul repetabil, dovezi per cerință, necunoscute și condiții obligatorii explicite; verificări pentru cazuri limită. |
| 7 / F1 | UI Streamlit minimă; integrare frontend/backend | Import text → raport demonstrabil end-to-end cu date sintetice. |
| 8–10 / F2 | CV master, trasabilitate, diff, DOCX; prompt injection și date private | Nicio afirmație fără sursă; istoric QA păstrat; versiuni pe aplicație; export verificat. PDF numai dacă avem conversie disponibilă verificată. |
| 11–13 / F3 | Prima sursă permisă, import link controlat, deduplicare; API/workflow | Permisiunea sursei documentată; duplicate și erori testate; nicio automatizare interzisă. |
| 14–15 / F4 | Dashboard și tracking; observability și delivery | Stări saved/applied/rejected/archived persistente, audit și preferințe editabile. Aplicarea este înregistrată manual. |
| 16–18 / F5 | Benchmark local, cloud doar autorizat; precision/recall, cost și latență | Aceleași exemple etichetate, versiuni și parametri înregistrați; măsurăm calitate, resurse și latență. |
| Ulterior / F6 | Experiment RAG și eventual agent/reviewer; governance | RAG comparat cu baseline; agenții numai dacă aduc beneficii măsurate, cu limite de iterații și aprobare pentru acțiuni externe. |

## Status și backlog

- F0: finalizată; mediu virtual creat și 2 teste SQLite trecute. Rezultatul execuției în docs/PROJECT_PROGRESS.md.
- F1: în lucru — contractele cerințelor și matching-ului, profilul fictiv, scoring-ul, eligibilitatea și extragerea locală Ollama implementate; 51 de teste trecute. Prima inference: 4/4 perechi citat/prioritate pe exemplul fictiv, 37,449 secunde. Matching-ul automat și UI nu sunt implementate. Politica de respingere este acceptată; ponderile și exemplele necesită încă revizuire/calibrare.
- F4, componentă anticipată pentru regula agreată: istoric al deciziilor în SQLite și listarea oportunităților fără joburile respinse. Dashboard și deduplicare neimplementate.
- F2–F6: neîncepute. Ollama prezent nu înseamnă integrare AI funcțională.
- În toate fazele: explicații și interviu în engleză; actualizare progres, verificări relevante și checkpoint Git.
- Criterii inițiale de prioritizare: Cluj onsite/hybrid/remote; România remote; Europa remote și relocări evaluate; roluri de management/product/BA/AI adoption, fără focus hands-on; EN/RO, fără germană; 3000 EUR net reper flexibil.
- RAG/embeddings/chunking/semantic search/fine-tuning: experiment educațional separat când devine oportun, fără a complica MVP.
- AI adoption, build versus buy, ROI și change management: discutate la prioritizare și benchmark; GDPR și secrets la introducerea datelor reale/API-urilor, cu surse actuale atunci.
