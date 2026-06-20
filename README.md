
# Rapport technique — Simulation d'orientation clinique multi‑agents

**Titre du projet** : Simulation d'orientation clinique multi‑agents

**Auteur** : Assaid Mohammed

**Professeur encadrant** : Mohamed Youssfi

**Niveau** : 4ème année Génie Informatique / IA

**Année universitaire** : 2025-2026

**Institution** : École supérieure de l'ingénierie informatique

---

Résumé (Abstract)
------------------
Ce document décrit la conception, l'implémentation et l'utilisation
d'un prototype académique de système d'orientation clinique basé
sur un workflow multi‑agents. Le système combine LangGraph pour la
coordination des agents, FastAPI pour l'API backend, un serveur MCP
pour l'accès à des recommandations de soins, et Streamlit pour le
frontend interactif. L'objectif est pédagogique : illustrer les
patrons d'architecture, les interruptions Human‑in‑the‑Loop et les
intégrations MCP/LLM, sans vocation clinique.

Mots‑clés: LangGraph, multi‑agents, FastAPI, MCP, Streamlit,
workflow clinique, simulation.

1. Contexte et objectifs
-------------------------
Le projet reproduit le scénario d'une consultation structurée en
quatre étapes : collecte initiale, questions patient (5 questions
séquentielles), revue médecin (human‑in‑the‑loop) et production du
rapport final. Le but pédagogique est de montrer comment orchestrer
plusieurs agents (DiagnosticAgent, PhysicianReview, ReportAgent)
avec interruptions, persistance d'état et enrichissement par un
référentiel de bonnes pratiques (MCP).

2. Méthodologie et architecture logicielle
-----------------------------------------
2.1 Vue d'ensemble

- `backend/` : implémente le graphe LangGraph et l'API FastAPI
  (`app/api.py`). Le graphe est défini via `langgraph.json` et les
  nœuds sont implémentés dans `backend/app/nodes/`.
- `mcp_server/` : serveur MCP autonome exposant l'outil
  `lookup_care_guideline` qui consulte `mcp_server/data/care_guidelines.json`.
- `frontend/` : interface Streamlit (`app.py`) permettant d'ouvrir
  une consultation, répondre aux questions, saisir la revue médecin
  et afficher le rapport final.

2.2 Composants clés

- `DiagnosticAgent` : pose successivement 5 questions au patient
  (interruption `patient_question`) puis produit une synthèse.
- `PhysicianReview` : présente la synthèse au médecin; attente
  d'une saisie humaine (interruption `physician_review`).
- `ReportAgent` : compile le rapport final structuré et le rend
  disponible via l'API.
- `mcp_client.py` / `mcp_server` : communication via MCP pour
  enrichir les recommandations intermédiaires.

3. Installation et exécution (reproductibilité)
----------------------------------------------
Prérequis : Python 3.11+, `pip`.

3.1 Environnement virtuel (recommandé)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3.2 Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

3.3 Lancer les services (développement)

Le prototype demande deux processus : l'API backend et le
frontend Streamlit. Le serveur MCP peut être lancé manuellement
si souhaité.

```bash
# Terminal 1 — API
cd backend
uvicorn app.api:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
streamlit run app.py

# (optionnel) Terminal 3 — serveur MCP
cd mcp_server
python server.py
```

L'API est exposée sur `http://localhost:8000` et le frontend
sur `http://localhost:8501`.

4. Protocoles d'expérimentation et cas tests
-------------------------------------------
Exemples de scénarios à reproduire pour valider le prototype :

- Cas 1 — Syndrome respiratoire léger : vérifier que les 5
  questions sont posées, que la recommandation MCP retourne un
  conseil adapté, et que la revue médecin permet d'ajouter un
  traitement avant génération du rapport final.
- Cas 2 — Signaux d'alerte (red flags) : vérifier que la
  synthèse attire l'attention du médecin et propose une conduite
  d'urgence.
- Cas 3 — Cas bénin : vérification du flux normal et du rapport.

5. Résultats attendus
---------------------
Pour chaque exécution :

- 5 questions patient collectées
- synthèse diagnostique préliminaire
- recommandation intermédiaire enrichie par le MCP
- revue humaine validant/complétant la conduite à tenir
- rapport final structuré disponible via l'API

6. Limitations et considérations éthiques
----------------------------------------
Ce prototype est strictement pédagogique. Il ne doit pas être
utilisé pour des décisions cliniques. Limitations principales :

- absence de validation clinique et d'évaluations de sécurité ;
- dépendance possible à des modèles LLM externes (si configurés) ;
- référentiel MCP simplifié et non exhaustif.

7. Reproductibilité et bonnes pratiques
--------------------------------------
- Versionner les dépendances (`requirements.txt`).
- Ne pas exposer de clés privées dans le dépôt ; utilisez un
  fichier `.env` (non commité) pour `OPENAI_API_KEY` si nécessaire.
- Reproduire les tests décrits dans la section 4 pour valider
  l'intégrité du workflow.

8. Conclusion
-------------
Le système illustre la coordination d'agents dans un contexte
clinique simulé, ainsi que l'intégration d'un référentiel via MCP
et l'interaction human‑in‑the‑loop. Il sert de base pour des
activités pédagogiques et extensions futures (évaluation, tests
utilisateurs, enrichissement du référentiel).

Remerciements
-------------
Merci aux contributeurs et aux enseignants ayant supervisé ce
projet. Ce travail est fourni à titre d'exemple académique.

Références
----------
- LangGraph — documentation et exemples.
- FastAPI — Starlette, ASGI et documentations associées.
- MCP — Model Context Protocol (outil d'extension).

Annexes
-------
Structure minimale du dépôt :

```
backend/
  app/
    api.py
    graph.py
    state.py
    nodes/
    tools/
  langgraph.json
  requirements.txt
frontend/
  app.py
mcp_server/
  server.py
  data/care_guidelines.json
```

Commandes rapides pour tests manuels :

```bash
# Obtenir un thread_id
curl -X POST http://localhost:8000/sessions/start

# Démarrer une consultation
curl -X POST "http://localhost:8000/consultation/start?thread_id=<ID>"

# Reprendre la consultation (réponse patient / revue)
curl -X POST http://localhost:8000/consultation/resume \
  -H "Content-Type: application/json" \
  -d '{"thread_id":"<ID>","value":"Réponse"}'

# Obtenir le rapport final
curl http://localhost:8000/consultation/<ID>/report
```

Licence
-------
Ce dépôt est fourni à des fins académiques. Si vous souhaitez une
licence explicite (MIT, Apache‑2.0, etc.), indiquez votre choix et
une licence sera ajoutée.

---

## 10. Déploiement / Notes production

- **Variables d'environnement** : créez un fichier `.env` dans
  `backend/` si vous souhaitez configurer des clés ou paramètres
  (par exemple pour `OPENAI_API_KEY` si vous utilisez des backends
  LLM externes). Le projet fonctionne en mode local sans clé par
  défaut pour les exercices académiques.
- **Processus requis** : en développement, lancez `uvicorn` pour
  l'API et `streamlit` pour le frontend. Le serveur MCP peut être
  démarré manuellement via :

```bash
cd mcp_server
python server.py
```

  En configuration locale, le backend lance normalement le MCP
  automatiquement lorsqu'il en a besoin.

## 11. Licence

Ce dépôt est fourni à des fins académiques et d'exemple. Vous pouvez
réutiliser le code sous réserve des droits d'auteur applicables. Si
vous souhaitez une licence explicite (MIT, Apache, etc.), indiquez
laquelle et je peux l'ajouter.
