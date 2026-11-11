# Interview preparation

Preferință actualizată: răspunsurile noi se formulează în română; versiunile în engleză de mai jos sunt materiale anterioare și rămân opționale.

## Cum explic profilul master și proveniența

„Pentru a evita afirmații inventate, am cerut ca profilul folosit la matching să fie legat de surse exacte. Agentul a implementat importul local TXT/DOCX/PDF, selecția de fragmente, revizuirea și versiuni separate, păstrând documentul integral și istoricul QA. Citatele și metadatele rămân în audit; modelul primește numai faptele selectate. Testele pe documente fictive au trecut. Nu pretind că a fost validat CV-ul meu real sau că extragerea oricărui PDF este completă.”

## Cum explic trecerea la reguli deterministe pentru limbi

„Am folosit evaluarea pentru a identifica unde un LLM nu era suficient de fiabil. Pentru limbile de lucru, agentul a implementat o reprezentare explicită a nivelurilor, dovezilor și condițiilor OR/AND și o evaluare deterministă în Python. Configurația este vizibilă în UI, intră în audit și modificarea ei invalidează aprobarea. Cele 123 de teste au trecut, iar opt cazuri cu adnotări fictive au rezultatul așteptat. Aceasta validează logica pe intrări structurate, nu extracția automată sau calitatea generală a modelului. Rolul meu a fost să stabilesc criteriile de produs; agentul a implementat și verificat soluția.”

## Cum explic de ce nu am activat un candidat de prompt

„Am folosit evaluarea pentru a decide dacă o schimbare merită activată. Agentul a implementat un prompt nou și l-a comparat cu versiunea veche. Cazurile inițiale au trecut de la două din trei la trei din trei, dar setul nou a expus o respingere greșită și dovezi irelevante. Am păstrat candidatul experimental și nevoia de revizuire. Testele de cod au trecut, însă asta nu înseamnă că modelul este sigur pentru filtrare autonomă. Următorul pas propus este să reprezentăm limbile și condițiile lor explicit și să verificăm logica în Python.”

Atribuire: utilizatorul a cerut continuarea și criteriile de produs; agentul a scris prompturile, cazurile și runnerul și a inspectat outputul. Nu susținem că utilizatorul a efectuat benchmark-ul sau că problemele observate au fost deja rezolvate.

## Cum explic o eroare găsită prin model evaluation

„Am stabilit cazuri de referință înainte de a rula modelul și am separat extragerea, matching-ul și eligibilitatea. Cele 101 teste de cod au trecut, însă evaluarea reală a identificat o dovadă ignorată în cazul unei limbi opționale. Decizia finală era totuși corectă, ceea ce ar fi ascuns problema dacă măsuram numai eligibilitatea. Agentul a implementat evaluarea și a inspectat rezultatele. Eu am autorizat criteriile de produs; corecția modelului și validarea pe exemple noi sunt încă de făcut. Nu prezint trei exemple fictive drept un benchmark reprezentativ.”

## Exemplu STAR — revizuirea unui rezultat AI pe date fictive

- **Situation:** „În primul exemplu demonstrativ, modelul a extras statusurile așteptate, dar explicația despre engleză modifica o informație din profilul fictiv.”
- **Task:** „Rolul meu a fost să verific dacă rezultatul era fidel surselor înainte de aplicare.”
- **Action:** „Am parcurs ghidat cele patru cerințe în interfață, am comparat explicația R2 cu dovada P2 și am corectat formularea, păstrând statusul parțial. Am verificat separat cerința opțională lipsă și informațiile necunoscute, apoi am confirmat analiza revizuită.”
- **Result:** „Scorul a rămas 60%, iar jobul De clarificat. Interfața a confirmat salvarea cu audit. Am demonstrat pe un exemplu fictiv de ce validitatea tehnică și fidelitatea explicației trebuie verificate separat.”

Atribuire și limite: utilizatorul a făcut walkthrough-ul și a confirmat salvarea prin conversație; agentul a scris codul, executat testele și ghidat revizuirea. Nu este un rezultat pe CV real, o creștere măsurată a preciziei sau o verificare independentă a bazei de către agent. Secțiunile mai vechi de mai jos descriu etapele anterioare acestei acceptări.

## Cum explic interfața și verificarea integrării

„Am urmărit un MVP personal care să poată fi folosit fără comenzi de dezvoltare. Agentul a construit interfața Streamlit peste serviciile Python, păstrând regulile și auditul în backend. Interacțiunile au fost testate cu AppTest, inclusiv invalidarea confirmării după editări și lipsa duplicatelor la rerun. Cele 94 de teste au trecut, iar serverul a răspuns corect prin HTTP. Testele au folosit profil fictiv și transport AI simulat; walkthrough-ul utilizatorului și evaluarea pe date reale nu sunt încă finalizate.”

## Cum explic aprobarea și auditul

„Am cerut ca aplicarea rezultatului AI să fie separată de generare și legată de o revizuire explicită. Agentul a implementat înregistrarea snapshoturilor, reviewerului declarat, notei și timpului aprobării. Decizia și auditul se scriu împreună, iar repetarea aceleiași operații nu creează duplicate. Cele 83 de teste locale au trecut. Simularea folosește date și reviewer fictivi; identitatea nu este autentificată, iar utilizatorul nu a aprobat încă analiza reală din proiect.”

## Cum explic trasabilitatea corecțiilor

