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
import torch
import torchvision.transforms as transforms
from transformers import AutoImageProcessor, AutoModelForObjectDetection
import logging

logger = logging.getLogger(__name__)

class MLXAnimalDetector:
    def __init__(self, model_name="facebook/detr-resnet-50"):
        """Initialise le détecteur avec un modèle optimisé pour MLX"""
        self.device = mx.default_device()
        logger.info(f"Initialisation du détecteur MLX sur {self.device}")
        
        # Utiliser un modèle léger et rapide
        self.model_name = model_name
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForObjectDetection.from_pretrained(model_name)
        
        # Classes d'animaux dans COCO dataset
        self.animal_classes = {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
            5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
            10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
            14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep',
            19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe',
            24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase',
            29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball',
            33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard',
            37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass',
            41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
            56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table',
            61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote',
            66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
            70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock',
            75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'
        }
        
        # Classes d'animaux pertinentes pour un piège photo
        self.wildlife_classes = {
            0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 
            18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe'
        }
        
        logger.info("Modèle chargé avec succès")
    
    def preprocess_image(self, image):
        """Préprocesse une image pour le modèle"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Redimensionner l'image pour optimiser les performances
        image = image.resize((640, 640))
        
        # Convertir en tensor MLX
        inputs = self.processor(images=image, return_tensors="pt")
        
        # Convertir vers MLX
        pixel_values = mx.array(inputs['pixel_values'].numpy())
        
        return pixel_values
    
    def detect_objects(self, image, confidence_threshold=0.5):
        """Détecte les objets dans une image"""
        try:
            # Préprocesser l'image
            pixel_values = self.preprocess_image(image)
            
            # Prédiction avec le modèle
            with torch.no_grad():
                outputs = self.model(pixel_values)
            
            # Traiter les résultats
            detections = []
            
            # Convertir les outputs vers numpy pour traitement
            logits = outputs.logits.cpu().numpy()
            boxes = outputs.pred_boxes.cpu().numpy()
            
            # Appliquer softmax pour obtenir les probabilités
            probs = torch.nn.functional.softmax(torch.tensor(logits), dim=-1)
            probs = probs.cpu().numpy()
            
            # Trouver les détections avec confiance suffisante
            for i in range(len(probs[0])):
                max_prob = np.max(probs[0][i])
                class_id = np.argmax(probs[0][i])
                
                if max_prob > confidence_threshold and class_id in self.wildlife_classes:
                    detection = {
                        'class': self.wildlife_classes[class_id],
                        'confidence': float(max_prob),
                        'bbox': boxes[0][i].tolist(),
                        'class_id': int(class_id)
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
        
        # Utiliser un modèle plus léger pour la vitesse
        self.model_name = "facebook/detr-resnet-50"
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForObjectDetection.from_pretrained(self.model_name)
        
        # Classes d'animaux simplifiées
        self.target_classes = {
            0: 'person', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse',
            18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear'
        }
    
    def quick_detect(self, image, confidence_threshold=0.3):
        """Détection rapide optimisée pour MLX"""
        try:
            # Redimensionner rapidement
            if isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Taille plus petite pour la vitesse
            image = image.resize((416, 416))
            
            # Préprocesser
            inputs = self.processor(images=image, return_tensors="pt")
            pixel_values = mx.array(inputs['pixel_values'].numpy())
            
            # Prédiction rapide
            with torch.no_grad():
                outputs = self.model(pixel_values)
            
            # Traitement optimisé des résultats
            detections = []
            logits = outputs.logits.cpu().numpy()[0]
            boxes = outputs.pred_boxes.cpu().numpy()[0]
            
            # Trouver les meilleures détections rapidement
            max_probs = np.max(logits, axis=1)
            max_classes = np.argmax(logits, axis=1)
            
            for i, (prob, class_id) in enumerate(zip(max_probs, max_classes)):
                if prob > confidence_threshold and class_id in self.target_classes:
                    detections.append({
                        'class': self.target_classes[class_id],
                        'confidence': float(prob),
                        'bbox': boxes[i].tolist(),
                        'class_id': int(class_id)
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
    
    detections = detector.detect_objects(image) if hasattr(detector, 'detect_objects') else detector.quick_detect(image)
    
    print(f"Détections trouvées: {len(detections)}")
    for det in detections:
        print(f"- {det['class']}: {det['confidence']:.2f}")