# Interview preparation

Preferință actualizată: răspunsurile noi se formulează în română; versiunile în engleză de mai jos sunt materiale anterioare și rămân opționale.

## Cum explic matching-ul bazat pe dovezi

„Pentru Job Hunter AI am cerut ca rezultatele comparației să fie explicabile. Agentul de dezvoltare a implementat un contract care leagă fiecare cerință de dovezi dintr-un profil fictiv și distinge între potrivire susținută, parțială, lipsă confirmată și informație necunoscută. Cele 18 teste locale au trecut. Acest lucru validează regulile și trasabilitatea datelor; nu dovedește încă precizia unui model AI. Rolul meu este să revizuiesc criteriile și exemplele, iar integrarea și evaluarea modelului sunt pași următori.”

Exemplul de matching este propus de agent, încă nerevizuit de utilizator. Utilizatorul a autorizat continuarea; nu presupunem că a validat semantic rezultatele sau a scris codul.

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
