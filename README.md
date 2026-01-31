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
**Note**: Pour limiter le nombre de technologies ou services différents, je vais préférer des solutions qui offrent plusieurs outils ou ont plusieurs intégrations supportées officiellement, comme LangFuse qui est d'ailleurs Open Source et peut être auto-hébergé.

## 4 Architecture de données et stockage
### Stockage résultats d'analyse:
PostgreSQL semble un bon choix. Assez standard, peut être auto-hébergé (docker) ou via différentes solutions cloud gérées selon équipe, expertise, budget etc.
Désultats stockés en JSONB pour flexibilité.

### Maintien de l'historique des requêtes:
(Plus de détail dans #5)
LangFuse (auto-hébergé ou SaaS) stocke par défaut tous les détails des requêtes dans une bd ClickHouse, qui est incluse dans le docker-compose. La bd est haute performance, permet de stocker et requêter efficacement de très grands volumes de données. Les métadonnées des requêtes sont stockées dans une bd PostgreSQL, aussi incluse dans le docker-compose.

### Cachage des données collectées:
Pour les données collectées et mises en cache, Valkey est un bon choix. BD très haute performance, flexible, license très permissive, plusieurs améliorations par rapport à Redis. Disponible en auto-hébergé ou via différents fournisseurs.


### Configuration des agents:
Solution de base: Config-as-code dans dépôt. Prompts et configs ont versioning, revues etc. Agnostique, très simple et flexible. Manque de fonctionnalités avancées pour évaluation etc.
En plus ou à la place de ça, LangFuse a plusieurs options pour gérer les prompts: versioning, expérimentation, traçabilité etc., directement lié à config des agents.

## 5 Monitoring et observabilité
- Tracing:
    Plusieurs options disponibles comme LangSmith, LangFuse etc.
    J'utiliserais LangFuse: Open source, hébergable localement (docker) ou en SaaS selon besoins.
    Localement, c'est gratuit(excepté matériel etc.) et on garde la main sur les données. Assez clé-en-main, simple d'avoir bonne traçabilité, incluant tous les appels d'outils, exécution etc. pour débogage et améliorations.

### Collection métriques performance:
Encore une fois, il est possible de se baser sur LangFuse.  Beaucoup de métriques sont collectées par défaut, comme les coûts des tokens, le temps d'exécution de chaque requête et appel d'outils etc. On peut donc calculer les taux de succès, la précision des choix d'outils et autres. 

Il est ensuite facile d'exporter ces métriques vers Grafana par exemple pour les visualiser puis analyser et les lier à d'autres métriques comme celles d'infrastructure.


### Alertes en cas de dysfonctionnement:
Ici le plus simple et efficace serait sûrement de se baser sur les métriques collectées par LangFuse. On peut suivre par exemple les couts, taux d'erreurs, latence etc. et déclencher des alertes si des seuils sont dépassés. Ses alertes peuvent être envoyées vers d'autres services graces à des Webhooks, par exemple vers Slack (implémentation officielle) ou autres.


### Mesure de la qualité des outputs
Plusieurs approches possibles, certaines dépendent de l'équipe, l'expertise etc.
Pour commencer, on peut utiliser une évaluation *LLM-as-a-judge* dans LangFuse par exemple, en choisissant un modèle assez performant pour évaluer la qualité des réponses avec un raisonnement similaire à celui d'un humain.

Ensuite, si on a un expert humain disponible, il est possible d'annoter les traces directement dans LangFuse. On peut juger de la qualité du raisonnement, du choix des outils, de la pertinence des réponses etc. On peut associer différents scores et tags aux traces. On peut donc comparer différents prompts, différents outils etc.

À même l'application, on peut aussi mettre en place un système de feedback utilisateur, par exemple avec des pouces haut/bas, pour collecter des données sur la qualité des réponses. Ce feedback serait associé à la trace correspondante et pourrait être sauvegardé dans une base de données.


## 6 Scaling et optimisation

### Gestion des pics de charge (100+):
L'architecture proposée devrait pouvoir gérer des pics de charge modérés comme on utilise des modèles de langage via API externes, mais pour des pics plus importants un système de file d'attente serait nécessaire. On pourrait utiliser Celery comme gestionnaire de tâches asynchrones avec RabbitMQ ou Redis pour la transmission des messages.
Dans ce cas, peut-être qu'utiliser Redis pour la mise en cache aurait plus de sens, histoire d'avoir un service de moins à maintenir.

### Optimisation des coûts des LLM:
Tout d'abord, il serait important de faire un certain suivi des coûts avec LangFuse ou autre plateforme utilisée ainsi que le fournisseur d'accès au LLM, comme OpenRouter.

Ensuite, utiliser une variété de modèles différents pour différentes tâches, en favorisant les moins coûteux quand c'est possible pourrait réduire les coûts globaux. L'option locale avec un modèle sur vLLM par exemple serait bonne si le matériel et l'expertise le permettent

Certaines tâches comme l'analyse de sentiments par exemple devraient peut-être être faites par des modèles beaucoup plus légers et moins coûteux que des LLMs, comme BERT, RoBERTa, etc. Utiliser des modèles de ce genre pourrait aussi réduire la latence.

### Implémentation d'un système de cache intelligent




## 7 Amélioration continue et A/B testing