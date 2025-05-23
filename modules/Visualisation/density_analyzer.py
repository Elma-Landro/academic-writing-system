"""
Module d'évaluation de la densité qualitative relative.
Permet de comparer la densité qualitative des sections du document par rapport à un paragraphe de référence.
"""

import re
import math
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import streamlit as st

# Téléchargement des ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DensityAnalyzer:
    """
    Classe pour analyser la densité qualitative d'un texte par rapport à un paragraphe de référence.
    """
    
    def __init__(self, reference_paragraph=None, lang='french'):
        """
        Initialise l'analyseur de densité.
        
        Args:
            reference_paragraph: Paragraphe de référence considéré comme ayant une haute densité qualitative
            lang: Langue du texte ('french' ou 'english')
        """
        self.reference_paragraph = reference_paragraph
        self.lang = lang
        self.stop_words = set(stopwords.words(lang if lang != 'french' else 'french'))
        self.reference_metrics = self._calculate_metrics(reference_paragraph) if reference_paragraph else None
    
    def set_reference_paragraph(self, paragraph):
        """
        Définit le paragraphe de référence.
        
        Args:
            paragraph: Paragraphe de référence
        """
        self.reference_paragraph = paragraph
        self.reference_metrics = self._calculate_metrics(paragraph)
    
    def _calculate_metrics(self, text):
        """
        Calcule les métriques de densité pour un texte.
        
        Args:
            text: Texte à analyser
        
        Returns:
            dict: Métriques de densité
        """
        if not text:
            return None
        
        # Tokenization
        sentences = sent_tokenize(text, language='french' if self.lang == 'french' else 'english')
        words = word_tokenize(text, language='french' if self.lang == 'french' else 'english')
        
        # Filtrage des mots vides
        filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in self.stop_words]
        
        # Calcul des métriques
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(1, sentence_count)
        avg_word_length = sum(len(word) for word in filtered_words) / max(1, len(filtered_words))
        lexical_diversity = len(set(filtered_words)) / max(1, len(filtered_words))
        
        # Calcul de la densité de connecteurs logiques
        connectors = self._count_connectors(text)
        connector_density = connectors / max(1, word_count)
        
        # Calcul de la densité de termes académiques
        academic_terms = self._count_academic_terms(text)
        academic_density = academic_terms / max(1, word_count)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'lexical_diversity': lexical_diversity,
            'connector_density': connector_density,
            'academic_density': academic_density
        }
    
    def _count_connectors(self, text):
        """
        Compte le nombre de connecteurs logiques dans le texte.
        
        Args:
            text: Texte à analyser
        
        Returns:
            int: Nombre de connecteurs
        """
        # Liste de connecteurs logiques en français
        french_connectors = [
            r'\bainsi\b', r'\bdonc\b', r'\bpar conséquent\b', r'\ben conséquence\b', r'\bpar suite\b',
            r'\bde ce fait\b', r'\bc\'est pourquoi\b', r'\bvoilà pourquoi\b', r'\bd\'où\b',
            r'\bcar\b', r'\ben effet\b', r'\beffectivement\b', r'\bdu fait que\b', r'\bétant donné que\b',
            r'\bvu que\b', r'\bpuisque\b', r'\bcomme\b', r'\bgrâce à\b', r'\bà cause de\b',
            r'\bmais\b', r'\bcependant\b', r'\btoutefois\b', r'\bpourtant\b', r'\bnéanmoins\b',
            r'\ben revanche\b', r'\bau contraire\b', r'\binversement\b', r'\bcontrairement à\b',
            r'\bou\b', r'\bsoit\b', r'\btantôt\b', r'\bd\'une part\b', r'\bd\'autre part\b',
            r'\bégalement\b', r'\bde même\b', r'\bde plus\b', r'\ben outre\b', r'\bpar ailleurs\b',
            r'\bensuite\b', r'\bpuis\b', r'\bd\'abord\b', r'\bensuite\b', r'\benfin\b',
            r'\bpremièrement\b', r'\bdeuxièmement\b', r'\btroisièmement\b', r'\ben premier lieu\b',
            r'\ben second lieu\b', r'\ben dernier lieu\b', r'\bd\'un côté\b', r'\bde l\'autre côté\b',
            r'\bnon seulement\b', r'\bmais encore\b', r'\bplus\b', r'\bmoins\b', r'\bautant\b',
            r'\baussi\b', r'\bplus que\b', r'\bmoins que\b', r'\bautant que\b', r'\baussi que\b',
            r'\bsi\b', r'\bà condition que\b', r'\bpourvu que\b', r'\ben admettant que\b',
            r'\bsupposons que\b', r'\bsoit\b', r'\bsachant que\b', r'\bétant donné que\b'
        ]
        
        # Liste de connecteurs logiques en anglais
        english_connectors = [
            r'\btherefore\b', r'\bhence\b', r'\bconsequently\b', r'\bthus\b', r'\bso\b',
            r'\bas a result\b', r'\baccordingly\b', r'\bfor this reason\b', r'\bbecause\b',
            r'\bsince\b', r'\bas\b', r'\bdue to\b', r'\bowing to\b', r'\bgiven that\b',
            r'\bin view of\b', r'\bon account of\b', r'\bbut\b', r'\bhowever\b', r'\bnevertheless\b',
            r'\byet\b', r'\bstill\b', r'\bon the contrary\b', r'\bin contrast\b', r'\binstead\b',
            r'\bor\b', r'\beither\b', r'\bneither\b', r'\bnor\b', r'\balternatively\b',
            r'\blikewise\b', r'\bsimilarly\b', r'\bin the same way\b', r'\balso\b', r'\btoo\b',
            r'\bfurthermore\b', r'\bmoreover\b', r'\bin addition\b', r'\bbesides\b', r'\bfirst\b',
            r'\bsecond\b', r'\bthird\b', r'\bnext\b', r'\bthen\b', r'\bfinally\b', r'\blastly\b',
            r'\bto begin with\b', r'\bin conclusion\b', r'\bon one hand\b', r'\bon the other hand\b',
            r'\bnot only\b', r'\bbut also\b', r'\bmore\b', r'\bless\b', r'\bas much as\b',
            r'\bas\b', r'\bthan\b', r'\bif\b', r'\bunless\b', r'\bprovided that\b', r'\bproviding that\b',
            r'\bin case\b', r'\bsuppose that\b', r'\bassuming that\b', r'\bgiven that\b'
        ]
        
        # Sélection de la liste de connecteurs en fonction de la langue
        connectors = french_connectors if self.lang == 'french' else english_connectors
        
        # Comptage des connecteurs
        count = 0
        for connector in connectors:
            count += len(re.findall(connector, text, re.IGNORECASE))
        
        return count
    
    def _count_academic_terms(self, text):
        """
        Compte le nombre de termes académiques dans le texte.
        
        Args:
            text: Texte à analyser
        
        Returns:
            int: Nombre de termes académiques
        """
        # Liste de termes académiques en français
        french_academic_terms = [
            r'\banalyse\b', r'\bétude\b', r'\brecherche\b', r'\bthéorie\b', r'\bconcept\b',
            r'\bparadigme\b', r'\bproblématique\b', r'\bhypothèse\b', r'\bméthodologie\b',
            r'\bapproche\b', r'\bperspective\b', r'\bcontexte\b', r'\bcadre\b', r'\bstructure\b',
            r'\bsystème\b', r'\bprocessus\b', r'\bmécanisme\b', r'\bphénomène\b', r'\bdynamique\b',
            r'\bfacteur\b', r'\bvariable\b', r'\bparticularité\b', r'\bspécificité\b', r'\bcaractéristique\b',
            r'\bélément\b', r'\bcomposante\b', r'\bdimension\b', r'\baspect\b', r'\bniveau\b',
            r'\bcritère\b', r'\bindicateur\b', r'\bparamètre\b', r'\bréférence\b', r'\bsource\b',
            r'\bdonnée\b', r'\binformation\b', r'\bconnaissance\b', r'\bsavoir\b', r'\bcompétence\b',
            r'\bcapacité\b', r'\bpotentiel\b', r'\bressource\b', r'\bmoyens\b', r'\boutils\b',
            r'\bméthode\b', r'\btechnique\b', r'\bstratégie\b', r'\bdémarche\b', r'\bprocédure\b',
            r'\bprotocole\b', r'\bmodèle\b', r'\bschéma\b', r'\bfigure\b', r'\btableau\b',
            r'\bgraphique\b', r'\bdiagramme\b', r'\billustration\b', r'\bexemple\b', r'\bcas\b',
            r'\bsituation\b', r'\bcontexte\b', r'\bcirconstance\b', r'\bcondition\b', r'\bmodalité\b',
            r'\bcontrainte\b', r'\blimite\b', r'\brestriction\b', r'\bobstacle\b', r'\bdifficulté\b',
            r'\bproblème\b', r'\bquestion\b', r'\binterrogation\b', r'\bréflexion\b', r'\bpensée\b',
            r'\bidée\b', r'\bnotion\b', r'\bconception\b', r'\breprésentations\b', r'\bperception\b',
            r'\binterprétation\b', r'\bcompréhension\b', r'\bsignification\b', r'\bsens\b', r'\bvaleur\b',
            r'\bimportance\b', r'\bpertinence\b', r'\butilité\b', r'\befficacité\b', r'\bperformance\b',
            r'\bqualité\b', r'\bquantité\b', r'\bintensité\b', r'\bfréquence\b', r'\bdurée\b',
            r'\bpériode\b', r'\bépoque\b', r'\bère\b', r'\bphase\b', r'\bétape\b', r'\bstade\b',
            r'\bcycle\b', r'\bévolution\b', r'\bdéveloppement\b', r'\bprogression\b', r'\btransformation\b',
            r'\bmodification\b', r'\bchangement\b', r'\bvariation\b', r'\baltération\b', r'\bmutation\b',
            r'\btransition\b', r'\bpassage\b', r'\btransfert\b', r'\btransmission\b', r'\bdiffusion\b',
            r'\bpropagation\b', r'\bexpansion\b', r'\bextension\b', r'\bélargissement\b', r'\bamplification\b',
            r'\baugmentation\b', r'\baccentuation\b', r'\bintensification\b', r'\brenforcément\b', r'\bconsolidation\b',
            r'\bstabilisation\b', r'\béquilibre\b', r'\bharmonie\b', r'\bcohérence\b', r'\bcohésion\b',
            r'\bunité\b', r'\btotalité\b', r'\bglobalité\b', r'\bensemble\b', r'\bcollectif\b',
            r'\bcommunauté\b', r'\bsociété\b', r'\bculture\b', r'\bcivilisation\b', r'\bhumanité\b'
        ]
        
        # Liste de termes académiques en anglais
        english_academic_terms = [
            r'\banalysis\b', r'\bstudy\b', r'\bresearch\b', r'\btheory\b', r'\bconcept\b',
            r'\bparadigm\b', r'\bproblem\b', r'\bhypothesis\b', r'\bmethodology\b', r'\bapproach\b',
            r'\bperspective\b', r'\bcontext\b', r'\bframework\b', r'\bstructure\b', r'\bsystem\b',
            r'\bprocess\b', r'\bmechanism\b', r'\bphenomenon\b', r'\bdynamics\b', r'\bfactor\b',
            r'\bvariable\b', r'\bparticularity\b', r'\bspecificity\b', r'\bcharacteristic\b', r'\belement\b',
            r'\bcomponent\b', r'\bdimension\b', r'\baspect\b', r'\blevel\b', r'\bcriterion\b',
            r'\bindicator\b', r'\bparameter\b', r'\breference\b', r'\bsource\b', r'\bdata\b',
            r'\binformation\b', r'\bknowledge\b', r'\bexpertise\b', r'\bcompetence\b', r'\bcapacity\b',
            r'\bpotential\b', r'\bresource\b', r'\bmeans\b', r'\btools\b', r'\bmethod\b',
            r'\btechnique\b', r'\bstrategy\b', r'\bapproach\b', r'\bprocedure\b', r'\bprotocol\b',
            r'\bmodel\b', r'\bschema\b', r'\bfigure\b', r'\btable\b', r'\bgraph\b', r'\bdiagram\b',
            r'\billustration\b', r'\bexample\b', r'\bcase\b', r'\bsituation\b', r'\bcontext\b',
            r'\bcircumstance\b', r'\bcondition\b', r'\bmodality\b', r'\bconstraint\b', r'\blimit\b',
            r'\brestriction\b', r'\bobstacle\b', r'\bdifficulty\b', r'\bproblem\b', r'\bquestion\b',
            r'\bquery\b', r'\breflection\b', r'\bthought\b', r'\bidea\b', r'\bnotion\b', r'\bconception\b',
            r'\brepresentation\b', r'\bperception\b', r'\binterpretation\b', r'\bunderstanding\b',
            r'\bsignificance\b', r'\bmeaning\b', r'\bvalue\b', r'\bimportance\b', r'\brelevance\b',
            r'\busefulness\b', r'\befficiency\b', r'\bperformance\b', r'\bquality\b', r'\bquantity\b',
            r'\bintensity\b', r'\bfrequency\b', r'\bduration\b', r'\bperiod\b', r'\bepoch\b', r'\bera\b',
            r'\bphase\b', r'\bstage\b', r'\bcycle\b', r'\bevolution\b', r'\bdevelopment\b', r'\bprogression\b',
            r'\btransformation\b', r'\bmodification\b', r'\bchange\b', r'\bvariation\b', r'\balteration\b',
            r'\bmutation\b', r'\btransition\b', r'\bpassage\b', r'\btransfer\b', r'\btransmission\b',
            r'\bdiffusion\b', r'\bpropagation\b', r'\bexpansion\b', r'\bextension\b', r'\benlargement\b',
            r'\bamplification\b', r'\bincrease\b', r'\baccentuation\b', r'\bintensification\b',
            r'\breinforcement\b', r'\bconsolidation\b', r'\bstabilization\b', r'\bequilibrium\b',
            r'\bharmony\b', r'\bcoherence\b', r'\bcohesion\b', r'\bunity\b', r'\btotality\b',
            r'\bglobality\b', r'\bensemble\b', r'\bcollective\b', r'\bcommunity\b', r'\bsociety\b',
            r'\bculture\b', r'\bcivilization\b', r'\bhumanity\b'
        ]
        
        # Sélection de la liste de termes académiques en fonction de la langue
        academic_terms = french_academic_terms if self.lang == 'french' else english_academic_terms
        
        # Comptage des termes académiques
        count = 0
        for term in academic_terms:
            count += len(re.findall(term, text, re.IGNORECASE))
        
        return count
    
    def calculate_density_score(self, text):
        """
        Calcule le score de densité qualitative d'un texte par rapport au paragraphe de référence.
        
        Args:
            text: Texte à analyser
        
        Returns:
            float: Score de densité qualitative (0-100)
        """
        if not text or not self.reference_metrics:
            return 0
        
        # Calcul des métriques pour le texte
        metrics = self._calculate_metrics(text)
        
        # Calcul des scores relatifs pour chaque métrique
        scores = {}
        
        # Score pour la longueur moyenne des phrases
        sentence_length_ratio = metrics['avg_sentence_length'] / self.reference_metrics['avg_sentence_length']
        scores['sentence_length'] = min(1.0, sentence_length_ratio) * 15  # 15% du score total
        
        # Score pour la longueur moyenne des mots
        word_length_ratio = metrics['avg_word_length'] / self.reference_metrics['avg_word_length']
        scores['word_length'] = min(1.0, word_length_ratio) * 15  # 15% du score total
        
        # Score pour la diversité lexicale
        diversity_ratio = metrics['lexical_diversity'] / self.reference_metrics['lexical_diversity']
        scores['lexical_diversity'] = min(1.0, diversity_ratio) * 25  # 25% du score total
        
        # Score pour la densité de connecteurs
        connector_ratio = metrics['connector_density'] / self.reference_metrics['connector_density']
        scores['connector_density'] = min(1.0, connector_ratio) * 20  # 20% du score total
        
        # Score pour la densité de termes académiques
        academic_ratio = metrics['academic_density'] / self.reference_metrics['academic_density']
        scores['academic_density'] = min(1.0, academic_ratio) * 25  # 25% du score total
        
        # Score total
        total_score = sum(scores.values())
        
        return total_score
    
    def get_density_category(self, score):
        """
        Retourne la catégorie de densité qualitative en fonction du score.
        
        Args:
            score: Score de densité qualitative (0-100)
        
        Returns:
            str: Catégorie de densité qualitative
        """
        if score >= 80:
            return "Très haute densité"
        elif score >= 60:
            return "Haute densité"
        elif score >= 40:
            return "Densité moyenne"
        elif score >= 20:
            return "Faible densité"
        else:
            return "Très faible densité"
    
    def get_density_color(self, score):
        """
        Retourne la couleur correspondant à la densité qualitative en fonction du score.
        
        Args:
            score: Score de densité qualitative (0-100)
        
        Returns:
            str: Code couleur hexadécimal
        """
        if score >= 80:
            return "#1E8449"  # Vert foncé
        elif score >= 60:
            return "#58D68D"  # Vert clair
        elif score >= 40:
            return "#F4D03F"  # Jaune
        elif score >= 20:
            return "#F5B041"  # Orange
        else:
            return "#EC7063"  # Rouge

