from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid
import hashlib
import os
from services.av_processor import AVProcessor
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

# Configuración
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-secret-key-super-segura-para-mvp")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY_PLACEHOLDER")

# Base de datos PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://practica_user:practica_pass@db:5432/practica_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🔧 Control de autenticación según entorno
# En desarrollo: autenticación deshabilitada
# En producción: autenticación habilitada
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DISABLE_AUTH = ENVIRONMENT == "development"  # False en producción, True en desarrollo

# Modelos de base de datos (SQLAlchemy)
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    correo = Column(String, unique=True, index=True)
    contrasena = Column(String)
    creado_en = Column(DateTime, default=datetime.utcnow)

class PracticaDB(Base):
    __tablename__ = "practicas"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    id_sesion = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
    transcripcion = Column(Text)
    metricas_json = Column(Text)  # JSON serializado
    puntuacion = Column(String)
    url_archivo = Column(String)
    comentario = Column(Text)  # Comentario generado por IA

class InsigniaDB(Base):
    __tablename__ = "insignias"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    nombre = Column(String)
    descripcion = Column(String)
    obtenida_en = Column(DateTime, default=datetime.utcnow)

class RachaDB(Base):
    __tablename__ = "rachas"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    racha_actual = Column(Integer, default=0)
    ultima_practica = Column(DateTime)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Dependency para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(title="MVP Practica Oral API", version="2.0.0")

# Inicializar procesador A/V
av_processor = AVProcessor()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad (simplificada para MVP)
import hashlib
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)  # auto_error=False permite requests sin token

# Entidades de dominio
class Usuario(BaseModel):
    id: int
    correo: str
    contrasena: Optional[str] = None  # No expuesto en respuestas

class SesionPractica(BaseModel):
    idSesion: str
    estado: str  # "grabando" | "procesando" | "listo"

class Metricas(BaseModel):
    # Audio
    transcripcion: str
    muletillas: int
    velocidad: str  # "lenta" | "normal" | "rápida"
    palabras_total: int
    duracion_segundos: float
    
    # Visual
    contacto_visual_porcentaje: float
    contacto_visual_nivel: str  # "alto" | "medio" | "bajo"
    expresividad_score: float
    expresividad_nivel: str  # "alta" | "media" | "baja"
    gestos_manos: str  # "frecuente" | "moderado" | "escaso"
    porcentaje_manos_visibles: float
    orientacion_cabeza: str  # "estable" | "inestable"
    postura: str  # "buena" | "regular" | "mala"
    alineacion_hombros: float
    
    # Calidad
    calidad_video: str  # "buena" | "aceptable" | "mala"
    calidad_audio: str  # "buena" | "aceptable" | "mala"

class Practica(BaseModel):
    id: int
    idSesion: str
    fecha: str  # ISO date
    transcripcion: str
    metricas: Metricas
    puntuacion: str  # "verde" | "amarillo" | "rojo"
    urlArchivo: str

class TareaDia(BaseModel):
    dia: int
    tarea: str

class Plan(BaseModel):
    semana: int
    objetivos: List[str]  # Lista de debilidades a mejorar
    tareas: List[TareaDia]  # Tareas específicas por día
    creadoEn: str  # ISO date-time

class Tendencias(BaseModel):
    muletillas: Dict[str, float]  # {"promedio_antes": X, "promedio_ahora": Y, "cambio": Z}
    contacto_visual: Dict[str, float]
    expresividad: Dict[str, float]
    velocidad: Dict[str, float]

class Progreso(BaseModel):
    totalPracticas: int
    puntuacionPromedio: str  # "verde" | "amarillo" | "rojo"
    tendencias: Tendencias
    ultimaPractica: Optional[str] = None  # ISO date

class Insignia(BaseModel):
    id: int
    nombre: str
    obtenidaEn: str  # ISO date

class Racha(BaseModel):
    id: int
    rachaActual: int
    unidad: str  # "dias" | "semanas"

# Modelos para requests
class UserRegister(BaseModel):
    correo: str
    contrasena: str

class UserLogin(BaseModel):
    correo: str
    contrasena: str

class PracticeFinalizar(BaseModel):
    idSesion: str
    urlArchivo: str

# Modelos de respuesta para Swagger
class AuthResponse(BaseModel):
    id: int
    correo: str
    token: str

class TokenResponse(BaseModel):
    token: str

class UserInfoResponse(BaseModel):
    id: int
    correo: str

class FinalizarPracticaResponse(BaseModel):
    idPractica: int
    estado: str
    resumen: str
    comentario: str
    metricas: Metricas

class AnalisisPracticaResponse(BaseModel):
    idPractica: int
    transcripcion: str
    metricas: Metricas
    puntuacion: str
    resumen: str
    comentario: str

class HistorialItem(BaseModel):
    id: int
    fecha: str
    puntuacion: str
    urlArchivo: str

class HistorialResponse(BaseModel):
    practicas: List[HistorialItem]

# "Base de datos" en memoria para MVP con entidades tipadas (Deprecado - usar PostgreSQL)
users_db: Dict[str, Usuario] = {}
practices_db: Dict[int, Practica] = {}
sessions_db: Dict[str, SesionPractica] = {}
plans_db: Dict[int, Plan] = {}
insignias_db: Dict[int, List[Insignia]] = {}  # por user_id
rachas_db: Dict[int, Racha] = {}  # por user_id
user_counter = 1
practice_counter = 1
plan_counter = 1
insignia_counter = 1

