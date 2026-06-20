# Diagnostic Médical — Système multi-agents (LangGraph)

Projet académique de simulation d'un workflow d'orientation clinique
multi-agents, réalisé avec LangGraph, LangChain, FastAPI, MCP et
Streamlit.

> **Avertissement** : ce système est un exercice académique. Il ne
> constitue pas un dispositif médical et ne fournit pas de
> diagnostic définitif. Toute synthèse ou recommandation produite
> reste une orientation clinique préliminaire qui ne remplace pas
> une consultation médicale.

---

## 1. Structure du projet

```
project/
├── backend/
│   ├── app/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── api.py
│   │   ├── nodes/
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   └── tools/
│   │       ├── patient_tools.py
│   │       ├── care_tools.py
│   │       └── mcp_client.py
│   ├── langgraph.json
│   ├── requirements.txt
│   └── .env
├── mcp_server/
│   ├── server.py
│   └── data/
│       └── care_guidelines.json
├── frontend/
│   └── app.py
└── README.md
```

---

## 2. Prérequis

- Python 3.11 ou supérieur
- pip

---

## 3. Installation

### 3.1 Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
```

Activation :

- Windows : `venv\Scripts\activate`
- macOS / Linux : `source venv/bin/activate`

### 3.2 Installer les dépendances du backend

```bash
cd backend
pip install -r requirements.txt
```

### 3.3 Installer les dépendances du frontend

Streamlit et requests sont déjà inclus dans `backend/requirements.txt`
(installation unique pour tout le projet).

---

## 4. Lancement du projet

Le projet nécessite **deux process actifs en parallèle** : l'API
FastAPI (backend) et l'interface Streamlit (frontend). Le serveur
MCP est lancé automatiquement par le backend à chaque appel (il n'a
pas besoin d'être démarré manuellement).

### 4.1 Démarrer l'API FastAPI

Dans un premier terminal, depuis le dossier `backend/` :

```bash
cd backend
uvicorn app.api:app --reload --port 8000
```

L'API est alors disponible sur `http://localhost:8000`.
La documentation interactive (Swagger) est disponible sur
`http://localhost:8000/docs`.

### 4.2 Démarrer le frontend Streamlit

Dans un second terminal, depuis le dossier `frontend/` :

```bash
cd frontend
streamlit run app.py
```

L'interface s'ouvre automatiquement dans le navigateur
(`http://localhost:8501`).

---

## 5. Test du graphe dans LangGraph Studio

Depuis le dossier `backend/`, avec l'environnement virtuel activé :

```bash
pip install langgraph-cli[inmem]
langgraph dev
```

LangGraph Studio s'ouvre alors dans le navigateur et permet de :

- visualiser le graphe (`Supervisor → DiagnosticAgent →
  PhysicianReview → ReportAgent`) ;
- exécuter le workflow pas à pas ;
- observer les interruptions Human-in-the-Loop (questions patient
  et revue médecin) ;
- inspecter l'état partagé (`MedicalState`) à chaque étape.

---

## 6. Utilisation de l'application

1. **Écran 1** : cliquer sur *Démarrer la consultation*.
2. **Écran 2** : répondre successivement aux 5 questions posées par
   le Diagnostic Agent.
3. **Écran 3** : consulter la synthèse clinique préliminaire et la
   recommandation intermédiaire, puis saisir le traitement ou la
   conduite à tenir proposée par le médecin traitant.
4. **Écran 4** : consulter le rapport final structuré.

---

## 7. Tester l'API directement (sans frontend)

```bash
curl -X POST http://localhost:8000/sessions/start

curl -X POST "http://localhost:8000/consultation/start?thread_id=<ID>"

curl -X POST http://localhost:8000/consultation/resume \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "<ID>", "value": "Réponse du patient"}'

curl http://localhost:8000/consultation/<ID>

curl http://localhost:8000/consultation/<ID>/report
```

---

## 8. Intégration MCP

Le serveur MCP (`mcp_server/server.py`) expose l'outil
`lookup_care_guideline`, qui consulte un référentiel local
(`mcp_server/data/care_guidelines.json`) pour enrichir la
recommandation intermédiaire produite par le Diagnostic Agent. Le
backend s'y connecte via `backend/app/tools/mcp_client.py`, en
lançant le serveur MCP comme sous-processus communiquant par
transport stdio (le serveur n'a donc pas besoin d'être démarré
séparément).

---

## 9. Jeux de tests suggérés

| Cas | Description | Élément attendu |
|---|---|---|
| Cas 1 | Syndrome respiratoire simple (toux, fièvre légère) | Recommandation prudence renforcée |
| Cas 2 | Cas avec red flags (difficulté respiratoire, douleur thoracique) | Recommandation consultation rapide |
| Cas 3 | Cas bénin (fatigue légère, pas de fièvre) | Recommandation repos/surveillance |

Pour chaque scénario, vérifier : les 5 questions posées, la
génération de la recommandation intermédiaire, la revue médecin, et
la production du rapport final.
