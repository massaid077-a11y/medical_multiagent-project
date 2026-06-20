"""
app.py (frontend)

Interface Streamlit du systeme de diagnostic medical multi-agents
(section 11 du cahier des charges).

Ecrans minimums (section 11.1) :
    Ecran 1 : saisie du cas initial patient.
    Ecran 2 : questions/reponses patient.
    Ecran 3 : revue medecin avec traitement ou conduite a tenir.
    Ecran 4 : rapport final.

Rappel (cadre pedagogique et ethique, section 2) : ce systeme est
un exercice academique. Il ne constitue pas un dispositif medical
et ne fournit pas de diagnostic definitif.
"""

import datetime
import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Dossier Clinique — Orientation Préliminaire",
    page_icon="⚕",
    layout="centered",
)

# =================================================================
# STYLE — identite visuelle "dossier clinique papier"
# =================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root {
    --paper: #f7f5f0;
    --paper-line: #d8d2c4;
    --ink: #1c2b2e;
    --clinical: #0e6e5e;
    --clinical-deep: #0a4f43;
    --alert: #a8431f;
    --muted: #6b6458;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        repeating-linear-gradient(
            180deg,
            transparent,
            transparent 35px,
            var(--paper-line) 35px,
            var(--paper-line) 36px
        ),
        var(--paper);
    color: var(--ink);
}

/* ---------- EN-TETE "DOSSIER" ---------- */
.chart-header {
    border-bottom: 3px double var(--ink);
    padding-bottom: 14px;
    margin-bottom: 28px;
}
.chart-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--clinical);
    margin-bottom: 4px;
}
.chart-title {
    font-family: 'Source Serif 4', serif;
    font-weight: 700;
    font-size: 34px;
    color: var(--ink);
    line-height: 1.1;
    margin: 0 0 6px 0;
}
.chart-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--muted);
}

/* ---------- BANDEAU AVERTISSEMENT ---------- */
.disclaimer-band {
    background: var(--ink);
    color: var(--paper);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 0.03em;
    padding: 9px 16px;
    margin-bottom: 26px;
    border-left: 4px solid var(--clinical);
}

/* ---------- TAMPON ID CONSULTATION ---------- */
.stamp {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--clinical-deep);
    border: 1.5px solid var(--clinical-deep);
    border-radius: 3px;
    padding: 4px 10px;
    transform: rotate(-1deg);
    letter-spacing: 0.04em;
    margin-bottom: 18px;
}

/* ---------- SECTION LABEL ---------- */
.field-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--clinical-deep);
    border-bottom: 1px solid var(--paper-line);
    padding-bottom: 6px;
    margin: 22px 0 12px 0;
}

/* ---------- CARTE CLINIQUE ---------- */
.clinical-card {
    background: #ffffff;
    border: 1px solid var(--paper-line);
    border-left: 3px solid var(--clinical);
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 2px 2px 0 rgba(28,43,46,0.04);
}
.clinical-card-alert {
    border-left: 3px solid var(--alert);
}
.clinical-card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 8px;
}
.clinical-card-body {
    font-family: 'Source Serif 4', serif;
    font-size: 15.5px;
    line-height: 1.55;
    color: var(--ink);
}

/* ---------- PROGRESSION QUESTIONS ---------- */
.progress-track {
    display: flex;
    gap: 8px;
    margin-bottom: 4px;
}
.progress-dot {
    width: 100%;
    height: 5px;
    background: var(--paper-line);
    border-radius: 1px;
}
.progress-dot.filled { background: var(--clinical); }

/* ---------- BOUTONS ---------- */
.stButton > button {
    background: var(--clinical-deep);
    color: var(--paper);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: none;
    border-radius: 2px;
    padding: 11px 22px;
    width: 100%;
    transition: 0.15s ease;
}
.stButton > button:hover {
    background: var(--clinical);
}