def render_density_settings(project_context, project_id):
    """
    Affiche les paramètres d'analyse de densité qualitative.
    
    Args:
        project_context: Instance de ProjectContext
        project_id: ID du projet
    """
    st.subheader("Paramètres d'analyse de densité qualitative")
    
    # Récupération du paragraphe de référence existant
    project = project_context.load_project(project_id)
    reference_paragraph = project.get("density_reference_paragraph", "")
    
    # Champ pour le paragraphe de référence
    st.write("Entrez un paragraphe de référence considéré comme ayant une haute densité qualitative :")
    new_reference = st.text_area("Paragraphe de référence", reference_paragraph, height=200)
    
    # Sélection de la langue
    lang = st.selectbox("Langue du texte", ["french", "english"], index=0)
    
    # Bouton pour enregistrer les paramètres
    if st.button("Enregistrer les paramètres de densité"):
        if new_reference:
            # Mise à jour du paragraphe de référence dans le projet
            project["density_reference_paragraph"] = new_reference
            project["density_reference_lang"] = lang
            
            # Sauvegarde du projet
            project_context.save_project(project)
            
            st.success("Paramètres d'analyse de densité qualitative enregistrés avec succès !")
        else:
            st.warning("Veuillez entrer un paragraphe de référence.")

def analyze_text_density(text, project_context, project_id):
    """
    Analyse la densité qualitative d'un texte par rapport au paragraphe de référence.
    
    Args:
        text: Texte à analyser
        project_context: Instance de ProjectContext
        project_id: ID du projet
    
    Returns:
        tuple: (score, catégorie, couleur)
    """
    # Récupération du paragraphe de référence
    project = project_context.load_project(project_id)
    reference_paragraph = project.get("density_reference_paragraph", "")
    lang = project.get("density_reference_lang", "french")
    
    if not reference_paragraph:
        return 0, "Pas de référence", "#CCCCCC"
    
    # Création de l'analyseur de densité
    analyzer = DensityAnalyzer(reference_paragraph, lang)
    
    # Calcul du score de densité
    score = analyzer.calculate_density_score(text)
    
    # Détermination de la catégorie et de la couleur
    category = analyzer.get_density_category(score)
    color = analyzer.get_density_color(score)
    
    return score, category, color

