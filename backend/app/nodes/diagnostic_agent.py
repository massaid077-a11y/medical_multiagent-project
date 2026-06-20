"""
diagnostic_agent.py

Noeud DiagnosticAgent (section 4.1 et 4.3 du cahier des charges) :
    - pose 5 questions successives au patient (via le tool ask_patient) ;
    - integre les reponses du patient dans l'etat du graphe ;
    - realise une pre-analyse et produit une synthese clinique
      preliminaire ;
    - genere une recommandation intermediaire (tool
      recommend_interim_care), enrichie par un appel MCP
      (mcp_client.lookup_care_guideline).

Les questions sont posees une par une grace au mecanisme
Human-in-the-Loop de LangGraph (interrupt / Command), qui met le
graphe en pause apres chaque question jusqu'a ce que le patient
reponde (section 4.2 / 4.3 du cahier des charges).
"""

from langgraph.types import interrupt

from app.state import MedicalState
from app.tools.patient_tools import get_question, total_questions
from app.tools.care_tools import recommend_interim_care
from app.tools.mcp_client import call_mcp_care_guideline


def diagnostic_agent_node(state: MedicalState) -> MedicalState:
    """
    Pose les 5 questions du protocole patient une par une (boucle
    Human-in-the-Loop), puis produit la synthese clinique
    preliminaire et la recommandation intermediaire une fois toutes
    les reponses recueillies.
    """
    answers = list(state.get("answers", []))
    question_count = state.get("question_count", 0)
    total = total_questions()

    # --- Boucle des 5 questions (Human-in-the-Loop patient) ---
    while question_count < total:
        question_text = get_question(question_count)
        # Met le graphe en pause : la question est exposee au client
        # (frontend) via l'interruption, qui devra reprendre avec
        # Command(resume=<reponse patient>).
        answer = interrupt(
            {
                "type": "patient_question",
                "question_index": question_count,
                "question": question_text,
            }
        )
        answers.append(answer)
        question_count += 1

    # --- Pre-analyse et synthese clinique preliminaire ---
    answers_summary = " | ".join(
        f"Q{i + 1}: {get_question(i)} -> R: {a}"
        for i, a in enumerate(answers)
    )

    diagnostic_summary = (
        "Synthese clinique preliminaire (orientation clinique, non "
        "definitive) : a partir des 5 reponses recueillies, le patient "
        f"rapporte les elements suivants -> {answers_summary}. "
        "Cette synthese est une orientation clinique preliminaire et "
        "ne constitue pas un diagnostic definitif."
    )

    # --- Recommandation intermediaire (tool local + enrichissement MCP) ---
    local_recommendation = recommend_interim_care.invoke(
        {"answers_summary": answers_summary}
    )
    mcp_recommendation = call_mcp_care_guideline(answers_summary)

    if mcp_recommendation:
        interim_care = (
            f"{local_recommendation} "
            f"(Reference complementaire via MCP : {mcp_recommendation})"
        )
    else:
        interim_care = local_recommendation

    return {
        "answers": answers,
        "question_count": question_count,
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care,
    }
