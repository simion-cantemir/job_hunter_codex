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
7. **Clarificare și decizie de produs:** Utilizatorul a propus excluderea. Am separat excluderea cerinței din scor (care ar crește artificial media) de respingerea jobului. Utilizatorul a acceptat respingerea jobului pentru lipsă obligatorie confirmată, cu istoric păstrat; limba de lucru este determinantă.

## Lecția 6 — Criteriu eliminatoriu și scor

1. **Ce este?** Un criteriu eliminatoriu blochează un job indiferent de media compatibilității.
2. **De ce?** Un scor mare la management nu compensează lipsa unei limbi obligatorii pentru munca zilnică.
3. **Cum?** Mandatory + confirmed_missing produce rejected. Partial/unknown cere clarificare. Decizia și motivul sunt salvate, iar listarea oportunităților exclude respingerile.
4. **Unde?** `jobhunter/eligibility.py`, `JobRepository.save_decision()`, `list_opportunities()` și `decision_history()`.
5. **Alternative?** O simplă medie poate ascunde un blocaj. Ștergerea jobului pierde motivul respingerii. Statusul păstrat permite explicații și reevaluare explicită. Evitarea reimporturilor duplicate va fi implementată separat.
6. **Interviu:** „Am stabilit că anumite cerințe sunt eliminatorii. Dacă o limbă obligatorie nu este cunoscută și acest lucru este confirmat, jobul este respins indiferent de scor. Agentul a implementat regula și păstrarea motivului în SQLite. Dacă informația este incompletă, cerem clarificare. Testele pe date fictive verifică atât filtrarea, cât și istoricul, dar interpretarea printr-un LLM nu este încă integrată.”
7. **Exercițiu pentru o sesiune ulterioară:** Diferența dintre „germană obligatorie”, „germană avantaj” și „engleză sau germană”. Nu am verificat încă înțelegerea ultimului caz.

## Lecția 7 — API și structured output, în practică

1. **Ce este?** Un API este o interfață prin care două programe schimbă cereri și răspunsuri. Structured output înseamnă date într-o formă prestabilită, aici JSON cu lista cerințelor.
2. **De ce?** Python trebuie să primească de la model date verificabile, pentru a le putea folosi în matching și scoring.
3. **Cum?** Python trimite un HTTP POST la Ollama local cu instrucțiuni, textul jobului și o schemă JSON. Ollama execută inference și returnează răspunsul. Python verifică structura și citatele; numără caracterele și generează ID-urile fără a le cere modelului.
4. **Unde?** `jobhunter/ollama.py` și demo-ul `jobhunter/extract_demo.py`. Prima rulare: 4/4 cerințe cu citate/priorități identice cu referința, în 37,449 secunde; fără profil personal.
5. **Alternative?** Am putea instala SDK-ul Ollama, util la integrare mai extinsă. Biblioteca standard este suficientă pentru acest apel și evită dependențe. Textul liber ar fi mai greu de validat. JSON valid nu garantează că sensul este corect.
6. **Interviu:** „Agentul de dezvoltare a integrat un model local prin API-ul Ollama. Aplicația îi trimite un job fictiv și primește cerințe structurate, apoi verifică citatele în textul original. Prima rulare a identificat cele patru cerințe așteptate. Am separat testele de transport simulate de rularea reală și nu generalizăm rezultatul unui singur exemplu. Matching-ul automat și evaluarea pe un set reprezentativ sunt pașii următori.”
7. **Verificare:** Utilizatorul a identificat corect independența formatului JSON față de corectitudinea interpretării. Am clarificat că JSON este solicitat explicit în integrarea noastră, nu implicit în orice utilizare Ollama.

## Lecția 8 — Human-in-the-loop și evaluarea explicațiilor

1. **Ce este?** O etapă în care o persoană verifică sau corectează o propunere AI înainte ca aplicația să îi aplice consecințele.
2. **De ce?** Modelul poate cita un ID valid și alege un status rezonabil, dar explicația poate modifica faptele. În rularea reală despre engleză, participarea la cursuri a fost reformulată greșit ca înscriere viitoare.
3. **Cum?** Fluxul produce un draft pending, scor provizoriu și eligibilitate propusă, fără să scrie decizii în SQLite. Revizuirea trebuie să compare citatul și faptele exacte, nu doar procentul. Acțiunea de aprobare/corectare nu este încă implementată.
4. **Unde?** `jobhunter/analysis.py`, `analyze_demo.py` și raportul real din docs/evaluations. Matching-ul local a dat 4/4 statusuri și referințe așteptate, dar explicațiile nu sunt automat validate semantic.
5. **Alternative?** Aplicarea imediată ar fi mai rapidă, dar ar transforma o interpretare greșită în respingere. Doar verificarea JSON și a ID-urilor ratează acest tip de eroare. Înainte de mai multă autonomie avem nevoie de exemple reprezentative și măsurători.
6. **Interviu:** „Am introdus o separare între propunerea AI și decizia aplicației. Modelul local compară cerințele cu un profil fictiv, iar Python verifică dovezile și calculează scorul. Prima rulare a potrivit statusurile așteptate, dar am observat și o explicație care modifica un fapt. De aceea rezultatul rămâne provizoriu și nu respinge automat joburi. Agentul a implementat fluxul; validarea semantică de către utilizator și interfața de revizuire sunt pașii următori.”
7. **Întrebare în așteptare:** Dacă statusul este corect, dar explicația schimbă un fapt din profil, putem considera rezultatul complet validat?

## Lecția 9 — Trasabilitatea unei corecții

1. **Ce este?** Posibilitatea de a vedea ce a spus modelul, ce propunem să schimbăm și de ce, fără pierderea originalului.
2. **De ce?** O explicație rescrisă fără istoric ar ascunde eroarea și ar face evaluarea modelului înșelătoare.
3. **Cum?** Păstrăm snapshoturile înainte/după și nota corecției. Un fingerprint identifică exact raportul, sursa și profilul folosite. Schimbarea datelor produce alt fingerprint. Acesta nu dovedește că o persoană a aprobat corecția.
4. **Unde?** `jobhunter/review.py`, raportul docs/evaluations/review_001.md și snapshotul propunerii. Pentru R2 afișăm participarea actuală la cursuri și nivelul profesional neconfirmat, păstrând și explicația greșită a modelului.
5. **Alternative?** Editarea directă a outputului ar fi mai simplă, dar pierde istoricul. Un nou apel LLM ar consuma resurse și nu ar demonstra că răspunsul nou este corect. Revizuirea pe surse este etapa necesară acum.
6. **Interviu:** „Am cerut ca revizuirea să arate împreună cerința, dovada originală și explicația AI. Agentul a implementat un raport lizibil și corecții propuse, păstrând versiunea originală și motivul modificării. Corecțiile sunt legate de datele exacte și nu constituie aprobare implicită. Cele 69 de teste locale au trecut. Acțiunea de aprobare și aplicarea auditată în baza de date urmează.”
7. **Exercițiu pentru revizuire:** Compară R2 cu dovada P2; corecția propusă trebuie să spună că persoana participă deja la cursuri, fără a pretinde că nivelul profesional este confirmat. Nu este încă revizuire realizată de utilizator.
