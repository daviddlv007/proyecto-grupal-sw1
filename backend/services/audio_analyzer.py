"""
Análisis de audio usando SpeechRecognition (LIVIANO) para transcripción y detección de muletillas
"""
import speech_recognition as sr
from pydub import AudioSegment
import re
import os
import tempfile
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioAnalyzer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Patrones de muletillas en español
        self.muletillas_patterns = [
            r'\beh+\b',
            r'\bum+\b',
            r'\bemm+\b',
            r'\bahh+\b',
            r'\beste\b',
            r'\bbueno\b',
            r'\bo sea\b',
            r'\bcomo que\b',
            r'\bpues\b',
            r'\bentonces\b',
            r'\bverdad\b',
            r'\bno\?\b',
        ]
    
    def transcribe_audio(self, video_path: str) -> Dict:
        """
        Transcribe el audio del video usando Google Speech Recognition (gratis, liviano)
        Returns: dict con transcripción y métricas básicas
        """
        audio_file = None
        try:
            logger.info(f"Iniciando transcripción de: {video_path}")
            
            # Extraer audio del MP4 usando pydub
            video = AudioSegment.from_file(video_path, format="mp4")
            duration_seconds = len(video) / 1000.0  # pydub usa milisegundos
            
            # Convertir a WAV temporal (SpeechRecognition necesita WAV)
            audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            video.export(audio_file.name, format="wav")
            
            # Transcribir con Google Speech Recognition
            with sr.AudioFile(audio_file.name) as source:
                audio_data = self.recognizer.record(source)
                try:
                    # Usar Google API (gratis, sin key para uso básico)
                    transcription = self.recognizer.recognize_google(
                        audio_data, 
                        language="es-ES"
                    )
                except sr.UnknownValueError:
                    logger.warning("No se pudo entender el audio")
                    transcription = ""
                except sr.RequestError as e:
                    logger.error(f"Error en el servicio de reconocimiento: {e}")
                    transcription = ""
            
            logger.info(f"Transcripción completada. Duración: {duration_seconds:.1f}s")
            
            return {
                "transcripcion": transcription,
                "duracion_segundos": duration_seconds,
                "idioma": "es"
            }
            
        except Exception as e:
            logger.error(f"Error al transcribir audio: {str(e)}")
            return {
                "transcripcion": "",
                "duracion_segundos": 0,
                "idioma": "es"
            }
        finally:
            # Limpiar archivo temporal
            if audio_file and os.path.exists(audio_file.name):
                try:
                    os.unlink(audio_file.name)
                except:
                    pass
    
    def detect_muletillas(self, transcription: str) -> Dict:
        """
        Detecta muletillas en la transcripción
        Returns: dict con cantidad y lista de muletillas encontradas
        """
        try:
            transcription_lower = transcription.lower()
            muletillas_found = []
            muletillas_count = 0
            
            for pattern in self.muletillas_patterns:
                matches = re.findall(pattern, transcription_lower, re.IGNORECASE)
                muletillas_count += len(matches)
                if matches:
                    muletillas_found.extend(matches)
            
            logger.info(f"Muletillas detectadas: {muletillas_count}")
            
            return {
                "muletillas_total": muletillas_count,
                "muletillas_lista": muletillas_found[:10]  # Primeras 10
            }
            
        except Exception as e:
            logger.error(f"Error al detectar muletillas: {str(e)}")
            return {
                "muletillas_total": 0,
                "muletillas_lista": []
            }
    
    def calculate_speech_rate(self, transcription: str, duration_seconds: float) -> Dict:
        """
        Calcula la velocidad de habla en palabras por minuto (WPM)
        """
        try:
            if duration_seconds == 0:
                return {"wpm": 0, "velocidad": "desconocida"}
            
            # Contar palabras
            words = transcription.split()
            word_count = len(words)
            
            # Calcular WPM
            duration_minutes = duration_seconds / 60
            wpm = word_count / duration_minutes if duration_minutes > 0 else 0
            
            # Clasificar velocidad
            if wpm < 120:
                velocidad = "lenta"
            elif wpm <= 180:
                velocidad = "normal"
            else:
                velocidad = "rápida"
            
            logger.info(f"Velocidad de habla: {wpm:.0f} WPM ({velocidad})")
            
            return {
                "wpm": round(wpm, 1),
                "velocidad": velocidad,
                "palabras_totales": word_count
            }
            
        except Exception as e:
            logger.error(f"Error al calcular velocidad de habla: {str(e)}")
            return {
                "wpm": 0,
                "velocidad": "desconocida",
                "palabras_totales": 0
            }
    
    def analyze_complete(self, video_path: str) -> Dict:
        """
        Análisis completo de audio: transcripción + muletillas + velocidad
        """
        try:
            # 1. Transcribir
            transcription_result = self.transcribe_audio(video_path)
            transcription = transcription_result["transcripcion"]
            duration = transcription_result["duracion_segundos"]
            
            if not transcription:
                logger.warning("No se pudo obtener transcripción")
                return self._default_audio_metrics()
            
            # 2. Detectar muletillas
            muletillas_result = self.detect_muletillas(transcription)
            
            # 3. Calcular velocidad de habla
            speech_rate_result = self.calculate_speech_rate(transcription, duration)
            
            # Calcular muletillas por minuto
            muletillas_por_minuto = 0
            if duration > 0:
                muletillas_por_minuto = (muletillas_result["muletillas_total"] / duration) * 60
            
            return {
                "transcripcion": transcription,
                "duracion_segundos": round(duration, 1),
                "muletillas_total": muletillas_result["muletillas_total"],
                "muletillas_por_minuto": round(muletillas_por_minuto, 1),
                "muletillas_ejemplos": muletillas_result["muletillas_lista"],
                "palabras_por_minuto": speech_rate_result["wpm"],
                "velocidad_nivel": speech_rate_result["velocidad"],
                "palabras_totales": speech_rate_result["palabras_totales"]
            }
            
        except Exception as e:
            logger.error(f"Error en análisis completo de audio: {str(e)}")
            return self._default_audio_metrics()
    
    def _default_audio_metrics(self) -> Dict:
        """Métricas por defecto en caso de error"""
        return {
            "transcripcion": "No se pudo procesar el audio",
            "duracion_segundos": 0,
            "muletillas_total": 0,
            "muletillas_por_minuto": 0,
            "muletillas_ejemplos": [],
            "palabras_por_minuto": 0,
            "velocidad_nivel": "desconocida",
            "palabras_totales": 0
        }
