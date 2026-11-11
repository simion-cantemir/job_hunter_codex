"""Local CV import/review UI. No LLM is called and no fact is auto-approved."""

from hashlib import sha256
import streamlit as st

from jobhunter.cv_import import import_cv
from jobhunter.master_profile import MasterProfileStore, prepare_master, approve_master


def master_profile_controls(database_path):
    store = MasterProfileStore(database_path)
    profiles = store.list_profiles()
    if "master_next_action" in st.session_state:
        st.session_state["master_action"] = st.session_state.pop("master_next_action")
    action = st.radio("Acțiune profil master", ["Folosește un profil salvat", "Importă și revizuiește un CV"],
                      index=0 if profiles else 1, key="master_action")
    if action == "Folosește un profil salvat":
        if not profiles:
            st.info("Nu există profil master salvat. Alege importul pentru a pregăti unul.")
            return None
        versions = [p["version"] for p in profiles]
        if "master_next_version" in st.session_state:
            st.session_state["master_saved_version"] = st.session_state.pop("master_next_version")
        labels = {p["version"]: f"{len(p['facts'])} fapte · {p['provenance']['approved_at'][:19]} · {p['version'][7:15]}" for p in profiles}
        version = st.selectbox("Versiunea profilului master", versions, format_func=labels.get, key="master_saved_version")
        profile = store.load(version)
        st.success("Profil master revizuit, încărcat din stocarea locală.")
        with st.expander("Fapte și citate din CV-ul master"):
            for fact, citation in zip(profile["facts"], profile["provenance"]["citations"]):
                st.caption(f"{fact['id']} · {citation['label']}")
                st.text(fact["text"])
            raw, document = store.source(version)
            st.caption("Originalul și textul integral păstrează și experiența QA/rolurile care nu au fost selectate ca fapte pentru matching.")
            st.text(document["text"])
            st.download_button("Descarcă CV-ul original păstrat local", raw, file_name=document["filename"], key="master_download_original")
        return profile

    st.info("Import local, fără model AI. Verifică textul integral înainte să confirmi faptele. Nu marca drept lipsă o competență doar pentru că nu apare în CV.")
    method = st.radio("Sursa CV-ului", ["Fișier TXT / DOCX / PDF", "Text lipit manual"], key="master_import_method")
    raw, filename = None, None
    if method == "Fișier TXT / DOCX / PDF":
        uploaded = st.file_uploader("Încarcă CV-ul master", type=["txt", "docx", "pdf"], max_upload_size=10, key="master_upload")
        if uploaded is not None:
            raw, filename = uploaded.getvalue(), uploaded.name
    else:
        pasted = st.text_area("Textul integral al CV-ului", key="master_pasted", height=250)
        if pasted.strip():
            raw, filename = pasted.encode("utf-8"), "cv-master-pasted.txt"
    input_id = None if raw is None else sha256(raw + filename.encode()).hexdigest()
    if input_id != st.session_state.get("master_import_id"):
        st.session_state["master_document"] = None
        st.session_state["master_import_id"] = input_id
    if st.button("Extrage textul CV-ului", key="master_extract", disabled=raw is None):
        try:
            st.session_state["master_document"] = import_cv(raw, filename)
        except ValueError as error:
            st.error(str(error))
    document = st.session_state.get("master_document")
    if document is None:
        return None
    for warning in document.warnings:
        st.warning(warning)
    with st.expander("Textul integral extras — verifică toate secțiunile", expanded=True):
        st.text(document.text)
    st.caption("Selectează blocuri complete și fidele sursei. Fără reformulări sau competențe inventate; originalul integral rămâne păstrat.")
    selected = st.multiselect("Blocuri verificate pentru profil", list(range(len(document.blocks))),
                              format_func=lambda index: f"{index + 1}. {document.blocks[index].text[:90]}",
                              key=f"master_blocks_{input_id}")
    selections = []
    for index in selected:
        st.text(document.blocks[index].text)
        kind = st.selectbox("Tipul informației din sursă", ["experience", "confirmed_gap"],
                            format_func=lambda value: "Experiență / informație declarată" if value == "experience" else "Lipsă declarată explicit în sursă",
                            key=f"master_kind_{input_id}_{index}")
        selections.append({"block_index": index, "kind": kind})
    if not selections:
        return None
    try:
        draft = prepare_master(document, selections)
    except ValueError as error:
        st.error(str(error))
        return None
    if draft.fingerprint != st.session_state.get("master_last_fingerprint"):
        st.session_state["master_revision"] = st.session_state.get("master_revision", 0) + 1
        st.session_state["master_last_fingerprint"] = draft.fingerprint
    reviewer = st.text_input("Reviewer profil master", key="master_reviewer")
    note = st.text_area("Nota revizuirii profilului", key="master_note")
    confirmed = st.checkbox("Am verificat extracția integrală și faptele selectate față de CV.",
                            key=f"master_confirmation_{st.session_state['master_revision']}_{draft.fingerprint}")
    if st.button("Confirmă și salvează profilul master", key="master_save",
                 disabled=not confirmed or not reviewer.strip() or not note.strip()):
        try:
            profile = approve_master(draft, expected_fingerprint=draft.fingerprint, reviewer=reviewer, note=note, confirmed=confirmed)
            store.save(document, raw, profile)
        except ValueError as error:
            st.error(str(error))
            return None
        st.session_state["master_next_action"] = "Folosește un profil salvat"
        st.session_state["master_next_version"] = profile["version"]
        st.rerun()
    return None
