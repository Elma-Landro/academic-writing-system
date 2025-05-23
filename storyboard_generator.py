"""
Module de génération automatique de storyboard académique selon le STORYBOARD ENGINE v1.

Ce module implémente le pipeline de traitement en 5 étapes pour construire
l'ossature narrative d'un article académique à partir d'un document source.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

from utils.ai_service import call_ai_safe

# Prompt principal du STORYBOARD ENGINE v1
STORYBOARD_PROMPT = """
# STORYBOARD ENGINE v1

## Objectif
Construire l'ossature narrative d'un article académique à partir d'une thèse ou d'un document long, en identifiant et fusionnant les thèses principales, sous-thèses, et matériaux exemplaires.

## 1. INPUTS
a. Document source : {document_source}
b. Niveau de structuration initiale : {structure_level}
c. Objet, problématique, fragments conceptuels : {problem_statement}
d. Mode de traitement : {processing_mode}
e. Nombre de citations par item : {citations_per_item} citations exactes avec n° de page
f. Contrainte : {constraints}

## 2. PIPELINE DE TRAITEMENT

### Étape 1 — Identification des thèses
- Extraire les thèses principales à partir {extraction_method}
- Formuler chaque thèse de manière claire et concise
- Identifier les relations logiques entre les thèses

### Étape 2 — Association de citations marquantes
- Sélectionner {citations_per_item} citations marquantes par sous-thèse
- Inclure systématiquement la pagination pour chaque citation
- Privilégier les citations qui illustrent ou renforcent la thèse

### Étape 3 — Fusion / articulation logique des thèses
- Regrouper les thèses connexes
- Établir une progression logique entre les groupes de thèses
- Identifier les tensions conceptuelles et les points de convergence

### Étape 4 — Proposition d'un enchaînement de sections
- Formuler des titres narratifs provisoires pour chaque section
- Assurer une progression argumentative cohérente
- Vérifier l'équilibre entre les différentes sections

### Étape 5 — {optional_step}
- Intégrer les thèses dans les sections types (introduction, méthodologie, etc.)
- Adapter la structure aux normes de la publication visée
- Vérifier la cohérence globale de la structure

## 3. OUTPUTS
a. Tableau synthétique (Thèses & arc narratif / Citations / Pages / Section de rattachement)
b. Proposition de structuration narrative (titre article + plan argumentatif)
c. Fichier annoté (si nécessaire)

