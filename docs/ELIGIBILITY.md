# Eligibilitate și istoric — politica 1

Politică acceptată de utilizator: o cerință obligatorie confirmată ca neîndeplinită respinge jobul din oportunități, indiferent de scor. Limba de lucru este un criteriu determinant. Nu ștergem jobul fizic; păstrăm motivul și istoricul.

## Reguli implementate

| Situație | Decizie |
|---|---|
| Mandatory + confirmed_missing | rejected |
| Mandatory + partial sau unknown | needs_review |
| Prioritate unknown | needs_review, până la clarificare |
| Nicio cerință extrasă | needs_review |
| Mandatory satisfăcute, fără priorități necunoscute | eligible; lipsurile opționale nu resping |

O respingere are prioritate față de motivele de clarificare. `eligible` înseamnă doar că filtrele implementate nu au identificat un blocaj; nu reprezintă recomandare automată sau aplicare. Scorul rămâne separat și păstrează cerința obligatorie lipsă cu zero puncte.

Exemplu fictiv: germană fluentă obligatorie și declarație explicită că persoana nu vorbește germană → respins. Germană opțională → nu respingem. Fără informații în profil → clarificare, nu lipsă confirmată. Nu deducem limba de lucru din limba anunțului și nu implementăm un parser de limbi în acest pas. Cerințele alternative precum „engleză SAU germană” trebuie interpretate corect înainte de aplicarea politicii; nu sunt două cerințe obligatorii independente.

## Implementare și persistență

`jobhunter/eligibility.py` validează cerințele față de textul sursă, profilul și matching-ul înainte să aplice regulile. Validarea provenienței nu garantează interpretarea semantică. Politica se aplică rezultatelor curate/revizuite. Workflow-ul AI integrat ulterior în `jobhunter/analysis.py` folosește motorul doar pentru o propunere, fără a persista sau aplica respingeri înainte de revizuire.

`JobRepository.save_decision()` adaugă o decizie în `job_decisions` cu status, motive, citatul cerinței, referințe la dovezi, versiunea profilului și a politicii, amprenta SHA-256 a textului și timestamp UTC. Amprenta trebuie să corespundă jobului stocat. Tabela suplimentară este creată fără ștergerea sau rescrierea joburilor existente.

`list_opportunities()` exclude joburile a căror ultimă decizie este rejected; include joburi noi, eligibile și de clarificat. `decision_history()` păstrează deciziile în ordine. O reevaluare explicită poate schimba statusul; istoricul anterior rămâne. Nu există încă UI, deduplicare la reimport sau mecanism automat care să evite reanalizarea unui job respins importat ca înregistrare nouă. Acestea urmează la discovery/tracking.

În această etapă păstrăm textul original plus metadatele deciziei; nu există încă politica finală de retenție sau arhivare redusă la un marker de deduplicare. Profilul real și documentele personale nu au fost introduse. Sunt necesare versiunile persistente ale profilului și analizelor înainte de auditul complet pe date reale.
