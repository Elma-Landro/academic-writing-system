
# Système de Rédaction Académique Intégré
## 🚀 Plateforme d'assistance IA pour la rédaction académique.

Une plateforme avancée combinant **intelligence artificielle** et **workflow de sédimentation progressive** pour révolutionner la rédaction académique structurée.

## 🎯 Architecture technique

### 🏗️ Structure modulaire
```
academic-writing-system/
├── core/                    # Modules fondamentaux
│   ├── auth_system.py      # Authentification OAuth2 Google
│   ├── database_layer.py   # Couche d'accès aux données SQLite
│   ├── adaptive_engine.py  # Moteur d'adaptation utilisateur
│   ├── integration_layer.py # Orchestration des services
│   └── project_context.py  # Contexte de projet persistant
├── modules/                 # Modules fonctionnels
│   ├── storyboard.py       # Structuration narrative
│   ├── redaction.py        # Assistance à la rédaction
│   ├── revision.py         # Révision assistée par IA
│   ├── finalisation.py     # Export et finalisation
│   └── visualization/      # Analyse et métriques
├── services/               # Services externes
│   └── ai_service.py       # Interface OpenAI/Venice AI
├── utils/                  # Utilitaires
│   ├── cache.py            # Système de cache intelligent
│   ├── validators.py       # Validation des données
│   └── error_handlers.py   # Gestion d'erreurs robuste
└── data/                   # Persistance des données
    ├── academic_writing.db # Base de données SQLite
    ├── cache/              # Cache des requêtes IA
    ├── projects/           # Projets utilisateur
    └── exports/            # Documents exportés
```

## 🔄 Workflow de sédimentation en 4 phases

### Phase 1: Storyboard (Structuration)
- **Engine**: STORYBOARD ENGINE v1 avec pipeline 5 étapes
- **Fonctionnalités**:
  - Extraction automatique de thèses depuis texte source
  - Association de citations contextuelles
  - Génération de structure narrative cohérente
  - Prompts d'écriture personnalisés
- **Sédimentation**: Structure → Contexte projet → Phases suivantes

### Phase 2: Rédaction (Création)
- **Assistance IA contextuelle** basée sur la sédimentation
- **Pré-remplissage intelligent** depuis les données de storyboard
- **Outils intégrés**:
  - Génération de paragraphes ciblés
  - Reformulation de passages
  - Développement d'arguments
  - Création de transitions

### Phase 3: Révision (Amélioration) 
- **Analyse de densité qualitative** en temps réel
- **Métriques automatiques**:
  - Score de cohérence narrative
  - Densité argumentative par section
  - Recommandations d'amélioration
- **Révision par paragraphe** ou section complète

### Phase 4: Finalisation (Export)
- **Amélioration ligne par ligne** avec IA
- **Export multi-format**: Markdown, HTML, LaTeX, PDF
- **Métriques de qualité** finales
- **Archivage** avec historique complet

## 🧠 Système de sédimentation progressive

### Principe fondamental
Chaque module enrichit le contexte global via trois dimensions relationnelles:

1. **Utilisateur ↔ Système**: Apprentissage des préférences et adaptation
2. **Système ↔ Contenu**: Enrichissement progressif des données entre modules  
3. **Système ↔ IA**: Optimisation continue des prompts et générations

### Implémentation technique
```python
# Exemple de flux de sédimentation
class SedimentationManager:
    def transfer_context(self, from_phase: str, to_phase: str, data: dict):
        """Transfert enrichi entre phases avec conservation du contexte"""
        enhanced_context = self.enrich_with_user_profile(data)
        return self.adapt_for_phase(enhanced_context, to_phase)
```

## 🔧 Technologies et services

### Stack technique principal  
- **Frontend**: Streamlit 1.31+ avec interface responsive
- **Backend**: Python 3.8+ avec architecture modulaire
- **Base de données**: SQLite avec SQLAlchemy ORM
- **Cache**: Système de cache intelligent multi-niveaux
- **Authentification**: OAuth2 Google avec gestion sécurisée des tokens

### Services IA intégrés
- **OpenAI GPT-4**: Service principal (gpt-4o, gpt-4o-mini)
- **Venice AI**: Service de fallback et diversification
- **Cache intelligent**: Optimisation coûts et performances
- **Validation**: Contrôle qualité automatique des générations

### Algorithmes spécialisés

#### STORYBOARD ENGINE v1
```python
# Pipeline de traitement automatique
def generate_automatic_storyboard(source_text: str) -> dict:
    steps = [
        extract_theses_from_text,      # Identification thèses
        associate_citations,           # Liens citations
        fuse_and_articulate,          # Fusion logique  
        propose_section_sequence,      # Enchaînement
        integrate_narrative_structure  # Structure finale
    ]
    return execute_pipeline(steps, source_text)
```

#### Analyseur de densité qualitative  
- **Métriques**: Cohérence, densité argumentative, fluidité narrative
- **Scoring**: Algorithme propriétaire 0-100 par section et global
- **Recommandations**: Suggestions contextuelles d'amélioration

## 💻 Installation et configuration technique

### Prérequis système
```bash
# Versions minimales requises
Python >= 3.8
Streamlit >= 1.31.0
SQLAlchemy >= 2.0
OpenAI Python >= 1.0
```

