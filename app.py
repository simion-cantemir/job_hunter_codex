"""Local Streamlit interface for Job Hunter AI's first reviewable workflow."""

from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3

import streamlit as st

from jobhunter.analysis import analyze_draft
from jobhunter.approval import review_fingerprint
from jobhunter.eligibility import evaluate_eligibility
from jobhunter.matching import validate_matches, validate_profile
from jobhunter.ollama import ExtractionError
from jobhunter.requirements import validate_requirements
from jobhunter.review import prepare_review, render_review
from jobhunter.scoring import score_requirements
from jobhunter.storage import JobRepository
from jobhunter.ui_session import ReviewSession
from jobhunter.languages import LANGUAGES, LEVELS, MINIMUMS, mentioned_languages
from jobhunter.profile_ui import master_profile_controls


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "tests" / "fixtures"
PRIORITIES = {"mandatory": "Obligatorie", "optional": "Opțională", "unknown": "Necunoscută"}
STATUSES = {"supported": "Susținută", "partial": "Parțială", "confirmed_missing": "Lipsă confirmată", "unknown": "Necunoscută"}
ELIGIBILITY = {"rejected": "Respins", "needs_review": "De clarificat", "eligible": "Fără blocaj identificat"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def repository():
    path = Path(os.environ.get("JOBHUNTER_DB_PATH", str(ROOT / "data/private/jobhunter-demo.sqlite3"))).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Baza locală trebuie să rămână în directorul proiectului.")
    path.parent.mkdir(parents=True, exist_ok=True)
    return JobRepository(path)


def show_history(repo):
    with st.expander("Joburi salvate și istoricul deciziilor"):
        jobs = repo.list_jobs()
        if not jobs:
            st.caption("Nicio analiză aplicată încă. Joburile sunt salvate la confirmare.")
            return
        for job in jobs:
            history = repo.decision_history(job.id)
            st.text(job.title)
            if not history:
                st.caption("Job salvat, fără decizie aplicată.")
            for decision in history:
                st.caption(f"{decision['created_at']} · {ELIGIBILITY[decision['status']]}")
                review = decision.get("review", {})
                if review:
                    st.text(f"Revizuit de: {review['reviewer']}")
                    st.text(review["note"])
                for reason in decision["reasons"]:
                    st.text(reason["explanation"])


def language_controls(workflow, base, facts_by_id):
    with st.expander("Limbi de lucru — reguli explicite în Python"):
        enabled = st.checkbox("Evaluează limbile pe date structurate", key=f"lang_{workflow.epoch}_enabled")
        st.caption("Verifică asocierea fiecărei limbi cu sursa și nivelul. Nu deducem niveluri din text sau din limba anunțului. Suport inițial: engleză, germană, franceză, spaniolă, română, italiană.")
        if not enabled:
            return None
        rules = []
        codes_in_use = set()
        for requirement in base.original_requirements["requirements"]:
            codes = list(mentioned_languages(requirement["quote"]))
            if not codes:
                continue
            st.text(requirement["quote"])
            key = f"lang_{workflow.epoch}_{requirement['id']}"
            operator = st.selectbox("Condiție între limbi", ["all", "any", "unclear"],
                                    index=0 if len(codes) == 1 else 2,
                                    format_func=lambda value: {"all": "Toate — AND", "any": "Cel puțin una — OR", "unclear": "Neclară, necesită revizuire"}[value], key=key + "_operator")
            minimum = st.selectbox("Nivelul minim cerut", list(MINIMUMS), format_func=MINIMUMS.get, key=key + "_minimum")
            rules.append({"requirement_id": requirement["id"], "operator": operator, "languages": codes, "minimum": minimum})
            codes_in_use.update(codes)
        abilities = []
        for code in LANGUAGES:
            if code not in codes_in_use:
                continue
            st.subheader(LANGUAGES[code])
            key = f"lang_{workflow.epoch}_{code}"
            level = st.selectbox("Nivel declarat în profil", list(LEVELS), format_func=LEVELS.get, key=key + "_level")
            kind = "confirmed_gap" if level == "none" else "experience"
            available = [ref for ref, fact in facts_by_id.items() if fact["kind"] == kind and code in mentioned_languages(fact["text"])]
            refs = st.multiselect("Dovezi pentru această limbă", available if level != "unknown" else [], key=key + "_evidence")
            for ref in refs:
                st.text(f"{ref}: {facts_by_id[ref]['text']}")
            abilities.append({"language": code, "level": level, "evidence_ids": refs})
        if not rules:
            st.warning("Nicio limbă din vocabularul inițial nu a fost recunoscută în cerințe. Verifică manual omisiunile; acest control nu este un parser universal.")
        return {"schema_version": "1", "abilities": abilities, "rules": rules}


def main():
    st.set_page_config(page_title="Job Hunter AI", page_icon="🔎", layout="wide")
    st.title("Job Hunter AI")
    st.caption("Oportunități explicabile. Dovezi înainte de decizii.")
    st.caption("Prototip local. Datele CV-ului nu sunt trimise către servicii cloud; analiza folosește Ollama local numai la cerere.")
    workflow = st.session_state.setdefault("workflow", ReviewSession())
    repo = repository()
    st.caption("CV → fragmente alese de tine → comparație cu cerințele unui job")
    title = st.session_state.get("job_title", "[SYNTHETIC] Engineering Manager")
    source = st.session_state.get("job_source", (FIXTURES / "job_001.txt").read_text(encoding="utf-8"))
    original_profile = load_json(FIXTURES / "profile_001.json")
    profile_mode = st.radio("Profil pentru analiză", ["Profil fictiv", "Profil master din CV"], index=1, key="profile_mode", horizontal=True)
    facts = []
    if profile_mode == "Profil fictiv":
        st.info("Profil fictiv activ — nu reprezintă experiența ta reală.")
        with st.expander("Profil fictiv folosit pentru comparație"):
            st.caption("Poți modifica datele de test. Orice schimbare invalidează analiza și confirmarea curente.")
            for fact, label in zip(original_profile["facts"], ["Leadership", "Engleză", "Experiență AI adoption"]):
                text = st.text_area(label, value=fact["text"], key=f"profile_{fact['id']}")
                kind = st.selectbox(f"Tipul dovezii — {label}", ["experience", "confirmed_gap"],
                                    index=0 if fact["kind"] == "experience" else 1,
                                    format_func=lambda value: "Experiență declarată" if value == "experience" else "Lipsă declarată explicit",
                                    key=f"kind_{fact['id']}")
                facts.append({"id": fact["id"], "kind": kind, "text": text})
        profile = {"version": original_profile["version"], "facts": facts}
        if facts != original_profile["facts"]:
            profile["version"] = "synthetic-edited-" + sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()[:16]
    else:
        try:
            profile = master_profile_controls(repo.database_path)
        except (ValueError, sqlite3.Error) as error:
            st.error(f"Profilul master nu a putut fi încărcat sau validat: {error}")
            profile = None
        if profile is None:
            workflow.sync_inputs(title, source, {"version": "master-pending", "facts": []})
            st.info("Alege fragmentele din CV și salvează selecția. Apoi vei putea introduce jobul pentru comparație.")
            return
    st.subheader("3. Compară fragmentele cu un job")
    if profile_mode == "Profil master din CV":
        title = st.session_state.get("job_title", "")
        source = st.session_state.get("job_source", "")
    title = st.text_input("Titlul jobului", value=title, key="job_title")
    source = st.text_area("Descrierea completă a jobului", value=source, height=220, key="job_source")
    st.caption("Modelul local extrage cerințele din job și le compară cu fragmentele alese. Rezultatul rămâne o propunere pe care o verifici.")
    changed = workflow.sync_inputs(title, source, profile)
    if changed and workflow.epoch > 1:
        st.warning("Datele s-au schimbat. Analiza și confirmarea anterioare au fost invalidate în sesiunea curentă.")
    col_demo, col_ai = st.columns(2)
    if col_demo.button("Încarcă analiza fictivă salvată", key="load_saved", use_container_width=True,
                       disabled=profile_mode != "Profil fictiv"):
        try:
            if source != (FIXTURES / "job_001.txt").read_text(encoding="utf-8") or profile != original_profile:
                raise ValueError("Analiza salvată corespunde numai jobului și profilului fictive inițiale. Pentru date modificate folosește analiza locală.")
            workflow.load_report(load_json(ROOT / "docs/evaluations/ollama_analysis_001_run_001.json"), title, source, profile)
        except ValueError as error:
            st.error(str(error))
    if col_ai.button("Analizează cu Ollama local", key="analyze", use_container_width=True):
        try:
            if not title.strip():
                raise ValueError("Completează titlul jobului.")
            # Clear an old result before inference; failures must not expose it as current.
            workflow.report = None
            workflow.approval = None
            workflow.revision += 1
            with st.spinner("Extrag cerințele și compar dovezile cu modelul local…"):
                # Match the saved-report contract: JSON arrays, not Python tuples.
                report = json.loads(json.dumps(asdict(analyze_draft(source, profile, recover_matching=True)), ensure_ascii=False))
            workflow.load_report(report, title, source, profile)
        except (ExtractionError, ValueError) as error:
            st.error(f"Analiza nu a reușit: {error}")
    show_history(repo)
    if workflow.report is None:
        st.caption("Încarcă exemplul salvat sau pornește analiza locală. Nicio decizie nu se aplică automat.")
        return
    base = prepare_review(workflow.report, source, profile)
    issues = workflow.report.get("matching", {}).get("issues", [])
    if issues:
        st.warning("Unele răspunsuri ale modelului nu au trecut validarea. Cerințele afectate sunt marcate ca necunoscute, fără dovezi inventate. Verifică-le manual înainte de confirmare.")
        for issue in issues:
            st.text(f"{issue['requirement_id'] or 'Matching'}: {issue['message']}")
    facts_by_id = {fact["id"]: fact for fact in profile["facts"]}
    originals = {m["requirement_id"]: m for m in base.original_matches["matches"]}
    changes = []
    st.header("Revizuiește cerințele și dovezile")
    st.caption("Verifică sensul fiecărei explicații, nu doar statusul. Corecțiile rămân propuneri până la confirmare.")
    for requirement in base.original_requirements["requirements"]:
        identifier = requirement["id"]
        match = originals[identifier]
        prefix = f"edit_{workflow.epoch}_{identifier}"
        with st.expander(f"{identifier} · {PRIORITIES[requirement['priority']]} · {STATUSES[match['status']]}", expanded=True):
            st.caption("Citat exact din anunț")
            st.text(requirement["quote"])
            left, right = st.columns(2)
            with left:
                st.caption("Explicația originală a modelului")
                st.text(match["explanation"])
                st.caption("Dovezi citate în profil")
                if not match["evidence_ids"]:
                    st.text("Fără dovezi concludente. Absența informației nu demonstrează lipsa experienței.")
                for ref in match["evidence_ids"]:
                    st.text(f"{ref}: {facts_by_id[ref]['text']}")
            with right:
                priority = st.selectbox("Prioritate revizuită", list(PRIORITIES), index=list(PRIORITIES).index(requirement["priority"]),
                                        format_func=PRIORITIES.get, key=prefix + "_priority")
                status = st.selectbox("Matching revizuit", list(STATUSES), index=list(STATUSES).index(match["status"]),
                                      format_func=STATUSES.get, key=prefix + "_status")
                evidence = st.multiselect("Dovezi pentru concluzie", list(facts_by_id), default=match["evidence_ids"],
                                          key=prefix + "_evidence")
                for ref in evidence:
                    st.text(f"{ref}: {facts_by_id[ref]['text']}")
                explanation = st.text_area("Explicație revizuită", value=match["explanation"], key=prefix + "_explanation")
                modified = (priority != requirement["priority"] or status != match["status"]
                            or evidence != match["evidence_ids"] or explanation != match["explanation"])
                if modified:
                    note = st.text_input("Motivul corecției", key=prefix + "_note")
                    changes.append({"requirement_id": identifier, "priority": priority, "status": status,
                                    "evidence_ids": evidence, "explanation": explanation, "note": note})
    workflow.set_changes(changes)
    workflow.set_language_review(language_controls(workflow, base, facts_by_id))
    try:
        material = workflow.material(title, source, profile)
        fingerprint = review_fingerprint(material)
        requirements = validate_requirements(material.revised_requirements, source)
        matches = validate_matches(material.revised_matches, requirements, validate_profile(profile))
        score = score_requirements(requirements, matches)
        decision = evaluate_eligibility(source, material.revised_requirements, profile, material.revised_matches)
    except ValueError as error:
        st.error(f"Corecțiile nu sunt încă valide. Completează motivul și verifică dovezile: {error}")
        return
    st.header("Rezultatul propus")
    score_text = "Indisponibil" if score.minimum_percent is None else f"{score.minimum_percent:.0f}–{score.maximum_percent:.0f}%"
    first, second = st.columns(2)
    first.metric("Compatibilitate pe cerințele incluse", score_text)
    second.metric("Eligibilitate propusă", ELIGIBILITY[decision.status])
    st.caption(f"Cerințe excluse pentru prioritate necunoscută: {len(score.excluded_requirement_ids)}. Scorul nu este probabilitate de angajare.")
    for reason in decision.reasons:
        st.warning(f"{reason.requirement_id or 'Analiză'}: {reason.explanation}")
    if not requirements:
        st.warning("Nu sunt cerințe extrase. Nu considera această analiză completă.")
    st.download_button("Descarcă raportul de revizuire", render_review(material), file_name="job-review.md", mime="text/markdown")
    st.header("Confirmă analiza și aplică rezultatul")
    st.caption("Confirmi fidelitatea analizei. Jobul poate rămâne de clarificat sau poate fi respins, conform cerințelor obligatorii.")
    reviewer = st.text_input("Numele reviewerului", key="reviewer")
    review_note = st.text_area("Nota revizuirii", key="review_note")
    approval_key = f"confirmation_{workflow.revision}_{fingerprint}"
    confirmed = st.checkbox("Am verificat cerințele, prioritățile, dovezile și explicațiile afișate.", key=approval_key)
    if st.button("Confirmă și aplică în istoricul local", key="apply_review", type="primary",
                 disabled=not confirmed or not reviewer.strip() or not review_note.strip()):
        try:
            workflow.apply(repo, title, source, profile, expected_fingerprint=fingerprint,
                           reviewer=reviewer, note=review_note, confirmed=confirmed)
        except (ValueError, sqlite3.Error) as error:
            st.error(f"Rezultatul nu a fost aplicat: {error}")
    if workflow.applied_decision_id is not None:
        st.success("Analiza revizuită a fost aplicată și auditul a fost salvat. Nicio aplicație sau mesaj nu a fost trimis.")


if __name__ == "__main__":
    main()
