# Système de Rédaction Académique

Un système complet pour structurer, rédiger et réviser des textes académiques avec assistance IA.

## Vision et concept

Le Système de Rédaction Académique Intégré est une plateforme complète conçue pour accompagner les chercheurs et académiques tout au long du processus de création de textes scientifiques. Contrairement aux outils d'écriture traditionnels ou aux assistants IA génériques, ce système repose sur une **logique de sédimentation progressive** où chaque étape enrichit la suivante, créant ainsi un flux de travail cohérent et une mémoire contextuelle riche.

## Fonctionnalités principales

- **Storyboard Engine** : Structuration narrative et organisation des idées
- **Agent de Déploiement Théorique** : Rédaction assistée par IA
- **Module de Révision** : Amélioration du style et de la cohérence
- **Finalisation** : Export dans différents formats (TXT, MD, JSON)
- **Gestion de l'historique** : Suivi des versions et restauration
- **Profil utilisateur** : Personnalisation de l'expérience
- **Moteur adaptatif** : Suggestions contextuelles et aide à la rédaction

## Architecture du système

Le système est organisé en modules distincts :

- **Core** : Modules fondamentaux (profil utilisateur, contexte de projet, moteur adaptatif, etc.)
- **Modules** : Fonctionnalités spécifiques (storyboard, rédaction, révision, finalisation)
- **Utils** : Services utilitaires (IA, cache, fonctions communes)

### Approche sédimentaire et relationnelle

Le cœur conceptuel du système repose sur trois dimensions relationnelles fondamentales :

1. **Relation utilisateur-système** : Le système apprend et s'adapte aux préférences stylistiques, disciplinaires et méthodologiques de l'utilisateur
2. **Relation système-contenu** : Chaque module transmet et enrichit les données au module suivant, assurant une continuité narrative et argumentative
3. **Relation système-modèle IA** : Une architecture robuste avec stratégies de fallback et cache optimise l'utilisation des services d'IA

Cette triple relation crée un environnement d'écriture qui devient progressivement plus personnalisé et efficace au fil de son utilisation.

## Architecture du système

Le système s'articule autour de quatre piliers fondamentaux :

### 1. Modules core (noyau relationnel)

Ces modules constituent l'épine dorsale du système et gèrent les relations fondamentales :

- **UserProfile** : Gestion des préférences utilisateur, styles d'écriture favoris et historique d'utilisation
- **ProjectContext** : Maintien du contexte global de chaque projet, métadonnées et structure
- **IntegrationLayer** : Orchestration des interactions entre tous les composants du système
- **AdaptiveEngine** : Adaptation dynamique des suggestions et du comportement du système
- **HistoryManager** : Suivi des versions et possibilité de revenir à des états antérieurs

### 2. Modules fonctionnels (workflow sédimentaire)

Ces modules correspondent aux étapes séquentielles du processus de rédaction académique :

- **Storyboard** : Structuration narrative et organisation des idées
- **Rédaction** : Création du contenu textuel avec assistance IA
- **Révision** : Amélioration du style, de la cohérence et de la rigueur
- **Finalisation** : Export et mise en forme finale du document

### 3. Services d'IA (intelligence adaptative)

L'intelligence du système repose sur des services d'IA robustes et redondants :

- **Service OpenAI** : Utilisation des modèles GPT pour la génération et l'analyse de texte
- **Service Venice** (fallback) : Alternative en cas d'indisponibilité du service principal
- **Système de cache** : Optimisation des performances et réduction des coûts d'API

### 4. Interface utilisateur (expérience fluide)

Une interface Streamlit intuitive et réactive qui guide l'utilisateur à travers le processus :

- **Navigation par onglets** suivant la progression naturelle du workflow
- **Visualisation constante** du plan et de la structure du document
- **Feedback immédiat** sur les actions et suggestions contextuelles

## Workflow sédimentaire

Le système implémente un workflow en quatre phases où chaque étape s'appuie sur les précédentes et prépare les suivantes :

### Phase 1 : Storyboard (structuration)

Cette phase initiale permet de définir l'ossature du document :

- Création de sections avec titres et descriptions
- Génération assistée de structures narratives
- Suggestions adaptées au type de document (article, thèse, etc.)
- Réorganisation intuitive des sections

**Sédimentation** : La structure créée ici devient le fondement pour toutes les phases suivantes.

### Phase 2 : Rédaction (création)

La phase de rédaction s'appuie directement sur la structure définie dans le storyboard :

- Édition section par section avec contexte global toujours visible
- Génération assistée de contenu basée sur les descriptions du storyboard
- Analyse en temps réel de la complexité et du style
- Suggestions stylistiques adaptées aux préférences utilisateur

