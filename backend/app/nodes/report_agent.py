"""
report_agent.py

Noeud ReportAgent : genere le rapport final structure (section 4.1
du cahier des charges), a partir de la synthese clinique, de la
recommandation intermediaire et du traitement propose par le
medecin traitant.

Conformement a la section 2 (cadre pedagogique et ethique), le
rapport final mentionne explicitement que ce systeme ne remplace
pas une consultation medicale.
"""

from app.state import MedicalState


def report_agent_node(state: MedicalState) -> MedicalState:
    """
    Assemble le rapport final structure a partir des differentes
    informations accumulees dans l'etat du graphe au fil du
    workflow.
    """
    diagnostic_summary = state.get("diagnostic_summary", "Non disponible.")
    interim_care = state.get("interim_care", "Non disponible.")
    physician_treatment = state.get("physician_treatment", "Non disponible.")

    final_report = (
        "=== RAPPORT FINAL - ORIENTATION CLINIQUE PRELIMINAIRE ===\n\n"
        f"1. Synthese clinique preliminaire :\n{diagnostic_summary}\n\n"
        f"2. Recommandation intermediaire :\n{interim_care}\n\n"
        f"3. Traitement / conduite a tenir propose par le medecin "
        f"traitant :\n{physician_treatment}\n\n"
        "--------------------------------------------------------\n"
        "Ce système ne remplace pas une consultation médicale.\n"
        "--------------------------------------------------------"
    )

    return {"final_report": final_report}