### Configuration complète
```bash
# 1. Clonage et installation
git clone https://github.com/Elma-Landro/academic-writing-system
cd academic-writing-system
pip install -r requirements.txt

# 2. Configuration secrets
cp secrets_template.toml secrets.toml
# Éditer avec vos clés API

# 3. Initialisation base de données
python -c "from core.database_layer import db_manager; db_manager.init_db()"

# 4. Lancement
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

### Configuration OAuth2 Google
```toml
[google_oauth]
client_id = "votre-client-id.googleusercontent.com"
client_secret = "votre-client-secret"
redirect_uri = "https://votre-app.replit.app/auth/callback"
```

### Configuration services IA
```toml
[openai]
api_key = "sk-..."
default_model = "gpt-4o"
fallback_model = "gpt-4o-mini"

[venice_ai]  # Service de fallback
api_key = "votre-clé-venice"
endpoint = "https://api.venice.ai/v1"
```

## 📊 Métriques et monitoring

### Système de cache intelligent
- **Hit rate** optimal: >85% pour requêtes récurrentes
- **TTL adaptatif**: Basé sur le type de contenu et fréquence d'usage
- **Invalidation**: Automatique lors de modifications contextuelles

### Métriques qualité
```python
# Exemple de métriques calculées
quality_metrics = {
    "coherence_score": 0.87,        # Cohérence narrative
    "density_score": 0.93,          # Densité argumentative  
    "section_balance": 0.78,        # Équilibre entre sections
    "transition_quality": 0.85,     # Qualité des transitions
    "global_score": 0.86            # Score global pondéré
}
```

## 🚀 API et extensibilité

### Core API
```python
from core.integration_layer import IntegrationLayer

# Initialisation du système
integration = IntegrationLayer()
project = integration.create_project(
    title="Mon Article",
    style="CRÉSUS-NAKAMOTO", 
    discipline="Sciences sociales"
)

# Génération storyboard
storyboard = integration.generate_storyboard(
    project_id=project.id,
    source_text="Texte de base..."
)

# Rédaction assistée
content = integration.assist_writing(
    section_id=storyboard.sections[0].id,
    assistance_type="develop_argument",
    context="Développer l'argument principal"
)
```

### Hooks d'extension
- **Pre/Post processing**: Hooks personnalisés pour chaque phase
- **Custom validators**: Validation métier spécialisée  
- **Export plugins**: Formats d'export additionnels
- **IA models**: Intégration de nouveaux modèles

## 🔍 Cas d'usage techniques

### Recherche académique
```python
# Configuration optimisée pour publication scientifique
config = {
    "style": "Académique",
    "citation_format": "APA",
    "structure_type": "IMRAD",
    "quality_threshold": 0.90,
    "ai_model": "gpt-4o"
}
```

### Mémoires et thèses  
```python
# Workflow long document avec sédimentation avancée
workflow = LongDocumentWorkflow(
    chapters=True,
    cross_references=True,
    bibliography_integration=True,
    progressive_revision=True
)
```

## 📈 Performance et scalabilité

### Optimisations implémentées
- **Lazy loading**: Chargement progressif des modules lourds
- **Request batching**: Groupement des appels IA pour efficacité
- **Context pruning**: Élagage intelligent du contexte pour limites tokens
- **Async processing**: Traitement asynchrone des tâches longues

### Limites techniques actuelles
- **Max tokens**: 4000 tokens par requête IA (sécurité)
- **Cache size**: 500MB par utilisateur (limite mémoire)
- **Concurrent users**: 50 utilisateurs simultanés optimaux
- **Project size**: 100 sections max par projet

## 🔮 Roadmap technique

### Version 2.0 (Q2 2024)
- [ ] Support LaTeX natif avec compilation
- [ ] API REST complète pour intégrations tierces  
- [ ] Système de plugins pour extensions custom
- [ ] Multi-modèles IA simultanés avec vote majoritaire

### Version 3.0 (Q4 2024)  
- [ ] Architecture microservices avec Docker
- [ ] Base de données PostgreSQL distribuée
- [ ] Intégration Zotero/Mendeley native
- [ ] Collaboration temps réel multi-utilisateurs

## 🤝 Contribution technique

### Guidelines développement
```python
# Standards de code requis
from typing import Dict, List, Optional, Any
import logging

class NewModule:
    """Documentation complète requise."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.logger = logging.getLogger(__name__)
        
    def process_data(self, data: List[str]) -> Optional[Dict]:
        """Type hints obligatoires pour toutes méthodes."""
        pass
```

### Tests et validation
- **Coverage minimum**: 80% pour nouveaux modules
- **Integration tests**: Obligatoires pour flux complets
- **Performance tests**: Benchmarks pour composants critiques
- **Security audit**: Validation sécurité pour authentification

## 📄 Licences et attributions

### Licence principale
**GPL v3** - Voir LICENSE pour détails complets

### Dépendances principales
- **Streamlit**: Apache 2.0
- **OpenAI Python**: MIT  
- **SQLAlchemy**: MIT
- **Python standard library**: PSF

---

## 🆘 Support technique

### Documentation développeur
- [API Reference](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)  
- [Extension Development](docs/extensions.md)
- [Deployment Guide](docs/deployment.md)

### Debugging et logs
```bash
# Activation logs détaillés
export ACADEMIC_WRITING_DEBUG=true
export ACADEMIC_WRITING_LOG_LEVEL=DEBUG
streamlit run app.py
```

**🚀 Système de rédaction académique avec IA - Architecture robuste et extensible**
