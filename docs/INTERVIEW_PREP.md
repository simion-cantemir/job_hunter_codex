# Interview preparation

Preferință actualizată: răspunsurile noi se formulează în română; versiunile în engleză de mai jos sunt materiale anterioare și rămân opționale.

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
