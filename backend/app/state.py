"""
state.py

Definition de l'etat partage du graphe LangGraph pour le workflow
de diagnostic medical multi-agents.

Cette structure correspond exactement a celle exigee dans le
cahier des charges (section 8 - Etat partage du graphe).
"""

from typing import Annotated
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    """
    Etat partage entre tous les agents du workflow de diagnostic
    medical (Supervisor, DiagnosticAgent, PhysicianReview, ReportAgent).
    """

    # Historique des messages de la conversation (questions/reponses)
    messages: Annotated[list, add_messages]

    # Prochain noeud a executer, decide par le Supervisor
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH",
    ]

    # Nombre de questions deja posees au patient (boucle des 5 questions)
    question_count: int

    # Liste des reponses du patient, dans l'ordre des questions posees
    answers: list

    # Recommandation intermediaire generee par le DiagnosticAgent
    interim_care: str

    # Synthese clinique preliminaire produite par le DiagnosticAgent
    diagnostic_summary: str

    # Traitement / conduite a tenir propose par le medecin traitant
    # (renseigne lors de l'etape Human-in-the-Loop : PhysicianReview)
    physician_treatment: str

    # Rapport final structure genere par le ReportAgent
    final_report: str
