# Learning journal

## 2026-11-10 — Lecția 1: LLM și cele două utilizări AI

1. **Ce este?** Un Large Language Model este un model antrenat pe volume mari de date pentru a prezice și genera secvențe de tokens. Tokens sunt fragmente de text, nu neapărat cuvinte. AI este domeniul larg, Machine Learning învață tipare din date, iar Generative AI produce conținut; un LLM este un exemplu de Generative AI.
2. **De ce ne trebuie?** Cerințele din joburi sunt formulate variat. Un LLM poate propune o structură comparabilă, dar răspunsurile trebuie validate. Codex ne ajută să dezvoltăm și să verificăm software-ul.
3. **Cum funcționează?** La inference, modelul primește instrucțiuni și date în context și generează tokens succesivi. Context window este capacitatea limitată de tokens folosită într-o solicitare, nu memorie permanentă. Training modifică parametrii; fine-tuning îi adaptează prin antrenare suplimentară; introducerea CV-ului într-un prompt nu este fine-tuning. Un răspuns fluent poate fi fals: hallucination. Reducem riscul cu surse, schemă, citate, verificări și evaluări.
4. **Unde apare?** Codex este coding agent în timpul dezvoltării: poate inspecta fișiere, propune/edită cod și rula comenzi în limitele accesului. În produs, un adaptor Python ar apela separat un model pentru extragerea cerințelor. Job Hunter trebuie să poată porni fără conversația Codex; inference necesită propriul runtime sau serviciu.
5. **Alternative?** Reguli Python sunt ieftine și repetabile pentru scoruri și validări, dar fragile pentru limbaj variat. Local LLM oferă control asupra datelor, cu consum RAM/VRAM și calitate de măsurat. Cloud poate oferi alte capabilități, dar introduce transfer de date, dependență de serviciu și cost autorizat separat. Nu avem încă măsurători comparative.
6. **Interviu:** vezi INTERVIEW_PREP.md pentru formularea de 30–60 secunde.
7. **Verificare, în așteptare:** Dacă închidem Codex, ce componentă ar trebui să permită aplicației să analizeze în continuare un job?

Status educațional: explicație pregătită și prezentată în sesiune; înțelegerea utilizatorului nu este încă verificată. Niciun exercițiu hands-on al utilizatorului nu este confirmat.

Surse oficiale consultate la 2026-11-10:
- https://developers.openai.com/api/docs/guides/code-generation — Codex ca agent de dezvoltare.
- https://developers.openai.com/api/docs/guides/chatgpt-api-credits — nu presupunem API gratuit pentru Plus; beneficiul descris este pentru planuri eligibile Pro/Business.
