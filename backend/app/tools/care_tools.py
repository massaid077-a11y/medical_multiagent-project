"""
care_tools.py

Tool charge de generer la recommandation intermediaire (section 4.4
du cahier des charges).

Cette recommandation reste volontairement prudente et generale :
elle ne constitue jamais un diagnostic definitif et ne remplace pas
l'avis du medecin traitant, conformement au cadre pedagogique et
ethique du projet (section 2).
"""

from langchain_core.tools import tool


# Mots-cles "red flags" (signes d'alerte) qui orientent la
# recommandation intermediaire vers une consultation rapide.
RED_FLAG_KEYWORDS = [
    "difficulte respiratoire",
    "douleur thoracique",
    "essoufflement",
    "evanouissement",
    "confusion",
    "sang",
]


@tool
def recommend_interim_care(answers_summary: str) -> str:
    """
    Genere une recommandation intermediaire prudente a partir d'un
    resume des reponses du patient.

    La recommandation peut inclure : repos, hydratation, surveillance,
    consultation rapide en cas d'aggravation (section 4.4 du cahier
    des charges). Elle ne remplace jamais l'avis du medecin traitant.

    Args:
        answers_summary: resume textuel des reponses du patient.

    Returns:
        Une recommandation intermediaire generale et prudente.
    """
    text = answers_summary.lower()
    has_red_flag = any(keyword in text for keyword in RED_FLAG_KEYWORDS)

    if has_red_flag:
        return (
            "Recommandation intermediaire (prudence renforcee) : "
            "compte tenu des elements rapportes, une consultation medicale "
            "rapide est conseillee. En attendant, privilegier le repos, "
            "une bonne hydratation et une surveillance etroite de "
            "l'evolution des symptomes. Cette recommandation reste "
            "generale et ne remplace pas l'avis du medecin traitant."
        )

    return (
        "Recommandation intermediaire : repos, hydratation reguliere et "
        "surveillance de l'evolution des symptomes sur les prochaines 24 a "
        "48 heures. Consulter rapidement un medecin en cas d'aggravation. "
        "Cette recommandation reste generale et ne remplace pas l'avis du "
        "medecin traitant."
    )
