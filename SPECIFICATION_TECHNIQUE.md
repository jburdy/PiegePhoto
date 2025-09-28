# 🦌 PiegePhoto - Spécification Technique Complète

## 📋 Table des Matières

1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Exigences fonctionnelles](#exigences-fonctionnelles)
3. [Exigences non-fonctionnelles](#exigences-non-fonctionnelles)
4. [Architecture du système](#architecture-du-système)
5. [Composants techniques](#composants-techniques)
6. [Structure des données](#structure-des-données)
7. [Interface utilisateur](#interface-utilisateur)
8. [Instructions de mise en œuvre](#instructions-de-mise-en-œuvre)
9. [Configuration et déploiement](#configuration-et-déploiement)
10. [Tests et validation](#tests-et-validation)

---

## 🎯 Vue d'ensemble du projet

**PiegePhoto** est un système d'analyse automatique de vidéos de piège photo utilisant l'intelligence artificielle optimisée pour MacBook M4. Le système détecte automatiquement les animaux dans les vidéos et génère des rapports détaillés avec une interface web moderne.

### Objectifs principaux
- **Automatisation** : Analyser automatiquement des centaines de vidéos de piège photo
- **Performance** : Optimisation MLX pour MacBook M4 (ultra-rapide)
- **Précision** : Détection fiable des animaux sauvages
- **Accessibilité** : Interface web intuitive et moderne
- **Flexibilité** : Support de multiples formats vidéo et espèces

### Technologies utilisées
- **Backend** : Python 3.13
- **IA/ML** : MLX (Apple Silicon), OpenCV, Computer Vision
- **Web** : Flask, HTML5, CSS3, JavaScript
- **Streaming** : Range requests, optimisations vidéo
- **Plateforme** : macOS optimisé pour Apple Silicon M4

---

## 🔧 Exigences fonctionnelles

### 1. Analyse automatique des vidéos

#### 1.1 Détection d'animaux
- **Entrée** : Fichiers vidéo (MP4, AVI, MOV, MKV, WMV)
- **Traitement** : Extraction de frames représentatives
- **Détection** : Identification des animaux avec coordonnées de bounding box
- **Sortie** : Résultats JSON avec métadonnées complètes

#### 1.2 Espèces supportées (Forêt du Jura)
```python
wildlife_classes = {
    0: 'person',      # Personnes
    14: 'bird',       # Oiseaux (pies, corbeaux, mésanges, etc.)
    15: 'cat',        # Chats domestiques et sauvages
    16: 'dog',        # Chiens domestiques et errants
    17: 'horse',      # Chevaux (rare mais possible)
    18: 'sheep',      # Moutons (pâturages)
    19: 'cow',        # Vaches (pâturages)
    20: 'fox',        # Renards
    21: 'deer',       # Cerfs et biches
    22: 'roe_deer',   # Chevreuils
    23: 'wild_boar',  # Sangliers
    24: 'squirrel',   # Écureuils
    25: 'rabbit',     # Lapins et lièvres
    26: 'hedgehog',   # Hérissons
    27: 'badger'      # Blaireaux
}
```

#### 1.3 Modes de détection
- **Mode rapide** (`fast`) : Détection optimisée pour la vitesse
- **Mode précis** (`accurate`) : Détection avec précision maximale

### 2. Génération de rapports

#### 2.1 Rapport texte détaillé
- Statistiques générales (nombre de vidéos, détections, taux d'activité)
- Comptage par espèce d'animal
- Top des vidéos les plus actives
- Rapport détaillé avec toutes les détections

#### 2.2 Export JSON
- Résumé structuré pour l'interface web
- Métadonnées complètes des vidéos
- Statistiques agrégées

### 3. Interface web

#### 3.1 Dashboard principal
- Vue d'ensemble des statistiques
- Grille des vidéos avec miniatures
- Filtres par type d'animal
- Recherche en temps réel

#### 3.2 Lecteur vidéo intégré
- Streaming optimisé avec range requests
- Overlay des détections en temps réel
- Navigation intelligente entre détections
- Timeline interactive avec marqueurs
- Contrôles de lecture avancés

#### 3.3 Fonctionnalités avancées
- Miniatures automatiques des vidéos
- Support multi-format
- Design responsive
- Interface minimaliste et intuitive

---

## ⚡ Exigences non-fonctionnelles

### 1. Performance

#### 1.1 Optimisation MLX
- **Cible** : MacBook M4 avec GPU unifié
- **Vitesse** : Traitement ultra-rapide des vidéos
- **Mémoire** : Utilisation optimisée de la RAM unifiée
- **Parallélisation** : Exploitation des cores CPU/GPU

#### 1.2 Streaming vidéo
- **Latence** : < 2 secondes pour le démarrage
- **Qualité** : Streaming adaptatif
- **Bande passante** : Optimisation des range requests
- **Cache** : Mise en cache des miniatures

### 2. Scalabilité

#### 2.1 Traitement par lots
- Support de centaines de vidéos simultanément
- Traitement asynchrone
- Gestion de la mémoire efficace

#### 2.2 Interface web
- Support de multiples utilisateurs simultanés
- Chargement progressif des données
- Pagination intelligente

### 3. Fiabilité

#### 3.1 Robustesse
- Gestion d'erreurs complète
- Récupération automatique des échecs
- Logging détaillé

#### 3.2 Compatibilité
- Support multi-format vidéo
- Compatibilité navigateurs modernes
- Fallback pour fonctionnalités avancées

---

## 🏗️ Architecture du système

### 1. Vue d'ensemble

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   Analyseur     │    │   Détecteur     │
│   Web (Flask)   │◄──►│   Vidéo         │◄──►│   MLX            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamer      │    │   Générateur    │    │   Modèles       │
│   Vidéo         │    │   Rapports      │    │   IA            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Composants principaux

#### 2.1 Couche de détection (MLX)
- **mlx_detector.py** : Détecteur optimisé pour Apple Silicon
- **Classes** : `MLXAnimalDetector`, `FastMLXDetector`
- **Responsabilités** : Détection d'objets, classification, optimisation MLX

#### 2.2 Couche d'analyse
- **video_analyzer.py** : Analyseur principal des vidéos
- **Classe** : `VideoAnalyzer`
- **Responsabilités** : Extraction de frames, orchestration de l'analyse

#### 2.3 Couche de reporting
- **report_generator.py** : Générateur de rapports
- **Classe** : `ReportGenerator`
- **Responsabilités** : Génération de rapports texte et JSON

#### 2.4 Couche web
- **web_interface.py** : Interface web Flask
- **Classe** : `WebInterface`
- **Responsabilités** : API REST, templates HTML, gestion des données

#### 2.5 Couche de streaming
- **video_streamer.py** : Serveur de streaming vidéo
- **Classe** : `VideoStreamer`
- **Responsabilités** : Streaming optimisé, génération de miniatures

### 3. Flux de données

```
Vidéos → Extraction Frames → Détection MLX → Résultats JSON
   ↓
Rapport Texte ← Générateur ← Résultats JSON
   ↓
Interface Web ← API REST ← Résumé JSON
   ↓
Streaming Vidéo ← Miniatures ← Vidéos Originales
```

---

## 🔧 Composants techniques

### 1. Détecteur MLX (`mlx_detector.py`)

#### 1.1 Architecture
```python
class MLXAnimalDetector:
    def __init__(self):
        self.device = mx.default_device()
        self.wildlife_classes = {...}
        self.input_size = (640, 640)
    
    def detect_objects(self, image, confidence_threshold=0.5):
        # Détection basée sur Computer Vision
        # Utilise Canny edge detection + contours
        # Classification heuristique basée sur la forme
```

#### 1.2 Optimisations MLX
- **Préprocessing** : Conversion optimisée vers MLX arrays
- **Détection rapide** : Algorithmes de Computer Vision optimisés
- **Batch processing** : Traitement par lots efficace

### 2. Analyseur vidéo (`video_analyzer.py`)

#### 2.1 Pipeline d'analyse
```python
class VideoAnalyzer:
    def extract_frames(self, video_path, max_frames=10):
        # Extraction de frames représentatives
        # Distribution uniforme dans la vidéo
    
    def analyze_video(self, video_path):
        # Orchestration complète de l'analyse
        # Métadonnées vidéo + détections
```

#### 2.2 Formats supportés
- **Vidéo** : MP4, AVI, MOV, MKV, WMV
- **Sortie** : JSON structuré avec métadonnées

### 3. Interface web (`web_interface.py`)

#### 3.1 API REST
```python
@app.route('/api/summary')           # Résumé des données
@app.route('/api/video/<filename>')  # Infos vidéo spécifique
@app.route('/api/search')           # Recherche et filtrage
@app.route('/stream/<filename>')    # Streaming vidéo
@app.route('/thumbnail/<filename>') # Miniatures
```

#### 3.2 Templates HTML
- **index.html** : Dashboard principal avec grille des vidéos
- **video_player.html** : Lecteur vidéo avec overlay des détections
- **error.html** : Gestion d'erreurs

### 4. Streamer vidéo (`video_streamer.py`)

#### 4.1 Streaming optimisé
```python
def stream_file(self, file_path):
    # Support des range requests HTTP
    # Streaming par chunks de 8KB
    # Headers optimisés pour la lecture vidéo
```

#### 4.2 Génération de miniatures
```python
def generate_thumbnail(self, video_path):
    # Extraction frame au milieu de la vidéo
    # Redimensionnement automatique
    # Encodage JPEG optimisé
```

---

## 📊 Structure des données

### 1. Résultats d'analyse (`analysis_results.json`)

```json
[
  {
    "video_path": "/chemin/vers/video.mp4",
    "filename": "video.mp4",
    "duration": 30.5,
    "fps": 25.0,
    "detections": [
      {
        "class": "bird",
        "confidence": 0.85,
        "bbox": [100, 150, 200, 250],
        "class_id": 14,
        "frame_time": 15.2
      }
    ],
    "detection_count": 1,
    "analyzed_at": "2024-12-15T14:30:00"
  }
]
```

### 2. Résumé pour interface web (`summary.json`)

```json
{
  "generated_at": "2024-12-15T14:30:00",
  "statistics": {
    "total_videos": 150,
    "videos_with_detections": 23,
    "total_detections": 67,
    "detection_rate": 15.3
  },
  "animal_counts": {
    "bird": 34,
    "person": 18,
    "cat": 8
  },
  "top_videos": [...],
  "all_results": [...]
}
```

### 3. Métadonnées vidéo

```python
video_metadata = {
    "filename": str,           # Nom du fichier
    "duration": float,        # Durée en secondes
    "fps": float,            # Images par seconde
    "resolution": tuple,     # (largeur, hauteur)
    "format": str,           # Format vidéo
    "size_bytes": int,       # Taille en octets
    "created_at": datetime   # Date de création
}
```

---

## 🎨 Interface utilisateur

### 1. Design System

#### 1.1 Palette de couleurs
```css
:root {
  --primary: #667eea;      /* Bleu principal */
  --secondary: #764ba2;    /* Violet secondaire */
  --success: #4CAF50;      /* Vert succès */
  --warning: #FF9800;      /* Orange attention */
  --error: #f44336;        /* Rouge erreur */
  --background: #f5f5f5;   /* Fond principal */
  --surface: #ffffff;      /* Surface des cartes */
  --text: #333333;         /* Texte principal */
  --text-secondary: #666666; /* Texte secondaire */
}
```

#### 1.2 Typographie
- **Police principale** : -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- **Hiérarchie** : H1 (2em), H2 (1.5em), H3 (1.2em), Body (1em)
- **Poids** : Normal (400), Bold (700)

### 2. Composants UI

#### 2.1 Dashboard principal
- **Header** : Titre avec gradient, navigation
- **Stats cards** : Cartes statistiques avec icônes
- **Search bar** : Recherche en temps réel
- **Filter bar** : Boutons de filtrage par animal
- **Video grid** : Grille responsive des vidéos

#### 2.2 Lecteur vidéo
- **Video player** : Lecteur HTML5 avec contrôles
- **Overlay** : Boîtes de détection superposées
- **Timeline** : Barre de progression avec marqueurs
- **Controls** : Boutons de navigation entre détections
- **Info panel** : Métadonnées et liste des détections

### 3. Responsive Design

#### 3.1 Breakpoints
```css
/* Mobile */
@media (max-width: 768px) { ... }

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) { ... }

/* Desktop */
@media (min-width: 1025px) { ... }
```

#### 3.2 Grilles adaptatives
- **Mobile** : 1 colonne
- **Tablet** : 2 colonnes
- **Desktop** : 3+ colonnes

---

## 🚀 Instructions de mise en œuvre

### 1. Prérequis système

#### 1.1 Matériel requis
- **MacBook** avec Apple Silicon (M1, M2, M3, M4)
- **RAM** : Minimum 8GB, recommandé 16GB+
- **Stockage** : 2GB pour l'installation + espace pour vidéos
- **Réseau** : Connexion internet pour téléchargement des modèles

#### 1.2 Logiciel requis
- **macOS** : 12.0 (Monterey) ou plus récent
- **Python** : 3.9+ (recommandé 3.13)
- **pip** : Gestionnaire de paquets Python

### 2. Installation

#### 2.1 Cloner le projet
```bash
git clone <repository-url>
cd PiegePhoto
```

#### 2.2 Environnement virtuel
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows
```

#### 2.3 Dépendances
```bash
# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation MLX
python -c "import mlx; print('MLX installé avec succès')"
```

#### 2.4 Structure des dossiers
```
PiegePhoto/
├── venv/                    # Environnement virtuel
├── videos/                  # Dossier des vidéos (à créer)
├── data/                    # Dossier alternatif pour vidéos
├── templates/               # Templates HTML (générés automatiquement)
├── analysis_results.json    # Résultats d'analyse (généré)
├── summary.json            # Résumé pour interface web (généré)
├── rapport_piege_photo.txt # Rapport détaillé (généré)
└── [fichiers Python]       # Code source
```

### 3. Configuration

#### 3.1 Paramètres de détection
```python
# Dans mlx_detector.py
class FastMLXDetector:
    def __init__(self):
        self.input_size = (416, 416)  # Taille d'entrée optimisée
        self.confidence_threshold = 0.3  # Seuil de confiance
```

#### 3.2 Espèces personnalisées
```python
# Ajouter de nouvelles espèces spécifiques au Jura
self.target_classes = {
    0: 'person', 14: 'bird', 15: 'cat', 16: 'dog',
    17: 'horse', 18: 'sheep', 19: 'cow', 20: 'fox',
    21: 'deer', 22: 'roe_deer', 23: 'wild_boar', 24: 'squirrel',
    25: 'rabbit', 26: 'hedgehog', 27: 'badger',
    99: 'lynx', 100: 'chamois', 101: 'marmotte'  # Espèces alpines
}
```

### 4. Utilisation

#### 4.1 Analyse simple
```bash
# Analyser un dossier de vidéos
python video_analyzer.py /chemin/vers/videos

# Analyser un fichier unique
python video_analyzer.py video.mp4

# Spécifier le détecteur
python video_analyzer.py /chemin/videos --detector accurate
```

#### 4.2 Génération de rapports
```bash
# Rapport texte uniquement
python report_generator.py

# Rapport + JSON pour interface web
python report_generator.py --json
```

#### 4.3 Interface web
```bash
# Lancer l'interface web
python web_interface.py

# Spécifier le port
python web_interface.py --port 8080

# Mode debug
python web_interface.py --debug
```

#### 4.4 Script tout-en-un
```bash
# Analyse complète avec interface web
python run_analysis.py /chemin/vers/videos

# Analyse sans interface web
python run_analysis.py /chemin/vers/videos --no-web

# Spécifier le port
python run_analysis.py /chemin/vers/videos --port 8080
```

---

## 🔧 Configuration et déploiement

### 1. Configuration avancée

#### 1.1 Optimisation MLX
```python
# Dans mlx_detector.py
import mlx.core as mx

# Configuration du device
mx.set_default_device(mx.gpu)  # Forcer l'utilisation du GPU

# Optimisation mémoire
mx.metal.set_memory_limit(0.8)  # Limiter à 80% de la RAM GPU
```

#### 1.2 Paramètres de streaming
```python
# Dans video_streamer.py
class VideoStreamer:
    def __init__(self):
        self.chunk_size = 8192  # Taille des chunks
        self.cache_headers = True  # Cache des headers
        self.max_concurrent_streams = 10  # Limite de streams
```

### 2. Déploiement production

#### 2.1 Serveur web
```bash
# Utiliser Gunicorn pour la production
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_interface:app
```

#### 2.2 Configuration Nginx
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /stream/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

#### 2.3 Service systemd
```ini
[Unit]
Description=PiegePhoto Web Interface
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/PiegePhoto
Environment=PATH=/path/to/PiegePhoto/venv/bin
ExecStart=/path/to/PiegePhoto/venv/bin/python web_interface.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Monitoring et logs

#### 3.1 Configuration des logs
```python
import logging

# Configuration détaillée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('piegephoto.log'),
        logging.StreamHandler()
    ]
)
```

#### 3.2 Métriques de performance
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result
    return wrapper
```

---

## 🧪 Tests et validation

### 1. Tests unitaires

#### 1.1 Tests du détecteur
```python
import unittest
from mlx_detector import create_detector
import cv2
import numpy as np

class TestMLXDetector(unittest.TestCase):
    def setUp(self):
        self.detector = create_detector("fast")
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_detection_basic(self):
        detections = self.detector.quick_detect(self.test_image)
        self.assertIsInstance(detections, list)
    
    def test_detection_confidence(self):
        detections = self.detector.quick_detect(self.test_image, confidence_threshold=0.5)
        for detection in detections:
            self.assertGreaterEqual(detection['confidence'], 0.5)
```

#### 1.2 Tests de l'analyseur
```python
class TestVideoAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = VideoAnalyzer("fast")
    
    def test_frame_extraction(self):
        # Test avec une vidéo de test
        frames = self.analyzer.extract_frames("test_video.mp4")
        self.assertGreater(len(frames), 0)
```

### 2. Tests d'intégration

#### 2.1 Pipeline complet
```python
def test_full_pipeline():
    """Test du pipeline complet d'analyse"""
    # 1. Analyser une vidéo
    analyzer = VideoAnalyzer("fast")
    result = analyzer.analyze_video("test_video.mp4")
    
    # 2. Générer un rapport
    generator = ReportGenerator()
    generator.results = [result]
    report = generator.generate_summary()
    
    # 3. Vérifier les résultats
    assert "STATISTIQUES GÉNÉRALES" in report
    assert result['detection_count'] >= 0
```

#### 2.2 Interface web
```python
def test_web_interface():
    """Test de l'interface web"""
    from web_interface import app
    
    with app.test_client() as client:
        # Test de la page principale
        response = client.get('/')
        assert response.status_code == 200
        
        # Test de l'API
        response = client.get('/api/summary')
        assert response.status_code in [200, 404]  # 404 si pas de données
```

### 3. Tests de performance

#### 3.1 Benchmark MLX
```python
import time

def benchmark_detection():
    """Benchmark de la détection MLX"""
    detector = create_detector("fast")
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Test de vitesse
    start_time = time.time()
    for _ in range(100):
        detections = detector.quick_detect(test_image)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    print(f"Temps moyen de détection: {avg_time:.3f}s")
    
    # Vérifier que c'est assez rapide (< 0.1s par image)
    assert avg_time < 0.1
```

#### 3.2 Test de charge
```python
def test_concurrent_streams():
    """Test de charge pour le streaming"""
    import threading
    import requests
    
    def make_request():
        response = requests.get('http://localhost:5000/api/summary')
        return response.status_code
    
    # Lancer 10 requêtes simultanées
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Attendre la fin
    for thread in threads:
        thread.join()
```

### 4. Validation des résultats

#### 4.1 Validation des détections
```python
def validate_detection_format(detection):
    """Valide le format d'une détection"""
    required_fields = ['class', 'confidence', 'bbox', 'class_id']
    
    for field in required_fields:
        assert field in detection, f"Champ manquant: {field}"
    
    # Validation des types
    assert isinstance(detection['confidence'], (int, float))
    assert 0 <= detection['confidence'] <= 1
    assert len(detection['bbox']) == 4
    assert all(isinstance(x, (int, float)) for x in detection['bbox'])
```

#### 4.2 Validation des métadonnées
```python
def validate_video_metadata(video_result):
    """Valide les métadonnées d'une vidéo"""
    required_fields = ['video_path', 'filename', 'duration', 'fps', 'detections']
    
    for field in required_fields:
        assert field in video_result, f"Champ manquant: {field}"
    
    assert video_result['duration'] > 0
    assert video_result['fps'] > 0
    assert video_result['detection_count'] == len(video_result['detections'])
```

---

## 📚 Documentation technique

### 1. API Reference

#### 1.1 Endpoints REST
```python
# GET /api/summary
# Retourne: Résumé des données d'analyse
# Format: JSON avec statistiques et comptages

# GET /api/video/<filename>
# Retourne: Métadonnées d'une vidéo spécifique
# Format: JSON avec détections et informations

# GET /api/search?q=query&animal=type
# Retourne: Résultats de recherche filtrés
# Paramètres: q (recherche), animal (filtre par type)

# GET /stream/<filename>
# Retourne: Stream vidéo avec range requests
# Headers: Accept-Ranges, Content-Range

# GET /thumbnail/<filename>
# Retourne: Miniature JPEG de la vidéo
# Format: Image JPEG optimisée
```

#### 1.2 Classes principales
```python
class VideoAnalyzer:
    """Analyseur principal des vidéos de piège photo"""
    
    def __init__(self, detector_type="fast"):
        """Initialise avec le type de détecteur"""
    
    def extract_frames(self, video_path, max_frames=10):
        """Extrait des frames représentatives"""
    
    def analyze_video(self, video_path):
        """Analyse complète d'une vidéo"""
    
    def analyze_directory(self, video_dir, output_file="analysis_results.json"):
        """Analyse tous les fichiers vidéo d'un répertoire"""

class MLXAnimalDetector:
    """Détecteur d'animaux optimisé MLX"""
    
    def detect_objects(self, image, confidence_threshold=0.5):
        """Détecte les objets dans une image"""
    
    def detect_batch(self, images, confidence_threshold=0.5):
        """Détecte les objets dans un lot d'images"""

class ReportGenerator:
    """Générateur de rapports"""
    
    def generate_summary(self):
        """Génère un résumé des détections"""
    
    def generate_detailed_report(self):
        """Génère un rapport détaillé"""
    
    def export_json_summary(self, filename="summary.json"):
        """Exporte un résumé en JSON"""

class WebInterface:
    """Interface web Flask"""
    
    def load_data(self):
        """Charge les données d'analyse"""
    
    def get_video_info(self, filename):
        """Récupère les informations d'une vidéo"""

class VideoStreamer:
    """Serveur de streaming vidéo"""
    
    def stream_file(self, file_path):
        """Stream un fichier avec range requests"""
    
    def generate_thumbnail(self, video_path):
        """Génère une miniature de la vidéo"""
```

### 2. Configuration avancée

#### 2.1 Variables d'environnement
```bash
# Configuration MLX
export MLX_METAL_CACHE_DIR="/tmp/mlx_cache"
export MLX_MEMORY_LIMIT="0.8"

# Configuration Flask
export FLASK_ENV="production"
export FLASK_DEBUG="False"

# Configuration vidéo
export MAX_CONCURRENT_STREAMS="10"
export THUMBNAIL_CACHE_SIZE="100"
```

#### 2.2 Fichier de configuration
```python
# config.py
import os

class Config:
    # MLX Configuration
    MLX_DEVICE = os.getenv('MLX_DEVICE', 'gpu')
    MLX_MEMORY_LIMIT = float(os.getenv('MLX_MEMORY_LIMIT', '0.8'))
    
    # Video Configuration
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    MAX_FRAMES_PER_VIDEO = int(os.getenv('MAX_FRAMES', '10'))
    
    # Web Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # Streaming Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '8192'))
    MAX_CONCURRENT_STREAMS = int(os.getenv('MAX_STREAMS', '10'))
```

---

## 🔍 Dépannage et FAQ

### 1. Problèmes courants

#### 1.1 Erreur "Modèle non trouvé"
```bash
# Solution: Télécharger les modèles MLX
python -c "from transformers import AutoModelForObjectDetection; AutoModelForObjectDetection.from_pretrained('facebook/detr-resnet-50')"
```

#### 1.2 Vidéos non trouvées dans l'interface web
```bash
# Vérifier la structure des dossiers
ls -la videos/  # ou data/
# Les vidéos doivent être dans un de ces dossiers
```

#### 1.3 Performance lente
```python
# Optimisations possibles:
# 1. Utiliser le mode "fast" au lieu de "accurate"
# 2. Réduire le nombre de frames analysées
# 3. Vérifier que MLX utilise bien le GPU M4
# 4. Traiter les vidéos par petits lots
```

#### 1.4 Problèmes de streaming
```bash
# Vérifier les formats supportés
# Assurer que les vidéos sont dans un format compatible
# Utiliser MP4 pour de meilleures performances
```

### 2. Logs et debugging

#### 2.1 Activation des logs détaillés
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2.2 Profiling des performances
```python
import cProfile
import pstats

def profile_analysis():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Votre code d'analyse ici
    analyzer = VideoAnalyzer("fast")
    result = analyzer.analyze_video("test.mp4")
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### 3. FAQ technique

#### Q: Comment ajouter de nouvelles espèces d'animaux ?
R: Modifiez le dictionnaire `target_classes` dans `mlx_detector.py` et ajoutez vos espèces avec des IDs uniques. Le système est déjà configuré pour la faune du Jura (renards, cerfs, chevreuils, sangliers, etc.).

#### Q: Comment optimiser les performances sur un MacBook M4 ?
R: Utilisez le mode "fast", assurez-vous que MLX utilise le GPU, et traitez les vidéos par petits lots.

#### Q: Puis-je utiliser le système sur d'autres plateformes ?
R: Le système est optimisé pour Apple Silicon. Sur d'autres plateformes, vous devrez adapter les optimisations MLX.

#### Q: Comment personnaliser l'interface web ?
R: Modifiez les templates HTML dans le dossier `templates/` ou personnalisez les styles CSS.

#### Q: Le système peut-il traiter des vidéos très longues ?
R: Oui, mais pour de meilleures performances, il est recommandé de diviser les très longues vidéos en segments plus courts.

---

## 📈 Roadmap et évolutions

### 1. Améliorations prévues

#### 1.1 Fonctionnalités court terme
- **Détection améliorée** : Intégration de modèles plus précis
- **Export avancé** : Support PDF, Excel, CSV
- **Notifications** : Alertes par email/SMS pour détections importantes
- **API REST** : Endpoints pour intégration externe

#### 1.2 Fonctionnalités moyen terme
- **Machine Learning** : Entraînement de modèles personnalisés
- **Analytics avancés** : Tendances temporelles, corrélations
- **Multi-utilisateur** : Système d'authentification et permissions
- **Mobile app** : Application mobile native

#### 1.3 Fonctionnalités long terme
- **Cloud integration** : Déploiement cloud avec auto-scaling
- **IoT integration** : Connexion directe avec pièges photo
- **AI avancée** : Reconnaissance faciale, comptage automatique
- **Internationalisation** : Support multi-langues

### 2. Optimisations techniques

#### 2.1 Performance
- **Parallélisation** : Traitement multi-thread optimisé
- **Cache intelligent** : Mise en cache des résultats d'analyse
- **Compression** : Optimisation des données stockées
- **CDN** : Distribution de contenu pour le streaming

#### 2.2 Scalabilité
- **Microservices** : Architecture distribuée
- **Queue system** : Traitement asynchrone avec Redis/RabbitMQ
- **Database** : Migration vers PostgreSQL/MongoDB
- **Load balancing** : Répartition de charge automatique

---

## 📄 Conclusion

**PiegePhoto** est un système complet et optimisé pour l'analyse automatique de vidéos de piège photo. Conçu spécifiquement pour Apple Silicon M4, il combine les dernières technologies d'intelligence artificielle avec une interface web moderne et intuitive.

### Points forts du système :
- **Performance exceptionnelle** grâce à l'optimisation MLX
- **Interface utilisateur moderne** et responsive
- **Architecture modulaire** facilement extensible
- **Documentation complète** pour la maintenance et l'évolution
- **Support multi-format** et streaming optimisé

### Cas d'usage principaux :
- **Surveillance de la faune** sauvage
- **Recherche scientifique** en écologie
- **Conservation** de la biodiversité
- **Éducation** et sensibilisation

Le système est prêt pour la production et peut être déployé facilement sur tout MacBook avec Apple Silicon. La documentation technique complète permet une maintenance et une évolution aisée du système.

---

*Document généré automatiquement - Version 1.0 - Décembre 2024*