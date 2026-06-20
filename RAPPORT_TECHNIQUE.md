# Rapport technique — Diagnostic Médical (Système multi-agents LangGraph)

## 1. Objectif du projet

Ce projet académique simule un workflow d'orientation clinique
multi-agents : recueil d'informations patient, production d'une
synthèse clinique préliminaire, validation humaine par un médecin
traitant, puis génération d'un rapport final structuré. Conformément
au cadre pédagogique et éthique fixé, le système ne constitue pas un
dispositif médical et ne fournit aucun diagnostic définitif.

## 2. Architecture générale

Le projet est organisé en trois composants indépendants :

- **backend/** : le graphe LangGraph (logique multi-agents) et l'API
  FastAPI qui l'expose.
- **mcp_server/** : un serveur MCP autonome exposant un outil de
  consultation d'un référentiel de recommandations de soins.
- **frontend/** : une interface Streamlit consommant l'API FastAPI.

Cette séparation permet de tester chaque couche indépendamment (le
graphe peut être exécuté directement en Python, visualisé dans
LangGraph Studio, ou piloté via l'API REST).

## 3. Le graphe LangGraph

### 3.1 État partagé (`state.py`)

L'état du graphe (`MedicalState`) est un `TypedDict` regroupant les
messages, le compteur de questions, les réponses du patient, la
synthèse clinique, la recommandation intermédiaire, le traitement
proposé par le médecin et le rapport final. Cette structure unique,
partagée par tous les nœuds, évite la duplication d'information et
permet la persistance/reprise du workflow via le checkpointer.

### 3.2 Nœuds (`nodes/`)

- **Supervisor** : nœud de routage pur, sans effet de bord. Il
  observe l'état courant et décide du prochain nœud à exécuter
  (`diagnostic_agent`, `physician_review`, `report_agent` ou
  `FINISH`). Cette approche centralise la logique d'orchestration et
  simplifie l'ajout d'agents futurs.
- **DiagnosticAgent** : pose les 5 questions du protocole patient une
  par une, via le mécanisme `interrupt()` de LangGraph. Comme un
  nœud interrompu est ré-exécuté depuis son début lors de la reprise,
  la boucle s'appuie sur `question_count` pour savoir où elle s'est
  arrêtée et éviter de reposer une question déjà répondue. Une fois
  les 5 réponses recueillies, le nœud produit la synthèse clinique et
  appelle le tool `recommend_interim_care`, enrichi par un appel MCP.
- **PhysicianReview** : second point Human-in-the-Loop. Il
  interrompt le graphe pour présenter au médecin la synthèse et la
  recommandation intermédiaire, et attend en retour le traitement ou
  la conduite à tenir.
- **ReportAgent** : assemble les trois informations accumulées
  (synthèse, recommandation, traitement médecin) en un rapport final
  structuré, incluant la mention obligatoire rappelant que le
  système ne remplace pas une consultation médicale.

### 3.3 Human-in-the-Loop

Le choix technique central de ce projet est l'utilisation de la
primitive `interrupt()` / `Command(resume=...)` de LangGraph (plutôt
qu'une gestion manuelle d'état côté API). Cette primitive permet de
suspendre l'exécution du graphe à un point précis, de sérialiser cet
état via un checkpointer (`InMemorySaver`), puis de reprendre
exactement où l'exécution s'était arrêtée dès qu'une valeur de
reprise est fournie. Deux interruptions sont utilisées : l'une dans
le `DiagnosticAgent` (questions patient), l'autre dans
`PhysicianReview` (validation médecin).

## 4. Tools et intégration MCP

Trois outils ont été développés :

- `ask_patient` (`patient_tools.py`) : expose les questions du
  protocole patient.
- `recommend_interim_care` (`care_tools.py`) : génère une
  recommandation intermédiaire prudente, avec une logique simple de
  détection de signaux d'alerte (« red flags ») dans le résumé des
  réponses patient.
- `lookup_care_guideline`, exposé par le **serveur MCP**
  (`mcp_server/server.py`) : consulte un référentiel JSON local de
  recommandations générales par mot-clé.

Le `mcp_client.py` du backend se connecte au serveur MCP via
transport **stdio** : il lance le serveur comme sous-processus,
établit une session MCP, puis appelle l'outil
`lookup_care_guideline` de manière asynchrone (encapsulée dans un
wrapper synchrone pour s'intégrer simplement dans le nœud
`DiagnosticAgent`). Ce choix de transport stdio évite d'avoir à gérer
un serveur réseau séparé : le serveur MCP est démarré et arrêté à la
demande, à chaque appel.

## 5. API FastAPI

L'API expose les cinq routes exigées et fait office de couche de
sérialisation entre le graphe LangGraph et le frontend :

- `POST /sessions/start` génère un identifiant de session
  (`thread_id`), clé du checkpointer LangGraph.
- `POST /consultation/start` initialise l'état et exécute le graphe
  jusqu'à la première interruption.
- `POST /consultation/resume` reprend l'exécution avec
  `Command(resume=...)` à partir de la valeur fournie par le client
  (réponse patient ou traitement médecin).
- `GET /consultation/{thread_id}` et
  `GET /consultation/{thread_id}/report` permettent de relire l'état
  courant ou le rapport final sans avancer le workflow.

Un point d'attention technique a été nécessaire : l'attribut
`snapshot.next` de LangGraph reste vide (`()`) lorsque le graphe est
en pause sur une interruption (contrairement à une fin normale de
workflow). La détection de fin de consultation (`is_finished`) se
base donc sur la présence ou l'absence d'interruptions actives dans
`snapshot.tasks`, et non sur `snapshot.next`.

## 6. Frontend Streamlit

Le frontend implémente les quatre écrans minimums exigés (saisie du
cas initial, questions/réponses patient, revue médecin, rapport
final) comme une machine à états pilotée par le champ `interrupt`
renvoyé par l'API : son `type` (`patient_question` ou
`physician_review`) déterminé quel écran afficher, et l'indicateur
`is_finished` déclenche l'affichage de l'écran de rapport final.

## 7. Limites et cadre académique

Conformément aux sections 2 et 4.4 du cahier des charges, toutes les
recommandations produites par le système restent volontairement
prudentes et génériques : aucune décision médicale n'est prise par
les agents eux-mêmes, la décision finale reposant systématiquement
sur la validation explicite d'un médecin traitant humain
(Human-in-the-Loop). Le système n'intègre pas de modèle de langage
externe par défaut : la logique de synthèse et de recommandation
repose sur des règles déterministes simples, suffisantes pour
démontrer l'architecture multi-agents et le mécanisme
Human-in-the-Loop dans un cadre académique.
