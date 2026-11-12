"""Local CV import/review UI. No LLM is called and no fact is auto-approved."""

from hashlib import sha256
import streamlit as st

from jobhunter.cv_import import import_cv
from jobhunter.master_profile import MasterProfileStore, prepare_master, approve_master, excerpt_ranges


def fragment_controls(document, input_id):
    """Select full parser blocks or copy exact, arbitrarily sized excerpts."""
    st.subheader("2. Alege fragmentele din CV")
    mode = st.radio("Cum alegi fragmentele?", ["Copy-paste din CV", "Selectează blocuri întregi"],
                    key=f"master_fragment_mode_{input_id}", horizontal=True)
    selections, inputs, invalid = [], [mode], False
    source_column, fragments_column = st.columns(2)
    with source_column:
        st.text_area("Textul CV-ului — selectează și copiază de aici", value=document.text,
                     height=420, disabled=True, key=f"master_source_{input_id}")
        st.caption("Poți copia și din documentul tău, dacă textul este identic cu cel afișat aici. Verifică datele și ordinea secțiunilor.")
    with fragments_column:
        if mode == "Selectează blocuri întregi":
            selected = st.multiselect("Blocuri din CV", list(range(len(document.blocks))),
                                      format_func=lambda index: f"{index + 1}. {document.blocks[index].text[:90]}",
                                      key=f"master_blocks_{input_id}")
            for index in selected:
                st.text(document.blocks[index].text)
                kind = _fragment_kind(f"master_kind_{input_id}_{index}")
                selections.append({"block_index": index, "kind": kind})
            inputs.append(selections)
        else:
            count_key = f"master_fragment_count_{input_id}"
            count = st.session_state.setdefault(count_key, 1)
            st.caption("Un fragment poate fi un rol, o realizare, o competență sau un paragraf. Include contextul relevant, de exemplu rolul și perioada.")
            for index in range(count):
                key = f"master_excerpt_{input_id}_{index}"
                text = st.text_area(f"Fragment {index + 1}", key=key, height=110)
                inputs.append(text)
                if not text.strip():
                    continue
                ranges = excerpt_ranges(document, text)
                if not ranges:
                    st.error(f"Fragmentul {index + 1} nu a fost găsit exact în CV. Copiază-l din textul afișat, fără reformulare.")
                    invalid = True
                    continue
                if len(ranges) > 1:
                    chosen = st.selectbox(f"Fragmentul {index + 1} apare de mai multe ori. Alege contextul corect", list(range(len(ranges))),
                                          format_func=lambda i, occurrences=ranges: f"Apariția {i + 1}: …{document.text[max(0, occurrences[i][0]-55):min(len(document.text), occurrences[i][1]+55)]}…",
                                          key=key + "_occurrence")
                else:
                    chosen = 0
                start, end = ranges[chosen]
                kind = _fragment_kind(key + "_kind")
                selections.append({"start": start, "end": end, "kind": kind})
                inputs.append((start, end, kind))
                st.caption("✓ Fragment găsit în CV. Sursa va fi păstrată.")
            if st.button("Adaugă încă un fragment", key=f"master_add_fragment_{input_id}", disabled=count >= 100):
                st.session_state[count_key] = count + 1
                st.rerun()
            st.caption("Pentru a elimina un fragment, golește caseta lui.")
    # Every edit, including an invalid or temporarily empty excerpt, revokes confirmation.
    signature = sha256(repr(inputs).encode()).hexdigest()
    if signature != st.session_state.get("master_selection_signature"):
        st.session_state["master_revision"] = st.session_state.get("master_revision", 0) + 1
        st.session_state["master_selection_signature"] = signature
    return None if invalid else selections


