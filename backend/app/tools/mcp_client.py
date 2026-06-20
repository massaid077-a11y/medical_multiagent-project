"""
mcp_client.py

Client MCP (Model Context Protocol) charge de se connecter au
serveur MCP (mcp_server/server.py) et d'appeler l'outil
"lookup_care_guideline" qu'il expose.

Conformement a la section 9 du cahier des charges, l'integration
d'au moins un outil via MCP est obligatoire. Ce client est utilise
par le DiagnosticAgent (nodes/diagnostic_agent.py) pour enrichir la
recommandation intermediaire avec un conseil issu du referentiel
MCP, en complement du tool LangChain recommend_interim_care.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Chemin absolu vers le serveur MCP (mcp_server/server.py)
_MCP_SERVER_PATH = (
    Path(__file__).resolve().parents[3] / "mcp_server" / "server.py"
)


async def _call_lookup_care_guideline_async(symptom_text: str) -> str:
    """
    Ouvre une connexion stdio vers le serveur MCP, initialise la
    session, puis appelle l'outil "lookup_care_guideline" avec le
    texte de symptome fourni.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(_MCP_SERVER_PATH)],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                "lookup_care_guideline",
                arguments={"symptom_text": symptom_text},
            )
            # Le contenu retourne par le serveur MCP est une liste de
            # blocs ; on concatene les blocs de type texte.
            text_parts = [
                block.text
                for block in result.content
                if hasattr(block, "text")
            ]
            return " ".join(text_parts) if text_parts else ""


def call_mcp_care_guideline(symptom_text: str) -> str:
    """
    Wrapper synchrone utilise par le reste du backend (LangGraph
    fonctionne ici en mode synchrone) pour appeler l'outil MCP
    "lookup_care_guideline" expose par mcp_server/server.py.

    Args:
        symptom_text: texte libre decrivant les symptomes rapportes
            par le patient.

    Returns:
        Le conseil de soin general retourne par le serveur MCP,
        ou une chaine vide en cas d'echec de connexion (le workflow
        continue alors avec la recommandation locale uniquement).
    """
    try:
        return asyncio.run(_call_lookup_care_guideline_async(symptom_text))
    except Exception as exc:  # pragma: no cover - degradation gracieuse
        print(f"[mcp_client] Avertissement : appel MCP indisponible ({exc})")
        return ""
