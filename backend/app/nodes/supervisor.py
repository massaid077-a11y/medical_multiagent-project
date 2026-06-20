"""
supervisor.py

Noeud Supervisor : orchestre le workflow et decide de l'etape
suivante (section 4.1 du cahier des charges).

Le Supervisor est traverse a plusieurs reprises dans le workflow
minimal attendu (section 5) :
    START -> Supervisor -> DiagnosticAgent -> Supervisor
    -> PhysicianReview -> Supervisor -> ReportAgent -> Supervisor -> END

A chaque passage, il lit l'etat courant et decide vers quel agent
metier rediriger le workflow, jusqu'a la decision finale "FINISH".
"""

from app.state import MedicalState


def supervisor_node(state: MedicalState) -> MedicalState:
    """
    Decide de la prochaine etape du workflow en fonction de
    l'avancement actuel de l'etat partage.

    Logique de decision :
        1. Si aucune synthese clinique n'a encore ete produite
           -> rediriger vers diagnostic_agent.
        2. Si la synthese existe mais que le medecin n'a pas encore
           valide de traitement -> rediriger vers physician_review.
        3. Si le traitement medecin existe mais qu'aucun rapport
           final n'a ete genere -> rediriger vers report_agent.
        4. Si le rapport final existe -> terminer le workflow (FINISH).
    """
    if not state.get("diagnostic_summary"):
        next_step = "diagnostic_agent"
    elif not state.get("physician_treatment"):
        next_step = "physician_review"
    elif not state.get("final_report"):
        next_step = "report_agent"
    else:
        next_step = "FINISH"

    return {"next": next_step}


def route_from_supervisor(state: MedicalState) -> str:
    """
    Fonction de routage conditionnel utilisee par le graphe
    (add_conditional_edges) pour lire la decision du Supervisor
    et diriger l'execution vers le noeud correspondant.
    """
    return state.get("next", "FINISH")
