# Schéma d'intégration de la logique de sédimentation entre modules

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
