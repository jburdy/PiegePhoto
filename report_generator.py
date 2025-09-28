#!/usr/bin/env python3
"""
Générateur de rapports pour l'analyse des vidéos de piège photo
"""

import json
import datetime
from collections import defaultdict, Counter
from pathlib import Path

class ReportGenerator:
    def __init__(self, results_file="analysis_results.json"):
        """Initialise le générateur de rapports"""
        self.results_file = results_file
        self.results = self.load_results()
    
    def load_results(self):
        """Charge les résultats d'analyse"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Fichier {self.results_file} non trouvé")
            return []
    
    def generate_summary(self):
        """Génère un résumé des détections"""
        if not self.results:
            return "Aucune donnée à analyser"
        
        # Statistiques générales
        total_videos = len(self.results)
        total_detections = sum(r['detection_count'] for r in self.results)
        
        # Comptage par type d'animal
        animal_counts = Counter()
        videos_with_detections = 0
        
        for result in self.results:
            if result['detection_count'] > 0:
                videos_with_detections += 1
                for detection in result['detections']:
                    animal_counts[detection['class']] += 1
        
        # Activité par heure (si les noms de fichiers contiennent des timestamps)
        hourly_activity = defaultdict(int)
        
        summary = f"""
=== RAPPORT D'ANALYSE DES VIDÉOS DE PIÈGE PHOTO ===
Généré le: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 STATISTIQUES GÉNÉRALES:
- Nombre total de vidéos analysées: {total_videos}
- Vidéos avec détections: {videos_with_detections}
- Total des détections: {total_detections}
- Taux de détection: {(videos_with_detections/total_videos*100):.1f}%

🐾 ANIMAUX DÉTECTÉS:
"""
        
        for animal, count in animal_counts.most_common():
            summary += f"- {animal}: {count} détections\n"
        
        if not animal_counts:
            summary += "- Aucun animal détecté\n"
        
        summary += f"""
📈 VIDÉOS LES PLUS ACTIVES:
"""
        
        # Top 10 des vidéos avec le plus de détections
        sorted_videos = sorted(self.results, key=lambda x: x['detection_count'], reverse=True)
        for i, video in enumerate(sorted_videos[:10]):
            if video['detection_count'] > 0:
                summary += f"{i+1}. {video['filename']}: {video['detection_count']} détections\n"
        
        return summary
    
    def generate_detailed_report(self):
        """Génère un rapport détaillé"""
        if not self.results:
            return "Aucune donnée à analyser"
        
        report = self.generate_summary()
        report += "\n\n=== RAPPORT DÉTAILLÉ ===\n\n"
        
        for result in self.results:
            if result['detection_count'] > 0:
                report += f"📹 {result['filename']}\n"
                report += f"   Durée: {result['duration']:.1f}s\n"
                report += f"   Détections: {result['detection_count']}\n"
                
                # Grouper les détections par type
                detections_by_type = defaultdict(list)
                for detection in result['detections']:
                    detections_by_type[detection['class']].append(detection)
                
                for animal_type, detections in detections_by_type.items():
                    report += f"   - {animal_type}: {len(detections)} détections\n"
                    for det in detections[:3]:  # Montrer les 3 premières
                        report += f"     * Confiance: {det['confidence']:.2f}, Temps: {det['frame_time']:.1f}s\n"
                
                report += "\n"
        
        return report
    
    def save_report(self, filename="rapport_piege_photo.txt"):
        """Sauvegarde le rapport dans un fichier"""
        report = self.generate_detailed_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Rapport sauvegardé dans {filename}")
        return filename
    
    def export_json_summary(self, filename="summary.json"):
        """Exporte un résumé en JSON pour l'interface web"""
        if not self.results:
            return {}
        
        # Statistiques générales
        total_videos = len(self.results)
        total_detections = sum(r['detection_count'] for r in self.results)
        
        # Comptage par type d'animal
        animal_counts = Counter()
        videos_with_detections = 0
        
        for result in self.results:
            if result['detection_count'] > 0:
                videos_with_detections += 1
                for detection in result['detections']:
                    animal_counts[detection['class']] += 1
        
        # Top vidéos
        top_videos = sorted(self.results, key=lambda x: x['detection_count'], reverse=True)[:10]
        
        summary = {
            "generated_at": datetime.datetime.now().isoformat(),
            "statistics": {
                "total_videos": total_videos,
                "videos_with_detections": videos_with_detections,
                "total_detections": total_detections,
                "detection_rate": round(videos_with_detections/total_videos*100, 1) if total_videos > 0 else 0
            },
            "animal_counts": dict(animal_counts),
            "top_videos": [
                {
                    "filename": v['filename'],
                    "detections": v['detection_count'],
                    "duration": v['duration']
                } for v in top_videos if v['detection_count'] > 0
            ],
            "all_results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Générateur de rapports")
    parser.add_argument("--input", "-i", default="analysis_results.json", help="Fichier de résultats")
    parser.add_argument("--output", "-o", default="rapport_piege_photo.txt", help="Fichier de rapport")
    parser.add_argument("--json", action="store_true", help="Exporter aussi en JSON")
    
    args = parser.parse_args()
    
    generator = ReportGenerator(args.input)
    
    # Générer le rapport texte
    generator.save_report(args.output)
    
    # Générer le JSON si demandé
    if args.json:
        generator.export_json_summary("summary.json")
        print("Résumé JSON exporté dans summary.json")

if __name__ == "__main__":
    main()