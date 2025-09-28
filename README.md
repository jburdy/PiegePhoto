# 🦌 Analyseur de Piège Photo avec IA (MLX)

Un système Python optimisé pour MacBook M4 utilisant MLX pour analyser automatiquement des centaines de vidéos de piège photo et générer des rapports détaillés.

## 🚀 Installation

```bash
# Installer les dépendances (optimisées pour MacBook M4)
pip install -r requirements.txt

# Les modèles MLX seront téléchargés automatiquement au premier lancement
python video_analyzer.py --help
```

## 📋 Utilisation

### 1. Analyser vos vidéos

```bash
# Analyser un dossier de vidéos (mode rapide par défaut)
python video_analyzer.py /chemin/vers/vos/videos

# Analyser avec détecteur précis (plus lent mais plus précis)
python video_analyzer.py /chemin/videos --detector accurate

# Analyser un seul fichier
python video_analyzer.py video.mp4

# Spécifier le fichier de sortie
python video_analyzer.py /chemin/videos --output mes_resultats.json --detector fast
```

### 2. Générer un rapport

```bash
# Générer un rapport texte
python report_generator.py

# Générer aussi un résumé JSON pour l'interface web
python report_generator.py --json
```

### 3. Interface web

```bash
# Lancer l'interface web
python web_interface.py

# Accéder à http://localhost:5000
```

## 📁 Structure du projet

```
PiegePhoto/
├── video_analyzer.py      # Analyseur principal avec MLX
├── mlx_detector.py        # Détecteur optimisé pour MacBook M4
├── report_generator.py    # Générateur de rapports
├── web_interface.py       # Interface web Flask
├── video_streamer.py      # Serveur de streaming vidéo
├── run_analysis.py        # Script principal tout-en-un
├── requirements.txt       # Dépendances Python (MLX)
├── README.md             # Ce fichier
├── analysis_results.json # Résultats d'analyse (généré)
├── summary.json          # Résumé pour l'interface web (généré)
├── rapport_piege_photo.txt # Rapport détaillé (généré)
└── templates/            # Templates HTML (généré)
    ├── index.html
    ├── video_player.html
    └── error.html
```

## 🎯 Fonctionnalités

### Analyse automatique
- **Détection d'animaux** avec MLX optimisé pour MacBook M4 (personnes, chats, chiens, chevaux, moutons, vaches, ours, oiseaux, etc.)
- **Traitement par lots** ultra-rapide de centaines de vidéos
- **Extraction intelligente** de frames représentatives
- **Filtrage par confiance** (seuil configurable)
- **Deux modes** : rapide (par défaut) et précis

### Rapports détaillés
- **Statistiques générales** (nombre de vidéos, détections, taux d'activité)
- **Comptage par espèce** d'animal
- **Top des vidéos** les plus actives
- **Rapport détaillé** avec toutes les détections

### Interface web
- **Dashboard moderne** avec statistiques visuelles
- **Recherche** dans les vidéos
- **Filtrage** par type d'animal
- **Visualisation** des détections par vidéo
- **Lecteur vidéo intégré** avec overlay des détections
- **Navigation intelligente** entre les détections
- **Miniatures automatiques** des vidéos
- **Streaming optimisé** avec support des range requests
- **Design responsive** et minimaliste

## ⚙️ Configuration

### Modèle IA
Le système utilise MLX avec des modèles DETR optimisés pour MacBook M4. Pour de meilleures performances :
- **Mode rapide** : DETR-ResNet-50 avec optimisations MLX (par défaut)
- **Mode précis** : DETR-ResNet-50 avec traitement complet
- Ajuster le seuil de confiance dans `mlx_detector.py`
- Modifier les classes d'animaux détectées dans `mlx_detector.py`

### Formats supportés
- **Vidéo** : MP4, AVI, MOV, MKV, WMV
- **Sortie** : JSON, TXT, HTML

## 🔧 Personnalisation

### Ajouter de nouvelles espèces
Modifiez le dictionnaire `target_classes` dans `mlx_detector.py` :

```python
self.target_classes = {
    0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse',
    18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
    # Ajoutez vos espèces ici
    99: 'cerf', 100: 'sanglier'
}
```

### Ajuster la sensibilité
Modifiez le seuil de confiance dans `mlx_detector.py` :

```python
frame_detections = self.detector.quick_detect(frame, confidence_threshold=0.3)  # Plus sensible
```

## 📊 Exemple de sortie

### Rapport texte
```
=== RAPPORT D'ANALYSE DES VIDÉOS DE PIÈGE PHOTO ===
Généré le: 15/12/2024 14:30

📊 STATISTIQUES GÉNÉRALES:
- Nombre total de vidéos analysées: 150
- Vidéos avec détections: 23
- Total des détections: 67
- Taux de détection: 15.3%

🐾 ANIMAUX DÉTECTÉS:
- bird: 34 détections
- person: 18 détections
- cat: 8 détections
- dog: 7 détections
```

### Interface web
- Dashboard avec cartes statistiques
- Grille des vidéos avec miniatures et détections
- **Lecteur vidéo intégré** avec overlay des détections
- **Navigation intelligente** : saut automatique entre détections
- **Timeline interactive** avec marqueurs de détections
- **Streaming optimisé** pour lecture fluide
- Filtres par animal
- Recherche en temps réel

## 🚨 Dépannage

### Erreur "Modèle non trouvé"
```bash
# Les modèles MLX seront téléchargés automatiquement au premier lancement
# Si problème, téléchargez manuellement :
python -c "from transformers import AutoModelForObjectDetection; AutoModelForObjectDetection.from_pretrained('facebook/detr-resnet-50')"
```

### Vidéos non trouvées dans l'interface web
Placez vos vidéos dans le dossier `videos/` ou `data/` à la racine du projet.

### Problèmes de lecture vidéo
- Assurez-vous que vos vidéos sont dans un format supporté (MP4 recommandé)
- Le serveur utilise le streaming avec range requests pour une lecture optimale
- Les miniatures sont générées automatiquement au milieu de chaque vidéo

### Performance lente
- Utilisez le mode `fast` au lieu de `accurate`
- Réduisez le nombre de frames analysées dans `extract_frames()`
- Assurez-vous que MLX utilise bien le GPU M4
- Traitez les vidéos par petits lots

## 📝 Notes

- **KISS** : Keep It Simple, Stupid - Interface minimaliste et intuitive
- **Performance** : Optimisé MLX pour MacBook M4 - ultra-rapide
- **Flexibilité** : Facilement extensible pour d'autres types de détection
- **Open Source** : Code modifiable selon vos besoins
- **Apple Silicon** : Exploite pleinement les capacités du M4

## 🤝 Contribution

Ce projet est conçu pour être simple et modulaire. N'hésitez pas à :
- Ajouter de nouvelles fonctionnalités
- Améliorer l'interface web
- Optimiser les performances MLX
- Ajouter le support d'autres modèles IA
- Améliorer la détection d'espèces sauvages spécifiques