/* ---------- INPUTS ---------- */
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid var(--paper-line) !important;
    border-radius: 2px !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 15px !important;
    color: var(--ink) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--clinical) !important;
    box-shadow: 0 0 0 1px var(--clinical) !important;
}

/* ---------- RAPPORT FINAL ---------- */
.report-sheet {
    background: #ffffff;
    border: 1px solid var(--paper-line);
    padding: 28px 26px;
    font-family: 'Source Serif 4', serif;
    font-size: 15px;
    line-height: 1.7;
    color: var(--ink);
    position: relative;
}
.report-sheet::before {
    content: "ORIENTATION PRÉLIMINAIRE";
    position: absolute;
    top: 16px;
    right: 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    color: var(--clinical);
    border: 1px solid var(--clinical);
    padding: 3px 8px;
    transform: rotate(3deg);
}
.report-section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--clinical-deep);
    margin: 18px 0 6px 0;
}
.report-section-title:first-child { margin-top: 0; }
.report-footer-note {
    margin-top: 22px;
    padding-top: 14px;
    border-top: 1px dashed var(--paper-line);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--alert);
    letter-spacing: 0.02em;
}

/* ---------- DIVERS ---------- */
hr { border-color: var(--paper-line) !important; }
[data-testid="stCaptionContainer"] { font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# =================================================================
# EN-TETE
# =================================================================
today = datetime.date.today().strftime("%d/%m/%Y")
st.markdown(f"""
<div class="chart-header">
    <div class="chart-eyebrow">Système d'orientation clinique · Simulation académique</div>
    <div class="chart-title">⚕ Dossier de consultation</div>
    <div class="chart-subtitle">Workflow multi-agents · {today}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-band">
⚠ EXERCICE ACADÉMIQUE — Ce système n'est pas un dispositif médical et ne fournit aucun diagnostic définitif.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Etat de session Streamlit
# ---------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "consultation_state" not in st.session_state:
    st.session_state.consultation_state = None
if "started" not in st.session_state:
    st.session_state.started = False


def call_api(method: str, path: str, **kwargs):
    """Appelle l'API FastAPI et gere les erreurs reseau de maniere simple."""
    url = f"{API_BASE_URL}{path}"
    try:
        if method == "POST":
            response = requests.post(url, timeout=30, **kwargs)
        else:
            response = requests.get(url, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        st.error(f"Connexion au serveur impossible : {exc}")
        return None


# =================================================================
# ECRAN 1 : Saisie du cas initial patient
# =================================================================
if not st.session_state.started:
    st.markdown('<div class="field-label">Étape 01 — Ouverture du dossier</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="clinical-card">
        <div class="clinical-card-title">Protocole</div>
        <div class="clinical-card-body">
            L'agent de diagnostic recueillera <strong>5 réponses</strong> auprès du patient,
            produira une synthèse clinique préliminaire, puis transmettra le dossier
            au médecin traitant pour validation avant l'émission du rapport final.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Ouvrir une nouvelle consultation", type="primary"):
        session_data = call_api("POST", "/sessions/start")
        if session_data:
            thread_id = session_data["thread_id"]
            state = call_api("POST", f"/consultation/start?thread_id={thread_id}")
            if state:
                st.session_state.thread_id = thread_id
                st.session_state.consultation_state = state
                st.session_state.started = True
                st.rerun()

# =================================================================
# ECRANS 2, 3, 4 : workflow en cours
# =================================================================
else:
    state = st.session_state.consultation_state
    interrupt = state.get("interrupt") if state else None
    short_id = st.session_state.thread_id[:8]

    st.markdown(f'<div class="stamp">DOSSIER N° {short_id}</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ECRAN 2 : Questions / reponses patient
    # -------------------------------------------------------------
    if interrupt and interrupt.get("type") == "patient_question":
        q_index = interrupt.get("question_index", 0)
        q_text = interrupt.get("question", "")

        st.markdown('<div class="field-label">Étape 02 — Entretien patient</div>', unsafe_allow_html=True)

        dots = "".join(
            f'<div class="progress-dot{" filled" if i <= q_index else ""}"></div>'
            for i in range(5)
        )
        st.markdown(f'<div class="progress-track">{dots}</div>', unsafe_allow_html=True)
        st.caption(f"Question {q_index + 1} sur 5")

        st.markdown(f"""
        <div class="clinical-card">
            <div class="clinical-card-title">Question posée par l'agent de diagnostic</div>
            <div class="clinical-card-body">{q_text}</div>
        </div>
        """, unsafe_allow_html=True)

        answer = st.text_input(
            "Réponse du patient", key=f"answer_{q_index}",
            label_visibility="collapsed", placeholder="Saisir la réponse du patient…"
        )

        if st.button("Enregistrer la réponse", type="primary"):
            if answer.strip():
                new_state = call_api(
                    "POST", "/consultation/resume",
                    json={"thread_id": st.session_state.thread_id, "value": answer},
                )
                if new_state:
                    st.session_state.consultation_state = new_state
                    st.rerun()
            else:
                st.warning("Veuillez saisir une réponse avant de continuer.")

    # -------------------------------------------------------------
    # ECRAN 3 : Revue medecin (Human-in-the-Loop)
    # -------------------------------------------------------------
    elif interrupt and interrupt.get("type") == "physician_review":
        st.markdown('<div class="field-label">Étape 03 — Revue du médecin traitant</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="clinical-card">
            <div class="clinical-card-title">Synthèse clinique préliminaire</div>
            <div class="clinical-card-body">{interrupt.get("diagnostic_summary", "")}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="clinical-card clinical-card-alert">
            <div class="clinical-card-title">Recommandation intermédiaire</div>
            <div class="clinical-card-body">{interrupt.get("interim_care", "")}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="field-label">Traitement ou conduite à tenir</div>', unsafe_allow_html=True)
        treatment = st.text_area(
            "Traitement", height=120, label_visibility="collapsed",
            placeholder="Saisir la prescription, le traitement ou la conduite à tenir…"
        )

        if st.button("Valider la revue médicale", type="primary"):
            if treatment.strip():
                new_state = call_api(
                    "POST", "/consultation/resume",
                    json={"thread_id": st.session_state.thread_id, "value": treatment},
                )
                if new_state:
                    st.session_state.consultation_state = new_state
                    st.rerun()
            else:
                st.warning("Veuillez saisir un traitement avant de valider.")

    # -------------------------------------------------------------
    # ECRAN 4 : Rapport final
    # -------------------------------------------------------------
    elif state and state.get("is_finished"):
        st.markdown('<div class="field-label">Étape 04 — Rapport final</div>', unsafe_allow_html=True)

        report_data = call_api("GET", f"/consultation/{st.session_state.thread_id}/report")
        if report_data:
            report_text = report_data["final_report"]

            parts = report_text.split("\n\n")
            body_html = ""
            for part in parts:
                if part.startswith("==="):
                    continue
                if part.startswith("---"):
                    continue
                if part.strip() == "Ce système ne remplace pas une consultation médicale.":
                    continue
                if ":\n" in part:
                    title, content = part.split(":\n", 1)
                    body_html += f'<div class="report-section-title">{title.strip()}</div><div>{content.strip()}</div>'
                else:
                    body_html += f"<div>{part}</div>"

            st.markdown(f"""
            <div class="report-sheet">
                {body_html}
                <div class="report-footer-note">
                    ⚠ Ce système ne remplace pas une consultation médicale.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ouvrir un nouveau dossier"):
            st.session_state.thread_id = None
            st.session_state.consultation_state = None
            st.session_state.started = False
            st.rerun()

    else:
        st.warning("État de consultation inattendu. Veuillez réinitialiser le dossier.")
        if st.button("Réinitialiser"):
            st.session_state.thread_id = None
            st.session_state.consultation_state = None
            st.session_state.started = False
            st.rerun()