"""
Análisis de video usando MediaPipe Face Mesh para análisis visual completo
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAnalyzer:
    def __init__(self):
        # Inicializar MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,  # Incluye iris para eye gaze
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Inicializar MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Inicializar MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Landmarks clave para análisis
        # Iris: 468-477 (iris izquierdo), 473-477 (iris derecho)
        # Ojos: 33, 133 (izquierdo), 362, 263 (derecho)
        # Boca: 61, 291, 0, 17
        # Cejas: 70, 300
        self.LEFT_IRIS = [469, 470, 471, 472]
        self.RIGHT_IRIS = [474, 475, 476, 477]
        self.LEFT_EYE = [33, 133, 160, 144]
        self.RIGHT_EYE = [362, 263, 385, 380]
        self.MOUTH = [61, 291, 0, 17, 13, 14]
        self.EYEBROWS = [70, 63, 105, 66, 107, 300, 293, 334, 296, 336]
        
    def analyze_video_complete(self, video_path: str) -> Dict:
        """
        Análisis completo de video: contacto visual, expresividad, estabilidad, manos, postura
        """
        try:
            # Limpiar métricas de sesiones anteriores
            self._all_gaze_metrics = []
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"No se pudo abrir el video: {video_path}")
                return self._default_metrics()
            
            # Variables de análisis
            total_frames = 0
            frames_with_face = 0
            eye_contact_frames = 0
            frames_with_hands = 0
            frames_with_pose = 0
            
            # Para expresividad (boca, cejas, manos)
            mouth_movements = []
            eyebrow_movements = []
            hand_movements = []  # Nueva métrica para manos
            
            # Para estabilidad (parpadeo y movimiento de cabeza)
            blink_count = 0
            head_movements = []
            previous_head_position = None
            previous_eye_state = None
            
            # Para postura
            shoulder_alignments = []
            
            # Procesar cada 2 frames para máxima precisión en videos cortos
            frame_skip = 2
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue
                
                total_frames += 1
                
                # Convertir BGR a RGB para MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]
                
                # Detectar face mesh
                face_results = self.face_mesh.process(rgb_frame)
                
                if face_results.multi_face_landmarks:
                    frames_with_face += 1
                    landmarks = face_results.multi_face_landmarks[0].landmark
                    
                    # 1. ANÁLISIS DE CONTACTO VISUAL (iris tracking)
                    is_looking_at_camera = self._analyze_eye_gaze(landmarks, w, h)
                    if is_looking_at_camera:
                        eye_contact_frames += 1
                    
                    # 2. ANÁLISIS DE EXPRESIVIDAD (movimiento facial)
                    mouth_movement = self._calculate_mouth_movement(landmarks)
                    eyebrow_movement = self._calculate_eyebrow_movement(landmarks)
                    mouth_movements.append(mouth_movement)
                    eyebrow_movements.append(eyebrow_movement)
                    
                    # 3. ANÁLISIS DE PARPADEO
                    current_eye_state = self._calculate_eye_open_ratio(landmarks)
                    if previous_eye_state is not None:
                        if previous_eye_state > 0.15 and current_eye_state < 0.1:
                            blink_count += 1
                    previous_eye_state = current_eye_state
                    
                    # 4. ANÁLISIS DE MOVIMIENTO DE CABEZA
                    current_head_pos = self._get_head_position(landmarks, w, h)
                    if previous_head_position is not None:
                        movement = np.linalg.norm(
                            np.array(current_head_pos) - np.array(previous_head_position)
                        ) / w
                        head_movements.append(movement)
                    previous_head_position = current_head_pos
                
                # Detectar manos y calcular movimiento
                hands_results = self.hands.process(rgb_frame)
                if hands_results.multi_hand_landmarks:
                    frames_with_hands += 1
                    # Calcular movimiento de manos (variación de posición)
                    hand_movement = self._calculate_hand_movement(hands_results.multi_hand_landmarks, w, h)
                    hand_movements.append(hand_movement)
                else:
                    # Sin manos visibles = sin movimiento
                    hand_movements.append(0.0)
                
                # Detectar postura
                pose_results = self.pose.process(rgb_frame)
                if pose_results.pose_landmarks:
                    frames_with_pose += 1
                    pose_landmarks = pose_results.pose_landmarks.landmark
                    
                    # Calcular alineación de hombros
                    left_shoulder = pose_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder = pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                    shoulder_alignment = abs(left_shoulder.y - right_shoulder.y)
                    shoulder_alignments.append(shoulder_alignment)
            
            cap.release()
            
            if total_frames == 0 or frames_with_face == 0:
                logger.warning("No se detectó cara en el video")
                return self._default_metrics()
            
            # Calcular métricas finales
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            duration_seconds = frame_count / fps
            
            # DEBUG: Logging de movimientos faciales
            logger.info(f"[EXPRESIVIDAD DEBUG] Mouth movements: n={len(mouth_movements)}, "
                       f"min={np.min(mouth_movements) if mouth_movements else 0:.4f}, "
                       f"max={np.max(mouth_movements) if mouth_movements else 0:.4f}, "
                       f"mean={np.mean(mouth_movements) if mouth_movements else 0:.4f}, "
                       f"std={np.std(mouth_movements) if mouth_movements else 0:.4f}")
            logger.info(f"[EXPRESIVIDAD DEBUG] Eyebrow movements: n={len(eyebrow_movements)}, "
                       f"min={np.min(eyebrow_movements) if eyebrow_movements else 0:.4f}, "
                       f"max={np.max(eyebrow_movements) if eyebrow_movements else 0:.4f}, "
                       f"mean={np.mean(eyebrow_movements) if eyebrow_movements else 0:.4f}, "
                       f"std={np.std(eyebrow_movements) if eyebrow_movements else 0:.4f}")
            
            # 1. Contacto visual - ENFOQUE SIMPLIFICADO Y ROBUSTO
            if hasattr(self, '_all_gaze_metrics') and len(self._all_gaze_metrics) > 0:
                data = self._all_gaze_metrics
                
                # Extraer las métricas más relevantes
                avg_deviations = np.array([m['avg_deviation'] for m in data])
                max_deviations = np.array([m['max_deviation'] for m in data])
                h_asymmetries = np.array([m['h_asymmetry'] for m in data])
                
                # Debug: Ver el rango de valores
                logger.info(f"[DEBUG] avg_deviations: min={np.min(avg_deviations):.4f}, max={np.max(avg_deviations):.4f}, mean={np.mean(avg_deviations):.4f}")
                
                # FILTRAR OUTLIERS: Remover valores donde avg_deviation > 2.0 (claramente errores de detección)
                valid_mask = avg_deviations < 2.0
                avg_deviations_clean = avg_deviations[valid_mask]
                max_deviations_clean = max_deviations[valid_mask]
                h_asymmetries_clean = h_asymmetries[valid_mask]
                
                logger.info(f"[FILTRO] Frames válidos: {len(avg_deviations_clean)}/{len(avg_deviations)} ({len(avg_deviations_clean)/len(avg_deviations)*100:.1f}%)")
                
                if len(avg_deviations_clean) < 3:  # Mínimo 3 frames para calcular estadísticas
                    logger.warning(f"Muy pocos frames válidos después de filtrar outliers: {len(avg_deviations_clean)}")
                    eye_contact_percentage = 0.0
                else:
                    # Calcular estadísticas robustas
                    metrics_stats = {
                        'avg_dev_mean': np.mean(avg_deviations_clean),
                        'avg_dev_median': np.median(avg_deviations_clean),
                        'avg_dev_std': np.std(avg_deviations_clean),
                        'avg_dev_p75': np.percentile(avg_deviations_clean, 75),
                        'avg_dev_p90': np.percentile(avg_deviations_clean, 90),
                        'max_dev_mean': np.mean(max_deviations_clean),
                        'max_dev_median': np.median(max_deviations_clean),
                        'max_dev_std': np.std(max_deviations_clean),
                        'max_dev_p75': np.percentile(max_deviations_clean, 75),
                        'max_dev_p90': np.percentile(max_deviations_clean, 90),
                        'h_asym_mean': np.mean(h_asymmetries_clean),
                        'h_asym_p75': np.percentile(h_asymmetries_clean, 75),
                    }
                
                # Logging exhaustivo para calibración
                logger.info("=" * 80)
                logger.info("ESTADÍSTICAS DE MIRADA:")
                for key, value in metrics_stats.items():
                    logger.info(f"  {key}: {value:.4f}")
                logger.info("=" * 80)
                
                # ============================================================
                # ALGORITMO MINIMALISTA - 2 VARIABLES CLAVE
                # ============================================================
                # 
                # Variable 1: avg_dev_std (Desviación Estándar)
                #   - Mide la VARIABILIDAD del movimiento de los ojos
                #   - Valor BAJO = mirada estable y consistente (mirando fijamente)
                #   - Valor ALTO = mirada errática (moviendo ojos constantemente)
                #
                # Variable 2: h_asym_p75 (Asimetría Horizontal P75)
                #   - Mide si ambos ojos miran al MISMO PUNTO
                #   - Valor BAJO = ojos alineados (ambos miran al mismo lugar)
                #   - Valor ALTO = ojos desalineados (cada ojo mira a diferente punto)
                #
                # ============================================================
                
                # DECISIÓN FINAL: Combinar mean (magnitud) y std (estabilidad)
                # mean = qué tan desviado está en promedio
                # std = qué tan estable/consistente es la mirada
                metric_mean = metrics_stats['avg_dev_mean']
                metric_std = metrics_stats['avg_dev_std']
                
                # Métrica combinada: 60% magnitud + 40% estabilidad
                combined_score = (metric_mean * 0.6) + (metric_std * 0.4)
                
                # Mapeo calibrado con desviación absoluta:
                # EXCELENTE: combined ≤ 0.008 → 100% (mirada centrada y estable)
                # MEDIO: combined = 0.010 → ~50%
                # MALO: combined ≥ 0.012 → 0% (desviada o inestable)
                if combined_score <= 0.008:
                    eye_contact_percentage = 100.0
                elif combined_score >= 0.012:
                    eye_contact_percentage = 0.0
                else:
                    # Interpolación lineal: (0.012 - valor) / 0.004 * 100
                    eye_contact_percentage = (0.012 - combined_score) / 0.004 * 100
                
                logger.info(f"[MÉTRICAS] mean={metric_mean:.4f}, std={metric_std:.4f}, combined={combined_score:.4f}")
                logger.info(f"[DECISIÓN] Contacto visual: {eye_contact_percentage:.1f}%")
                logger.info("=" * 80)
            else:
                # Método original como fallback
                eye_contact_percentage = (eye_contact_frames / frames_with_face) * 100 if frames_with_face > 0 else 0
            
            eye_contact_level = self._classify_eye_contact(eye_contact_percentage)
            
            # 2. Expresividad completa - BOCA + CEJAS + MANOS
            # La expresividad en oratoria combina movimiento facial y gestual
            # No modificamos el análisis de contacto visual (ojos)
            if len(mouth_movements) > 2 and len(eyebrow_movements) > 2 and len(hand_movements) > 2:
                # === BOCA: Sonrisas y apertura ===
                mouth_std = np.std(mouth_movements)
                mouth_range = np.max(mouth_movements) - np.min(mouth_movements)
                mouth_expressiveness = (mouth_std * 0.7) + (mouth_range * 0.3)
                
                # === CEJAS: Elevaciones para énfasis ===
                eyebrow_std = np.std(eyebrow_movements)
                eyebrow_range = np.max(eyebrow_movements) - np.min(eyebrow_movements)
                eyebrow_expressiveness = (eyebrow_std * 0.7) + (eyebrow_range * 0.3)
                
                # === MANOS: Gestos y movimientos ===
                hand_std = np.std(hand_movements)
                hand_range = np.max(hand_movements) - np.min(hand_movements)
                # Normalizar: si nunca hay manos visibles, el score es 0
                # Si hay manos, medir variación de movimiento
                hand_expressiveness = (hand_std * 0.7) + (hand_range * 0.3)
                
                # Score final: 40% boca, 30% cejas, 30% manos
                # La boca es ligeramente más importante, pero manos también son clave
                expressiveness_score = (mouth_expressiveness * 0.4) + \
                                      (eyebrow_expressiveness * 0.3) + \
                                      (hand_expressiveness * 0.3)
                
                logger.info(f"[EXPRESIVIDAD] boca: std={mouth_std:.4f}, range={mouth_range:.4f}, score={mouth_expressiveness:.4f}")
                logger.info(f"[EXPRESIVIDAD] cejas: std={eyebrow_std:.4f}, range={eyebrow_range:.4f}, score={eyebrow_expressiveness:.4f}")
                logger.info(f"[EXPRESIVIDAD] manos: std={hand_std:.4f}, range={hand_range:.4f}, score={hand_expressiveness:.4f}")
                logger.info(f"[EXPRESIVIDAD] SCORE FINAL={expressiveness_score:.4f}")
            else:
                expressiveness_score = 0.0
                logger.warning("[EXPRESIVIDAD] Muy pocos frames para calcular")
            
            expressiveness_level = self._classify_expressiveness(expressiveness_score)
            
            # 3. Estabilidad/Confianza
            avg_head_movement = np.mean(head_movements) if head_movements else 0
            blinks_per_minute = (blink_count / duration_seconds) * 60 if duration_seconds > 0 else 0
            confidence_score = self._calculate_confidence_score(avg_head_movement, blinks_per_minute)
            confidence_level = self._classify_confidence(confidence_score)
            
            # 4. Manos visibles
            hands_percentage = (frames_with_hands / total_frames) * 100 if total_frames > 0 else 0
            
            # 5. Alineación de hombros
            avg_shoulder_alignment = np.mean(shoulder_alignments) if shoulder_alignments else 0.02
            
            logger.info(f"Análisis visual completado:")
            logger.info(f"  - Contacto visual: {eye_contact_percentage:.1f}% ({eye_contact_level})")
            logger.info(f"  - Expresividad: {expressiveness_score:.2f} ({expressiveness_level})")
            logger.info(f"  - Confianza: {confidence_score:.2f} ({confidence_level})")
            logger.info(f"  - Manos visibles: {hands_percentage:.1f}%")
            logger.info(f"  - Alineación hombros: {avg_shoulder_alignment:.3f}")
            
            return {
                # Contacto visual
                "contacto_visual_porcentaje": round(eye_contact_percentage, 1),
                "contacto_visual_nivel": eye_contact_level,
                
                # Expresividad
                "expresividad_score": round(expressiveness_score, 4),  # 4 decimales para no perder precisión
                "expresividad_nivel": expressiveness_level,
                
                # Confianza/Estabilidad
                "confianza_score": round(confidence_score, 2),
                "confianza_nivel": confidence_level,
                "parpadeos_por_minuto": round(blinks_per_minute, 1),
                "movimiento_cabeza": round(avg_head_movement, 3),
                
                # Manos
                "porcentaje_manos_visibles": round(hands_percentage, 1),
                
                # Postura
                "alineacion_hombros_promedio": round(avg_shoulder_alignment, 3),
                
                # Estadísticas
                "frames_procesados": total_frames,
                "frames_con_cara": frames_with_face,
                "duracion_segundos": round(duration_seconds, 1)
            }
            
        except Exception as e:
            logger.error(f"Error al analizar video: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._default_metrics()
    
    def _analyze_eye_gaze(self, landmarks, frame_width, frame_height):
        """
        Analiza la dirección de la mirada usando vectores estándar de iris
        Enfoque simplificado basado en estándares de la industria
        landmarks: ya es face_landmarks.landmark (lista de NormalizedLandmark)
        """
        try:
            # ============ ENFOQUE ESTÁNDAR: Posición relativa del iris ============
            # Usar solo los landmarks esenciales de MediaPipe
            
            # Iris centers
            left_iris = landmarks[469]
            right_iris = landmarks[474]
            
            # Eye corners (para normalización)
            # CRÍTICO: Necesitamos que left.x < right.x para ambos ojos
            # Ojo izquierdo: 33 y 133 funcionan correctamente
            # Ojo derecho: Según logs, landmark 362 tiene MAYOR X que 263
            #              Por tanto: 263 debe ser "left" y 362 debe ser "right"
            left_eye_left = landmarks[33]    # Ojo izquierdo: esquina izquierda
            left_eye_right = landmarks[133]  # Ojo izquierdo: esquina derecha  
            right_eye_left = landmarks[263]  # Ojo derecho: esquina con MENOR X (cerca de nariz)
            right_eye_right = landmarks[362] # Ojo derecho: esquina con MAYOR X (exterior)
            
            # Eye vertical bounds
            left_eye_top = landmarks[159]
            left_eye_bottom = landmarks[145]
            right_eye_top = landmarks[386]
            right_eye_bottom = landmarks[374]
            
            # Calcular posición normalizada del iris (0.0 a 1.0)
            # Centro perfecto = 0.5, 0.5
            def normalize_iris_position(iris, eye_corner1, eye_corner2, eye_top, eye_bottom, eye_name="eye"):
                # Centro del ojo
                eye_min_x = min(eye_corner1.x, eye_corner2.x)
                eye_max_x = max(eye_corner1.x, eye_corner2.x)
                eye_center_x = (eye_min_x + eye_max_x) / 2
                eye_center_y = (eye_top.y + eye_bottom.y) / 2
                
                # DESVIACIÓN ABSOLUTA (sin normalizar)
                # Funciona para videos móvil, limitado en PC
                deviation_x = abs(iris.x - eye_center_x)
                deviation_y = abs(iris.y - eye_center_y)
                deviation = np.sqrt(deviation_x**2 + deviation_y**2)
                
                # Posición relativa (legacy, no se usa)
                h_pos = 0.5
                v_pos = 0.5
                
                return h_pos, v_pos, deviation
            
            left_h, left_v, left_dev = normalize_iris_position(
                left_iris, left_eye_left, left_eye_right, left_eye_top, left_eye_bottom, "LEFT_EYE"
            )
            right_h, right_v, right_dev = normalize_iris_position(
                right_iris, right_eye_left, right_eye_right, right_eye_top, right_eye_bottom, "RIGHT_EYE"
            )
            
            # Métricas clave
            avg_deviation = (left_dev + right_dev) / 2
            max_deviation = max(left_dev, right_dev)
            h_asymmetry = abs(left_h - right_h)
            v_asymmetry = abs(left_v - right_v)
            
            # ============ LOGGING EXHAUSTIVO PARA CALIBRACIÓN ============
            if not hasattr(self, '_all_gaze_metrics'):
                self._all_gaze_metrics = []
            
            # Solo agregar si al menos un ojo tiene datos válidos (deviation > 0)
            # Si ambos devolvieron (0.5, 0.5, 0.0), significa que fueron descartados
            if left_dev > 0 or right_dev > 0:
                frame_data = {
                    'left_h': left_h,
                    'left_v': left_v,
                    'left_dev': left_dev,
                    'right_h': right_h,
                    'right_v': right_v,
                    'right_dev': right_dev,
                    'avg_deviation': avg_deviation,
                    'max_deviation': max_deviation,
                    'h_asymmetry': h_asymmetry,
                    'v_asymmetry': v_asymmetry,
                }
                self._all_gaze_metrics.append(frame_data)
            else:
                # Debug: frame descartado porque ambos ojos son inválidos
                if not hasattr(self, '_logged_invalid_frame'):
                    logger.info(f"[DEBUG] Frame descartado: left_dev={left_dev}, right_dev={right_dev}")
                    self._logged_invalid_frame = True
            
            # Retornar True si ambos ojos miran cerca del centro
            # Este valor legacy no se usa en la decisión final
            return avg_deviation < 0.15
            
        except Exception as e:
            logger.error(f"Error en análisis de mirada: {e}")
            return False
    
    def _calculate_eye_width(self, landmarks, eye_indices: List[int], w: int) -> float:
        """Calcula el ancho del ojo"""
        try:
            eye_points = [landmarks[i] for i in eye_indices]
            x_coords = [p.x * w for p in eye_points]
            return max(x_coords) - min(x_coords)
        except:
            return 1.0
    
    def _calculate_mouth_movement(self, landmarks) -> float:
        """
        Calcula el movimiento/apertura de la boca (apertura vertical)
        Retorna la apertura vertical sin normalización (valores absolutos)
        """
        try:
            # Puntos superior e inferior de la boca
            upper = landmarks[13]  # Upper lip
            lower = landmarks[14]  # Lower lip
            
            # Distancia vertical (apertura) - valores normalizados ya por MediaPipe [0-1]
            mouth_height = abs(upper.y - lower.y)
            
            # MediaPipe ya proporciona coordenadas normalizadas [0-1]
            # No necesitamos normalizar más, solo retornar la apertura directa
            return mouth_height
            
        except Exception as e:
            return 0.0
    
    def _calculate_eyebrow_movement(self, landmarks) -> float:
        """
        Calcula la posición de las cejas relativa a los ojos
        Retorna la distancia normalizada entre cejas y ojos
        """
        try:
            # Puntos de cejas (promedio)
            eyebrow_points = [landmarks[i].y for i in self.EYEBROWS]
            avg_eyebrow_y = np.mean(eyebrow_points)
            
            # Puntos de ojos (promedio) para normalización
            left_eye_top = landmarks[159]
            right_eye_top = landmarks[386]
            avg_eye_y = (left_eye_top.y + right_eye_top.y) / 2
            
            # Distancia vertical entre cejas y ojos
            # Negativo = cejas levantadas, positivo = cejas bajas
            eyebrow_eye_distance = abs(avg_eyebrow_y - avg_eye_y)
            
            return eyebrow_eye_distance
            
        except Exception as e:
            return 0.0
    
    def _calculate_hand_movement(self, hand_landmarks_list, frame_width: int, frame_height: int) -> float:
        """
        Calcula el movimiento/amplitud de las manos
        Retorna una métrica de cuánto se mueven las manos (dispersión espacial)
        """
        try:
            if not hand_landmarks_list:
                return 0.0
            
            # Recolectar todas las posiciones de puntos de manos
            all_points = []
            for hand_landmarks in hand_landmarks_list:
                for landmark in hand_landmarks.landmark:
                    # Normalizado [0-1], no necesitamos multiplicar por w/h
                    all_points.append((landmark.x, landmark.y))
            
            if len(all_points) < 2:
                return 0.0
            
            # Calcular la dispersión (desviación estándar) de posiciones
            x_coords = [p[0] for p in all_points]
            y_coords = [p[1] for p in all_points]
            
            x_std = np.std(x_coords)
            y_std = np.std(y_coords)
            
            # Combinar dispersión en X e Y (movimiento total)
            movement = np.sqrt(x_std**2 + y_std**2)
            
            return movement
            
        except Exception as e:
            return 0.0
    
    def _calculate_eye_open_ratio(self, landmarks) -> float:
        """
        Calcula qué tan abiertos están los ojos (para detectar parpadeo)
        """
        try:
            # Ojo izquierdo: puntos verticales
            left_top = landmarks[159]
            left_bottom = landmarks[145]
            left_height = abs(left_top.y - left_bottom.y)
            
            # Ojo derecho
            right_top = landmarks[386]
            right_bottom = landmarks[374]
            right_height = abs(right_top.y - right_bottom.y)
            
            avg_height = (left_height + right_height) / 2
            return avg_height
            
        except:
            return 0.2  # Valor por defecto (ojos abiertos)
    
    def _get_head_position(self, landmarks, w: int, h: int) -> Tuple[float, float]:
        """
        Obtiene la posición de la cabeza (centro de la cara)
        """
        try:
            # Usar punto de la nariz como referencia
            nose_tip = landmarks[1]
            return (nose_tip.x * w, nose_tip.y * h)
        except:
            return (0, 0)
    
    def _get_landmark_center(self, landmarks, indices: List[int], w: int, h: int) -> Tuple[float, float]:
        """
        Calcula el centro de un conjunto de landmarks
        """
        points = [landmarks[i] for i in indices]
        center_x = np.mean([p.x for p in points]) * w
        center_y = np.mean([p.y for p in points]) * h
        return (center_x, center_y)
    
    def _classify_eye_contact(self, percentage: float) -> str:
        if percentage >= 70:
            return "alto"
        elif percentage >= 40:
            return "medio"
        else:
            return "bajo"
    
    def _classify_expressiveness(self, score: float) -> str:
        # Score basado en variación de boca + cejas + manos
        # Umbrales calibrados basados en pruebas reales:
        # - Video CON expresividad: ~0.0277
        # - Video SIN expresividad: ~0.0092
        # - Video BUENA oratoria: ~0.0595
        # - Video MALA oratoria: ~0.0020
        if score >= 0.0200:
            return "alta"
        elif score >= 0.0100:
            return "media"
        else:
            return "baja"
    
    def _calculate_confidence_score(self, head_movement: float, blinks_per_min: float) -> float:
        """
        Calcula score de confianza basado en estabilidad
        - Menos movimiento de cabeza = más confianza
        - Parpadeo normal (15-20/min) = más confianza
        """
        # Normalizar movimiento de cabeza (escala 0-1, invertida)
        movement_score = max(0, 1 - (head_movement * 20))
        
        # Normalizar parpadeo (15-20 es óptimo, fuera de rango penaliza)
        if 12 <= blinks_per_min <= 25:
            blink_score = 1.0
        elif blinks_per_min < 12:
            blink_score = blinks_per_min / 12
        else:
            blink_score = max(0, 1 - ((blinks_per_min - 25) / 30))
        
        # Promedio ponderado
        confidence = (movement_score * 0.6 + blink_score * 0.4)
        return confidence
    
    def _classify_confidence(self, score: float) -> str:
        if score >= 0.7:
            return "alta"
        elif score >= 0.4:
            return "media"
        else:
            return "baja"
    
    def _default_metrics(self) -> Dict:
        """Métricas por defecto en caso de error"""
        return {
            "contacto_visual_porcentaje": 0.0,
            "contacto_visual_nivel": "desconocido",
            "expresividad_score": 0.0,
            "expresividad_nivel": "desconocida",
            "confianza_score": 0.0,
            "confianza_nivel": "desconocida",
            "parpadeos_por_minuto": 0.0,
            "movimiento_cabeza": 0.0,
            "porcentaje_manos_visibles": 0.0,
            "alineacion_hombros_promedio": 0.0,
            "frames_procesados": 0,
            "frames_con_cara": 0,
            "duracion_segundos": 0.0
        }
    
    def cleanup(self):
        """Liberar recursos de MediaPipe"""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'hands'):
            self.hands.close()
        if hasattr(self, 'pose'):
            self.pose.close()
            self.face_mesh.close()

