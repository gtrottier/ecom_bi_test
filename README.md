# Ecommerce BI Agent

## Description

Simple système agentique d'analyse de données e-commerce. Utilise plusieurs outils (mock) pour scraper des données, analyser les tendances et les sentiments, et générer des rapports.

Pour minimiser les dépendances, Docker est utilisé.
Pour un setup de développement, uv/poetry. 
## Installation

### Prérequis

- git
- Docker
- uv package manager (préférablement, sinon pip ou poetry peuvent fonctionner)
- python >= 3.12

**Note**: Non-requis mais on suppose un shell POSIX (bash, zsh, etc) et les permissions nécessaires. Commandes roulées à partir de la racine du dépôt.

### Installation

1. Cloner le dépôt

2. Environnement virtuel, selon package manager:
    - (uv) `uv sync`
    - (pip) `python -m venv .venv && source .venv/bin/activate && pip install .`
    - (poetry) `poetry install`

***RESTE A VENIR***



# Théorie, améliorations possibles etc.

## 4 Architecture de données et stockage
- Stockage résultats d'analyse:
PostgreSQL semble un bon choix. Assez standard, peut être en docker ou différentes solutions cloud gérées selon équipe, expertise, budget etc.
Désultats stockés en JSONB pour flexibilité.

- Maintien de l'historique des requêtes:
(Plus de détail dans #5)
LangFuse (auto-hébergé ou SaaS) stocke par défaut tous les détails des requêtes dans une bd ClickHouse, qui est incluse dans le docker-compose. La bd est haute performance, permet de stocker et requêter efficacement de très grands volumes de données. Les métadonnées des requêtes sont stockées dans une bd PostgreSQL, aussi incluse dans le docker-compose.

- Cachage des données collectées:
Pour les données collectées et mises en cache, Valkey est un bon choix. BD très haute performance, flexible, license très permissive, plusieurs améliorations par rapport à Redis. Disponible en auto-hébergé ou via différents fournisseurs.

- Configuration des agents:
Solution de base: Config-as-code dans dépôt. Prompts et configs ont versioning, revues etc. Agnostique, très simple et flexible. Manque de fonctionnalités avancées pour évaluation etc.
En plus ou à la place de ça, LangFuse a plusieurs options pour gérer les prompts: versioning, expérimentation, traçabilité etc., directement lié à config des agents.

## 5 Monitoring et observabilité
- Tracing:
    Plusieurs options disponibles comme LangSmith, LangFuse etc.
    J'utiliserais LangFuse: Open source, hébergable localement (docker) ou en SaaS selon besoins.
    Localement, c'est gratuit(excepté matériel etc.) et on garde la main sur les données. Assez clé-en-main, simple d'avoir traçabilité de base et améliorer graduellement.

- Collection métriques performance:

- Alertes en cas de dysfonctionnement:

- Mesure de la qualité des outputs


## 6 Scaling et optimisation

## 7 Amélioration continue et A/B testing