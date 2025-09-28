#!/usr/bin/env python3
"""
Script principal pour lancer l'analyse complète des vidéos de piège photo
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}")
    print(f"Commande: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Terminé")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}")
        print(f"Erreur: {e.stderr}")
        return False

def main():
    """Script principal d'analyse"""
    print("🦌 ANALYSEUR DE PIÈGE PHOTO - SCRIPT PRINCIPAL")
    print("=" * 50)
    
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python run_analysis.py <chemin_vers_videos> [options]")
        print("\nOptions:")
        print("  --no-web     : Ne pas lancer l'interface web")
        print("  --port PORT  : Port pour l'interface web (défaut: 5000)")
        print("\nExemple:")
        print("  python run_analysis.py /chemin/vers/mes/videos")
        print("  python run_analysis.py ./videos --no-web")
        sys.exit(1)
    
    video_path = sys.argv[1]
    launch_web = "--no-web" not in sys.argv
    port = "5000"
    
    # Extraire le port si spécifié
    if "--port" in sys.argv:
        try:
            port_idx = sys.argv.index("--port")
            port = sys.argv[port_idx + 1]
        except (IndexError, ValueError):
            print("❌ Port invalide, utilisation du port par défaut 5000")
    
    # Vérifier que le chemin existe
    if not os.path.exists(video_path):
        print(f"❌ Le chemin {video_path} n'existe pas")
        sys.exit(1)
    
    print(f"📁 Analyse des vidéos dans: {video_path}")
    print(f"🌐 Interface web: {'Activée' if launch_web else 'Désactivée'}")
    if launch_web:
        print(f"🔌 Port web: {port}")
    
    # Étape 1: Analyser les vidéos
    detector_type = "fast"  # Utiliser le détecteur rapide par défaut
    if "--detector" in sys.argv:
        try:
            detector_idx = sys.argv.index("--detector")
            detector_type = sys.argv[detector_idx + 1]
        except (IndexError, ValueError):
            print("❌ Type de détecteur invalide, utilisation du mode rapide")
    
    if not run_command([
        "python", "video_analyzer.py", video_path, "--output", "analysis_results.json", "--detector", detector_type
    ], "Analyse des vidéos avec MLX"):
        print("❌ L'analyse a échoué")
        sys.exit(1)
    
    # Étape 2: Générer le rapport
    if not run_command([
        "python", "report_generator.py", "--input", "analysis_results.json", "--json"
    ], "Génération du rapport"):
        print("❌ La génération du rapport a échoué")
        sys.exit(1)
    
    # Étape 3: Lancer l'interface web (optionnel)
    if launch_web:
        print(f"\n🌐 Lancement de l'interface web sur le port {port}")
        print("📱 Ouvrez votre navigateur sur: http://localhost:" + port)
        print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
        
        try:
            subprocess.run([
                "python", "web_interface.py", "--port", port
            ], check=True)
        except KeyboardInterrupt:
            print("\n👋 Interface web arrêtée")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors du lancement de l'interface web: {e}")
    else:
        print("\n✅ Analyse terminée!")
        print("📄 Consultez le fichier 'rapport_piege_photo.txt' pour le rapport détaillé")
        print("🌐 Pour lancer l'interface web plus tard: python web_interface.py")

if __name__ == "__main__":
    main()