#!/usr/bin/env python3
"""
Interface web simple pour visualiser les résultats d'analyse des vidéos
"""

from flask import Flask, render_template, jsonify, send_file, request
import json
import os
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebInterface:
    def __init__(self, results_file="analysis_results.json", summary_file="summary.json"):
        self.results_file = results_file
        self.summary_file = summary_file
        self.data = self.load_data()
    
    def load_data(self):
        """Charge les données d'analyse"""
        try:
            if os.path.exists(self.summary_file):
                with open(self.summary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    # Créer un résumé basique
                    return {
                        "statistics": {
                            "total_videos": len(results),
                            "videos_with_detections": sum(1 for r in results if r['detection_count'] > 0),
                            "total_detections": sum(r['detection_count'] for r in results),
                            "detection_rate": 0
                        },
                        "animal_counts": {},
                        "top_videos": [],
                        "all_results": results
                    }
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            return None
    
    def get_video_info(self, filename):
        """Récupère les informations d'une vidéo spécifique"""
        if not self.data or 'all_results' not in self.data:
            return None
        
        for result in self.data['all_results']:
            if result['filename'] == filename:
                return result
        return None

# Instance globale
web_interface = WebInterface()

@app.route('/')
def index():
    """Page principale"""
    if not web_interface.data:
        return render_template('error.html', message="Aucune donnée d'analyse trouvée")
    
    return render_template('index.html', data=web_interface.data)

@app.route('/api/summary')
def api_summary():
    """API pour récupérer le résumé"""
    if not web_interface.data:
        return jsonify({"error": "Aucune donnée disponible"}), 404
    
    return jsonify(web_interface.data)

@app.route('/api/video/<filename>')
def api_video_info(filename):
    """API pour récupérer les infos d'une vidéo"""
    video_info = web_interface.get_video_info(filename)
    if not video_info:
        return jsonify({"error": "Vidéo non trouvée"}), 404
    
    return jsonify(video_info)

@app.route('/video/<filename>')
def serve_video(filename):
    """Sert une vidéo spécifique"""
    # Chercher le fichier vidéo dans le dossier des vidéos
    video_paths = [
        f"videos/{filename}",
        f"data/{filename}",
        filename
    ]
    
    for path in video_paths:
        if os.path.exists(path):
            return send_file(path)
    
    return "Vidéo non trouvée", 404

@app.route('/api/search')
def api_search():
    """API de recherche dans les résultats"""
    query = request.args.get('q', '').lower()
    animal_filter = request.args.get('animal', '')
    
    if not web_interface.data or 'all_results' not in web_interface.data:
        return jsonify({"error": "Aucune donnée disponible"}), 404
    
    results = web_interface.data['all_results']
    
    # Filtrer par nom de fichier
    if query:
        results = [r for r in results if query in r['filename'].lower()]
    
    # Filtrer par type d'animal
    if animal_filter:
        filtered_results = []
        for result in results:
            for detection in result['detections']:
                if detection['class'] == animal_filter:
                    filtered_results.append(result)
                    break
        results = filtered_results
    
    return jsonify(results)

def create_templates():
    """Crée les templates HTML"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Template principal
    index_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyse Piège Photo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .content {
            padding: 30px;
        }
        .search-bar {
            margin-bottom: 20px;
        }
        .search-bar input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .video-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            transition: transform 0.2s;
        }
        .video-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .video-header {
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }
        .video-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .video-stats {
            font-size: 0.9em;
            color: #666;
        }
        .detections {
            padding: 15px;
        }
        .detection-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .detection-item:last-child {
            border-bottom: none;
        }
        .animal-type {
            font-weight: bold;
            color: #667eea;
        }
        .confidence {
            font-size: 0.8em;
            color: #666;
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .filter-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .filter-btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦌 Analyse Piège Photo</h1>
            <p>Surveillance automatique de la faune sauvage</p>
        </div>
        
        {% if data %}
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.total_videos }}</div>
                <div>Vidéos analysées</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.videos_with_detections }}</div>
                <div>Vidéos avec activité</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.total_detections }}</div>
                <div>Détections totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.detection_rate }}%</div>
                <div>Taux de détection</div>
            </div>
        </div>
        
        <div class="content">
            <div class="search-bar">
                <input type="text" id="searchInput" placeholder="Rechercher une vidéo...">
            </div>
            
            <div class="filter-bar">
                <div class="filter-btn active" data-animal="">Tous</div>
                {% for animal, count in data.animal_counts.items() %}
                <div class="filter-btn" data-animal="{{ animal }}">{{ animal }} ({{ count }})</div>
                {% endfor %}
            </div>
            
            <div class="video-grid" id="videoGrid">
                {% for video in data.all_results %}
                {% if video.detection_count > 0 %}
                <div class="video-card" data-filename="{{ video.filename }}">
                    <div class="video-header">
                        <div class="video-name">{{ video.filename }}</div>
                        <div class="video-stats">
                            {{ video.detection_count }} détection(s) • {{ "%.1f"|format(video.duration) }}s
                        </div>
                    </div>
                    <div class="detections">
                        {% for detection in video.detections[:5] %}
                        <div class="detection-item">
                            <span class="animal-type">{{ detection.class }}</span>
                            <span class="confidence">{{ "%.0f"|format(detection.confidence * 100) }}%</span>
                        </div>
                        {% endfor %}
                        {% if video.detections|length > 5 %}
                        <div class="detection-item">
                            <span style="color: #666;">... et {{ video.detections|length - 5 }} autres</span>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
                {% endfor %}
            </div>
            
            {% if data.all_results|selectattr('detection_count', '>', 0)|list|length == 0 %}
            <div class="no-data">
                <h3>Aucune activité détectée</h3>
                <p>Les vidéos analysées ne contiennent pas d'animaux détectés.</p>
            </div>
            {% endif %}
        </div>
        {% else %}
        <div class="no-data">
            <h3>Aucune donnée disponible</h3>
            <p>Veuillez d'abord analyser vos vidéos avec le script d'analyse.</p>
        </div>
        {% endif %}
    </div>
    
    <script>
        // Recherche en temps réel
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.video-card');
            
            cards.forEach(card => {
                const filename = card.dataset.filename.toLowerCase();
                if (filename.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
        // Filtres par animal
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                // Mettre à jour les boutons actifs
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const animal = this.dataset.animal;
                const cards = document.querySelectorAll('.video-card');
                
                if (animal === '') {
                    // Afficher tous
                    cards.forEach(card => card.style.display = 'block');
                } else {
                    // Filtrer par animal (simulation - en réalité il faudrait une API)
                    cards.forEach(card => {
                        const detections = card.querySelectorAll('.animal-type');
                        let hasAnimal = false;
                        detections.forEach(det => {
                            if (det.textContent === animal) {
                                hasAnimal = true;
                            }
                        });
                        card.style.display = hasAnimal ? 'block' : 'none';
                    });
                }
            });
        });
    </script>
</body>
</html>
    """
    
    with open(templates_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Template d'erreur
    error_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Erreur - Analyse Piège Photo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .error-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        .error-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        .error-message {
            color: #666;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h2>Erreur</h2>
        <div class="error-message">{{ message }}</div>
    </div>
</body>
</html>
    """
    
    with open(templates_dir / "error.html", 'w', encoding='utf-8') as f:
        f.write(error_html)

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interface web pour l'analyse des vidéos")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port du serveur")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse du serveur")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    
    args = parser.parse_args()
    
    # Créer les templates
    create_templates()
    
    print(f"🌐 Interface web démarrée sur http://{args.host}:{args.port}")
    print("📁 Assurez-vous que vos vidéos sont dans le dossier 'videos/' ou 'data/'")
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()