"""
api.py

API FastAPI exposant le graphe LangGraph du workflow de diagnostic
medical (section 10 du cahier des charges).

Routes obligatoires :
    POST /sessions/start
    POST /consultation/start
    POST /consultation/resume
    GET  /consultation/{thread_id}
    GET  /consultation/{thread_id}/report
"""

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.types import Command

from app.graph import graph

app = FastAPI(
    title="Diagnostic Medical (Simulation academique)",
    description=(
        "API de simulation pedagogique d'un workflow d'orientation "
        "clinique multi-agents. Ce systeme est un exercice academique : "
        "il ne constitue pas un dispositif medical et ne fournit pas de "
        "diagnostic definitif."
    ),
    version="1.0.0",
)

# Autorise les appels depuis un frontend local (Streamlit / React / etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Schemas de requete
# ---------------------------------------------------------------
class ResumeRequest(BaseModel):
    thread_id: str
    value: str


# ---------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------
def _serialize_state(thread_id: str) -> dict:
    """
    Construit une representation serialisable de l'etat courant du
    graphe pour un thread_id donne, incluant les informations
    d'interruption en cours (question patient ou revue medecin) si
    le workflow est en pause.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)

    interrupts = []
    for task in snapshot.tasks:
        for interrupt_obj in getattr(task, "interrupts", []) or []:
            interrupts.append(interrupt_obj.value)

    has_pending_interrupt = len(interrupts) > 0
    has_more_work = len(snapshot.next) > 0

    return {
        "thread_id": thread_id,
        "values": snapshot.values,
        "next": list(snapshot.next),
        "interrupt": interrupts[0] if interrupts else None,
        "is_finished": not has_pending_interrupt and not has_more_work,
    }


# ---------------------------------------------------------------
# Routes obligatoires (section 10 du cahier des charges)
# ---------------------------------------------------------------
@app.post("/sessions/start")
def start_session():
    """
    Cree un nouvel identifiant de session (thread_id) utilise pour
    suivre une consultation au travers du graphe LangGraph.
    """
    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id}


@app.post("/consultation/start")
def start_consultation(thread_id: str | None = None):
    """
    Demarre une nouvelle consultation : initialise l'etat du graphe
    et execute le workflow jusqu'a la premiere interruption (la
    premiere question posee au patient par le DiagnosticAgent).
    """
    if not thread_id:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"messages": [], "question_count": 0, "answers": []}

    graph.invoke(initial_state, config)

    return _serialize_state(thread_id)


@app.post("/consultation/resume")
def resume_consultation(request: ResumeRequest):
    """
    Reprend une consultation interrompue (reponse du patient a une
    question, ou traitement propose par le medecin traitant lors de
    la revue Human-in-the-Loop), et execute le workflow jusqu'a la
    prochaine interruption ou jusqu'a la fin (rapport final).
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    snapshot = graph.get_state(config)
    has_pending_interrupt = any(
        getattr(task, "interrupts", None) for task in snapshot.tasks
    )
    if not has_pending_interrupt:
        raise HTTPException(
            status_code=400,
            detail="Cette consultation est déjà terminée.",
        )

    graph.invoke(Command(resume=request.value), config)

    return _serialize_state(request.thread_id)


@app.get("/consultation/{thread_id}")
def get_consultation(thread_id: str):
    """
    Retourne l'etat courant complet d'une consultation (utile pour
    afficher la progression du workflow dans le frontend).
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)

    if snapshot.values == {}:
        raise HTTPException(
            status_code=404,
            detail="Consultation introuvable pour ce thread_id.",
        )

    return _serialize_state(thread_id)


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    """
    Retourne le rapport final structure de la consultation, une
    fois le workflow termine. Mentionne explicitement que ce
    systeme ne remplace pas une consultation medicale.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)

    final_report = snapshot.values.get("final_report")
    if not final_report:
        raise HTTPException(
            status_code=404,
            detail="Le rapport final n'est pas encore disponible pour cette consultation.",
        )

    return {"thread_id": thread_id, "final_report": final_report}
