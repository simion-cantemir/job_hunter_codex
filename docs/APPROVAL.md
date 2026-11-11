# Aprobare explicită și aplicare auditată

Implementare: `jobhunter/approval.py` și `JobRepository.apply_approved_review()`. Din 2026-11-11 sunt accesibile și din [UI locală](LOCAL_UI.md), cu numele reviewerului, notă și confirmare explicită a materialului afișat.

## Flux

1. `review_fingerprint(material)` identifică snapshoturile originale și revizuite, profilul, sursa, notele corecțiilor și rezultatul recalculat de scoring/eligibilitate.
2. După revizuirea explicită, `approve_review()` cere acel fingerprint, numele reviewerului, o notă și `confirmed=True`. Un simplu acord de continuare a dezvoltării nu reprezintă această confirmare.
3. Rezultatul este o înregistrare `ReviewApproval` cu timestamp UTC, snapshot JSON și rezultatul aprobat. Materialul original rămâne pending ca artefact istoric; aprobarea este separată.
4. `apply_approved_review()` revalidează aprobarea față de materialul curent și jobul stocat, recalculează rezultatul și scrie decizia plus auditul în aceeași tranzacție SQLite.

Orice schimbare a sursei, profilului, explicațiilor, corecțiilor sau rezultatului rubricii/politicii invalidează aprobarea veche. Schimbările trebuie descrise complet în istoricul înainte/după; nu sunt acceptate revizuiri tacite. Un draft sau o propunere nu este acceptat în loc de `ReviewApproval`.

Tabela nouă `review_approvals` păstrează înregistrarea completă, inclusiv snapshoturile originale și revizuite, rezultatul, reviewerul și nota. `job_decisions` păstrează legătura cu aprobarea și scorul revizuit. Nu se șterg joburi sau decizii vechi. Dacă inserarea auditului eșuează, tranzacția revine integral; nu rămâne o decizie fără înregistrarea aprobării.

Reaplicarea exact a aceleiași înregistrări este idempotentă: returnează aceeași decizie fără duplicate. O înregistrare diferită pentru același material deja aplicat este respinsă explicit. O analiză/corecție nouă produce alt fingerprint și necesită aprobare nouă.

Aprobarea corectitudinii analizei nu înseamnă că jobul este potrivit. În exemplul fictiv scorul rămâne 60%, iar eligibilitatea needs_review: engleza și importanța experienței cu furnizorii necesită clarificare. Dacă o lipsă obligatorie este confirmată și analiza este aprobată, aplicarea exclude jobul din oportunități și păstrează motivul.

## Simulare verificată

```powershell
.\.venv\Scripts\python.exe -m jobhunter.approval_demo
```

Demo-ul folosește explicit `[SYNTHETIC] Demo reviewer`, aprobă numai în sensul simulării tehnice și aplică rezultatul într-o bază temporară din proiect, eliminată la final. Scrie un rezumat în `docs/evaluations/approval_001.demo.json`, cu `real_user_approval=false`. Nu modifică propunerea utilizatorului sau o bază persistentă și nu apelează Ollama.

Rezultatul observat: o decizie, o înregistrare de aprobare, replay fără duplicate, jobul rămâne în oportunitățile de clarificat. Cele 83 de teste au trecut, inclusiv rollback, sursă greșită, snapshot modificat, reguli de scoring schimbate și respingerea unei cerințe obligatorii lipsă într-un caz fictiv separat.

## Limite

Actualizare: adnotările opționale `language_review` sunt păstrate în snapshot și recomputate la verificarea aprobării. Schimbarea lor invalidează aprobarea chiar dacă scorul rămâne același. Pentru materialele vechi fără adnotări, serializarea canonică rămâne compatibilă; fingerprintul demonstrației anterioare este verificat prin test de regresie.

- Numele reviewerului este declarat de apelant; nu există autentificare sau semnătură digitală. Hashurile identifică datele, nu dovedesc identitatea ori o revizuire reală. Testele validează mecanismul, nu semantica unei analize.
- `save_decision()` rămâne un API de nivel jos pentru date curate/revizuite și teste istorice. Fluxurile AI trebuie să folosească `apply_approved_review()`. Nu pretindem că aplicația rezistă unui cod local malițios sau editării manuale a bazei.
- Există UI de confirmare locală; nu există revocare a aprobării sau conturi multi-user. Nu s-a obținut aprobarea utilizatorului pentru raportul R2 și nu a fost aplicată de agent o decizie reală. Testele UI folosesc revieweri fictivi și baze temporare.
- Aprobarea nu trimite aplicații, mesaje sau emailuri și nu autorizează astfel de acțiuni.
