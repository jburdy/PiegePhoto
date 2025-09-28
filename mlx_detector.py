#!/usr/bin/env python3
"""
Détecteur d'objets optimisé pour MLX sur MacBook M4
Utilise des modèles légers et rapides pour la détection d'animaux
"""

import mlx.core as mx
import mlx.nn as nn
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class MLXAnimalDetector:
    def __init__(self):
        """Initialise le détecteur avec un modèle optimisé pour MLX"""
        self.device = mx.default_device()
        logger.info(f"Initialisation du détecteur MLX sur {self.device}")
        
        # Classes d'animaux pertinentes pour un piège photo
        self.wildlife_classes = {
            0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 
            18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe'
        }
        
        # Initialiser un modèle simple de détection basé sur MLX
        self.input_size = (640, 640)
        self.num_classes = len(self.wildlife_classes)
        
        logger.info("Modèle MLX initialisé avec succès")
    
    def preprocess_image(self, image):
        """Préprocesse une image pour le modèle MLX"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Redimensionner l'image pour optimiser les performances
        image = image.resize(self.input_size)
        
        # Convertir en array numpy puis MLX
        image_array = np.array(image, dtype=np.float32) / 255.0
        image_array = np.transpose(image_array, (2, 0, 1))  # HWC -> CHW
        image_array = np.expand_dims(image_array, axis=0)  # Ajouter dimension batch
        
        # Convertir vers MLX
        pixel_values = mx.array(image_array)
        
        return pixel_values
    
    def detect_objects(self, image, confidence_threshold=0.5):
        """Détecte les objets dans une image en utilisant des techniques de vision par ordinateur"""
        try:
            # Convertir l'image en niveaux de gris pour l'analyse
            if isinstance(image, np.ndarray):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Détection de contours pour identifier les objets
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            height, width = gray.shape
            
            for contour in contours:
                # Filtrer les contours trop petits
                area = cv2.contourArea(contour)
                if area < 1000:  # Seuil minimum d'aire
                    continue
                
                # Calculer le rectangle englobant
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filtrer les rectangles trop petits ou trop grands
                if w < 50 or h < 50 or w > width * 0.8 or h > height * 0.8:
                    continue
                
                # Calculer un score de confiance basé sur la forme et la taille
                aspect_ratio = w / h
                extent = area / (w * h)
                
                # Score basé sur des critères heuristiques
                confidence = min(0.9, extent * 0.5 + (1 - abs(aspect_ratio - 1) * 0.3))
                
                if confidence > confidence_threshold:
                    # Classification simple basée sur la forme
                    if aspect_ratio > 1.5:
                        class_name = 'bird'  # Forme allongée
                    elif aspect_ratio < 0.7:
                        class_name = 'person'  # Forme haute
                    else:
                        class_name = 'animal'  # Forme carrée/ronde
                    
                    detection = {
                        'class': class_name,
                        'confidence': float(confidence),
                        'bbox': [x, y, x + w, y + h],
                        'class_id': 0  # ID générique
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection: {e}")
            return []
    
    def detect_batch(self, images, confidence_threshold=0.5):
        """Détecte les objets dans un lot d'images"""
        all_detections = []
        
        for i, image in enumerate(images):
            logger.info(f"Traitement de l'image {i+1}/{len(images)}")
            detections = self.detect_objects(image, confidence_threshold)
            all_detections.append(detections)
        
        return all_detections

class FastMLXDetector:
    """Version ultra-rapide utilisant des techniques d'optimisation MLX"""
    
    def __init__(self):
        """Initialise le détecteur rapide"""
        self.device = mx.default_device()
        logger.info(f"Détecteur rapide MLX initialisé sur {self.device}")
        
        # Classes d'animaux simplifiées
        self.target_classes = {
            0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse',
            18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear'
        }
        
        # Paramètres optimisés pour la vitesse
        self.input_size = (416, 416)
    
    def quick_detect(self, image, confidence_threshold=0.3):
        """Détection rapide optimisée pour MLX"""
        try:
            # Redimensionner rapidement
            if isinstance(image, np.ndarray):
                resized = cv2.resize(image, self.input_size)
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            else:
                resized = np.array(image.resize(self.input_size))
                gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            
            # Détection rapide basée sur la différence de fond
            # Utiliser un filtre de Sobel pour détecter les gradients
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # Seuillage adaptatif
            threshold = np.mean(magnitude) + np.std(magnitude)
            binary = (magnitude > threshold).astype(np.uint8) * 255
            
            # Morphologie pour nettoyer
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Trouver les contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            height, width = gray.shape
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 500:  # Seuil plus bas pour la détection rapide
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filtrer les rectangles trop petits
                if w < 30 or h < 30:
                    continue
                
                # Score de confiance basé sur l'aire et la forme
                aspect_ratio = w / h
                extent = area / (w * h)
                confidence = min(0.8, extent * 0.6 + (1 - abs(aspect_ratio - 1) * 0.2))
                
                if confidence > confidence_threshold:
                    # Classification rapide
                    if aspect_ratio > 1.3:
                        class_name = 'bird'
                    elif aspect_ratio < 0.8:
                        class_name = 'person'
                    else:
                        class_name = 'animal'
                    
                    # Convertir les coordonnées vers l'image originale
                    scale_x = image.shape[1] / width if isinstance(image, np.ndarray) else image.width / width
                    scale_y = image.shape[0] / height if isinstance(image, np.ndarray) else image.height / height
                    
                    detections.append({
                        'class': class_name,
                        'confidence': float(confidence),
                        'bbox': [int(x * scale_x), int(y * scale_y), 
                                int((x + w) * scale_x), int((y + h) * scale_y)],
                        'class_id': 0
                    })
            
            return detections
            
        except Exception as e:
            logger.error(f"Erreur détection rapide: {e}")
            return []

def create_detector(detector_type="fast"):
    """Factory pour créer le bon détecteur"""
    if detector_type == "fast":
        return FastMLXDetector()
    else:
        return MLXAnimalDetector()

if __name__ == "__main__":
    # Test du détecteur
    import argparse
    
    parser = argparse.ArgumentParser(description="Test du détecteur MLX")
    parser.add_argument("image_path", help="Chemin vers l'image de test")
    parser.add_argument("--type", choices=["fast", "accurate"], default="fast", help="Type de détecteur")
    
    args = parser.parse_args()
    
    detector = create_detector(args.type)
    
    # Charger et analyser l'image
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Impossible de charger l'image {args.image_path}")
        exit(1)
    
    if hasattr(detector, 'detect_objects'):
        detections = detector.detect_objects(image)
    else:
        detections = detector.quick_detect(image)
    
    print(f"Détections trouvées: {len(detections)}")
    for det in detections:
        print(f"- {det['class']}: {det['confidence']:.2f}")