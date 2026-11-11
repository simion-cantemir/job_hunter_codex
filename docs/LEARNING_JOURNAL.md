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

## Lecția 10 — Aprobare explicită, tranzacție și idempotency

1. **Ce este?** Aprobarea înregistrează cine declară că a revizuit exact anumite date. Tranzacția scrie decizia și auditul împreună; idempotency evită duplicatele la repetarea aceleiași operații.
2. **De ce?** Nu vrem ca o confirmare veche să se aplice altui raport, nici o decizie fără motiv sau o aplicare duplicată la retry.
3. **Cum?** Înregistrarea conține snapshoturile, identitatea calculată a datelor și rezultatului, reviewerul, nota și timpul UTC. SQLite salvează totul într-o tranzacție; o eroare anulează întreaga scriere. Aceeași înregistrare reaplicată întoarce aceeași decizie.
4. **Unde?** `jobhunter/approval.py`, `JobRepository.apply_approved_review()` și demo-ul fictiv de aprobare. Aprobarea corectitudinii unui raport poate produce în continuare status needs_review pentru potrivirea candidatului.
5. **Alternative?** Un boolean generic approved fără snapshot ar putea rămâne activ după modificarea datelor. Scrieri separate pot lăsa audit incomplet. Autentificarea și semnăturile ar oferi alte garanții, dar nu sunt implementate în prototipul personal.
6. **Interviu:** „Agentul a implementat aprobarea legată de datele exacte, separată de propunerea AI. Decizia și auditul sunt salvate atomic, iar repetarea aceleiași aplicări nu creează duplicate. Cele 83 de teste tehnice au trecut, inclusiv cazurile de date modificate și eroare la salvarea auditului. Demonstrația folosește un reviewer fictiv; nu o prezint drept aprobare umană reală sau autentificare.”
7. **Verificare:** Utilizatorul a răspuns corect că după modificarea profilului aprobarea veche este invalidată. Aprobarea și analiza anterioare rămân în istoric, legate de datele de atunci.

## 2026-11-11 — Lecția 11: Frontend, backend și starea sesiunii

1. **Ce este?** Frontend-ul este interfața cu care interacționezi. Backend-ul conține logica de analiză, validare, scoring și stocare. Starea sesiunii păstrează temporar analiza și editările din browserul curent.
2. **De ce?** Putem folosi aplicația fără comenzi Python și putem schimba interfața fără să rescriem regulile de produs.
3. **Cum?** Streamlit reexecută scriptul când modifici un widget. De aceea apelurile LLM și scrierile în SQLite trebuie declanșate doar prin acțiuni explicite. Sesiunea identifică datele curente și elimină confirmarea după schimbări; SQLite păstrează istoricul după închiderea browserului.
4. **Unde?** `app.py` afișează ecranele, `jobhunter/ui_session.py` coordonează starea, iar serviciile Python existente fac analiza și aplicarea. AppTest verifică interacțiunile fără un browser.
5. **Alternative?** Un frontend separat și FastAPI ar permite mai mult control pentru un produs multi-user, dar introduc mai multe componente. Streamlit este suficient pentru MVP-ul personal; nu oferă implicit autentificare sau garanția corectitudinii interpretării AI.
6. **Interviu:** „Agentul a construit o interfață locală peste serviciile Python existente. Am păstrat separat analiza propusă, revizuirea și aplicarea, astfel încât un rerun al interfeței să nu genereze inference sau decizii duplicate. Cele 94 de teste au trecut, inclusiv schimbarea datelor și confirmarea explicită. Serverul local a fost verificat prin HTTP; nu am efectuat încă acceptance walkthrough cu utilizatorul sau validare pe CV-ul real.”
7. **Verificare în UI, confirmată de utilizator:** După reîncărcare vede jobul și decizia De clarificat, o singură dată. Persistența și lipsa duplicatului au fost confirmate în conversație; agentul nu a inspectat independent baza privată.

## Primul walkthrough de acceptare — efectuat de utilizator

