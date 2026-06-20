"""
graph.py

Assemblage du graphe LangGraph complet du workflow de diagnostic
medical, conformement au workflow minimal attendu (section 5 du
cahier des charges) :

    START
     |
     v
    Supervisor
     |
     v
    DiagnosticAgent
     |
     +--> Tool: ask_patient (boucle jusqu'a 5 questions)
     |
     +--> Tool: recommend_interim_care
     |
     v
    Supervisor
     |
     v
    PhysicianReview (Human-in-the-Loop)
     |
     v
    Supervisor
     |
     v
    ReportAgent
     |
     v
    Supervisor
     |
     v
    END
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node, route_from_supervisor
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def build_graph():
    """
    Construit et compile le graphe LangGraph du workflow de
    diagnostic medical, avec un checkpointer en memoire permettant
    la persistance de l'etat entre les interruptions
    Human-in-the-Loop (patient et medecin).
    """
    builder = StateGraph(MedicalState)

    # --- Declaration des noeuds ---
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    # --- Arete d'entree : START -> Supervisor ---
    builder.add_edge(START, "supervisor")

    # --- Routage conditionnel depuis le Supervisor ---
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        },
    )

    # --- Chaque agent metier retourne vers le Supervisor ---
    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    # --- Compilation avec checkpointer (necessaire pour interrupt/Command) ---
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph


# Instance de graphe utilisee par l'API FastAPI (api.py) et par
# LangGraph Studio (via langgraph.json).
graph = build_graph()
