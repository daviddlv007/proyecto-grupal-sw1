from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid
import hashlib

# Configuración
SECRET_KEY = "tu-secret-key-super-segura-para-mvp"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# FastAPI app
app = FastAPI(title="MVP Practica Oral API", version="1.1.0")

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
security = HTTPBearer()

# Entidades de dominio
class Usuario(BaseModel):
    id: int
    correo: str
    contrasena: Optional[str] = None  # No expuesto en respuestas

class SesionPractica(BaseModel):
    idSesion: str
    estado: str  # "grabando" | "procesando" | "listo"

class Metricas(BaseModel):
    muletillas: int
    fluidez: str
    velocidad: str
    claridad: str
    contactoVisual: str
    expresividad: str

class Practica(BaseModel):
    id: int
    idSesion: str
    fecha: str  # ISO date
    transcripcion: str
    metricas: Metricas
    puntuacion: str  # "verde" | "amarillo" | "rojo"
    urlArchivo: str

class Plan(BaseModel):
    id: int
    semana: int
    tareas: List[str]
    creadoEn: str  # ISO date-time

class Tendencias(BaseModel):
    muletillas: int
    fluidez: int
    contactoVisual: int
    expresividad: int
    claridad: int

class Progreso(BaseModel):
    id: int
    totalPracticas: int
    puntuacionPromedio: str  # "verde" | "amarillo" | "rojo"
    tendencias: Tendencias

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

# "Base de datos" en memoria para MVP con entidades tipadas
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Usuario:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = users_db.get(correo)
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Endpoints de autenticación
@app.post("/auth/registrar")
async def registrar(user_req: UserRegister):
    global user_counter
    
    if user_req.correo in users_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = hash_password(user_req.contrasena)
    
    user = Usuario(
        id=user_counter,
        correo=user_req.correo,
        contrasena=hashed_password
    )
    
    users_db[user_req.correo] = user
    
    # Inicializar datos del usuario
    insignias_db[user_counter] = [
        Insignia(
            id=1,
            nombre="Primera práctica",
            obtenidaEn="2025-09-01"
        )
    ]
    
    rachas_db[user_counter] = Racha(
        id=user_counter,
        rachaActual=1,
        unidad="dias"
    )
    
    user_counter += 1
    
    token = create_access_token(data={"sub": user_req.correo})
    
    return {
        "id": user.id,
        "correo": user.correo,
        "token": token
    }

@app.post("/auth/login")
async def login(user_req: UserLogin):
    db_user = users_db.get(user_req.correo)
    
    if not db_user or not verify_password(user_req.contrasena, db_user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = create_access_token(data={"sub": user_req.correo})
    
    return {"token": token}

@app.get("/auth/yo")
async def yo(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "correo": current_user.correo
    }

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

@app.post("/practica/finalizar")
async def finalizar_practica(data: PracticeFinalizar, current_user: Usuario = Depends(get_current_user)):
    global practice_counter
    
    session = sessions_db.get(data.idSesion)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Actualizar estado de sesión
    session.estado = "procesando"
    
    # Crear práctica con datos mock
    metricas = Metricas(
        muletillas=5,
        fluidez="alta",
        velocidad="rápida",
        claridad="media",
        contactoVisual="alto",
        expresividad="media"
    )
    
    practica = Practica(
        id=practice_counter,
        idSesion=data.idSesion,
        fecha=datetime.utcnow().strftime("%Y-%m-%d"),
        transcripcion="Hola a todos, hoy voy a hablar sobre...",
        metricas=metricas,
        puntuacion="amarillo",
        urlArchivo=data.urlArchivo
    )
    
    practices_db[practice_counter] = practica
    practice_counter += 1
    
    # Simular procesamiento completado
    session.estado = "listo"
    
    return {
        "idPractica": practica.id,
        "estado": "procesando"
    }

@app.get("/practica/{id}/analisis")
async def analisis_practica(id: int, current_user: Usuario = Depends(get_current_user)):
    practice = practices_db.get(id)
    
    if not practice:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    
    return {
        "idPractica": practice.id,
        "transcripcion": practice.transcripcion,
        "metricas": practice.metricas.model_dump(),
        "puntuacion": practice.puntuacion,
        "resumen": "El discurso fue comprensible, con buen contacto visual pero exceso de muletillas."
    }

@app.get("/practica/historial")
async def historial_practicas(current_user: Usuario = Depends(get_current_user)):
    user_practices = [
        {
            "id": p.id,
            "fecha": p.fecha,
            "puntuacion": p.puntuacion,
            "urlArchivo": p.urlArchivo
        }
        for p in practices_db.values()
    ]
    
    return user_practices

@app.get("/practica/{id}")
async def detalle_practica(id: int, current_user: Usuario = Depends(get_current_user)) -> Practica:
    practice = practices_db.get(id)
    
    if not practice:
        raise HTTPException(status_code=404, detail="Práctica no encontrada")
    
    return practice

# Endpoints adicionales
@app.get("/plan/actual")
async def plan_actual(current_user: Usuario = Depends(get_current_user)) -> Plan:
    # Datos mock para MVP
    plan = Plan(
        id=7,
        semana=1,
        tareas=[
            "Haz 3 charlas de 2 minutos sobre temas aleatorios",
            "Practica reducción de muletillas",
            "Concéntrate en claridad y ritmo"
        ],
        creadoEn="2025-09-23T10:15:00Z"
    )
    return plan

@app.get("/progreso/resumen")
async def progreso_resumen(current_user: Usuario = Depends(get_current_user)) -> Progreso:
    user_practices = [p for p in practices_db.values()]
    
    tendencias = Tendencias(
        muletillas=-20,
        fluidez=15,
        contactoVisual=12,
        expresividad=10,
        claridad=8
    )
    
    progreso = Progreso(
        id=current_user.id,
        totalPracticas=len(user_practices),
        puntuacionPromedio="verde",
        tendencias=tendencias
    )
    
    return progreso

@app.get("/recompensas/insignias")
async def insignias(current_user: Usuario = Depends(get_current_user)) -> List[Insignia]:
    user_insignias = insignias_db.get(current_user.id, [])
    return user_insignias

@app.get("/recompensas/racha")
async def racha(current_user: Usuario = Depends(get_current_user)) -> Racha:
    user_racha = rachas_db.get(current_user.id)
    if not user_racha:
        # Crear racha por defecto si no existe
        user_racha = Racha(
            id=current_user.id,
            rachaActual=5,
            unidad="dias"
        )
        rachas_db[current_user.id] = user_racha
    
    return user_racha

# Endpoint de salud
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)