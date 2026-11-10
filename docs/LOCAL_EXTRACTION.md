# Prima integrare Ollama

`jobhunter/ollama.py` folosește biblioteca standard Python pentru POST la `http://127.0.0.1:11434/api/chat`. Modelul este fixat la `llama3.2:3b`, deja instalat; adaptorul nu descarcă modele și nu configurează cloud. Proxy-urile sistemului sunt ignorate și redirecturile sunt refuzate pentru acest apel.

## Flux și utilizare

```powershell
.\.venv\Scripts\python.exe -m jobhunter.extract_demo
```

Comanda citește exclusiv jobul fictiv din `tests/fixtures/job_001.txt`, afișează rezultatul și comparația cu exemplul așteptat. Nu modifică SQLite și nu face matching cu profilul. Comparația folosește perechi citat/prioritate, fără a pretinde că un singur exemplu este un benchmark reprezentativ. Rezultatul de referință a fost propus de agent și nu este încă revizuit de utilizator.

Python trimite instrucțiuni în mesajul system și jobul ca date JSON în mesajul user. Modelul returnează doar prioritatea și citatul. Python calculează ID-urile și pozițiile în sursă și apelează validatorul existent. Citările inexistente, ambigue (apar de mai multe ori) sau duplicate sunt respinse. Nu reparăm automat citate și nu extragem procente de compatibilitate din răspuns.

Ollama primește schema JSON prin `format` și `stream: false`, conform [API chat](https://docs.ollama.com/api/chat) și [structured outputs](https://docs.ollama.com/capabilities/structured-outputs), consultate la 2026-11-10. Schema constrânge forma răspunsului; validarea sursei și evaluarea sensului rămân responsabilități separate.

## Limite și erori

- Prompt version `requirements-1`; temperature 0, seed 42, context 8192 tokens, maximum 1024 tokens generați. Temperatura mică reduce variația, fără garanție de reproducibilitate absolută.
- Maximum 8000 caractere de sursă în acest experiment, fără trunchiere automată. Limita în caractere nu garantează încadrarea oricărui text în contextul exprimat în tokens; tokenizarea și calibrarea pentru joburi lungi rămân de realizat.
- Timeout de conexiune/citire de 60 secunde implicit, configurabil până la 120 secunde; nu este un deadline absolut pentru toate operațiile de transport. Răspuns de maximum 256000 bytes. Fără retry automat. Un timeout al clientului nu garantează anularea imediată a inference pe server.
- Erorile HTTP, lipsa serviciului/modelului, JSON invalid, output neterminat sau limita de tokens atinsă produc `ExtractionError`, fără folosirea unui rezultat parțial. Mesajele de eroare nu includ textul jobului sau corpul răspunsului HTTP.
- `keep_alive: "0"` solicită eliberarea modelului după răspuns; nu schimbă configurația persistentă Ollama. Testul real poate încărca modelul și utiliza CPU/GPU/RAM/VRAM.
- Promptul tratează anunțul ca date neîncredere și nu oferă tools. Această delimitare nu garantează imunitate la prompt injection sau corectitudine semantică. Un citat real poate fi totuși clasificat greșit ori unele cerințe pot lipsi.
- Golul de cerințe rămâne gol; politica de eligibilitate existentă cere revizuire, nu declară automat potrivire.

Testele unitare folosesc transport simulat; rularea reală este separată și trebuie raportată distinct. Nu s-au transmis date personale sau CV-uri în acest pas.

## Rezultat observat

Prima rulare locală a reușit: 4 cerințe, toate cu citat și prioritate identice cu exemplul așteptat. Timp observat: 37,449 secunde, 396 tokens de prompt și 102 tokens generați conform răspunsului Ollama. Datele sunt salvate în `docs/evaluations/ollama_job_001_run_001.json`. Nu am măsurat utilizarea GPU, separarea timpului de încărcare sau distribuția latenței pe rulări repetate. Cele 51 de teste locale au trecut, independent de această rulare reală.