def render_density_analysis(text, project_context, project_id):
    """
    Affiche l'analyse de densité qualitative d'un texte.
    
    Args:
        text: Texte à analyser
        project_context: Instance de ProjectContext
        project_id: ID du projet
    """
    # Analyse de la densité qualitative
    score, category, color = analyze_text_density(text, project_context, project_id)
    
    # Affichage du résultat
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: {color}; color: white;">
        <h4 style="margin: 0;">Densité qualitative : {category}</h4>
        <p style="margin: 5px 0 0 0;">Score : {score:.1f}/100</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupération du paragraphe de référence
    project = project_context.load_project(project_id)
    reference_paragraph = project.get("density_reference_paragraph", "")
    
    if reference_paragraph:
        with st.expander("Voir le paragraphe de référence"):
            st.write(reference_paragraph)
    else:
        st.info("Aucun paragraphe de référence n'a été défini. Veuillez en définir un dans les paramètres d'analyse de densité qualitative.")

def integrate_density_analysis_in_preview(document_preview_path):
    """
    Intègre l'analyse de densité qualitative dans le module de prévisualisation.
    
    Args:
        document_preview_path: Chemin vers le fichier document_preview.py
    """
    import os
    
    # Vérification que le fichier existe
    if not os.path.exists(document_preview_path):
        return False, "Le fichier document_preview.py n'existe pas."
    
    # Lecture du contenu actuel
    with open(document_preview_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Importation du module d'analyse de densité
    import_statement = """
from modules.density_analyzer import analyze_text_density
"""
    
    # Vérification si l'importation est déjà présente
    if "from modules.density_analyzer import" not in content:
        # Trouver la section d'importation
        import_section_end = content.find("def render_document_preview")
        if import_section_end == -1:
            return False, "Structure du fichier document_preview.py non reconnue."
        
        # Insérer l'importation
        content = content[:import_section_end] + import_statement + content[import_section_end:]
    
    # Code pour l'analyse de densité
    density_code = """
            # Analyse de la densité qualitative
            score, category, color = analyze_text_density(content, project_context, project_id)
            
            # Affichage du résultat
            st.markdown(f'''
            <div style="padding: 5px; border-radius: 3px; background-color: {color}; color: white; display: inline-block; margin-bottom: 10px;">
                <span style="font-weight: bold;">Densité : {category}</span> ({score:.1f}/100)
            </div>
            ''', unsafe_allow_html=True)
"""
    
    # Vérification si le code d'analyse de densité est déjà présent
    if "Analyse de la densité qualitative" not in content:
        # Trouver l'endroit où insérer le code
        insert_point = content.find("st.markdown(content)")
        if insert_point == -1:
            return False, "Structure du fichier document_preview.py non reconnue."
        
        # Insérer le code
        content = content[:insert_point] + density_code + content[insert_point:]
    
    # Écriture du contenu modifié
    with open(document_preview_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, "Intégration de l'analyse de densité qualitative dans la prévisualisation réussie."

def integrate_density_analysis_in_timeline(document_timeline_path):
    """
    Intègre l'analyse de densité qualitative dans le module de timeline.
    
    Args:
        document_timeline_path: Chemin vers le fichier document_timeline_with_stats.py
    """
    import os
    
    # Vérification que le fichier existe
    if not os.path.exists(document_timeline_path):
        return False, "Le fichier document_timeline_with_stats.py n'existe pas."
    
    # Lecture du contenu actuel
    with open(document_timeline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Importation du module d'analyse de densité
    import_statement = """
from modules.density_analyzer import analyze_text_density
"""
    
    # Vérification si l'importation est déjà présente
    if "from modules.density_analyzer import" not in content:
        # Trouver la section d'importation
        import_section_end = content.find("def render_document_timeline")
        if import_section_end == -1:
            return False, "Structure du fichier document_timeline_with_stats.py non reconnue."
        
        # Insérer l'importation
        content = content[:import_section_end] + import_statement + content[import_section_end:]
    
    # Code pour l'analyse de densité dans la timeline
    density_code = """
        # Calcul des scores de densité qualitative pour chaque version
        density_scores = []
        for version in versions:
            version_data = version.get("data", {})
            sections = version_data.get("sections", [])
            
            # Concaténation du contenu de toutes les sections
            full_content = ""
            for section in sections:
                full_content += section.get("content", "") + "\\n\\n"
            
            # Analyse de la densité qualitative
            score, category, color = analyze_text_density(full_content, project_context, project_id)
            
            density_scores.append({
                "timestamp": version.get("timestamp", ""),
                "score": score,
                "category": category,
                "color": color
            })
        
        # Graphique d'évolution de la densité qualitative
        if len(density_scores) > 1:
            st.subheader("Évolution de la densité qualitative")
            
            # Préparation des données pour le graphique
            timestamps = []
            scores = []
            colors = []
            
            for stat in reversed(density_scores):
                try:
                    date_obj = datetime.datetime.fromisoformat(stat["timestamp"])
                    formatted_date = date_obj.strftime("%d/%m %H:%M")
                except:
                    formatted_date = stat["timestamp"][:10]
                
                timestamps.append(formatted_date)
                scores.append(stat["score"])
                colors.append(stat["color"])
            
            # Création du graphique
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # Barres pour les scores de densité
            bars = ax.bar(timestamps, scores, color=colors)
            
            # Ajout des valeurs au-dessus des barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}',
                        ha='center', va='bottom', rotation=0)
            
            # Personnalisation du graphique
            ax.set_xlabel('Versions')
            ax.set_ylabel('Score de densité qualitative')
            ax.set_ylim(0, 100)
            ax.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # Rotation des labels de l'axe x pour une meilleure lisibilité
            plt.xticks(rotation=45)
            
            # Ajustement automatique de la mise en page
            fig.tight_layout()
            
            # Affichage du graphique
            st.pyplot(fig)
"""
    
    # Vérification si le code d'analyse de densité est déjà présent
    if "Évolution de la densité qualitative" not in content:
        # Trouver l'endroit où insérer le code
        insert_point = content.find("# Graphique d'évolution du nombre de caractères")
        if insert_point == -1:
            return False, "Structure du fichier document_timeline_with_stats.py non reconnue."
        
        # Insérer le code
        content = content[:insert_point] + density_code + "\n        " + content[insert_point:]
    
    # Code pour l'affichage de la densité dans les éléments de la timeline
    timeline_density_code = """
            # Analyse de la densité qualitative
            full_content = ""
            for section in sections:
                full_content += section.get("content", "") + "\\n\\n"
            
            score, category, color = analyze_text_density(full_content, project_context, project_id)
            
            # Affichage de la densité qualitative
            st.markdown(f'''
            <div style="padding: 5px; border-radius: 3px; background-color: {color}; color: white; display: inline-block; margin-bottom: 10px;">
                <span style="font-weight: bold;">Densité : {category}</span> ({score:.1f}/100)
            </div>
            ''', unsafe_allow_html=True)
"""
    
    # Vérification si le code d'affichage de la densité est déjà présent
    if "Analyse de la densité qualitative" not in content:
        # Trouver l'endroit où insérer le code
        insert_point = content.find("# Titre du document", content.find("# Affichage de la version sélectionnée"))
        if insert_point == -1:
            return False, "Structure du fichier document_timeline_with_stats.py non reconnue."
        
        # Insérer le code
        content = content[:insert_point] + timeline_density_code + "\n        " + content[insert_point:]
    
    # Écriture du contenu modifié
    with open(document_timeline_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, "Intégration de l'analyse de densité qualitative dans la timeline réussie."

def integrate_density_analysis_in_app(app_py_path):
    """
    Intègre l'analyse de densité qualitative dans l'application principale.
    
    Args:
        app_py_path: Chemin vers le fichier app.py
    """
    import os
    
    # Vérification que le fichier existe
    if not os.path.exists(app_py_path):
        return False, "Le fichier app.py n'existe pas."
    
    # Lecture du contenu actuel
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Code pour l'ajout d'une page de paramètres de densité
    density_page_code = """
    # Page de paramètres d'analyse de densité qualitative
    elif st.session_state.get("page") == "density_settings":
        project_id = st.session_state.current_project_id
        st.title("Paramètres d'analyse de densité qualitative")
        
        from modules.density_analyzer import render_density_settings
        render_density_settings(project_context, project_id)
        
        # Bouton pour retourner à la page précédente
        if st.button("Retour"):
            st.session_state.page = st.session_state.get("previous_page", "project_overview")
            st.rerun()
"""
    
    # Vérification si le code de la page de densité est déjà présent
    if "Page de paramètres d'analyse de densité qualitative" not in content:
        # Trouver la section des pages
        pages_section = content.find("if st.session_state.get(\"page\")")
        if pages_section == -1:
            return False, "Structure des pages non reconnue."
        
        # Trouver la fin de la section des pages
        pages_section_end = content.find("if __name__ ==", pages_section)
        if pages_section_end == -1:
            pages_section_end = len(content)
        
        # Insérer le code de la page
        content = content[:pages_section_end] + density_page_code + content[pages_section_end:]
    
    # Code pour l'ajout d'un bouton dans la barre latérale
    sidebar_button_code = """
        if st.sidebar.button("📊 Paramètres de densité"):
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "density_settings"
            st.rerun()
"""
    
    # Vérification si le code du bouton est déjà présent
    if "📊 Paramètres de densité" not in content:
        # Trouver la section de la barre latérale
        sidebar_section = content.find("st.sidebar.subheader(\"Visualisation du document\")")
        if sidebar_section == -1:
            return False, "Structure de la barre latérale non reconnue."
        
        # Trouver la fin de la section de la barre latérale
        sidebar_section_end = content.find("# Page principale", sidebar_section)
        if sidebar_section_end == -1:
            sidebar_section_end = content.find("if st.session_state.get(\"page\")", sidebar_section)
        
        if sidebar_section_end == -1:
            return False, "Structure de la barre latérale non reconnue."
        
        # Insérer le code du bouton
        content = content[:sidebar_section_end] + sidebar_button_code + content[sidebar_section_end:]
    
    # Écriture du contenu modifié
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, "Intégration de l'analyse de densité qualitative dans l'application principale réussie."

def integrate_density_analysis_in_all_modules(base_path):
    """
    Intègre l'analyse de densité qualitative dans tous les modules.
    
    Args:
        base_path: Chemin de base du projet
    """
    import os
    
    # Chemins des fichiers
    app_py_path = os.path.join(base_path, "app.py")
    document_preview_path = os.path.join(base_path, "modules", "document_preview.py")
    document_timeline_path = os.path.join(base_path, "modules", "document_timeline_with_stats.py")
    
    # Intégration dans l'application principale
    app_success, app_message = integrate_density_analysis_in_app(app_py_path)
    
    # Intégration dans les modules
    preview_success, preview_message = integrate_density_analysis_in_preview(document_preview_path)
    timeline_success, timeline_message = integrate_density_analysis_in_timeline(document_timeline_path)
    
    # Résultats
    results = {
        "app.py": {"success": app_success, "message": app_message},
        "document_preview.py": {"success": preview_success, "message": preview_message},
        "document_timeline_with_stats.py": {"success": timeline_success, "message": timeline_message}
    }
    
    return results
