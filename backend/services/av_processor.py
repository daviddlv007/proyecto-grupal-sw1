"""
Procesador unificado de audio y video para análisis completo de prácticas orales
"""
import os
import tempfile
import requests
from typing import Dict
import logging
from .video_analyzer import VideoAnalyzer
from .audio_analyzer import AudioAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AVProcessor:
    def __init__(self):
        self.video_analyzer = VideoAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
    
    def download_video(self, url: str) -> str:
        """
        Descarga el video desde una URL a un archivo temporal
        Returns: ruta del archivo temporal
        """
        try:
            logger.info(f"Descargando video desde: {url}")
            
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_path = temp_file.name
            
            # Descargar video
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Guardar en archivo temporal
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Video descargado exitosamente: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error al descargar video: {str(e)}")
            raise
    
    def process_video(self, video_url: str) -> Dict:
        """
        Procesa un video completo: descarga + análisis de audio y video
        Returns: dict con todas las métricas calculadas
        """
        temp_video_path = None
        
        try:
            # 1. Descargar video
            temp_video_path = self.download_video(video_url)
            
            # 2. Análisis de video COMPLETO (contacto visual, expresividad, confianza)
            logger.info("Iniciando análisis de video...")
            video_metrics = self.video_analyzer.analyze_video_complete(temp_video_path)
            
            # 3. Análisis de audio (transcripción, muletillas, velocidad)
            logger.info("Iniciando análisis de audio...")
            audio_metrics = self.audio_analyzer.analyze_complete(temp_video_path)
            
            # 4. Calcular puntuación general
            puntuacion = self._calculate_score(video_metrics, audio_metrics)
            
            # 5. Generar resumen
            resumen = self._generate_summary(video_metrics, audio_metrics)
            
            result = {
                "video": video_metrics,
                "audio": audio_metrics,
                "puntuacion": puntuacion,
                "resumen": resumen,
                "procesamiento_exitoso": True
            }
            
            logger.info("Procesamiento completado exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"Error al procesar video: {str(e)}")
            return {
                "video": {},
                "audio": {},
                "puntuacion": "rojo",
                "resumen": f"Error al procesar el video: {str(e)}",
                "procesamiento_exitoso": False
            }
        
        finally:
            # Limpiar archivo temporal
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.unlink(temp_video_path)
                    logger.info("Archivo temporal eliminado")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal: {e}")
    
    def _calculate_score(self, video_metrics: Dict, audio_metrics: Dict) -> str:
        """
        Calcula puntuación general basada en métricas
        Returns: "verde" | "amarillo" | "rojo"
        
        LÓGICA DE NEGOCIO:
        - Postura mala es un factor crítico que NO permite verde
        - Se necesita al menos 70% del score Y postura buena/regular para verde
        - Cualquier métrica muy baja fuerza amarillo o rojo
        """
        score = 0
        max_score = 5
        
        # Contacto visual (0-1 punto)
        contact_level = video_metrics.get("contacto_visual_nivel", "bajo")
        if contact_level == "alto":
            score += 1
        elif contact_level == "medio":
            score += 0.5
        
        # Expresividad (0-1 punto)
        expressiveness_level = video_metrics.get("expresividad_nivel", "baja")
        if expressiveness_level == "alta":
            score += 1
        elif expressiveness_level == "media":
            score += 0.5
        
        # Confianza (0-1 punto)
        confidence_level = video_metrics.get("confianza_nivel", "baja")
        if confidence_level == "alta":
            score += 1
        elif confidence_level == "media":
            score += 0.5
        
        # Muletillas (0-1 punto)
        muletillas_per_min = audio_metrics.get("muletillas_por_minuto", 0)
        if muletillas_per_min <= 2:
            score += 1
        elif muletillas_per_min <= 5:
            score += 0.5
        
        # Velocidad de habla (0-1 punto)
        velocidad = audio_metrics.get("velocidad_nivel", "desconocida")
        if velocidad == "normal":
            score += 1
        elif velocidad in ["lenta", "rápida"]:
            score += 0.5
        
        # Calcular porcentaje base
        percentage = (score / max_score) * 100
        
        # ⚠️ CONSISTENCIA SEMÁNTICA: Postura mala es factor limitante
        # No se puede obtener verde con postura mala, sin importar otras métricas
        # Esta es una regla de negocio que garantiza coherencia
        
        # Obtener postura desde main.py (clasificada en finalizar_practica)
        # Como no tenemos acceso directo aquí, usamos alineación de hombros
        alineacion_hombros = video_metrics.get("alineacion_hombros_promedio", 0)
        
        # Clasificar postura igual que en main.py
        if alineacion_hombros < 0.015:
            postura = "buena"
        elif alineacion_hombros < 0.03:
            postura = "regular"
        else:
            postura = "mala"
        
        # Aplicar lógica de negocio coherente
        if percentage >= 70 and postura in ["buena", "regular"]:
            return "verde"
        elif percentage >= 70 and postura == "mala":
            # Degrada a amarillo si tiene postura mala
            return "amarillo"
        elif percentage >= 40:
            return "amarillo"
        else:
            return "rojo"
    
    def _generate_summary(self, video_metrics: Dict, audio_metrics: Dict) -> str:
        """
        Genera un resumen textual del análisis
        """
        parts = []
        
        # Contacto visual
        contact_level = video_metrics.get("contacto_visual_nivel", "desconocido")
        contact_pct = video_metrics.get("contacto_visual_porcentaje", 0)
        parts.append(f"Contacto visual {contact_level} ({contact_pct:.0f}%)")
        
        # Expresividad
        expr_level = video_metrics.get("expresividad_nivel", "desconocida")
        parts.append(f"Expresividad {expr_level}")
        
        # Confianza
        conf_level = video_metrics.get("confianza_nivel", "desconocida")
        parts.append(f"Confianza {conf_level}")
        
        # Muletillas
        muletillas = audio_metrics.get("muletillas_total", 0)
        muletillas_per_min = audio_metrics.get("muletillas_por_minuto", 0)
        parts.append(f"{muletillas} muletillas ({muletillas_per_min:.1f}/min)")
        
        # Velocidad
        wpm = audio_metrics.get("palabras_por_minuto", 0)
        velocidad = audio_metrics.get("velocidad_nivel", "desconocida")
        parts.append(f"Velocidad {velocidad} ({wpm:.0f} palabras/min)")
        
        # Duración
        duration = audio_metrics.get("duracion_segundos", 0)
        parts.append(f"Duración: {duration:.0f}s")
        
        return ". ".join(parts) + "."
