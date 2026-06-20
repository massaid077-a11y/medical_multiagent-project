"""
physician_review.py

Noeud PhysicianReview : etape Human-in-the-Loop representant le
medecin traitant (section 4.1 et 4.2 du cahier des charges).

Le medecin recoit la synthese clinique et la recommandation
intermediaire produites par le DiagnosticAgent, puis propose un
traitement ou une conduite a tenir avant que le ReportAgent ne
genere le rapport final.
"""

from langgraph.types import interrupt

from app.state import MedicalState


def physician_review_node(state: MedicalState) -> MedicalState:
    """
    Met le graphe en pause pour permettre au medecin traitant de
    consulter la synthese clinique et la recommandation
    intermediaire, puis de proposer un traitement ou une conduite a
    tenir.

    Le workflow reprend lorsque le client (frontend) envoie
    Command(resume=<traitement propose par le medecin>).
    """
    physician_treatment = state.get("physician_treatment")

    if not physician_treatment:
        physician_treatment = interrupt(
            {
                "type": "physician_review",
                "diagnostic_summary": state.get("diagnostic_summary", ""),
                "interim_care": state.get("interim_care", ""),
                "message": (
                    "Revue medecin requise : veuillez consulter la "
                    "synthese clinique et la recommandation intermediaire, "
                    "puis proposer un traitement ou une conduite a tenir."
                ),
            }
        )

    return {"physician_treatment": physician_treatment}
