# Learning journal

## 2026-11-10 — Lecția 1: LLM și cele două utilizări AI

1. **Ce este?** Un Large Language Model este un model antrenat pe volume mari de date pentru a prezice și genera secvențe de tokens. Tokens sunt fragmente de text, nu neapărat cuvinte. AI este domeniul larg, Machine Learning învață tipare din date, iar Generative AI produce conținut; un LLM este un exemplu de Generative AI.
2. **De ce ne trebuie?** Cerințele din joburi sunt formulate variat. Un LLM poate propune o structură comparabilă, dar răspunsurile trebuie validate. Codex ne ajută să dezvoltăm și să verificăm software-ul.
3. **Cum funcționează?** La inference, modelul primește instrucțiuni și date în context și generează tokens succesivi. Context window este capacitatea limitată de tokens folosită într-o solicitare, nu memorie permanentă. Training modifică parametrii; fine-tuning îi adaptează prin antrenare suplimentară; introducerea CV-ului într-un prompt nu este fine-tuning. Un răspuns fluent poate fi fals: hallucination. Reducem riscul cu surse, schemă, citate, verificări și evaluări.
4. **Unde apare?** Codex este coding agent în timpul dezvoltării: poate inspecta fișiere, propune/edită cod și rula comenzi în limitele accesului. În produs, un adaptor Python ar apela separat un model pentru extragerea cerințelor. Job Hunter trebuie să poată porni fără conversația Codex; inference necesită propriul runtime sau serviciu.
5. **Alternative?** Reguli Python sunt ieftine și repetabile pentru scoruri și validări, dar fragile pentru limbaj variat. Local LLM oferă control asupra datelor, cu consum RAM/VRAM și calitate de măsurat. Cloud poate oferi alte capabilități, dar introduce transfer de date, dependență de serviciu și cost autorizat separat. Nu avem încă măsurători comparative.
6. **Interviu:** vezi INTERVIEW_PREP.md pentru formularea de 30–60 secunde.
7. **Verificare:** Utilizatorul a identificat corect LLM-ul local. Am clarificat că Ollama servește modelul, iar Python coordonează analiza și scoring-ul.

Status educațional: distincția de bază Codex/runtime verificată prin răspunsul utilizatorului. Niciun exercițiu hands-on al utilizatorului nu este confirmat.

Surse oficiale consultate la 2026-11-10:
- https://developers.openai.com/api/docs/guides/code-generation — Codex ca agent de dezvoltare.
- https://developers.openai.com/api/docs/guides/chatgpt-api-credits — nu presupunem API gratuit pentru Plus; beneficiul descris este pentru planuri eligibile Pro/Business.

## Lecția 2 — Persistență și application state

1. **Ce este?** Persistența înseamnă păstrarea datelor după oprirea unui proces. Application state este informația despre joburi și, ulterior, analize/stări; nu este memoria unui LLM.
2. **De ce?** Un job importat trebuie să rămână disponibil când redeschidem aplicația.
3. **Cum?** Python scrie într-un fișier SQLite și confirmă tranzacția. Un nou obiect poate reciti înregistrarea. Testul închide conexiunile și verifică recitirea printr-o instanță nouă. Mediul `.venv` izolează pachetele proiectului, nu datele sau securitatea procesului.
4. **Unde?** `jobhunter/storage.py`: `JobRepository.add()` și `get()`. Testul din `tests/test_storage.py` verifică păstrarea textului, inclusiv diacritice și text care seamănă cu SQL; parametrii îl păstrează ca date.
5. **Alternative?** Un dicționar în memorie pierde datele la oprire. JSON este simplu pentru exporturi, dar SQLite oferă interogări și tranzacții fără server separat. Nu alegem încă un server de baze de date pentru un utilizator local.
6. **Interviu:** “We separated application state from model inference. A small Python repository persists job descriptions in SQLite, and an integration test checks that a fresh repository instance can retrieve the committed data. Parameterized queries keep imported text separate from SQL commands. This validates the storage foundation; it does not yet validate AI extraction or matching quality.”
7. **Întrebare în așteptare:** Dacă oprim Ollama, joburile salvate în SQLite se pierd?