# Funciones de utilidad (simplificadas para MVP)
def hash_password(password: str) -> str:
    # Para MVP, usamos SHA256 simple (en producción usar bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generar_comentario_ia(metricas: Metricas) -> str:
    """
    Genera un comentario de retroalimentación usando OpenAI API.
    Por ahora retorna un comentario basado en reglas hasta que se configure la API key.
    """
    # TODO: Cuando el usuario configure OPENAI_API_KEY, descomentar la integración real
    # import openai
    # openai.api_key = OPENAI_API_KEY
    # 
    # prompt = f"""Eres un coach de oratoria. Analiza estas métricas de una práctica oral y da retroalimentación breve (máximo 3 oraciones):
    # - Muletillas: {metricas.muletillas}
    # - Velocidad: {metricas.velocidad}
    # - Contacto visual: {metricas.contacto_visual_nivel} ({metricas.contacto_visual_porcentaje}%)
    # - Expresividad: {metricas.expresividad_nivel}
    # - Gestos: {metricas.gestos_manos}
    # - Postura: {metricas.postura}
    # 
    # Sé específico, constructivo y motivador."""
    # 
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{"role": "user", "content": prompt}],
    #     max_tokens=150
    # )
    # return response.choices[0].message.content
    
    # Generación basada en reglas (mientras no hay API key configurada)
    comentarios = []
    
    # Evaluar muletillas
    if metricas.muletillas == 0:
        comentarios.append("¡Excelente! No detectamos muletillas en tu discurso.")
    elif metricas.muletillas <= 2:
        comentarios.append("Buen trabajo con las muletillas, solo detectamos un par.")
    elif metricas.muletillas <= 5:
        comentarios.append(f"Detectamos {metricas.muletillas} muletillas. Intenta hacer pausas conscientes en lugar de usar palabras de relleno.")
    else:
        comentarios.append(f"Encontramos {metricas.muletillas} muletillas. Practica hacer pausas deliberadas para reducirlas significativamente.")
    
    # Evaluar contacto visual
    if metricas.contacto_visual_nivel == "alto":
        comentarios.append(f"Tu contacto visual fue excelente ({metricas.contacto_visual_porcentaje:.0f}%), mantienes bien la conexión con la audiencia.")
    elif metricas.contacto_visual_nivel == "medio":
        comentarios.append(f"Tu contacto visual está en un nivel aceptable ({metricas.contacto_visual_porcentaje:.0f}%). Intenta mantener la mirada más tiempo hacia la cámara.")
    else:
        comentarios.append(f"Tu contacto visual necesita mejora ({metricas.contacto_visual_porcentaje:.0f}%). Practica mirando directamente a la cámara durante tus ensayos.")
    
    # Evaluar expresividad
    if metricas.expresividad_nivel == "alta":
        comentarios.append("Tu expresividad facial es muy buena, transmites emoción naturalmente.")
    elif metricas.expresividad_nivel == "media":
        comentarios.append("Tu expresividad es moderada. Intenta exagerar un poco más tus expresiones faciales para conectar mejor con la audiencia.")
    else:
        comentarios.append("Trabaja en tu expresividad facial: practica frente al espejo moviendo más las cejas, sonriendo y mostrando emociones al hablar.")
    
    # Evaluar velocidad
    if metricas.velocidad == "lenta":
        comentarios.append("Tu velocidad es un poco lenta. Intenta aumentar el ritmo ligeramente para mantener el interés.")
    elif metricas.velocidad == "rápida":
        comentarios.append("Hablas un poco rápido. Respira y ralentiza el ritmo para que tu audiencia pueda seguirte mejor.")
    
    # Evaluar gestos
    if metricas.gestos_manos == "escaso":
        comentarios.append("Usa más tus manos para enfatizar ideas clave, esto ayuda a mantener el interés visual.")
    
    # Evaluar postura
    if metricas.postura == "mala":
        comentarios.append("Trabaja en tu postura: mantén los hombros relajados y alineados para proyectar más confianza.")
    
    # Seleccionar los 3-4 comentarios más relevantes
    return " ".join(comentarios[:4])

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    # 🔧 MODO DESARROLLO: Bypass de autenticación
    if DISABLE_AUTH:
        # Retornar usuario de prueba sin validar token
        return Usuario(
            id=999,
            correo="test@development.local",
            contrasena=None
        )
    
    # Autenticación normal
    if not credentials:
        raise HTTPException(status_code=401, detail="Credenciales no proporcionadas")
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_db = db.query(UsuarioDB).filter(UsuarioDB.correo == correo).first()
        if user_db is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return Usuario(
            id=user_db.id,
            correo=user_db.correo,
            contrasena=None
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Endpoints de autenticación
@app.post("/auth/registrar", response_model=AuthResponse)
async def registrar(user_req: UserRegister, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(UsuarioDB).filter(UsuarioDB.correo == user_req.correo).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = hash_password(user_req.contrasena)
    
    # Crear usuario en BD
    user_db = UsuarioDB(
        correo=user_req.correo,
        contrasena=hashed_password
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    
    # Inicializar racha del usuario
    racha = RachaDB(
        user_id=user_db.id,
        racha_actual=0,
        ultima_practica=None
    )
    db.add(racha)
    db.commit()
    
    token = create_access_token(data={"sub": user_req.correo})
    
    return AuthResponse(
        id=user_db.id,
        correo=user_db.correo,
        token=token
    )

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_req: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UsuarioDB).filter(UsuarioDB.correo == user_req.correo).first()
    
    if not db_user or not verify_password(user_req.contrasena, db_user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = create_access_token(data={"sub": user_req.correo})
    
    return TokenResponse(token=token)

@app.get("/auth/yo", response_model=UserInfoResponse)
async def yo(current_user: Usuario = Depends(get_current_user)):
    return UserInfoResponse(
        id=current_user.id,
        correo=current_user.correo
    )

# Endpoints de práctica
@app.post("/practica/iniciar")
async def iniciar_practica(current_user: Usuario = Depends(get_current_user)) -> SesionPractica:
    session_id = str(uuid.uuid4())[:8]
    
    sesion = SesionPractica(
        idSesion=session_id,
        estado="grabando"
    )
    
    sessions_db[session_id] = sesion
    
    return sesion

@app.post("/practica/finalizar", response_model=FinalizarPracticaResponse)
async def finalizar_practica(
    data: PracticeFinalizar, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = sessions_db.get(data.idSesion)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Actualizar estado de sesión
    session.estado = "procesando"
    
    try:
        # Procesar video con análisis real
        analisis_resultado = av_processor.process_video(data.urlArchivo)
        
        if not analisis_resultado.get("procesamiento_exitoso"):
            raise HTTPException(status_code=500, detail="Error al procesar el video")
        
        # Extraer métricas del análisis
        video_data = analisis_resultado["video"]
        audio_data = analisis_resultado["audio"]
        
        # Clasificar gestos de manos
        manos_pct = video_data.get("porcentaje_manos_visibles", 0)
        if manos_pct >= 50:
            gestos = "frecuente"
        elif manos_pct >= 20:
            gestos = "moderado"
        else:
            gestos = "escaso"
        
        # Clasificar orientación de cabeza
        mov_cabeza = video_data.get("movimiento_cabeza", 0)
        orientacion = "estable" if mov_cabeza < 0.02 else "inestable"
        
        # Clasificar postura
        # NOTA: Umbrales calibrados para videos móviles (verticales)
        # Videos móviles tienen valores ~20-40x más altos que videos de escritorio
        # debido a diferencias en encuadre y orientación de cámara
        alineacion = video_data.get("alineacion_hombros_promedio", 0)
        
        # Detectar si es video móvil (valores altos de alineación)
        if alineacion > 0.1:
            # Umbrales para videos móviles (vertical)
            if alineacion < 0.68:
                postura = "buena"       # < 0.68: Postura recta y alineada
            elif alineacion < 0.75:
                postura = "regular"     # 0.68-0.75: Postura aceptable
            else:
                postura = "mala"        # >= 0.75: Postura desalineada
        else:
            # Umbrales para videos de escritorio (horizontal) - legacy
            if alineacion < 0.015:
                postura = "buena"
            elif alineacion < 0.03:
                postura = "regular"
            else:
                postura = "mala"
        
        # Clasificar calidad de video/audio (simplificado)
        calidad_video = "buena" if video_data.get("frames_con_cara", 0) > 0 else "mala"
        calidad_audio = "buena" if audio_data.get("palabras_totales", 0) > 0 else "mala"
        
        # Crear métricas optimizadas
        metricas = Metricas(
            transcripcion=audio_data.get("transcripcion", ""),
            muletillas=audio_data.get("muletillas_total", 0),
            velocidad=audio_data.get("velocidad_nivel", "normal"),
            palabras_total=audio_data.get("palabras_totales", 0),
            duracion_segundos=audio_data.get("duracion_segundos", 0),
            contacto_visual_porcentaje=video_data.get("contacto_visual_porcentaje", 0),
            contacto_visual_nivel=video_data.get("contacto_visual_nivel", "medio"),
            expresividad_score=video_data.get("expresividad_score", 0.0),
            expresividad_nivel=video_data.get("expresividad_nivel", "media"),
            gestos_manos=gestos,
            porcentaje_manos_visibles=manos_pct,
            orientacion_cabeza=orientacion,
            postura=postura,
            alineacion_hombros=alineacion,
            calidad_video=calidad_video,
            calidad_audio=calidad_audio
        )
        
        # Generar comentario de retroalimentación
        comentario = generar_comentario_ia(metricas)
        
        # Crear práctica en base de datos
        practica_db = PracticaDB(
            user_id=current_user.id,
            id_sesion=data.idSesion,
            transcripcion=audio_data.get("transcripcion", ""),
            metricas_json=json.dumps(metricas.model_dump()),
            puntuacion=analisis_resultado.get("puntuacion", "amarillo"),
            url_archivo=data.urlArchivo,
            comentario=comentario
        )
        db.add(practica_db)
        db.commit()
        db.refresh(practica_db)
        
        # Actualizar insignias y racha
        _actualizar_recompensas(current_user.id, practica_db.id, db)
        
        # Marcar sesión como lista
        session.estado = "listo"
        
        return FinalizarPracticaResponse(
            idPractica=practica_db.id,
            estado="listo",
            resumen=analisis_resultado.get("resumen", "Análisis completado"),
            comentario=comentario,
            metricas=metricas
        )
        
    except HTTPException:
        raise
    except Exception as e:
        session.estado = "error"
        raise HTTPException(status_code=500, detail=f"Error al procesar práctica: {str(e)}")

@app.get("/practica/{id}/analisis", response_model=AnalisisPracticaResponse)
async def analisis_practica(
    id: int, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    practice = db.query(PracticaDB).filter(
        PracticaDB.id == id,
        PracticaDB.user_id == current_user.id
    ).first()
    
    if not practice:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    
    metricas = Metricas(**json.loads(practice.metricas_json))
    
    return AnalisisPracticaResponse(
        idPractica=practice.id,
        transcripcion=practice.transcripcion,
        metricas=metricas,
        puntuacion=practice.puntuacion,
        resumen="Análisis detallado de tu práctica oral.",
        comentario=practice.comentario
    )

@app.get("/practica/historial", response_model=List[HistorialItem])
async def historial_practicas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    practicas = db.query(PracticaDB).filter(
        PracticaDB.user_id == current_user.id
    ).order_by(PracticaDB.fecha.desc()).all()
    
    return [
        HistorialItem(
            id=p.id,
            fecha=p.fecha.isoformat(),
            puntuacion=p.puntuacion,
            urlArchivo=p.url_archivo
        )
        for p in practicas
    ]

@app.get("/practica/{id}", response_model=Practica)
async def detalle_practica(
    id: int, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    practice = db.query(PracticaDB).filter(
        PracticaDB.id == id,
        PracticaDB.user_id == current_user.id
    ).first()
    
    if not practice:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    
    metricas = Metricas(**json.loads(practice.metricas_json))
    
    return Practica(
        id=practice.id,
        idSesion=practice.id_sesion,
        fecha=practice.fecha.isoformat(),
        transcripcion=practice.transcripcion,
        metricas=metricas,
        puntuacion=practice.puntuacion,
        urlArchivo=practice.url_archivo
    )

# Funciones auxiliares para lógica de negocio

def _actualizar_recompensas(user_id: int, practice_id: int, db: Session):
    """Actualiza insignias y racha automáticamente al completar una práctica"""
    
    # Obtener práctica actual
    practica = db.query(PracticaDB).filter(PracticaDB.id == practice_id).first()
    if not practica:
        return
    
    metricas = Metricas(**json.loads(practica.metricas_json))
    
    # Total de prácticas del usuario
    total_practicas = db.query(PracticaDB).filter(PracticaDB.user_id == user_id).count()
    
    # Helper para verificar si ya tiene una insignia
    def tiene_insignia(nombre: str) -> bool:
        return db.query(InsigniaDB).filter(
            InsigniaDB.user_id == user_id,
            InsigniaDB.nombre == nombre
        ).first() is not None
    
    def crear_insignia(nombre: str, descripcion: str):
        insignia = InsigniaDB(
            user_id=user_id,
            nombre=nombre,
            descripcion=descripcion
        )
        db.add(insignia)
    
    # === INSIGNIAS POR CANTIDAD DE PRÁCTICAS ===
    if total_practicas == 1 and not tiene_insignia("🎯 Primera práctica"):
        crear_insignia("🎯 Primera práctica", "Completaste tu primera sesión de práctica")
    
    if total_practicas == 3 and not tiene_insignia("🔥 Constancia"):
        crear_insignia("🔥 Constancia", "Realizaste 3 prácticas consecutivas")
    
    if total_practicas == 5 and not tiene_insignia("⭐ Practicante dedicado"):
        crear_insignia("⭐ Practicante dedicado", "Alcanzaste 5 sesiones de práctica")
    
    if total_practicas == 10 and not tiene_insignia("🏆 Orador en formación"):
        crear_insignia("🏆 Orador en formación", "Completaste 10 prácticas de oratoria")
    
    if total_practicas == 20 and not tiene_insignia("💎 Maestro de la práctica"):
        crear_insignia("💎 Maestro de la práctica", "Alcanzaste 20 sesiones de entrenamiento")
    
    if total_practicas == 50 and not tiene_insignia("👑 Orador profesional"):
        crear_insignia("👑 Orador profesional", "Impresionante: 50 prácticas completadas")
    
    # === INSIGNIAS POR MÉTRICAS ESPECÍFICAS ===
    
    # Muletillas
    if metricas.muletillas == 0 and not tiene_insignia("🎤 Cero muletillas"):
        crear_insignia("🎤 Cero muletillas", "Completaste una práctica sin ninguna muletilla")
    
    # Contacto visual
    if metricas.contacto_visual_porcentaje >= 80 and not tiene_insignia("👁️ Mirada profesional"):
        crear_insignia("👁️ Mirada profesional", "Mantuviste contacto visual por encima del 80%")
    
    if metricas.contacto_visual_porcentaje >= 90 and not tiene_insignia("👀 Conexión total"):
        crear_insignia("👀 Conexión total", "Contacto visual superior al 90%")
    
    # Expresividad
    if metricas.expresividad_nivel == "alta" and not tiene_insignia("😊 Expresivo natural"):
        crear_insignia("😊 Expresivo natural", "Tu expresividad facial fue excepcional")
    
    # Gestos
    if metricas.gestos_manos == "frecuente" and not tiene_insignia("👐 Manos comunicativas"):
        crear_insignia("👐 Manos comunicativas", "Usaste gestos de manos de forma efectiva")
    
    # Postura
    if metricas.postura == "buena" and not tiene_insignia("🧍 Postura impecable"):
        crear_insignia("🧍 Postura impecable", "Mantuviste una excelente postura corporal")
    
    # Velocidad ideal
    if metricas.velocidad == "normal" and not tiene_insignia("⏱️ Ritmo perfecto"):
        crear_insignia("⏱️ Ritmo perfecto", "Tu velocidad de habla fue ideal")
    
    # Práctica perfecta (todos los criterios altos)
    if (metricas.muletillas <= 1 and 
        metricas.contacto_visual_porcentaje >= 75 and
        metricas.expresividad_nivel in ["alta", "media"] and
        metricas.velocidad == "normal" and
        metricas.postura == "buena" and
        not tiene_insignia("💫 Práctica perfecta")):
        crear_insignia("💫 Práctica perfecta", "Excelencia en todos los criterios de evaluación")
    
    # Práctica larga
    if metricas.duracion_segundos >= 180 and not tiene_insignia("📢 Orador resistente"):
        crear_insignia("📢 Orador resistente", "Presentación de más de 3 minutos")
    
    if metricas.duracion_segundos >= 300 and not tiene_insignia("🎙️ Conferenciante"):
        crear_insignia("🎙️ Conferenciante", "Presentación de más de 5 minutos")
    
    # Muchas palabras
    if metricas.palabras_total >= 200 and not tiene_insignia("📚 Verboso efectivo"):
        crear_insignia("📚 Verboso efectivo", "Más de 200 palabras en una práctica")
    
    # === RACHA ===
    # Lógica de negocio: Racha = días CONSECUTIVOS con al menos 1 práctica
    # No es cantidad de prácticas, sino días seguidos practicando
    racha = db.query(RachaDB).filter(RachaDB.user_id == user_id).first()
    if racha:
        # Obtener todas las prácticas del usuario
        todas_practicas = db.query(PracticaDB).filter(
            PracticaDB.user_id == user_id
        ).order_by(PracticaDB.fecha.desc()).all()
        
        # Extraer fechas únicas (días en que practicó)
        fechas_unicas = set(p.fecha.date() for p in todas_practicas)
        fechas_ordenadas = sorted(fechas_unicas, reverse=True)
        
        # Calcular días consecutivos desde hoy hacia atrás
        from datetime import timedelta
        racha_dias = 0
        fecha_esperada = datetime.utcnow().date()
        
        for fecha_practica in fechas_ordenadas:
            if fecha_practica == fecha_esperada:
                racha_dias += 1
                fecha_esperada -= timedelta(days=1)
            else:
                break  # Se rompió la racha consecutiva
        
        racha.racha_actual = racha_dias
        racha.ultima_practica = datetime.utcnow()
    
    # Insignias por racha
    if racha and racha.racha_actual >= 7 and not tiene_insignia("📅 Semana completa"):
        crear_insignia("📅 Semana completa", "7 prácticas realizadas")
    
    if racha and racha.racha_actual >= 30 and not tiene_insignia("📆 Mes dedicado"):
        crear_insignia("📆 Mes dedicado", "30 prácticas completadas")
    
    db.commit()

def _calcular_tendencias(user_id: int, db: Session) -> Tendencias:
    """
    Calcula tendencias reales basadas en las prácticas almacenadas
    
    LÓGICA DE NEGOCIO:
    - Compara últimas N prácticas vs N prácticas previas
    - Para entrenamiento, "últimas 3 sesiones" es más intuitivo que "segunda mitad"
    - Si hay menos de 6 prácticas, compara última vs resto (mejor que nada)
    """
    practicas = db.query(PracticaDB).filter(
        PracticaDB.user_id == user_id
    ).order_by(PracticaDB.fecha).all()
    
    if len(practicas) == 0:
        return Tendencias(
            muletillas={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            contacto_visual={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            expresividad={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            velocidad={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0}
        )
    
    # Ventana de comparación: últimas N sesiones
    VENTANA = 3
    total = len(practicas)
    
    if total < 2:
        # Con 1 práctica no hay tendencia
        return Tendencias(
            muletillas={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            contacto_visual={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            expresividad={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0},
            velocidad={"promedio_antes": 0, "promedio_ahora": 0, "cambio": 0}
        )
    elif total < 2 * VENTANA:
        # Pocas prácticas: comparar últimas vs primeras
        mitad = max(1, total // 2)
        practicas_antes = practicas[:mitad]
        practicas_ahora = practicas[mitad:]
    else:
        # Suficientes prácticas: últimas VENTANA vs VENTANA previas
        practicas_ahora = practicas[-VENTANA:]
        practicas_antes = practicas[-2*VENTANA:-VENTANA]
    
    # Convertir a métricas
    def obtener_metricas(practicas_list):
        return [Metricas(**json.loads(p.metricas_json)) for p in practicas_list]
    
    metricas_antes = obtener_metricas(practicas_antes)
    metricas_ahora = obtener_metricas(practicas_ahora)
    
    # Calcular promedios
    def promedio_muletillas(metricas_list):
        if not metricas_list:
            return 0
        return sum(m.muletillas for m in metricas_list) / len(metricas_list)
    
    def promedio_contacto(metricas_list):
        if not metricas_list:
            return 0
        return sum(m.contacto_visual_porcentaje for m in metricas_list) / len(metricas_list)
    
    def promedio_expresividad(metricas_list):
        if not metricas_list:
            return 0
        return sum(m.expresividad_score for m in metricas_list) / len(metricas_list)
    
    def promedio_velocidad(metricas_list):
        if not metricas_list:
            return 0
        # Convertir a número: lenta=0, normal=1, rápida=2
        valores = []
        for m in metricas_list:
            if m.velocidad == "lenta":
                valores.append(0)
            elif m.velocidad == "normal":
                valores.append(1)
            else:
                valores.append(2)
        return sum(valores) / len(valores) if valores else 1
    
    muletillas_antes = promedio_muletillas(metricas_antes)
    muletillas_ahora = promedio_muletillas(metricas_ahora)
    
    contacto_antes = promedio_contacto(metricas_antes)
    contacto_ahora = promedio_contacto(metricas_ahora)
    
    expresividad_antes = promedio_expresividad(metricas_antes)
    expresividad_ahora = promedio_expresividad(metricas_ahora)
    
    velocidad_antes = promedio_velocidad(metricas_antes)
    velocidad_ahora = promedio_velocidad(metricas_ahora)
    
    return Tendencias(
        muletillas={
            "promedio_antes": round(muletillas_antes, 1),
            "promedio_ahora": round(muletillas_ahora, 1),
            "cambio": round(((muletillas_antes - muletillas_ahora) / max(muletillas_antes, 0.1)) * 100, 1)
        },
        contacto_visual={
            "promedio_antes": round(contacto_antes, 1),
            "promedio_ahora": round(contacto_ahora, 1),
            "cambio": round(((contacto_ahora - contacto_antes) / max(contacto_antes, 0.1)) * 100, 1)
        },
        expresividad={
            "promedio_antes": round(expresividad_antes, 2),
            "promedio_ahora": round(expresividad_ahora, 2),
            "cambio": round(((expresividad_ahora - expresividad_antes) / max(expresividad_antes, 0.01)) * 100, 1)
        },
        velocidad={
            "promedio_antes": round(velocidad_antes, 2),
            "promedio_ahora": round(velocidad_ahora, 2),
            "cambio": round(((velocidad_ahora - velocidad_antes) / max(velocidad_antes, 0.1)) * 100, 1)
        }
    )

def _identificar_debilidades(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Identifica las principales debilidades del usuario basándose en las últimas prácticas"""
    
    # Obtener últimas 5 prácticas
    practicas = db.query(PracticaDB).filter(
        PracticaDB.user_id == user_id
    ).order_by(PracticaDB.fecha.desc()).limit(5).all()
    
    if not practicas:
        return [
            {"area": "contacto_visual", "nivel": "bajo", "prioridad": 1},
            {"area": "muletillas", "nivel": "medio", "prioridad": 2},
            {"area": "expresividad", "nivel": "medio", "prioridad": 3}
        ]
    
    # Analizar métricas
    metricas_list = [Metricas(**json.loads(p.metricas_json)) for p in practicas]
    
    debilidades = []
    
    # Analizar muletillas
    promedio_muletillas = sum(m.muletillas for m in metricas_list) / len(metricas_list)
    if promedio_muletillas > 5:
        debilidades.append({"area": "muletillas", "nivel": "alto", "prioridad": 1, "valor": promedio_muletillas})
    elif promedio_muletillas > 2:
        debilidades.append({"area": "muletillas", "nivel": "medio", "prioridad": 2, "valor": promedio_muletillas})
    
    # Analizar contacto visual
    promedio_contacto = sum(m.contacto_visual_porcentaje for m in metricas_list) / len(metricas_list)
    if promedio_contacto < 50:
        debilidades.append({"area": "contacto_visual", "nivel": "alto", "prioridad": 1, "valor": promedio_contacto})
    elif promedio_contacto < 70:
        debilidades.append({"area": "contacto_visual", "nivel": "medio", "prioridad": 2, "valor": promedio_contacto})
    
    # Analizar expresividad
    promedio_expresividad = sum(m.expresividad_score for m in metricas_list) / len(metricas_list)
    niveles_bajos = sum(1 for m in metricas_list if m.expresividad_nivel == "baja")
    if niveles_bajos > len(metricas_list) / 2:
        debilidades.append({"area": "expresividad", "nivel": "alto", "prioridad": 1, "valor": promedio_expresividad})
    elif promedio_expresividad < 0.06:
        debilidades.append({"area": "expresividad", "nivel": "medio", "prioridad": 2, "valor": promedio_expresividad})
    
    # Analizar velocidad
    velocidades = [m.velocidad for m in metricas_list]
    velocidad_problemas = velocidades.count("lenta") + velocidades.count("rápida")
    if velocidad_problemas > len(metricas_list) / 2:
        debilidades.append({"area": "velocidad", "nivel": "medio", "prioridad": 2, "valor": velocidad_problemas})
    
    # Analizar gestos
    gestos = [m.gestos_manos for m in metricas_list]
    gestos_escasos = gestos.count("escaso")
    if gestos_escasos > len(metricas_list) / 2:
        debilidades.append({"area": "gestos", "nivel": "medio", "prioridad": 2, "valor": gestos_escasos})
    
    # Analizar postura
    posturas = [m.postura for m in metricas_list]
    posturas_malas = posturas.count("mala") + posturas.count("regular")
    if posturas_malas > len(metricas_list) / 2:
        debilidades.append({"area": "postura", "nivel": "medio", "prioridad": 3, "valor": posturas_malas})
    
    # Ordenar por prioridad
    debilidades.sort(key=lambda x: (x["prioridad"], -x.get("valor", 0)))
    
    # Si no hay debilidades, enfocarse en perfeccionamiento
    if not debilidades:
        return [
            {"area": "perfeccionamiento", "nivel": "avanzado", "prioridad": 1},
            {"area": "confianza", "nivel": "avanzado", "prioridad": 2}
        ]
    
    return debilidades[:3]  # Máximo 3 debilidades

def _generar_plan_dinamico(debilidades: List[Dict[str, Any]]) -> Plan:
    """Genera un plan semanal personalizado basado en las debilidades del usuario"""
    
    # Base de ejercicios por área y nivel
    ejercicios_por_area = {
        "muletillas": {
            "alto": [
                "Graba 1 minuto de discurso. Por cada muletilla, haz 10 segundos de pausa y repite la frase sin ella",
                "Lee en voz alta 3 minutos sustituyendo TODAS las muletillas por pausas de 2 segundos",
                "Practica un discurso de 2 minutos con un familiar que cuente tus muletillas. Meta: máximo 3",
                "Graba explicando un concepto complejo sin usar 'eh', 'este', 'entonces'. Si lo haces, empieza de nuevo",
                "Técnica del espejo: habla 5 minutos mirándote, cada muletilla = anotación. Objetivo: bajar a la mitad"
            ],
            "medio": [
                "Graba 2 minutos y anota cada muletilla. Vuelve a grabar intentando reducir 50%",
                "Practica reemplazar muletillas con respiraciones profundas conscientes",
                "Lee noticias en voz alta durante 5 minutos, haciendo pausas en lugar de muletillas",
                "Graba respondiendo 3 preguntas improvisadas sin usar palabras de relleno"
            ]
        },
        "contacto_visual": {
            "alto": [
                "Ejercicio de fijación: mira un punto en la cámara por 30 segundos sin desviar la mirada",
                "Graba 2 minutos manteniendo contacto visual 90% del tiempo. Revisa y corrige",
                "Practica con un compañero: mantén contacto visual durante 3 minutos de conversación",
                "Técnica 'regla 80/20': 80% mirando a cámara, 20% a notas. Practica con un speech de 3 minutos",
                "Graba presentando algo que amas, enfocándote solo en mantener la mirada en la lente"
            ],
            "medio": [
                "Mira a la cámara mientras cuentas una historia de 1 minuto",
                "Practica alternar entre cámara y notas: 10 segundos cámara, 2 segundos notas",
                "Graba un video de 2 minutos intentando mantener contacto visual 70%+",
                "Ejercicio con espejo: mantén contacto visual contigo mismo durante 2 minutos hablando"
            ]
        },
        "expresividad": {
            "alto": [
                "Ejercicio de exageración: frente al espejo, exagera TODAS tus expresiones por 3 minutos",
                "Graba leyendo un cuento infantil con máxima expresividad facial",
                "Practica contar 3 emociones diferentes (alegría, sorpresa, preocupación) con tu rostro",
                "Técnica 'rostro activo': graba 2 minutos moviendo cejas, sonriendo, mostrando sorpresa al hablar",
                "Imita a tu orador favorito: copia sus expresiones faciales durante 5 minutos"
            ],
            "medio": [
                "Practica sonreír mientras hablas durante 2 minutos frente al espejo",
                "Graba explicando algo emocionante, enfocándote en mostrar emoción en tu rostro",
                "Ejercicio de cejas: sube y baja las cejas mientras hablas para enfatizar ideas",
                "Graba contando una anécdota divertida con expresiones faciales naturales"
            ]
        },
        "velocidad": {
            "medio": [
                "Cronometra: lee un párrafo y cuenta las palabras. Objetivo: 130-150 palabras/minuto",
                "Practica hablar con un metrónomo a 140 BPM (palabras por minuto)",
                "Graba un discurso de 2 minutos, luego ajusta tu velocidad según feedback",
                "Técnica de respiración: respira cada 10-15 palabras para controlar el ritmo",
                "Lee noticias en voz alta durante 5 minutos manteniendo velocidad constante"
            ]
        },
        "gestos": {
            "medio": [
                "Practica hablar con las manos: usa gestos para ilustrar cada idea principal",
                "Graba 2 minutos manteniendo las manos siempre visibles y en movimiento",
                "Técnica '3 gestos base': practica abierto, cerrado y señalar mientras hablas",
                "Mira TED Talks y copia los gestos de manos de los oradores durante 5 minutos",
                "Explica un concepto visual (ej: tamaños, direcciones) usando SOLO gestos"
            ]
        },
        "postura": {
            "medio": [
                "Ejercicio de alineación: párate con espalda contra la pared 2 minutos, luego graba manteniendo esa postura",
                "Practica 'power pose' por 1 minuto antes de grabar tu discurso",
                "Graba de cuerpo completo y revisa: hombros relajados, espalda recta, peso equilibrado",
                "Técnica de anclaje: pies separados ancho de hombros, practica hablar 3 minutos",
                "Ejercicio con libro: equilibra un libro en la cabeza mientras hablas 2 minutos"
            ]
        },
        "perfeccionamiento": {
            "avanzado": [
                "Graba una presentación de 5 minutos aplicando TODAS las técnicas aprendidas",
                "Practica improvisación: elige 3 temas al azar y habla 1 minuto de cada uno",
                "Simula una entrevista: responde 5 preguntas difíciles manteniendo calma y claridad",
                "Técnica del storytelling: cuenta una historia personal con inicio, desarrollo y cierre en 3 minutos",
                "Masterclass: prepara y graba una mini-clase de 7 minutos sobre algo que dominas"
            ]
        },
        "confianza": {
            "avanzado": [
                "Habla sobre tus logros durante 3 minutos con seguridad y sin minimizar",
                "Graba respondiendo críticas constructivas con calma y profesionalismo",
                "Practica mantener contacto visual y postura poderosa durante 5 minutos de discurso",
                "Presenta un tema controversial defendiendo tu posición con seguridad",
                "Graba una auto-presentación profesional de 2 minutos (elevator pitch)"
            ]
        }
    }
    
    # Generar tareas para la semana
    tareas_plan = []
    dia = 1
    objetivos_nombres = []
    
    # Día 1: Evaluación inicial
    tareas_plan.append(TareaDia(
        dia=1,
        tarea="📊 Evaluación: Graba un video libre de 2-3 minutos para establecer tu línea base de esta semana"
    ))
    dia += 1
    
    # Días 2-6: Ejercicios específicos según debilidades (2 ejercicios por debilidad)
    for debilidad in debilidades[:3]:
        area = debilidad["area"]
        nivel = debilidad.get("nivel", "medio")
        objetivos_nombres.append(area)
        
        ejercicios = ejercicios_por_area.get(area, {}).get(nivel, ejercicios_por_area.get(area, {}).get("medio", []))
        
        # Seleccionar ejercicios variados
        import random
        ejercicios_seleccionados = random.sample(ejercicios, min(2, len(ejercicios)))
        
        for ejercicio in ejercicios_seleccionados:
            if dia <= 6:
                tareas_plan.append(TareaDia(dia=dia, tarea=f"🎯 {area.replace('_', ' ').title()}: {ejercicio}"))
                dia += 1
    
    # Día 7: Evaluación final y comparación
    tareas_plan.append(TareaDia(
        dia=7,
        tarea="✅ Evaluación final: Graba el mismo video del día 1 y compara tu progreso en las áreas trabajadas"
    ))
    
    # Completar días faltantes si es necesario
    ejercicios_generales = [
        "🎤 Practica libre: Graba 3 minutos sobre un tema de tu elección aplicando todo lo aprendido",
        "📚 Lee en voz alta: 5 minutos de un libro o artículo, enfocándote en claridad y expresividad",
        "🎭 Improvisación: Elige 3 palabras al azar y crea un discurso de 2 minutos conectándolas",
        "🎬 Análisis: Ve un TED Talk, identifica 3 técnicas del orador e imítalas en un video de 2 minutos"
    ]
    
    while dia <= 7:
        import random
        tarea_general = random.choice(ejercicios_generales)
        tareas_plan.append(TareaDia(dia=dia, tarea=tarea_general))
        dia += 1
    
    return Plan(
        semana=1,
        objetivos=objetivos_nombres[:3],
        tareas=tareas_plan,
        creadoEn=datetime.utcnow().isoformat()
    )

# Endpoints adicionales
@app.get("/plan/actual", response_model=Plan)
async def plan_actual(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Plan:
    """Genera un plan personalizado basado en las debilidades detectadas"""
    debilidades = _identificar_debilidades(current_user.id, db)
    plan = _generar_plan_dinamico(debilidades)
    return plan

@app.get("/progreso/resumen", response_model=Progreso)
async def progreso_resumen(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Progreso:
    """Calcula el progreso real del usuario basándose en sus prácticas"""
    practicas = db.query(PracticaDB).filter(
        PracticaDB.user_id == current_user.id
    ).all()
    
    if len(practicas) == 0:
        return Progreso(
            totalPracticas=0,
            puntuacionPromedio="amarillo",
            tendencias=_calcular_tendencias(current_user.id, db),
            ultimaPractica=None
        )
    
    # Calcular puntuación promedio
    puntuaciones = {"verde": 0, "amarillo": 0, "rojo": 0}
    for p in practicas:
        puntuaciones[p.puntuacion] += 1
    
    if puntuaciones["verde"] > len(practicas) / 2:
        puntuacion_promedio = "verde"
    elif puntuaciones["rojo"] > len(practicas) / 2:
        puntuacion_promedio = "rojo"
    else:
        puntuacion_promedio = "amarillo"
    
    # Última práctica
    ultima = max(practicas, key=lambda p: p.fecha)
    
    return Progreso(
        totalPracticas=len(practicas),
        puntuacionPromedio=puntuacion_promedio,
        tendencias=_calcular_tendencias(current_user.id, db),
        ultimaPractica=ultima.fecha.isoformat()
    )

@app.get("/recompensas/insignias", response_model=List[Insignia])
async def insignias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Insignia]:
    """Devuelve las insignias obtenidas por el usuario"""
    insignias_db_list = db.query(InsigniaDB).filter(
        InsigniaDB.user_id == current_user.id
    ).order_by(InsigniaDB.obtenida_en.desc()).all()
    
    return [
        Insignia(
            id=i.id,
            nombre=i.nombre,
            obtenidaEn=i.obtenida_en.isoformat()
        )
        for i in insignias_db_list
    ]

@app.get("/recompensas/racha", response_model=Racha)
async def racha(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Racha:
    """Devuelve la racha actual del usuario"""
    racha_db = db.query(RachaDB).filter(RachaDB.user_id == current_user.id).first()
    
    if not racha_db:
        # Crear racha inicial
        racha_db = RachaDB(
            user_id=current_user.id,
            racha_actual=0,
            ultima_practica=None
        )
        db.add(racha_db)
        db.commit()
        db.refresh(racha_db)
    
    return Racha(
        id=racha_db.id,
        rachaActual=racha_db.racha_actual,
        unidad="dias"
    )

# Endpoint de administración
@app.post("/admin/limpiar-bd")
async def limpiar_base_datos(db: Session = Depends(get_db)):
    """
    ⚠️ PELIGRO: Elimina TODOS los datos de la base de datos.
    Solo usar en desarrollo/testing.
    """
    try:
        # Eliminar todos los registros
        db.query(InsigniaDB).delete()
        db.query(PracticaDB).delete()
        db.query(RachaDB).delete()
        db.query(UsuarioDB).delete()
        
        # Limpiar sesiones en memoria
        sessions_db.clear()
        
        db.commit()
        
        return {
            "status": "success",
            "mensaje": "Base de datos limpiada completamente",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar BD: {str(e)}")

# Endpoint de salud
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)