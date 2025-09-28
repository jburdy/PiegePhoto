#!/usr/bin/env python3
"""
Serveur de streaming vidéo optimisé pour l'interface web
Permet la lecture fluide des vidéos avec support des formats multiples
"""

import os
import mimetypes
from flask import Flask, request, Response, send_file, abort
import cv2
import logging

logger = logging.getLogger(__name__)

class VideoStreamer:
    def __init__(self, app, video_dir=None):
        """Initialise le streamer vidéo"""
        self.app = app
        self.video_dir = video_dir
        self.setup_routes()
    
    def setup_routes(self):
        """Configure les routes de streaming"""
        
        @self.app.route('/stream/<filename>')
        def stream_video(filename):
            """Stream une vidéo avec support du range requests"""
            video_paths = []
            
            # Ajouter le dossier vidéo spécifique si défini
            if self.video_dir:
                video_paths.append(os.path.join(self.video_dir, filename))
            
            # Ajouter les chemins par défaut
            video_paths.extend([
                f"videos/{filename}",
                f"data/{filename}",
                filename
            ])
            
            video_path = None
            for path in video_paths:
                if os.path.exists(path):
                    video_path = path
                    break
            
            if not video_path:
                abort(404)
            
            return self.stream_file(video_path)
        
        @self.app.route('/thumbnail/<filename>')
        def get_thumbnail(filename):
            """Génère une miniature de la vidéo"""
            video_paths = []
            
            # Ajouter le dossier vidéo spécifique si défini
            if self.video_dir:
                video_paths.append(os.path.join(self.video_dir, filename))
            
            # Ajouter les chemins par défaut
            video_paths.extend([
                f"videos/{filename}",
                f"data/{filename}",
                filename
            ])
            
            video_path = None
            for path in video_paths:
                if os.path.exists(path):
                    video_path = path
                    break
            
            if not video_path:
                abort(404)
            
            return self.generate_thumbnail(video_path)
    
    def stream_file(self, file_path):
        """Stream un fichier avec support des range requests pour la lecture vidéo"""
        range_header = request.headers.get('Range', None)
        byte_start = 0
        byte_end = None
        
        if range_header:
            match = range_header.replace('bytes=', '').split('-')
            byte_start = int(match[0]) if match[0] else 0
            byte_end = int(match[1]) if match[1] else None
        
        file_size = os.path.getsize(file_path)
        
        if byte_end is None:
            byte_end = file_size - 1
        
        content_length = byte_end - byte_start + 1
        
        def generate():
            with open(file_path, 'rb') as f:
                f.seek(byte_start)
                remaining = content_length
                while remaining:
                    chunk_size = min(8192, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        response = Response(generate(), 
                          206,  # Partial Content
                          {
                              'Content-Type': mimetypes.guess_type(file_path)[0] or 'video/mp4',
                              'Accept-Ranges': 'bytes',
                              'Content-Length': str(content_length),
                              'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                          },
                          direct_passthrough=True)
        
        return response
    
    def generate_thumbnail(self, video_path):
        """Génère une miniature de la vidéo"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Aller au milieu de la vidéo
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Redimensionner la miniature
                height, width = frame.shape[:2]
                max_size = 300
                if width > height:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                else:
                    new_height = max_size
                    new_width = int(width * max_size / height)
                
                frame_resized = cv2.resize(frame, (new_width, new_height))
                
                # Encoder en JPEG
                _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                return Response(buffer.tobytes(), 
                              mimetype='image/jpeg',
                              headers={'Cache-Control': 'public, max-age=3600'})
            else:
                abort(404)
                
        except Exception as e:
            logger.error(f"Erreur génération miniature: {e}")
            abort(500)

def optimize_video_for_web(video_path, output_path=None):
    """Optimise une vidéo pour le streaming web"""
    if output_path is None:
        name, ext = os.path.splitext(video_path)
        output_path = f"{name}_web{ext}"
    
    # Utiliser ffmpeg pour optimiser (si disponible)
    import subprocess
    
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-c:v', 'libx264',  # Codec H.264
            '-preset', 'fast',   # Encodage rapide
            '-crf', '23',        # Qualité équilibrée
            '-c:a', 'aac',       # Audio AAC
            '-movflags', '+faststart',  # Optimisation pour streaming
            '-y',                # Overwrite
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Vidéo optimisée: {output_path}")
        return output_path
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("FFmpeg non disponible, utilisation de la vidéo originale")
        return video_path

if __name__ == "__main__":
    # Test du streamer
    app = Flask(__name__)
    streamer = VideoStreamer(app)
    
    print("🎬 Serveur de streaming vidéo démarré")
    print("📁 Placez vos vidéos dans le dossier 'videos/' ou 'data/'")
    print("🌐 Accédez aux vidéos via /stream/<filename>")
    print("🖼️ Miniatures disponibles via /thumbnail/<filename>")
    
    app.run(host='127.0.0.1', port=5001, debug=True)