def _fragment_kind(key):
    with st.expander("Opțiune avansată: lipsă declarată explicit"):
        st.caption("Lasă valoarea implicită pentru experiență, educație sau competențe. Absența unei mențiuni din CV nu dovedește o lipsă.")
        return st.selectbox("Tipul fragmentului", ["experience", "confirmed_gap"],
                            format_func=lambda value: "Informație din CV" if value == "experience" else "Lipsă declarată explicit în sursă", key=key)


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
        labels = {p["version"]: f"{len(p['facts'])} fragmente · {p['provenance']['approved_at'][:19]} · {p['version'][7:15]}" for p in profiles}
        version = st.selectbox("Versiunea profilului master", versions, format_func=labels.get, key="master_saved_version")
        profile = store.load(version)
        st.success(f"{len(profile['facts'])} fragmente din CV sunt pregătite pentru comparația cu jobul.")
        if st.button("Alege alte fragmente din acest CV", key="master_reselect"):
            st.session_state["master_next_action"] = "Importă și revizuiește un CV"
            st.session_state["master_import_method"] = "CV deja salvat"
            st.session_state["master_reuse_version"] = version
            st.rerun()
        with st.expander("Fragmentele alese și CV-ul original"):
            for fact, citation in zip(profile["facts"], profile["provenance"]["citations"]):
                st.caption(f"{fact['id']} · {citation['label']}")
                st.text(fact["text"])
            raw, document = store.source(version)
            st.caption("Originalul și textul integral păstrează și experiența QA/rolurile care nu au fost selectate ca fapte pentru matching.")
            st.text(document["text"])
            st.download_button("Descarcă CV-ul original păstrat local", raw, file_name=document["filename"], key="master_download_original")
        return profile

    st.subheader("1. Încarcă CV-ul")
    st.caption("Citim textul documentului local. Tu alegi ce fragmente vor fi comparate cu jobul.")
    methods = ["Fișier TXT / DOCX / PDF", "Text lipit manual"] + (["CV deja salvat"] if profiles else [])
    method = st.radio("Sursa CV-ului", methods, key="master_import_method")
    raw, filename = None, None
    if method == "Fișier TXT / DOCX / PDF":
        uploaded = st.file_uploader("Încarcă CV-ul master", type=["txt", "docx", "pdf"], max_upload_size=10, key="master_upload")
        if uploaded is not None:
            raw, filename = uploaded.getvalue(), uploaded.name
    elif method == "Text lipit manual":
        pasted = st.text_area("Textul integral al CV-ului", key="master_pasted", height=250)
        if pasted.strip():
            raw, filename = pasted.encode("utf-8"), "cv-master-pasted.txt"
    else:
        version = st.selectbox("CV salvat", [p["version"] for p in profiles], key="master_reuse_version")
        raw, saved_document = store.source(version)
        filename = saved_document["filename"]
    input_id = None if raw is None else sha256(raw + filename.encode()).hexdigest()
    if input_id != st.session_state.get("master_import_id"):
        st.session_state["master_document"] = None
        st.session_state["master_import_id"] = input_id
        if raw is not None:
            try:
                st.session_state["master_document"] = import_cv(raw, filename)
            except ValueError as error:
                st.error(str(error))
    if st.button("Recitește textul CV-ului", key="master_extract", disabled=raw is None):
        try:
            st.session_state["master_document"] = import_cv(raw, filename)
        except ValueError as error:
            st.error(str(error))
    document = st.session_state.get("master_document")
    if document is None:
        return None
    for warning in document.warnings:
        st.warning(warning)
    selections = fragment_controls(document, input_id)
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
    st.success(f"Ai ales {len(draft.profile['facts'])} fragmente pentru comparație.")
    reviewer = st.text_input("Numele tău", key="master_reviewer")
    note = st.text_area("Notă despre selecție", value="Fragmente copiate din CV și verificate înainte de comparație.", key="master_note")
    confirmed = st.checkbox("Am verificat textul citit din CV și fragmentele alese sunt copiate corect.",
                            key=f"master_confirmation_{st.session_state['master_revision']}_{draft.fingerprint}")
    if st.button("Salvează fragmentele și continuă la job", key="master_save",
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
