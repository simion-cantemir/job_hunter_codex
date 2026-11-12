# Diagnosticarea matching-ului

Actualizare: 2026-11-12.

Mesajul vechi „Model matching failed JSON, coverage or evidence validation” grupa mai multe cauze. Nu putem identifica retrospectiv cauza exactă a rulării utilizatorului: răspunsul respectiv nu a fost inspectat sau păstrat pentru diagnostic.

## Comportament

Schema `matching-schema-2` limitează ID-urile dovezilor la faptele profilului curent și cere numărul exact de rezultate. Validatorul Python verifică în continuare acoperirea unică, statusurile și tipurile dovezilor. Schema nu garantează interpretarea corectă a surselor.

API-ul `propose_matches()` rămâne strict implicit. Erorile au acum categorii explicite: JSON invalid, cerință omisă/duplicată, dovezi inexistente, dovezi de tip nepotrivit, explicație lipsă etc. Diagnosticul nu include textul brut al modelului sau ID-uri externe neverificate.

UI activează explicit recuperarea conservatoare. Un rezultat invalid devine `unknown`, fără dovezi, cu explicație că necesită revizuire manuală. Rezultatele valide structural sunt păstrate pentru revizuire. Dacă întregul JSON este invalid, toate cerințele devin necunoscute. Nu alegem între rezultate duplicate și nu inventăm experiență sau lipsuri. Lista finală trece din nou prin validatorul strict.

Problemele sunt afișate în UI. Analiza rămâne `pending_semantic_review`; aprobarea explicită a snapshotului este necesară pentru aplicare. Timeouturile și erorile de transport nu sunt recuperate astfel. Extragerea cerințelor păstrează propriile validări stricte.

## Verificare și limite

152 teste trecute, inclusiv cazuri simulate de JSON invalid, acoperire incompletă, duplicate și dovezi invalide; AppTest verifică deschiderea revizuirii fără salvare sau aprobare implicită. Testele obișnuite nu apelează Ollama.

`python -m jobhunter.matching_recovery_demo` a apelat Ollama local pe un profil master și un job exclusiv fictive: 4/4 rezultate valide structural, fără diagnostic de recuperare, `needs_review`, nicio decizie aplicată. Rezumat: [matching_recovery_001.smoke.json](evaluations/matching_recovery_001.smoke.json). Este un smoke check, nu un benchmark semantic sau reproducerea incidentului privat. Calea de recuperare este verificată prin testele simulate.

Pentru reluare, repornește Streamlit, selectează profilul master deja salvat și reia analiza. Nu este necesară reimportarea CV-ului salvat. Revizuiește sursele și orice rezultat necunoscut înainte de confirmare. CV-ul și baza privată nu au fost accesate pentru această corecție.