Utilizatorul a verificat R1–R4 în UI, a identificat explicația nefidela pentru engleză și a confirmat corectarea R2, păstrând 60% / De clarificat. A confirmat apoi mesajul de salvare cu audit. Aceasta este practică reală de revizuire și acceptare pe date fictive; codul și testele automate au fost realizate de agent.

Ce am consolidat: o corecție de explicație nu trebuie să schimbe automat statusul sau scorul; lipsa opțională nu respinge, iar informația absentă rămâne necunoscută. Salvarea, vizibilitatea după reîncărcare și apariția unei singure decizii sunt confirmate de utilizator, fără inspecția independentă a bazei private de către agent.

## Lecția 12 — Unit tests versus model evaluation

1. **Ce este?** Unit tests verifică reguli și calcule controlate. Model evaluation compară outputul modelului real cu rezultate de referință pe exemple alese.
2. **De ce?** Testele de cod pot trece în timp ce modelul interpretează greșit datele. În acest pas, 101 teste au trecut, dar unul dintre cele trei cazuri reale a avut matching greșit.
3. **Cum?** Stabilim așteptările înaintea rulării și nu le trimitem modelului. Măsurăm separat extragerea, matching-ul și eligibilitatea. Păstrăm erorile și explicațiile brute; un rezultat de 2/3 pe trei exemple nu este precizie generală.
4. **Unde?** `jobhunter/evaluate_languages.py` și raportul language_eval_001.md. Modelul a ignorat lipsa explicită de germană când cerința era opțională; eligibilitatea a rămas corectă, însă matching-ul și intervalul scorului nu sunt cele așteptate.
5. **Alternative?** Verificarea exclusivă a deciziei finale ar fi raportat 3/3 și ar fi ascuns eroarea intermediară. Ajustarea repetată numai pe aceste trei exemple riscă overfitting la test; folosim și cazuri noi înainte să declarăm o îmbunătățire.
6. **Interviu:** „Am separat verificarea codului de evaluarea modelului. Pe trei cazuri fictive de limbă, eligibilitatea propusă a fost corectă de trei ori, dar matching-ul complet a corespuns referinței doar în două cazuri. Agentul a identificat că modelul ignora o lipsă explicită când cerința era opțională. Am păstrat rezultatul ca baseline și nu îl prezentăm drept precizie generală; corecția și verificarea pe exemple noi sunt pasul următor.”
7. **Întrebare pentru verificare:** Dacă decizia finală este corectă, dar modelul a ignorat o dovadă explicită, considerăm întreaga analiză corectă?

## Lecția 13 — Regression checks și decizia de a nu activa un candidat

1. **Ce este?** Verificăm dacă o schimbare rezolvă eroarea cunoscută fără să introducă probleme pe alte cazuri. Un candidat poate rămâne experimental chiar dacă scorul mediu crește.
2. **De ce?** Matching-2 a corectat cazul opțional inițial, dar a atribuit greșit dovezi despre alte limbi unei cerințe de spaniolă. Această eroare ar putea elimina o oportunitate validă dacă nu există revizuire.
3. **Cum?** Am versionat promptul, păstrat baseline-ul, definit cinci exemple noi înainte de rulare și comparat variantele pe același set. Nu am ajustat promptul după rezultatele exemplelor noi. Am păstrat candidatul opt-in, fără modificarea defaultului.
4. **Unde?** `ai_matching.py`, selecția --matching-prompt din evaluate_languages.py și docs/evaluations/matching_v2_comparison.md. Cazuri inițiale: 2/3 → 3/3; noi: 2/5 → 3/5. Acestea nu sunt estimări de precizie generală.
5. **Alternative?** Activarea imediată după 3/3 pe setul inițial ar ascunde problema. Iterarea numai pe aceleași exemple poate produce overfitting la evaluare. Pentru limbi putem folosi date explicite și reguli deterministe, cu revizuire a extracției, înainte să cerem mai multă autonomie modelului.
6. **Interviu:** „Agentul a testat o nouă versiune de prompt care a rezolvat eroarea cunoscută. Verificarea pe cinci exemple noi a găsit însă dovezi atribuite limbii greșite și o respingere nejustificată. Candidatul nu a fost activat implicit; am păstrat rezultatele și revizuirea umană. Cele 104 teste de cod au trecut, dar nu le confund cu validarea calității modelului. Soluția propusă mai departe este modelarea explicită a limbilor și verificarea logicii în cod.”
7. **Întrebare pentru verificare:** Este suficient că noul prompt trece toate exemplele pe care le-am folosit pentru a-l îmbunătăți?

