#!/usr/bin/env python3
"""
Analyseur de vidéos de piège photo avec IA
Détecte automatiquement les animaux et génère des rapports
"""

import cv2
import os
import json
import datetime
from pathlib import Path
import numpy as np
from PIL import Image
import logging
from mlx_detector import create_detector

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    def __init__(self, detector_type="fast"):
        """Initialise l'analyseur avec le détecteur MLX optimisé"""
        self.detector = create_detector(detector_type)
        self.results = []
        logger.info(f"Analyseur initialisé avec détecteur {detector_type}")
        
    def extract_frames(self, video_path, max_frames=10):
        """Extrait quelques frames représentatives de la vidéo"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Prendre des frames espacées dans la vidéo
        if frame_count > max_frames:
            step = frame_count // max_frames
            frame_indices = [i * step for i in range(max_frames)]
        else:
            frame_indices = list(range(frame_count))
            
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                
        cap.release()
        return frames
    
    def analyze_video(self, video_path):
        """Analyse une vidéo et retourne les détections"""
        logger.info(f"Analyse de {video_path}")
        
        # Extraire les métadonnées de la vidéo
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        cap.release()
        
        # Extraire quelques frames pour l'analyse
        frames = self.extract_frames(video_path)
        
        detections = []
        for i, frame in enumerate(frames):
            # Détection avec MLX
            frame_detections = self.detector.quick_detect(frame, confidence_threshold=0.5)
            
            for detection in frame_detections:
                detection['frame_time'] = (i * duration) / len(frames)
                detections.append(detection)
        
        # Créer le résultat final
        video_result = {
            'video_path': str(video_path),
            'filename': os.path.basename(video_path),
            'duration': duration,
            'fps': fps,
            'detections': detections,
            'detection_count': len(detections),
            'analyzed_at': datetime.datetime.now().isoformat()
        }
        
        return video_result
    
    def analyze_directory(self, video_dir, output_file="analysis_results.json"):
        """Analyse tous les fichiers vidéo d'un répertoire"""
        video_dir = Path(video_dir)
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
        
        video_files = []
        for ext in video_extensions:
            video_files.extend(video_dir.glob(f"*{ext}"))
            video_files.extend(video_dir.glob(f"*{ext.upper()}"))
        
        logger.info(f"Trouvé {len(video_files)} fichiers vidéo")
        
        all_results = []
        for video_file in video_files:
            try:
                result = self.analyze_video(video_file)
                all_results.append(result)
                logger.info(f"✓ {video_file.name}: {result['detection_count']} détections")
            except Exception as e:
                logger.error(f"Erreur avec {video_file}: {e}")
        
        # Sauvegarder les résultats
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Résultats sauvegardés dans {output_file}")
        return all_results

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyseur de vidéos de piège photo avec MLX")
    parser.add_argument("video_path", help="Chemin vers le fichier vidéo ou dossier")
    parser.add_argument("--output", "-o", default="analysis_results.json", help="Fichier de sortie")
    parser.add_argument("--detector", choices=["fast", "accurate"], default="fast", help="Type de détecteur MLX")
    
    args = parser.parse_args()
    
    analyzer = VideoAnalyzer(detector_type=args.detector)
    
    if os.path.isfile(args.video_path):
        # Analyse d'un seul fichier
        result = analyzer.analyze_video(args.video_path)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump([result], f, indent=2, ensure_ascii=False)
        print(f"Analyse terminée: {result['detection_count']} détections")
    else:
        # Analyse d'un dossier
        results = analyzer.analyze_directory(args.video_path, args.output)
        total_detections = sum(r['detection_count'] for r in results)
        print(f"Analyse terminée: {len(results)} vidéos, {total_detections} détections au total")

if __name__ == "__main__":
    main()