Analyse le document fourni et applique rigoureusement ce processus en 5 étapes pour produire une ossature narrative complète et cohérente.
"""

def generate_storyboard_prompt(
    document_source="thèse, article",
    structure_level="titres et sous-titres de section",
    problem_statement="",
    processing_mode="Extraction des thèses à partir du dernier niveau de titrage (niveau 3), ou extraction libre",
    citations_per_item="4 à 8",
    constraints="nombre de caractères, attendus formels",
    extraction_method="des titres de niveau 3 dans le document",
    optional_step="(optionnel) Intégration des thèses dans les sections types"
):
    """
    Génère un prompt personnalisé pour le STORYBOARD ENGINE v1.
    
    Args:
        document_source: Type de document source
        structure_level: Niveau de structuration initiale
        problem_statement: Objet, problématique, fragments conceptuels
        processing_mode: Mode de traitement des thèses
        citations_per_item: Nombre de citations par item
        constraints: Contraintes formelles
        extraction_method: Méthode d'extraction des thèses
        optional_step: Description de l'étape optionnelle
        
    Returns:
        Prompt formaté pour le STORYBOARD ENGINE
    """
    return STORYBOARD_PROMPT.format(
        document_source=document_source,
        structure_level=structure_level,
        problem_statement=problem_statement,
        processing_mode=processing_mode,
        citations_per_item=citations_per_item,
        constraints=constraints,
        extraction_method=extraction_method,
        optional_step=optional_step
    )

def extract_theses_and_citations(document_text: str, level: int = 3) -> List[Dict[str, Any]]:
    """
    Extrait les thèses et citations potentielles d'un document basé sur les titres de niveau spécifié.
    
    Args:
        document_text: Texte du document source
        level: Niveau de titre à considérer comme thèses (par défaut: 3 pour les titres H3)
        
    Returns:
        Liste de dictionnaires contenant les thèses et leur contenu associé
    """
    # Pattern pour détecter les titres selon le niveau
    heading_marker = '#' * level
    heading_pattern = rf"(?m)^{heading_marker}\s+(.*?)$"
    
    # Trouver tous les titres du niveau spécifié
    headings = re.finditer(heading_pattern, document_text)
    
    theses = []
    last_pos = 0
    
    for i, match in enumerate(headings):
        heading_text = match.group(1).strip()
        start_pos = match.end()
        
        # Chercher le prochain titre (de n'importe quel niveau supérieur ou égal)
        next_heading = re.search(r"(?m)^#{1,6}\s+", document_text[start_pos:])
        
        if next_heading:
            end_pos = start_pos + next_heading.start()
            content = document_text[start_pos:end_pos].strip()
        else:
            content = document_text[start_pos:].strip()
        
        # Extraire les citations potentielles (texte entre guillemets)
        citation_pattern = r"[«""]([^«""]+)[»""]"
        citations = re.finditer(citation_pattern, content)
        
        citation_list = []
        for citation_match in citations:
            citation_text = citation_match.group(1).strip()
            
            # Chercher une référence de page à proximité
            page_ref = None
            context = content[max(0, citation_match.start() - 30):min(len(content), citation_match.end() + 30)]
            page_match = re.search(r"(?:p\.?|page)\s*(\d+(?:-\d+)?)", context)
            
            if page_match:
                page_ref = page_match.group(1)
            
            citation_list.append({
                "text": citation_text,
                "page": page_ref or "N/A"
            })
        
        theses.append({
            "title": heading_text,
            "content": content,
            "citations": citation_list[:8]  # Limiter à 8 citations maximum
        })
        
        last_pos = start_pos
    
    return theses

def generate_automatic_storyboard(
    document_text: str,
    problem_statement: str = "",
    constraints: str = "",
    extraction_level: int = 3,
    citations_per_item: int = 5
) -> Dict[str, Any]:
    """
    Génère automatiquement un storyboard académique à partir d'un document source.
    
    Args:
        document_text: Texte complet du document source
        problem_statement: Problématique ou objectif de l'article
        constraints: Contraintes formelles (longueur, format, etc.)
        extraction_level: Niveau de titre pour l'extraction des thèses
        citations_per_item: Nombre de citations à inclure par thèse
        
    Returns:
        Dictionnaire contenant le storyboard généré avec toutes ses composantes
    """
    # Étape 1 & 2: Extraction des thèses et citations du document
    extracted_theses = extract_theses_and_citations(document_text, extraction_level)
    
    # Préparation des données pour le prompt
    theses_text = ""
    for i, thesis in enumerate(extracted_theses):
        theses_text += f"\nThèse {i+1}: {thesis['title']}\n"
        
        # Ajouter les citations extraites
        if thesis['citations']:
            theses_text += "Citations associées:\n"
            for j, citation in enumerate(thesis['citations'][:citations_per_item]):
                theses_text += f"- \"{citation['text']}\" (p. {citation['page']})\n"
    
    # Génération du prompt personnalisé
    prompt = generate_storyboard_prompt(
        document_source="document fourni ci-dessous",
        structure_level=f"titres de niveau {extraction_level}",
        problem_statement=problem_statement,
        processing_mode=f"Extraction des thèses à partir des titres de niveau {extraction_level}",
        citations_per_item=str(citations_per_item),
        constraints=constraints,
        extraction_method=f"des titres de niveau {extraction_level} dans le document"
    )
    
    # Ajout des thèses extraites au prompt
    full_prompt = f"{prompt}\n\nDOCUMENT SOURCE (EXTRAITS):\n{document_text[:1000]}...\n\nTHÈSES ET CITATIONS EXTRAITES:\n{theses_text}\n\nVeuillez générer le storyboard complet selon le pipeline en 5 étapes."
    
    # Appel à l'API IA pour générer le storyboard
    result = call_ai_safe(
        prompt=full_prompt,
        max_tokens=4000,
        temperature=0.3,  # Température basse pour un résultat plus structuré
        model="gpt-4o"
    )
    
    # Traitement et structuration de la réponse
    storyboard_text = result.get("text", "")
    
    # Extraction du tableau synthétique et de la proposition de structure
    # (Ces patterns sont approximatifs et pourraient nécessiter des ajustements)
    table_pattern = r"(?:Tableau synthétique|TABLEAU SYNTHÉTIQUE)(.*?)(?:Proposition de structuration|PROPOSITION DE STRUCTURATION)"
    table_match = re.search(table_pattern, storyboard_text, re.DOTALL)
    
    structure_pattern = r"(?:Proposition de structuration|PROPOSITION DE STRUCTURATION)(.*?)(?:Fichier annoté|FICHIER ANNOTÉ|$)"
    structure_match = re.search(structure_pattern, storyboard_text, re.DOTALL)
    
    # Extraction des sections proposées
    sections = []
    if structure_match:
        structure_text = structure_match.group(1).strip()
        section_pattern = r"(?:^|\n)(\d+\.\s*.*?)(?=\n\d+\.\s*|\n\n|$)"
        section_matches = re.finditer(section_pattern, structure_text, re.DOTALL)
        
        for section_match in section_matches:
            section_text = section_match.group(1).strip()
            # Séparer le titre de la description
            title_parts = section_text.split("\n", 1)
            title = re.sub(r"^\d+\.\s*", "", title_parts[0].strip())
            description = title_parts[1].strip() if len(title_parts) > 1 else ""
            
            sections.append({
                "title": title,
                "content": description
            })
    
    # Construction du résultat final
    return {
        "raw_response": storyboard_text,
        "table": table_match.group(1).strip() if table_match else "",
        "structure": structure_match.group(1).strip() if structure_match else "",
        "sections": sections,
        "theses": extracted_theses
    }

def parse_storyboard_sections(storyboard_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Convertit le résultat du storyboard en sections formatées pour l'application.
    
    Args:
        storyboard_result: Résultat de la fonction generate_automatic_storyboard
        
    Returns:
        Liste de sections formatées pour l'ajout au projet
    """
    sections = []
    
    # Ajouter les sections proposées
    for i, section in enumerate(storyboard_result.get("sections", [])):
        sections.append({
            "title": section.get("title", f"Section {i+1}"),
            "content": section.get("content", "")
        })
    
    # Si aucune section n'a été extraite, créer des sections à partir du tableau
    if not sections and storyboard_result.get("table"):
        table_text = storyboard_result.get("table", "")
        # Tenter d'extraire des lignes du tableau
        rows = re.split(r"\n+", table_text)
        
        for i, row in enumerate(rows):
            if row.strip() and i > 0:  # Ignorer l'en-tête
                parts = re.split(r"\s*\|\s*", row.strip())
                if len(parts) >= 2:
                    title = parts[0].strip()
                    content = " | ".join(parts[1:]).strip()
                    
                    sections.append({
                        "title": title,
                        "content": content
                    })
    
    # Si toujours aucune section, créer une section avec le résultat brut
    if not sections:
        sections.append({
            "title": "Storyboard généré",
            "content": storyboard_result.get("raw_response", "")
        })
    
    return sections