## Lecția 14 — Alegerea codului determinist când LLM-ul nu este suficient

1. **Ce este?** Reprezentăm explicit datele necesare unei decizii și aplicăm reguli verificabile în Python, în loc să cerem modelului să deducă totul din text.
2. **De ce?** Prompturile testate atribuiau dovezi limbii greșite. Spaniola nemenționată nu trebuie evaluată folosind lipsa germanei sau francezei.
3. **Cum?** Adnotările stabilesc limba, nivelul, dovada și operatorul OR/AND. Codul evaluează logica și produce explicații românești din șabloane. Operatorul sau nivelul neclar păstrează unknown. Un reviewer trebuie în continuare să confirme că adnotările sunt fidele sursei.
4. **Unde?** languages.py, secțiunea UI dedicată și language_review din snapshotul aprobării. 123 teste trecute; 8/8 cazuri pe adnotări fictive explicite, fără inference nou.
5. **Alternative?** Un prompt mai lung a îmbunătățit unele exemple, dar nu a rezolvat generalizarea. Modelarea explicită reduce incertitudinea calculului, cu prețul revizuirii datelor de intrare și al unui domeniu inițial limitat. Nu avem nevoie de multi-agent sau fine-tuning pentru această logică.
6. **Interviu:** „După ce evaluările au arătat dovezi atribuite limbii greșite, am separat interpretarea sursei de logica de eligibilitate. Agentul a implementat reguli Python pe limbă, nivel, dovezi și OR/AND, integrate în UI și audit. Cele opt cazuri curate trec, dar nu le prezint ca precizie de 100% a modelului: adnotările sunt explicite și trebuie revizuite. Extracția generală și profilul real din CV rămân pașii următori.”
7. **Verificare amânată:** Diferența dintre reguli corecte pe intrări structurate și extragere corectă din text. Utilizatorul a cerut să lucrăm cap-coadă și să explicăm la final, fără întrebări intermediare repetate.

## Lecția 15 — Proveniență și profil master

1. **Ce este?** Proveniența arată din ce document și fragment exact provine o afirmație. Profilul master este o versiune revizuită a faptelor folosite la matching.
2. **De ce?** Nu vrem să transformăm o interpretare sau o omisiune într-o competență inventată. Păstrăm originalul integral și istoricul QA/rolurile vechi ca sursă pentru etapele ulterioare.
3. **Cum?** Importul local produce text și blocuri cu poziții. Reviewerul selectează excerpts exacte și confirmă. Versiunea profilului, citatele și metadatele revizuirii sunt salvate separat de fișierul original. O nouă selecție sau sursă produce altă versiune; hashul identifică datele, nu dovedește identitatea reviewerului.
4. **Unde?** cv_import.py, master_profile.py și UI Profil master din CV. 142 teste trecute; demonstrație cu 5 fapte fictive și surse exacte. Nu există CV real importat încă.
5. **Alternative?** LLM extraction ar putea propune fapte, dar ar necesita evaluare și revizuire suplimentare. În această etapă selectăm exact sursa, fără reformulare. RAG nu este necesar pentru această trasabilitate; o bază locală și citatele sunt suficiente.
6. **Interviu:** „Agentul a implementat importul local al CV-ului și un profil master versionat cu citate exacte. Originalul și istoricul profesional sunt păstrate, iar faptele selectate necesită confirmare. Am separat importul și proveniența de matching-ul AI: metadatele reviewerului și fișierul nu sunt trimise modelului. Cele 142 de teste au trecut pe documente fictive; importul și validarea CV-ului meu real nu sunt încă finalizate.”
7. **Verificare amânată:** Text extras din PDF nu înseamnă automat extracție completă sau profil aprobat. Preferința utilizatorului rămâne explicație la final, fără quiz intermediar.
