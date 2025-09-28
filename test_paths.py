#!/usr/bin/env python3
"""
Script utilitaire pour tester les chemins de vidéos
"""

import os
import sys
from pathlib import Path

def test_video_paths(video_dir, filename):
    """Teste les chemins de vidéos"""
    print(f"🔍 Test des chemins pour: {filename}")
    print(f"📁 Dossier vidéo: {video_dir}")
    print("-" * 50)
    
    # Chemins à tester
    video_paths = []
    
    if video_dir:
        video_paths.append(os.path.join(video_dir, filename))
    
    video_paths.extend([
        f"videos/{filename}",
        f"data/{filename}",
        filename
    ])
    
    found_paths = []
    
    for i, path in enumerate(video_paths, 1):
        exists = os.path.exists(path)
        status = "✅ TROUVÉ" if exists else "❌ NON TROUVÉ"
        print(f"{i}. {path:<40} {status}")
        
        if exists:
            found_paths.append(path)
            # Afficher les infos du fichier
            stat = os.stat(path)
            size_mb = stat.st_size / (1024 * 1024)
            print(f"   📊 Taille: {size_mb:.1f} MB")
    
    print("-" * 50)
    
    if found_paths:
        print(f"✅ {len(found_paths)} chemin(s) valide(s) trouvé(s)")
        print(f"🎯 Premier chemin valide: {found_paths[0]}")
    else:
        print("❌ Aucun chemin valide trouvé")
        print("\n💡 Solutions possibles:")
        print("1. Créer un symlink: ln -s /chemin/vers/videos videos")
        print("2. Copier les vidéos dans le dossier 'data/'")
        print("3. Utiliser --video-dir /chemin/vers/videos avec web_interface.py")
    
    return found_paths

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("Usage: python test_paths.py <dossier_videos> [nom_fichier_video]")
        print("\nExemples:")
        print("  python test_paths.py /Users/jb/Videos")
        print("  python test_paths.py /Users/jb/Videos video1.mp4")
        sys.exit(1)
    
    video_dir = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(video_dir):
        print(f"❌ Le dossier {video_dir} n'existe pas")
        sys.exit(1)
    
    if not os.path.isdir(video_dir):
        print(f"❌ {video_dir} n'est pas un dossier")
        sys.exit(1)
    
    print(f"📁 Dossier vidéo: {video_dir}")
    
    # Lister les fichiers vidéo
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}
    video_files = []
    
    for file in os.listdir(video_dir):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    if not video_files:
        print("❌ Aucun fichier vidéo trouvé dans le dossier")
        sys.exit(1)
    
    print(f"🎬 {len(video_files)} fichier(s) vidéo trouvé(s):")
    for i, file in enumerate(video_files[:10], 1):  # Afficher max 10 fichiers
        print(f"  {i}. {file}")
    
    if len(video_files) > 10:
        print(f"  ... et {len(video_files) - 10} autres")
    
    print()
    
    # Tester avec un fichier spécifique ou le premier trouvé
    test_file = filename or video_files[0]
    
    if filename and filename not in video_files:
        print(f"⚠️  Le fichier {filename} n'a pas été trouvé dans le dossier")
        print("Utilisation du premier fichier trouvé")
        test_file = video_files[0]
    
    test_video_paths(video_dir, test_file)
    
    print("\n🚀 Pour lancer l'interface web avec ce dossier:")
    print(f"python web_interface.py --video-dir '{video_dir}'")

if __name__ == "__main__":
    main()