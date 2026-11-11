# Raport de revizuire și corecții propuse

Comandă demonstrabilă, fără Ollama:

```powershell
.\.venv\Scripts\python.exe -m jobhunter.review_demo
```

Generează `docs/evaluations/review_001.md` și snapshotul `review_001.proposal.json` folosind analiza fictivă deja salvată. Comanda reface aceste două artefacte demonstrative; nu suprascrie analiza originală și nu schimbă SQLite. Nu necesită pachete suplimentare sau inference. Mesajele terminalului sunt fără diacritice pentru compatibilitate cu Windows cp1252; fișierele sunt UTF-8.

## Ce se poate verifica

- Fiecare cerință este afișată cu prioritatea, matching-ul și citatul exact din job.
- Fiecare ID de dovadă este însoțit de textul original din profil. Sunt afișate și jobul/profilul integral pentru identificarea omisiunilor.
- Explicația originală a modelului rămâne vizibilă chiar când este greșită.
- Corecția propusă include valorile înainte/după și un motiv. Demo-ul corectează numai explicația R2, păstrând mandatory/partial și dovada P2.
- Scorul și eligibilitatea sunt recalculate din datele validate; valorile numerice salvate în raportul AI nu sunt tratate drept adevăr.
- Textul extern este escaped în Markdown, pentru a păstra citatele ca text, fără linkuri active sau HTML injectat.

Implementare: `jobhunter/review.py`. Materialul este legat prin SHA-256 de raportul complet, textul-sursă și snapshotul profilului. Corecțiile care indică alt fingerprint sunt respinse. Amprenta identifică datele; nu autentifică un reviewer și nu dovedește aprobarea.

Analiza istorică din primul demo avea numai versiunea profilului, nu hashul lui. Nu putem certifica retroactiv identitatea profilului original doar din acel raport; în acest pas legăm explicit profilul furnizat la materialul de revizuire. Pentru date reale trebuie persistate snapshoturile și versiunile de la generarea analizei.

## Limite explicite

`prepare_review()` construiește doar propuneri, inclusiv după corectare: pending_semantic_review și decision_applied=false. [Aprobarea backend și aplicarea auditată](APPROVAL.md) sunt implementate separat și accesibile din UI Streamlit locală. Nu există reviewer autentificat. Faptul că agentul a redactat corecția nu constituie revizuire umană.

Schema corecțiilor permite schimbarea priorității, statusului, dovezilor și explicației pentru cerințe existente, după revalidare. Nu adaugă/șterge cerințe sau fapte din profil și nu schimbă citatele. Omisiunile de extragere se semnalează la revizuire; editarea lor necesită o extensie ulterioară. Validarea tehnică nu garantează sensul corecției.

Testele verifică afișarea dovezilor, păstrarea erorii originale, neaplicarea deciziilor, respingerea fingerprintului greșit, revalidarea dovezilor și recalcularea scorului. Cele 69 de teste ale suitei au trecut. Demo-ul a fost executat și raportul generat a fost inspectat textual; nu s-a efectuat un test într-un browser sau o aprobare de către utilizator.