**Sédimentation** : Le contenu créé ici enrichit la structure et prépare la phase de révision.

### Phase 3 : Révision (amélioration)

La révision travaille directement sur le contenu rédigé :

- Analyse stylistique et grammaticale contextuelle
- Suggestions de citations pertinentes
- Révision assistée avec plusieurs modes (style, grammaire, clarification, condensation)
- Navigation fluide entre sections pour maintenir la cohérence globale

**Sédimentation** : Les améliorations apportées ici affinent le document pour la finalisation.

### Phase 4 : Finalisation (exportation)

La dernière phase assemble tous les éléments en un document cohérent :

- Prévisualisation du document complet
- Options d'export multiples (TXT, MD, JSON, avec PDF/DOCX à venir)
- Inclusion optionnelle des métadonnées
- Marquage du projet comme terminé avec sauvegarde dans l'historique
- # Schéma d'intégration de la logique de sédimentation entre modules

## Principe fondamental

La logique de sédimentation consiste à faire en sorte que chaque module du système (Storyboard → Rédaction → Révision → Finalisation) s'appuie sur les données générées par le module précédent, avec un pré-remplissage automatique et une transmission fluide des informations.

## Flux de données entre modules

### 1. Storyboard → Rédaction

- Le **Storyboard** génère la structure narrative (titres d'article, sections, sous-sections)
- La **Rédaction** reçoit automatiquement cette structure et propose des formulaires pré-remplis avec:
  - Les titres de sections définis dans le storyboard
  - Des suggestions de contenu basées sur les thèses et citations identifiées
  - Des indications narratives pour guider la rédaction de chaque section

### 2. Rédaction → Révision

- La **Rédaction** produit le contenu textuel de chaque section
- La **Révision** reçoit ce contenu et propose:
  - Une analyse automatique du style et de la cohérence
  - Des suggestions d'amélioration contextuelles
  - Des options de révision adaptées au style défini dans les préférences

### 3. Révision → Finalisation

- La **Révision** affine le contenu section par section
- La **Finalisation** assemble automatiquement toutes les sections révisées et propose:
  - Une prévisualisation du document complet
  - Des options d'export adaptées au type de document
  - Des suggestions finales pour la cohérence globale

## Implémentation technique

### Modifications requises pour chaque module

#### Module Storyboard

1. Ajouter des champs pour:
   - Titre de l'article
   - Structure existante (sections et sous-sections)
   - Thèses principales par section

2. Sauvegarder dans le contexte du projet:
   - La structure narrative complète
   - Les thèses et citations associées à chaque section
   - Les contraintes formelles définies

#### Module Rédaction

1. Modifier l'interface pour:
   - Afficher la structure définie dans le storyboard
   - Pré-remplir les champs avec les thèses et citations identifiées
   - Proposer des suggestions de contenu basées sur le storyboard

2. Ajouter une fonctionnalité de:
   - Génération assistée basée sur les thèses du storyboard
   - Vérification de cohérence avec la structure narrative
   - Sauvegarde des versions intermédiaires

#### Module Révision

1. Adapter l'interface pour:
   - Afficher le contenu rédigé avec la structure narrative
   - Proposer des analyses contextuelles basées sur le style défini
   - Suggérer des améliorations spécifiques à chaque section

2. Ajouter des outils de:
   - Révision assistée par paragraphe
   - Vérification de la cohérence entre sections
   - Suggestions de transitions entre les parties

#### Module Finalisation

1. Enrichir l'interface pour:
   - Assembler automatiquement toutes les sections révisées
   - Proposer une prévisualisation structurée selon le storyboard
   - Offrir des options d'export adaptées au type de document

2. Ajouter des fonctionnalités de:
   - Vérification finale de cohérence globale
   - Génération de métadonnées basées sur le processus complet
   - Export multi-format avec structure préservée

## Persistance des données

Pour assurer la continuité entre les modules, toutes les données générées doivent être:

1. Sauvegardées dans le contexte du projet via `project_context`
2. Accessibles à tous les modules via `integration_layer`
3. Versionnées à chaque étape via `history_manager`
4. Enrichies progressivement par l'`adaptive_engine`

Cette architecture garantit que chaque module peut accéder aux données des modules précédents et les enrichir, créant ainsi une véritable sédimentation progressive du contenu académique.


## Mémoire contextuelle à trois niveaux

Le système maintient une mémoire contextuelle riche à trois niveaux distincts :

### 1. Niveau projet

- Structure complète du document (sections, titres, contenus)
- Métadonnées (type, discipline, longueur cible)
- Historique des versions avec descriptions des modifications
- Statut d'avancement global et par section

### 2. Niveau utilisateur

- Préférences stylistiques et disciplinaires
- Historique des projets et activités
- Statistiques d'utilisation pour personnalisation
- Suggestions adaptées aux habitudes d'écriture

### 3. Niveau contenu

- Analyse de complexité et de style par section
- Suggestions contextuelles basées sur le contenu existant
- Cohérence narrative et argumentative entre sections
- Citations et références pertinentes au domaine

## Avantages et cas d'usage

### Pour les chercheurs et académiques

- **Gain de temps** : Structuration guidée et assistance à chaque étape
- **Cohérence améliorée** : Maintien de la continuité narrative et argumentative
- **Personnalisation** : Adaptation au style et aux préférences individuelles
- **Traçabilité** : Historique complet des versions et modifications

### Pour les étudiants

- **Apprentissage méthodologique** : Guide pas à pas du processus d'écriture académique
- **Feedback immédiat** : Suggestions d'amélioration en temps réel
- **Structure rigoureuse** : Aide à la construction logique des arguments
- **Flexibilité** : Adaptation à différents types de travaux académiques

### Pour les équipes de recherche

- **Collaboration** : Base commune pour la structuration et la rédaction
- **Standardisation** : Maintien d'un style cohérent à travers les documents
- **Documentation** : Historique détaillé du processus de création
- **Efficacité** : Réduction du temps consacré aux aspects formels

## Perspectives d'évolution

Le système est conçu pour évoluer selon plusieurs axes :

### Intégrations futures

- **Gestionnaires bibliographiques** (Zotero, Mendeley)
- **Outils de visualisation de données** pour intégration de graphiques
- **Plateformes de publication académique** pour soumission directe

### Améliorations techniques

- **Interface plus dynamique et interactive** avec animations et transitions fluides
- **Support multiformat** complet (PDF, DOCX, LaTeX)
- **Collaboration en temps réel** entre plusieurs utilisateurs
- **Analyse sémantique avancée** pour suggestions plus pertinentes

### Personnalisation avancée

- **Styles disciplinaires spécifiques** (sciences dures, sciences sociales, etc.)
- **Templates personnalisables** pour différents types de publications
- **Adaptation aux normes éditoriales** de revues spécifiques
- **Apprentissage continu** des préférences utilisateur

## Conclusion

Le Système de Rédaction Académique Intégré représente une approche novatrice de l'assistance à l'écriture scientifique, fondée sur une logique de sédimentation progressive et une triple relation (utilisateur-système, système-contenu, système-modèle IA). 

En capitalisant sur les forces de l'intelligence artificielle tout en maintenant l'utilisateur au centre du processus créatif, ce système offre un équilibre optimal entre assistance automatisée et contrôle humain, permettant aux chercheurs et académiques de se concentrer sur le fond de leur travail plutôt que sur les aspects formels et techniques.


## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
OPENAI_API_KEY=votre_clé_api_openai
VENICE_API_KEY=votre_clé_api_venice (optionnel)
```

2. Assurez-vous que les dossiers de données sont créés (ils seront automatiquement créés au premier lancement) :

```
data/
├── cache/
├── exports/
├── history/
├── profiles/
└── projects/
```

## Utilisation

### Lancement de l'application

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse http://localhost:8501

### Workflow recommandé

1. **Création d'un projet** : Définissez le titre, la description et les préférences
2. **Storyboard** : Structurez votre document en sections
3. **Rédaction** : Rédigez le contenu de chaque section
4. **Révision** : Améliorez le style et la cohérence
5. **Finalisation** : Exportez votre document dans le format souhaité

## Styles d'écriture

Le système prend en charge plusieurs styles d'écriture académique :

- **Standard** : Style académique standard, clair et précis
- **Académique** : Style académique formel avec terminologie spécialisée
- **CRÉSUS-NAKAMOTO** : Style analytique avec tensions conceptuelles et perspective historique
- **AcademicWritingCrypto** : Style technique orienté crypto-ethnographie

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Remerciements

- Méthodologie Michelat pour la structure de workflow
- Agent de Construction Sectionnelle pour les techniques de rédaction
- OpenAI pour les services d'IA
- 
## Outil de diagnostic OAuth

Ce dépôt inclut un fichier `auth_debug_tool.py` pour tester et vérifier la configuration OAuth Google (secrets, redirection, permissions, etc.).

- Lancez-le temporairement à la place de `app.py` si vous rencontrez des problèmes d'authentification.
- Aucun impact sur le fonctionnement de l'application principale.
