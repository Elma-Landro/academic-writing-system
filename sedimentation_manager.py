
"""
Gestionnaire de sédimentation - Orchestration des flux de données entre modules
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class SedimentationPhase(Enum):
    """Phases de sédimentation du système."""
    STORYBOARD = "storyboard"
    REDACTION = "redaction"
    REVISION = "revision"
    FINALISATION = "finalisation"

@dataclass
class SectionData:
    """Structure de données pour une section."""
    section_id: str
    title: str
    description: str = ""
    content: str = ""
    theses: List[str] = None
    citations: List[str] = None
    status: str = "created"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.theses is None:
            self.theses = []
        if self.citations is None:
            self.citations = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SedimentationContext:
    """Contexte de sédimentation pour un projet."""
    project_id: str
    current_phase: SedimentationPhase
    sections: List[SectionData]
    global_metadata: Dict[str, Any]
    transitions_log: List[Dict[str, Any]]
    
    def __post_init__(self):
        if not self.sections:
            self.sections = []
        if not self.transitions_log:
            self.transitions_log = []

class SedimentationManager:
    """Gestionnaire central de la logique de sédimentation."""
    
    def __init__(self, project_context, history_manager):
        self.project_context = project_context
        self.history_manager = history_manager
        self.transitions = {
            SedimentationPhase.STORYBOARD: self._prepare_redaction_data,
            SedimentationPhase.REDACTION: self._prepare_revision_data,
            SedimentationPhase.REVISION: self._prepare_finalisation_data
        }
    
    def get_sedimentation_context(self, project_id: str) -> SedimentationContext:
        """Récupère le contexte de sédimentation d'un projet."""
        project = self.project_context.load_project(project_id)
        if not project:
            return self._create_empty_context(project_id)
        
        # Extraire les données de sédimentation du projet
        sedimentation_data = project.get('sedimentation', {})
        
        sections = [
            SectionData(**section_data) 
            for section_data in sedimentation_data.get('sections', [])
        ]
        
        return SedimentationContext(
            project_id=project_id,
            current_phase=SedimentationPhase(sedimentation_data.get('current_phase', 'storyboard')),
            sections=sections,
            global_metadata=sedimentation_data.get('global_metadata', {}),
            transitions_log=sedimentation_data.get('transitions_log', [])
        )
    
    def save_sedimentation_context(self, context: SedimentationContext) -> bool:
        """Sauvegarde le contexte de sédimentation."""
        try:
            # Convertir en dictionnaire pour la sauvegarde
            sedimentation_data = {
                'current_phase': context.current_phase.value,
                'sections': [asdict(section) for section in context.sections],
                'global_metadata': context.global_metadata,
                'transitions_log': context.transitions_log,
                'last_updated': datetime.now().isoformat()
            }
            
            # Sauvegarder dans le projet
            project = self.project_context.load_project(context.project_id)
            if project:
                project['sedimentation'] = sedimentation_data
                return self.project_context.save_project(context.project_id, project)
            
            return False
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du contexte de sédimentation: {e}")
            return False
    
    def transition_to_phase(self, project_id: str, target_phase: SedimentationPhase) -> Dict[str, Any]:
        """Effectue une transition vers une nouvelle phase."""
        context = self.get_sedimentation_context(project_id)
        
        # Vérifier si la transition est valide
        if not self._is_valid_transition(context.current_phase, target_phase):
            return {
                'success': False,
                'error': f"Transition invalide de {context.current_phase.value} vers {target_phase.value}"
            }
        
        # Préparer les données pour la nouvelle phase
        if context.current_phase in self.transitions:
            transition_result = self.transitions[context.current_phase](context)
            if not transition_result['success']:
                return transition_result
        
        # Effectuer la transition
        old_phase = context.current_phase
        context.current_phase = target_phase
        
        # Logger la transition
        context.transitions_log.append({
            'from_phase': old_phase.value,
            'to_phase': target_phase.value,
            'timestamp': datetime.now().isoformat(),
            'sections_count': len(context.sections)
        })
        
        # Sauvegarder
        success = self.save_sedimentation_context(context)
        
        # Créer une version dans l'historique
        if success:
            self.history_manager.save_version(
                project_id,
                f"Transition vers {target_phase.value}",
                {
                    'phase': target_phase.value,
                    'sections_count': len(context.sections),
                    'transition_data': transition_result.get('data', {})
                }
            )
        
        return {
            'success': success,
            'context': context,
            'transition_data': transition_result.get('data', {}) if 'transition_result' in locals() else {}
        }
    
    def _prepare_redaction_data(self, context: SedimentationContext) -> Dict[str, Any]:
        """Prépare les données pour la phase de rédaction."""
        redaction_data = {
            'pre_filled_sections': [],
            'narrative_structure': context.global_metadata.get('narrative_structure', {}),
            'writing_guidelines': {}
        }
        
        for section in context.sections:
            section_redaction = {
                'section_id': section.section_id,
                'title': section.title,
                'description': section.description,
                'suggested_content': self._generate_content_suggestions(section),
                'theses': section.theses,
                'citations': section.citations,
                'writing_prompts': self._generate_writing_prompts(section)
            }
            redaction_data['pre_filled_sections'].append(section_redaction)
        
        return {'success': True, 'data': redaction_data}
    
    def _prepare_revision_data(self, context: SedimentationContext) -> Dict[str, Any]:
        """Prépare les données pour la phase de révision."""
        revision_data = {
            'content_analysis': {},
            'style_suggestions': {},
            'coherence_check': {}
        }
        
        # Analyser le contenu existant
        total_words = 0
        sections_with_content = 0
        
        for section in context.sections:
            if section.content:
                sections_with_content += 1
                word_count = len(section.content.split())
                total_words += word_count
                
                revision_data['content_analysis'][section.section_id] = {
                    'word_count': word_count,
                    'has_theses': len(section.theses) > 0,
                    'has_citations': len(section.citations) > 0,
                    'completion_status': 'complete' if word_count > 100 else 'incomplete'
                }
        
        revision_data['global_stats'] = {
            'total_words': total_words,
            'sections_with_content': sections_with_content,
            'completion_rate': sections_with_content / len(context.sections) if context.sections else 0
        }
        
        return {'success': True, 'data': revision_data}
    
    def _prepare_finalisation_data(self, context: SedimentationContext) -> Dict[str, Any]:
        """Prépare les données pour la phase de finalisation."""
        finalisation_data = {
            'document_structure': [],
            'export_metadata': {},
            'quality_metrics': {}
        }
        
        # Assembler la structure du document
        for section in context.sections:
            finalisation_data['document_structure'].append({
                'section_id': section.section_id,
                'title': section.title,
                'content': section.content,
                'word_count': len(section.content.split()) if section.content else 0,
                'theses_count': len(section.theses),
                'citations_count': len(section.citations)
            })
        
        # Calculer les métriques de qualité
        total_words = sum(len(s.content.split()) if s.content else 0 for s in context.sections)
        total_theses = sum(len(s.theses) for s in context.sections)
        total_citations = sum(len(s.citations) for s in context.sections)
        
        finalisation_data['quality_metrics'] = {
            'total_words': total_words,
            'total_sections': len(context.sections),
            'total_theses': total_theses,
            'total_citations': total_citations,
            'average_words_per_section': total_words / len(context.sections) if context.sections else 0
        }
        
        return {'success': True, 'data': finalisation_data}
    
    def _generate_content_suggestions(self, section: SectionData) -> List[str]:
        """Génère des suggestions de contenu pour une section."""
        suggestions = []
        
        if section.theses:
            suggestions.append(f"Développer les thèses: {', '.join(section.theses[:2])}")
        
        if section.citations:
            suggestions.append(f"Intégrer les citations de: {', '.join(section.citations[:2])}")
        
        if section.description:
            suggestions.append(f"S'appuyer sur la description: {section.description[:100]}...")
        
        return suggestions
    
    def _generate_writing_prompts(self, section: SectionData) -> List[str]:
        """Génère des prompts d'écriture pour une section."""
        prompts = [
            f"Rédigez une introduction pour la section '{section.title}'",
            f"Développez les arguments principaux de '{section.title}'",
            f"Concluez la section '{section.title}' en liant aux sections suivantes"
        ]
        return prompts
    
    def _is_valid_transition(self, current: SedimentationPhase, target: SedimentationPhase) -> bool:
        """Vérifie si une transition entre phases est valide."""
        valid_transitions = {
            SedimentationPhase.STORYBOARD: [SedimentationPhase.REDACTION],
            SedimentationPhase.REDACTION: [SedimentationPhase.REVISION, SedimentationPhase.STORYBOARD],
            SedimentationPhase.REVISION: [SedimentationPhase.FINALISATION, SedimentationPhase.REDACTION],
            SedimentationPhase.FINALISATION: [SedimentationPhase.REVISION]
        }
        
        return target in valid_transitions.get(current, [])
    
    def _create_empty_context(self, project_id: str) -> SedimentationContext:
        """Crée un contexte de sédimentation vide."""
        return SedimentationContext(
            project_id=project_id,
            current_phase=SedimentationPhase.STORYBOARD,
            sections=[],
            global_metadata={},
            transitions_log=[]
        )
    
    def add_section(self, project_id: str, title: str, description: str = "") -> str:
        """Ajoute une nouvelle section au contexte."""
        context = self.get_sedimentation_context(project_id)
        
        section_id = f"section_{len(context.sections) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        new_section = SectionData(
            section_id=section_id,
            title=title,
            description=description
        )
        
        context.sections.append(new_section)
        self.save_sedimentation_context(context)
        
        return section_id
    
    def update_section(self, project_id: str, section_id: str, **updates) -> bool:
        """Met à jour une section du contexte."""
        context = self.get_sedimentation_context(project_id)
        
        for section in context.sections:
            if section.section_id == section_id:
                for key, value in updates.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
                
                return self.save_sedimentation_context(context)
        
        return False
    
    def get_transition_readiness(self, project_id: str, target_phase: SedimentationPhase) -> Dict[str, Any]:
        """Évalue la préparation pour une transition de phase."""
        context = self.get_sedimentation_context(project_id)
        
        readiness = {
            'ready': False,
            'requirements_met': [],
            'requirements_missing': [],
            'warnings': []
        }
        
        if target_phase == SedimentationPhase.REDACTION:
            # Vérifications pour passer à la rédaction
            if len(context.sections) > 0:
                readiness['requirements_met'].append("Sections créées")
            else:
                readiness['requirements_missing'].append("Aucune section créée")
            
            sections_with_description = sum(1 for s in context.sections if s.description)
            if sections_with_description >= len(context.sections) * 0.5:
                readiness['requirements_met'].append("Descriptions suffisantes")
            else:
                readiness['requirements_missing'].append("Descriptions manquantes")
        
        elif target_phase == SedimentationPhase.REVISION:
            # Vérifications pour passer à la révision
            sections_with_content = sum(1 for s in context.sections if s.content)
            if sections_with_content >= len(context.sections) * 0.7:
                readiness['requirements_met'].append("Contenu suffisant")
            else:
                readiness['requirements_missing'].append("Contenu insuffisant")
        
        elif target_phase == SedimentationPhase.FINALISATION:
            # Vérifications pour passer à la finalisation
            sections_complete = sum(1 for s in context.sections if s.content and len(s.content.split()) > 50)
            if sections_complete == len(context.sections):
                readiness['requirements_met'].append("Toutes les sections complètes")
            else:
                readiness['requirements_missing'].append("Sections incomplètes")
        
        readiness['ready'] = len(readiness['requirements_missing']) == 0
        
        return readiness