„Am cerut ca un rezultat AI să poată fi verificat față de surse, iar eventualele corecții să păstreze originalul și motivul schimbării. Agentul a implementat un raport în care cerințele, dovezile și explicațiile apar împreună. Corecția unei explicații greșite despre engleză este propusă separat, fără a o prezenta drept aprobare umană. Cele 69 de teste tehnice au trecut. Urmează aprobarea explicită și aplicarea cu audit în baza de date.”

## Cum explic diferența dintre o propunere AI și o decizie

„Pentru a controla consecințele erorilor AI, am separat raportul propus de aplicarea unei decizii. Agentul a implementat un flux local de extragere, matching și calcul determinist, care produce doar un draft pentru revizuire. Cele patru statusuri și referințele la dovezi au corespuns exemplului așteptat, dar o explicație a modificat un fapt din profil. Asta ne-a arătat de ce validarea structurii nu este suficientă. Cele 60 de teste locale verifică regulile tehnice, iar revizuirea semantică și evaluarea pe mai multe exemple urmează.”

Limite de atribuire: utilizatorul a definit constrângerile și autorizat pasul; agentul a implementat și inspectat outputul real. Nu susținem că utilizatorul a aprobat semantic raportul sau că testele măsoară deja precizia pe joburi reale.

## Cum explic prima integrare locală AI

„Am urmărit o integrare simplă și verificabilă înainte de automatizări complexe. Agentul a conectat Python la modelul local prin API-ul Ollama și a implementat validarea răspunsului structurat și a citatelor. Prima rulare pe un job fictiv a returnat cele patru cerințe așteptate, în aproximativ 37 de secunde. Cele 51 de teste locale verifică separat transportul și regulile aplicației. Rezultatul unui singur caz nu demonstrează precizia generală; nu am validat încă matching-ul automat sau utilizarea pe date personale.”

Atribuire: agentul a implementat adaptorul și a executat verificările. Utilizatorul a autorizat pasul; nu atribuim utilizatorului scrierea manuală a codului ori un benchmark pe care nu l-a realizat.

## Cum explic un criteriu eliminatoriu

„Am decis ca un job să fie respins dacă o cerință obligatorie este confirmată ca neîndeplinită, cu atenție specială la limba de lucru. Scorul general nu poate compensa acel blocaj. Agentul a implementat politica și istoricul motivelor în SQLite; cele 41 de teste locale au trecut. Datele necunoscute cer clarificare și nu sunt tratate ca lipsuri confirmate. Integrarea modelului și validarea pe anunțuri reale urmează.”

Atribuire: utilizatorul a stabilit și acceptat comportamentul eliminatoriu; agentul a implementat și executat testele. Nu există încă validare a acurateței unui LLM.

## Cum explic matching-ul bazat pe dovezi

„Pentru Job Hunter AI am cerut ca rezultatele comparației să fie explicabile. Agentul de dezvoltare a implementat un contract care leagă fiecare cerință de dovezi dintr-un profil fictiv și distinge între potrivire susținută, parțială, lipsă confirmată și informație necunoscută. Cele 18 teste locale au trecut. Acest lucru validează regulile și trasabilitatea datelor; nu dovedește încă precizia unui model AI. Rolul meu este să revizuiesc criteriile și exemplele, iar integrarea și evaluarea modelului sunt pași următori.”

Exemplul de matching este propus de agent, încă nerevizuit de utilizator. Utilizatorul a autorizat continuarea; nu presupunem că a validat semantic rezultatele sau a scris codul.

## Cum explic scoring-ul transparent

„Am cerut ca produsul să ofere explicații verificabile, iar agentul de dezvoltare a implementat un calcul determinist separat de modelul AI. Rubrica inițială folosește ponderi explicite și păstrează informațiile necunoscute prin intervale și avertizări. Cerințele cu importanță neprecizată sunt listate separat, în afara calculului. Cele 29 de teste locale au trecut. Ponderile sunt încă experimentale, iar integrarea modelului și evaluarea pe joburi reale urmează; nu prezint scorul ca probabilitate de angajare.”

## Explain the two roles of AI in this project — 30–60 seconds

“I am approaching Job Hunter AI as a product and delivery learning project. I defined the target users, job preferences and safety constraints. The proposed architecture separates the coding agent used to develop the software from the language model the application will call at runtime. Codex assists with implementation and technical checks. The application model would extract requirements from job descriptions, while Python would validate evidence and calculate a transparent score. At this stage, environment discovery and planning are complete; the application and model quality have not yet been validated. My role is to review product decisions and acceptance criteria, rather than claim that I manually wrote the implementation.”

## Dovezi și atribuirea contribuțiilor

- Utilizator: cerințe de produs, constrângeri, obiective profesionale și educaționale.
- Agent AI: diagnostic, documentație, arhitectură propusă și componentă minimă de stocare SQLite.
- Verificat tehnic de agent: versiuni tool-uri, hardware, listarea modelului, absența prototipului în director, mediu virtual și 2 teste de integrare SQLite.
- Verificat prin răspunsul utilizatorului: distincția de bază dintre Codex și LLM-ul local al aplicației.
- Verificat prin răspunsul utilizatorului: persistența SQLite este independentă de Ollama.
- Agent AI, F1: contract de extragere, validator de proveniență și primul exemplu sintetic; suita de 9 teste a trecut. Exemplul nu este încă revizuit uman și nu există rezultate de inference măsurate.
- Neconfirmat: acceptarea întregii arhitecturi de utilizator, inference, UI și eficiența matching-ului.

Nu există încă un rezultat de produs validat pentru un exemplu STAR. Îl vom adăuga după o livrare reală, cu Situation/Task/Action/Result susținute de dovezi și contribuții atribuite corect.
