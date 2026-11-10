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
7. **Verificare:** Utilizatorul a răspuns corect: joburile rămân în SQLite la oprirea Ollama. Persistența este independentă de inference.

## Lecția 3 — Data contract și golden example

1. **Ce este?** Un data contract definește forma și regulile datelor acceptate. Un golden example este un exemplu cu rezultatul corect așteptat, folosit ca referință de evaluare.
2. **De ce?** Viitorul LLM poate răspunde incomplet sau inventa cerințe. Stabilim ce acceptă aplicația înainte de a integra modelul.
3. **Cum?** Validatorul verifică lista de cerințe, prioritățile și citatele cu poziții exacte în text. Outputul invalid este respins. Acest control nu certifică sensul sau completitudinea răspunsului.
4. **Unde?** `jobhunter/requirements.py`, exemplul din `tests/fixtures/` și explicația din `docs/REQUIREMENTS_CONTRACT.md`. Matching-ul cu profilul nu este încă implementat.
5. **Alternative?** Textul liber este ușor de afișat, dar greu de verificat și comparat. Un contract explicit permite teste repetabile; pentru un contract mai complex putem evalua ulterior o bibliotecă de validare. Acum biblioteca standard este suficientă.
6. **Interviu:** “Before integrating the language model, we defined an explicit output contract and a synthetic reference example. Each requirement must include a priority and an exact source quote. Python rejects structurally invalid output or evidence that does not match the job description. This improves traceability, but it does not prove semantic accuracy or completeness. Those need separate evaluation against reviewed examples.”
7. **Clarificare:** Utilizatorul nu a înțeles întrebarea. Am explicat prin exemple mandatory/optional/unknown și răspunsul corect: unknown când prioritatea nu este precizată. Nu considerăm încă înțelegerea verificată independent.

Preferință actualizată: explicațiile și răspunsurile de interviu în română; engleză doar la cerere.

## Lecția 4 — Matching bazat pe dovezi

1. **Ce este?** Compararea fiecărei cerințe cu fapte din profil, cu o explicație și o legătură spre dovadă.
2. **De ce?** Un profil poate omite o experiență reală; nu trebuie să transformăm absența informației într-un verdict negativ.
3. **Cum?** Fiecare rezultat are status, referințe spre fapte și explicație. Lipsa confirmată cere o declarație explicită; fără informație concludentă păstrăm unknown. Validatorul verifică referințele, nu sensul explicației.
4. **Unde?** `jobhunter/matching.py` și profilul exclusiv sintetic din fixtures. Nu există încă matching automat sau model conectat.
5. **Alternative?** Un paragraf liber este simplu de generat, dar greu de auditat. ID-urile de dovezi și statusurile explicite permit verificări repetabile. Validarea semantică și revizuirea rămân necesare.
6. **Interviu:** „Am separat lipsa unei competențe de lipsa informațiilor despre ea. Pentru fiecare cerință, rezultatul de comparație trebuie să indice dovezi din profil și o explicație. O lipsă confirmată necesită o declarație explicită; altfel informația rămâne necunoscută. Am implementat și testat aceste reguli pe date fictive. Evaluarea automată cu un model AI urmează să fie integrată și măsurată separat.”
7. **Verificare:** Utilizatorul a răspuns corect că nu putem afirma lipsa experienței, fiindcă CV-ul poate fi incomplet. Distincția lipsă/necunoscut este înțeleasă la nivelul exemplului.

## Lecția 5 — Scoring determinist și incertitudine

1. **Ce este?** Un calcul cu reguli explicite: aceleași date și aceiași parametri dau același rezultat.
2. **De ce?** Putem explica fiecare punct și verifica aritmetica fără să cerem LLM-ului un procent subiectiv.
3. **Cum?** Pondere 2 pentru mandatory, 1 pentru optional; contribuție integrală, jumătate sau zero pentru supported/partial/confirmed_missing. Matching unknown produce un interval. Prioritatea unknown exclude explicit cerința din calcul.
4. **Unde?** `jobhunter/scoring.py`; exemplul fictiv obține 60% pe cele trei cerințe cu prioritate cunoscută. Furnizorii sunt excluși cu avertizare. Dacă engleza devine unknown, rezultatul este 40–80%.
5. **Alternative?** Un procent produs direct de LLM este simplu de solicitat, dar mai greu de reprodus. Codul verifică calculul, însă nu poate compensa automat o interpretare greșită. Ponderile vor necesita calibrare și revizuire.
6. **Interviu:** „Am separat interpretarea textului de calculul compatibilității. Scorul este calculat în Python, cu ponderi și contribuții vizibile. Dacă nu avem suficiente informații, afișăm un interval, iar condițiile obligatorii neclarificate au avertizări separate. Testele confirmă aritmetica pe date fictive; nu pretindem că scorul reprezintă probabilitatea angajării sau că precizia analizei AI a fost deja validată.”
7. **Întrebare în așteptare:** Dacă scorul este mare, dar o cerință obligatorie lipsește, ar trebui să păstrăm o avertizare vizibilă?
