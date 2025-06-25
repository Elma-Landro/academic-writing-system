
"""
Academic Writing System - Native Web Application
Flask-based application that works directly in Replit environment.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'academic-writing-system-key')

# Import your existing modules
try:
    from core.database_layer import db_manager
    from services.ai_service import ai_service
    from core.config_manager import config_manager
    logger.info("Core modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')

@app.route('/app')
def main_app():
    """Main application interface."""
    return render_template('app.html')

@app.route('/api/projects', methods=['GET', 'POST'])
def handle_projects():
    """Handle project operations."""
    if request.method == 'GET':
        # Return list of projects
        try:
            # For demo, return mock data
            projects = [
                {
                    'id': 1,
                    'title': 'Mon Premier Article',
                    'type': 'Article académique',
                    'status': 'draft_in_progress',
                    'updated_at': '2024-01-15'
                }
            ]
            return jsonify({'projects': projects})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        # Create new project
        data = request.get_json()
        try:
            project = {
                'id': len(session.get('projects', [])) + 1,
                'title': data.get('title'),
                'description': data.get('description'),
                'type': data.get('project_type'),
                'style': data.get('style'),
                'status': 'created',
                'created_at': datetime.now().isoformat()
            }
            
            if 'projects' not in session:
                session['projects'] = []
            session['projects'].append(project)
            
            return jsonify({'project': project, 'message': 'Project created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/storyboard/<int:project_id>', methods=['GET', 'POST'])
def handle_storyboard(project_id):
    """Handle storyboard operations."""
    if request.method == 'GET':
        # Return storyboard for project
        storyboard = {
            'sections': [
                {
                    'id': 1,
                    'title': 'Introduction',
                    'content': 'Introduction générale au sujet...',
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'title': 'Développement',
                    'content': 'Développement des arguments principaux...',
                    'status': 'in_progress'
                }
            ]
        }
        return jsonify(storyboard)
    
    elif request.method == 'POST':
        # Generate or update storyboard
        data = request.get_json()
        try:
            # Here you would use your AI service
            generated_storyboard = {
                'sections': [
                    {
                        'id': 1,
                        'title': 'Introduction',
                        'content': f"Introduction générée pour: {data.get('topic', 'sujet non spécifié')}",
                        'status': 'generated'
                    }
                ]
            }
            return jsonify(generated_storyboard)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/redaction/<int:project_id>', methods=['POST'])
def handle_redaction(project_id):
    """Handle content generation."""
    data = request.get_json()
    try:
        # Simulate AI content generation
        generated_content = f"""
        # {data.get('title', 'Section')}
        
        {data.get('brief', 'Contenu généré automatiquement par l\'IA...')}
        
        ## Développement
        
        Ce paragraphe développe les idées principales de la section.
        Il utilise un style {data.get('style', 'académique')} adapté au contexte.
        
        ## Conclusion de section
        
        Cette section conclut sur les points essentiels abordés.
        """
        
        return jsonify({
            'content': generated_content,
            'word_count': len(generated_content.split()),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/revision/<int:project_id>', methods=['POST'])
def handle_revision(project_id):
    """Handle content revision."""
    data = request.get_json()
    try:
        content = data.get('content', '')
        
        # Simulate revision analysis
        suggestions = [
            {
                'type': 'style',
                'message': 'Considérez renforcer l\'argumentation dans le deuxième paragraphe',
                'position': 150
            },
            {
                'type': 'grammar',
                'message': 'Vérifiez l\'accord du participe passé ligne 3',
                'position': 89
            }
        ]
        
        return jsonify({
            'suggestions': suggestions,
            'score': 85,
            'word_count': len(content.split())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
