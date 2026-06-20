"""
server.py

Serveur MCP (Model Context Protocol) exposant un outil de
consultation d'un referentiel de recommandations de soins generales.

Conformement a la section 9 du cahier des charges, l'integration
d'au moins un outil via MCP est obligatoire. Ce serveur expose
l'outil "lookup_care_guideline", utilise par le mcp_client.py du
backend pour enrichir la recommandation intermediaire produite par
le DiagnosticAgent.

Lancement (mode autonome, transport stdio) :
    python server.py
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------
# Chargement du referentiel de recommandations (data/care_guidelines.json)
# ---------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "data" / "care_guidelines.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    _GUIDELINES = json.load(f)["care_guidelines"]


# ---------------------------------------------------------------
# Serveur MCP
# ---------------------------------------------------------------
mcp = FastMCP("medical-care-guidelines")


@mcp.tool()
def lookup_care_guideline(symptom_text: str) -> str:
    """
    Recherche dans le referentiel de recommandations de soins
    generales le conseil correspondant au symptome decrit.

    Args:
        symptom_text: texte libre decrivant le(s) symptome(s)
            rapporte(s) par le patient (ex : "fievre depuis 2 jours").

    Returns:
        Le conseil de soin general correspondant, issu du
        referentiel data/care_guidelines.json. Cette recommandation
        reste generale et ne remplace pas l'avis du medecin traitant.
    """
    text = symptom_text.lower()

    for entry in _GUIDELINES:
        if entry["keyword"] != "defaut" and entry["keyword"] in text:
            return entry["advice"]

    # Aucune correspondance specifique : conseil par defaut
    default_entry = next(
        (e for e in _GUIDELINES if e["keyword"] == "defaut"), None
    )
    if default_entry:
        return default_entry["advice"]
    return "Repos et surveillance generale recommandes."


if __name__ == "__main__":
    # Lance le serveur MCP en mode stdio (utilisable par un client MCP
    # ou par LangGraph Studio / mcp_client.py du backend).
    mcp.run(transport="stdio")
