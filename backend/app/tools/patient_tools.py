"""
patient_tools.py

Tool charge de gerer la collecte des reponses du patient.
Le cahier des charges (section 4.3) exige que les questions soient
gerees via un tool, et que les reponses soient integrees a l'etat
du graphe.

Conformement a la section 2 (cadre pedagogique et ethique), ce projet
est un exercice academique. Le systeme ne fournit pas de diagnostic
definitif et ne doit jamais etre presente comme un dispositif medical.
"""

from langchain_core.tools import tool


# Liste fixe des 5 questions posees successivement au patient par
# le DiagnosticAgent (section 4.3 du cahier des charges).
PATIENT_QUESTIONS = [
    "Quel est le symptome principal qui vous amene a consulter aujourd'hui ?",
    "Depuis combien de temps ressentez-vous ce symptome ?",
    "Avez-vous de la fievre, et si oui, depuis combien de temps ?",
    "Ressentez-vous des difficultes respiratoires ou des douleurs associees ?",
    "Avez-vous des antecedents medicaux ou prenez-vous un traitement en cours ?",
]


@tool
def ask_patient(question_index: int) -> str:
    """
    Retourne la question patient correspondant a l'index donne
    (boucle des 5 questions successives gerees par le DiagnosticAgent).

    Args:
        question_index: index de la question a poser (0 a 4).

    Returns:
        Le texte de la question correspondante, ou un message
        indiquant que toutes les questions ont ete posees.
    """
    if 0 <= question_index < len(PATIENT_QUESTIONS):
        return PATIENT_QUESTIONS[question_index]
    return "Toutes les questions ont deja ete posees au patient."


def get_question(index: int) -> str:
    """
    Fonction utilitaire (non-tool) utilisee directement par le
    DiagnosticAgent pour recuperer la question a l'index donne.
    """
    if 0 <= index < len(PATIENT_QUESTIONS):
        return PATIENT_QUESTIONS[index]
    return ""


def total_questions() -> int:
    """Retourne le nombre total de questions du protocole patient."""
    return len(PATIENT_QUESTIONS)
