#!/usr/bin/env python3
"""
Interface web simple pour visualiser les résultats d'analyse des vidéos
"""

from flask import Flask, render_template, jsonify, send_file, request
import json
import os
from pathlib import Path
import logging
from video_streamer import VideoStreamer

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

# Initialiser le streamer vidéo
video_streamer = VideoStreamer(app)

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
            return send_file(path, mimetype='video/mp4')
    
    return "Vidéo non trouvée", 404

@app.route('/video_player/<filename>')
def video_player(filename):
    """Page de lecteur vidéo avec détections"""
    video_info = web_interface.get_video_info(filename)
    if not video_info:
        return render_template('error.html', message="Vidéo non trouvée")
    
    return render_template('video_player.html', 
                         video_info=video_info, 
                         filename=filename)

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
    
    # Template principal amélioré
    index_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦌 Piège Photo Jura</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 10px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-size: 14px;
            line-height: 1.4;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 1.8em;
        }
        .header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-2px);
        }
        .stat-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 0.8em;
            color: #666;
            margin-top: 2px;
        }
        .content {
            padding: 15px;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        .search-bar {
            flex: 1;
            min-width: 200px;
        }
        .search-bar input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .filter-bar {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        .filter-btn {
            padding: 6px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 12px;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .timeline-section {
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }
        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .timeline-title {
            font-weight: bold;
            color: #333;
        }
        .timeline-controls {
            display: flex;
            gap: 5px;
        }
        .timeline-btn {
            padding: 4px 8px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }
        .timeline-btn:hover {
            background: #667eea;
            color: white;
        }
        .timeline-chart {
            height: 60px;
            background: white;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }
        .timeline-bar {
            height: 100%;
            display: flex;
            align-items: end;
        }
        .timeline-hour {
            flex: 1;
            border-right: 1px solid #eee;
            position: relative;
            min-height: 20px;
        }
        .timeline-hour:last-child {
            border-right: none;
        }
        .timeline-detection {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: #667eea;
            border-radius: 2px 2px 0 0;
            opacity: 0.7;
        }
        .timeline-hour-label {
            position: absolute;
            top: -20px;
            left: 0;
            font-size: 10px;
            color: #666;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
        }
        .video-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            transition: all 0.2s;
        }
        .video-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .video-header {
            padding: 12px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }
        .video-name {
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 13px;
        }
        .video-stats {
            font-size: 11px;
            color: #666;
        }
        .video-thumbnail {
            margin: 8px 0;
            border-radius: 4px;
            overflow: hidden;
        }
        .video-thumbnail img {
            width: 100%;
            height: 80px;
            object-fit: cover;
            transition: transform 0.2s;
        }
        .video-thumbnail:hover img {
            transform: scale(1.05);
        }
        .detections {
            padding: 12px;
        }
        .detection-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid #eee;
            font-size: 12px;
        }
        .detection-item:last-child {
            border-bottom: none;
        }
        .animal-type {
            font-weight: bold;
            color: #667eea;
        }
        .confidence {
            font-size: 11px;
            color: #666;
        }
        .time-badge {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            margin-left: 5px;
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
        .video-actions {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        .watch-btn {
            display: inline-block;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9em;
            transition: background 0.2s;
        }
        .watch-btn:hover {
            background: #5a6fd8;
            color: white;
            text-decoration: none;
        }
        .video-thumbnail {
            margin: 10px 0;
            border-radius: 4px;
            overflow: hidden;
        }
        .video-thumbnail img {
            transition: transform 0.2s;
        }
        .video-thumbnail:hover img {
            transform: scale(1.05);
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
                <div class="stat-label">Vidéos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.videos_with_detections }}</div>
                <div class="stat-label">Avec activité</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.total_detections }}</div>
                <div class="stat-label">Détections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ data.statistics.detection_rate }}%</div>
                <div class="stat-label">Taux</div>
            </div>
        </div>
        
        <div class="content">
            <div class="controls">
                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="🔍 Rechercher une vidéo...">
                </div>
                
                <div class="filter-bar">
                    <div class="filter-btn active" data-animal="">Tous</div>
                    {% for animal, count in data.animal_counts.items() %}
                    <div class="filter-btn" data-animal="{{ animal }}">{{ animal }} ({{ count }})</div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="timeline-section">
                <div class="timeline-header">
                    <div class="timeline-title">📅 Activité dans le temps</div>
                    <div class="timeline-controls">
                        <button class="timeline-btn" onclick="setTimelineView('day')">Jour</button>
                        <button class="timeline-btn" onclick="setTimelineView('week')">Semaine</button>
                        <button class="timeline-btn active" onclick="setTimelineView('hour')">Heure</button>
                    </div>
                </div>
                <div class="timeline-chart" id="timelineChart">
                    <div class="timeline-bar" id="timelineBar">
                        <!-- Timeline générée par JavaScript -->
                    </div>
                </div>
            </div>
            
            <div class="video-grid" id="videoGrid">
                {% for video in data.all_results %}
                {% if video.detection_count > 0 %}
                <div class="video-card" data-filename="{{ video.filename }}" data-timestamp="{{ video.analyzed_at }}">
                    <div class="video-header">
                        <div class="video-name">{{ video.filename }}</div>
                        <div class="video-stats">
                            {{ video.detection_count }} détection(s) • {{ "%.1f"|format(video.duration) }}s
                        </div>
                        <div class="video-thumbnail">
                            <img src="/thumbnail/{{ video.filename }}" alt="Miniature">
                        </div>
                    </div>
                    <div class="detections">
                        {% for detection in video.detections[:4] %}
                        <div class="detection-item">
                            <span class="animal-type">{{ detection.class }}</span>
                            <span class="time-badge">{{ "%.1f"|format(detection.frame_time) }}s</span>
                            <span class="confidence">{{ "%.0f"|format(detection.confidence * 100) }}%</span>
                        </div>
                        {% endfor %}
                        <div class="video-actions">
                            <a href="/video_player/{{ video.filename }}" class="watch-btn">📹 Regarder</a>
                        </div>
                        {% if video.detections|length > 4 %}
                        <div class="detection-item">
                            <span style="color: #666; font-size: 11px;">... et {{ video.detections|length - 4 }} autres</span>
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
        // Données globales
        const videoData = {{ data.all_results | tojson }};
        let currentTimelineView = 'hour';
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            generateTimeline();
            setupEventListeners();
        });
        
        // Recherche en temps réel
        function setupEventListeners() {
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
                        // Filtrer par animal
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
        }
        
        // Génération de la timeline
        function generateTimeline() {
            const timelineBar = document.getElementById('timelineBar');
            timelineBar.innerHTML = '';
            
            // Grouper les détections par période
            const timeGroups = groupDetectionsByTime();
            
            // Créer les barres de timeline
            Object.keys(timeGroups).forEach(timeKey => {
                const hourDiv = document.createElement('div');
                hourDiv.className = 'timeline-hour';
                hourDiv.title = `${timeKey}: ${timeGroups[timeKey]} détections`;
                
                // Ajouter le label
                const label = document.createElement('div');
                label.className = 'timeline-hour-label';
                label.textContent = timeKey;
                hourDiv.appendChild(label);
                
                // Ajouter la barre de détection
                if (timeGroups[timeKey] > 0) {
                    const detectionBar = document.createElement('div');
                    detectionBar.className = 'timeline-detection';
                    const height = Math.min(100, (timeGroups[timeKey] / Math.max(...Object.values(timeGroups))) * 100);
                    detectionBar.style.height = height + '%';
                    hourDiv.appendChild(detectionBar);
                }
                
                timelineBar.appendChild(hourDiv);
            });
        }
        
        // Grouper les détections par période
        function groupDetectionsByTime() {
            const groups = {};
            
            videoData.forEach(video => {
                if (video.detection_count > 0) {
                    const date = new Date(video.analyzed_at);
                    let timeKey;
                    
                    switch(currentTimelineView) {
                        case 'hour':
                            timeKey = date.getHours() + 'h';
                            break;
                        case 'day':
                            timeKey = date.getDate() + '/' + (date.getMonth() + 1);
                            break;
                        case 'week':
                            const weekStart = new Date(date);
                            weekStart.setDate(date.getDate() - date.getDay());
                            timeKey = 'S' + Math.ceil(weekStart.getDate() / 7);
                            break;
                    }
                    
                    if (!groups[timeKey]) {
                        groups[timeKey] = 0;
                    }
                    groups[timeKey] += video.detection_count;
                }
            });
            
            return groups;
        }
        
        // Changer la vue de la timeline
        function setTimelineView(view) {
            currentTimelineView = view;
            
            // Mettre à jour les boutons actifs
            document.querySelectorAll('.timeline-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Régénérer la timeline
            generateTimeline();
        }
        
        // Animation des cartes au survol
        document.querySelectorAll('.video-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-4px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
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
    
    # Template du lecteur vidéo amélioré
    video_player_html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📹 {{ video_info.filename }} - Piège Photo Jura</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 10px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-size: 14px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 1.4em;
        }
        .back-btn {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            transition: background 0.2s;
        }
        .back-btn:hover {
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
        }
        .video-container {
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            margin: 15px;
        }
        .video-player {
            width: 100%;
            height: auto;
            max-height: 60vh;
            display: block;
        }
        .video-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
        }
        .detection-box {
            position: absolute;
            border: 2px solid #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
            pointer-events: none;
            border-radius: 4px;
        }
        .detection-label {
            position: absolute;
            top: -25px;
            left: 0;
            background: #ff6b6b;
            color: white;
            padding: 2px 8px;
            font-size: 11px;
            border-radius: 4px;
            font-weight: bold;
        }
        .video-info {
            padding: 15px;
        }
        .video-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .video-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        .stat-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        .stat-number {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 0.8em;
            color: #666;
            margin-top: 2px;
        }
        .detections-list {
            margin-top: 20px;
        }
        .detection-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
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
            font-size: 0.9em;
            color: #666;
        }
        .time-marker {
            font-size: 0.8em;
            color: #999;
        }
        .controls {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        .control-btn {
            padding: 10px 20px;
            margin: 0 5px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .control-btn:hover {
            background: #5a6fd8;
        }
        .control-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .timeline {
            margin: 15px 0;
        }
        .timeline-bar {
            width: 100%;
            height: 6px;
            background: #ddd;
            border-radius: 3px;
            position: relative;
            cursor: pointer;
        }
        .timeline-progress {
            height: 100%;
            background: #667eea;
            border-radius: 3px;
            width: 0%;
        }
        .detection-markers {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
        }
        .detection-marker {
            position: absolute;
            top: -2px;
            width: 4px;
            height: 10px;
            background: #ff6b6b;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📹 {{ video_info.filename }}</h1>
            <a href="/" class="back-btn">← Retour à la liste</a>
        </div>
        
        <div class="video-container">
            <video id="videoPlayer" class="video-player" controls preload="metadata">
                <source src="/stream/{{ filename }}" type="video/mp4">
                Votre navigateur ne supporte pas la lecture vidéo.
            </video>
            <div class="video-overlay" id="videoOverlay"></div>
        </div>
        
        <div class="video-info">
            <div class="video-title">{{ video_info.filename }}</div>
            
            <div class="video-stats">
                <div class="stat-item">
                    <div class="stat-number">{{ video_info.detection_count }}</div>
                    <div class="stat-label">Détections</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ "%.1f"|format(video_info.duration) }}s</div>
                    <div class="stat-label">Durée</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ "%.1f"|format(video_info.fps) }}</div>
                    <div class="stat-label">FPS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ video_info.detections|length }}</div>
                    <div class="stat-label">Espèces</div>
                </div>
            </div>
            
            <div class="detections-list">
                <h3 style="margin: 0 0 10px 0; font-size: 1.1em;">🦌 Détections trouvées :</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
                    {% for detection in video_info.detections %}
                    <div class="detection-item" data-time="{{ detection.frame_time }}" style="background: #f8f9fa; padding: 8px; border-radius: 6px; border-left: 3px solid #667eea;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="animal-type" style="font-weight: bold; color: #667eea;">{{ detection.class }}</span>
                                <span class="time-marker" style="font-size: 0.8em; color: #666; margin-left: 5px;">{{ "%.1f"|format(detection.frame_time) }}s</span>
                            </div>
                            <div class="confidence" style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 10px; font-size: 0.8em;">{{ "%.0f"|format(detection.confidence * 100) }}%</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="jumpToDetection(0)">⏮️ Premier</button>
            <button class="control-btn" onclick="jumpToDetection(-1)">⏪ Précédent</button>
            <button class="control-btn" onclick="jumpToDetection(1)">⏩ Suivant</button>
            <button class="control-btn" onclick="jumpToDetection(-2)">⏭️ Dernier</button>
            
            <div class="timeline">
                <div class="timeline-bar" onclick="seekToTime(event)">
                    <div class="timeline-progress" id="timelineProgress"></div>
                    <div class="detection-markers" id="detectionMarkers"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const video = document.getElementById('videoPlayer');
        const overlay = document.getElementById('videoOverlay');
        const timelineProgress = document.getElementById('timelineProgress');
        const detectionMarkers = document.getElementById('detectionMarkers');
        
        // Données des détections
        const detections = {{ video_info.detections | tojson }};
        let currentDetectionIndex = 0;
        
        // Mettre à jour la barre de progression
        video.addEventListener('timeupdate', function() {
            const progress = (video.currentTime / video.duration) * 100;
            timelineProgress.style.width = progress + '%';
            
            // Mettre à jour les détections visibles
            updateDetectionOverlay();
        });
        
        // Créer les marqueurs de détection sur la timeline
        function createDetectionMarkers() {
            detections.forEach((detection, index) => {
                const marker = document.createElement('div');
                marker.className = 'detection-marker';
                marker.style.left = (detection.frame_time / {{ video_info.duration }} * 100) + '%';
                marker.title = `${detection.class} (${Math.round(detection.confidence * 100)}%)`;
                marker.onclick = (e) => {
                    e.stopPropagation();
                    jumpToTime(detection.frame_time);
                };
                detectionMarkers.appendChild(marker);
            });
        }
        
        // Mettre à jour l'overlay des détections
        function updateDetectionOverlay() {
            overlay.innerHTML = '';
            
            detections.forEach(detection => {
                const timeDiff = Math.abs(video.currentTime - detection.frame_time);
                if (timeDiff < 2) { // Afficher les détections dans un rayon de 2 secondes
                    const box = document.createElement('div');
                    box.className = 'detection-box';
                    
                    // Positionner la boîte (simplifié - en réalité il faudrait les coordonnées exactes)
                    const bbox = detection.bbox;
                    box.style.left = (bbox[0] * 100) + '%';
                    box.style.top = (bbox[1] * 100) + '%';
                    box.style.width = ((bbox[2] - bbox[0]) * 100) + '%';
                    box.style.height = ((bbox[3] - bbox[1]) * 100) + '%';
                    
                    const label = document.createElement('div');
                    label.className = 'detection-label';
                    label.textContent = `${detection.class} (${Math.round(detection.confidence * 100)}%)`;
                    box.appendChild(label);
                    
                    overlay.appendChild(box);
                }
            });
        }
        
        // Aller à une détection spécifique
        function jumpToDetection(direction) {
            if (direction === 0) {
                currentDetectionIndex = 0;
            } else if (direction === -2) {
                currentDetectionIndex = detections.length - 1;
            } else {
                currentDetectionIndex += direction;
                if (currentDetectionIndex < 0) currentDetectionIndex = 0;
                if (currentDetectionIndex >= detections.length) currentDetectionIndex = detections.length - 1;
            }
            
            if (detections[currentDetectionIndex]) {
                jumpToTime(detections[currentDetectionIndex].frame_time);
            }
        }
        
        // Aller à un temps spécifique
        function jumpToTime(time) {
            video.currentTime = time;
        }
        
        // Chercher dans la vidéo en cliquant sur la timeline
        function seekToTime(event) {
            const rect = event.currentTarget.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = clickX / rect.width;
            const time = percentage * video.duration;
            video.currentTime = time;
        }
        
        // Initialiser les marqueurs quand la vidéo est chargée
        video.addEventListener('loadedmetadata', createDetectionMarkers);
        
        // Mettre en surbrillance la détection actuelle dans la liste
        video.addEventListener('timeupdate', function() {
            document.querySelectorAll('.detection-item').forEach((item, index) => {
                const detection = detections[index];
                if (detection && Math.abs(video.currentTime - detection.frame_time) < 1) {
                    item.style.background = '#f0f8ff';
                } else {
                    item.style.background = 'transparent';
                }
            });
        });
    </script>
</body>
</html>
    """
    
    with open(templates_dir / "video_player.html", 'w', encoding='utf-8') as f:
        f.write(video_player_html)

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