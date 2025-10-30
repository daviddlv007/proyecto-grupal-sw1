# 🎤 API Práctica Oral# 🎤 API Práctica Oral



Sistema de análisis y entrenamiento de oratoria con IA. Procesa videos, extrae métricas de audio/video con MediaPipe, genera planes personalizados y gamificación con insignias.Sistema de análisis y entrenamiento de oratoria con IA. Procesa videos, extrae métricas de audio/video con MediaPipe, genera planes personalizados y gamificación con insignias.



## 🏗️ Arquitectura## �️ Arquitectura



**Stack**: FastAPI + PostgreSQL + MediaPipe + OpenCV + Caddy (HTTPS)  **Stack**: FastAPI + PostgreSQL + MediaPipe + OpenCV + Caddy (HTTPS)  

**Autenticación**: JWT (habilitada en producción, deshabilitada en desarrollo)  **Autenticación**: JWT (habilitada en producción, deshabilitada en desarrollo)  

**Persistencia**: PostgreSQL con SQLAlchemy ORM  **Persistencia**: PostgreSQL con SQLAlchemy ORM

**Deployment**: Docker Compose con health checks

## � Inicio Rápido

## 🚀 Inicio Rápido

### Desarrollo Local (autenticación deshabilitada)

### Desarrollo Local (autenticación deshabilitada)

```bash

```bashgit clone https://github.com/daviddlv007/proyecto-grupal-sw1.git

git clone https://github.com/daviddlv007/proyecto-grupal-sw1.gitcd proyecto-grupal-sw1

cd proyecto-grupal-sw1docker-compose -f docker-compose.dev.yml up --build -d

docker-compose -f docker-compose.dev.yml up --build -d```

```

✅ API: http://localhost:8000  

✅ API: http://localhost:8000  📚 Docs: http://localhost:8000/docs

📚 Docs: http://localhost:8000/docs

### Producción (autenticación habilitada)

### Producción (autenticación habilitada)

```bash

```bash./deploy.sh

./deploy.sh```

```

✅ API: https://softwaredlv.duckdns.org  

✅ API: https://softwaredlv.duckdns.org  📚 Docs: https://softwaredlv.duckdns.org/docs

📚 Docs: https://softwaredlv.duckdns.org/docs

### Ejecutar Tests

### Tests Completos

```bash

```bash# Editar test_api_complete_v2.sh:

# Editar línea 11 o 14 de test_api_complete_v2.sh según el entorno:# - Línea 11: BASE_URL="http://localhost:8000" (desarrollo)

# BASE_URL="http://localhost:8000"              # Desarrollo# - Línea 14: BASE_URL="https://softwaredlv.duckdns.org" (producción)

# BASE_URL="https://softwaredlv.duckdns.org"    # Producción

./test_api_complete_v2.sh

./test_api_complete_v2.sh```

```

## 📚 API Endpoints Completos

El script incluye limpieza de BD al final (opcional).

### 🔐 Autenticación

## 📚 Endpoints- `POST /auth/registrar` - Registro de usuarios con hash de contraseña

- `POST /auth/login` - Login con JWT (válido 24 horas)

### Autenticación (solo producción)- `GET /auth/yo` - Información del usuario autenticado

| Método | Endpoint | Descripción |

|--------|----------|-------------|### � Práctica y Análisis

| POST | `/auth/registrar` | Crear cuenta |- `POST /practica/iniciar` - Inicia sesión de grabación

| POST | `/auth/login` | Login → JWT (24h) |- `POST /practica/finalizar` - **Procesa video completo** con análisis real de audio/video

| GET | `/auth/yo` | Info usuario autenticado |- `GET /practica/{id}/analisis` - Análisis detallado con comentario de IA

- `GET /practica/historial` - Lista todas las prácticas del usuario

### Práctica- `GET /practica/{id}` - Detalle completo de una práctica

| Método | Endpoint | Descripción |

|--------|----------|-------------|### 📈 Progreso y Entrenamiento

| POST | `/practica/iniciar` | Inicia sesión de grabación |- `GET /plan/actual` - **Plan semanal personalizado** basado en debilidades

| POST | `/practica/finalizar` | Procesa video (análisis completo) |- `GET /progreso/resumen` - Resumen de progreso con tendencias temporales

| GET | `/practica/{id}/analisis` | Análisis detallado + comentario IA |

| GET | `/practica/historial` | Lista todas las prácticas |### 🏆 Recompensas

- `GET /recompensas/insignias` - Lista de 23 insignias obtenidas

### Progreso- `GET /recompensas/racha` - Racha actual del usuario

| Método | Endpoint | Descripción |

|--------|----------|-------------|### ⚙️ Administración

| GET | `/plan/actual` | Plan semanal personalizado |- `POST /admin/limpiar-bd` - Limpia toda la base de datos (⚠️ solo desarrollo)

| GET | `/progreso/resumen` | Tendencias y resumen |- `GET /health` - Health check del sistema

| GET | `/recompensas/insignias` | Insignias obtenidas (23 tipos) |

| GET | `/recompensas/racha` | Racha de días consecutivos |## 📊 Métricas Implementadas



### Admin### Análisis de Video (MediaPipe)

| Método | Endpoint | Descripción |- **Contacto Visual**: Orientación de mirada usando vectores faciales (alto >75%, medio 50-75%, bajo <50%)

|--------|----------|-------------|- **Expresividad Facial**: Movimiento de boca (40%) + cejas (30%) + manos (30%)

| POST | `/admin/limpiar-bd` | Limpia BD (usar con cuidado) |- **Gestos de Manos**: Detección y frecuencia (frecuente >50%, moderado 20-50%, escaso <20%)

| GET | `/health` | Health check |- **Postura Corporal**: Alineación de hombros (buena <0.015, regular 0.015-0.03, mala >0.03)

- **Orientación de Cabeza**: Estabilidad del movimiento cefálico

## 📊 Análisis Implementado

### Análisis de Audio

### Video (MediaPipe)- **Transcripción**: Google Speech Recognition

- **Contacto Visual**: Orientación de mirada (alto >75%, medio 50-75%, bajo <50%)- **Muletillas**: Detección de "eh", "este", "emm", "entonces", etc.

- **Expresividad Facial**: Movimiento boca (40%) + cejas (30%) + manos (30%)- **Velocidad**: Palabras/minuto (lenta <100, normal 100-160, rápida >160)

- **Gestos**: Frecuencia (frecuente >50%, moderado 20-50%, escaso <20%)- **Conteo de Palabras**: Total pronunciadas

- **Postura**: Alineación hombros (buena <0.015, regular 0.015-0.03, mala >0.03)

## 🏆 Sistema de Insignias (23 Tipos)

### Audio (Google Speech Recognition)

- **Transcripción**: Texto completo del discurso### Por Cantidad

- **Muletillas**: Detección de "eh", "este", "emm", "entonces"- 🎯 Primera práctica (1) → 👑 Orador profesional (50)

- **Velocidad**: Palabras/minuto (lenta <100, normal 100-160, rápida >160)

- **Palabras Totales**: Conteo completo### Por Métricas

- 🎤 Cero muletillas

## 🏆 Sistema de Gamificación- 👁️ Mirada profesional (>80%)

- 👀 Conexión total (>90%)

**23 tipos de insignias** basadas en:- 😊 Expresivo natural

- Cantidad de prácticas (1, 5, 10, 25, 50)- 👐 Manos comunicativas

- Métricas específicas (cero muletillas, contacto visual >80%, expresividad alta)- 🧍 Postura impecable

- Duración (resistencia >3 min, conferenciante >5 min)- ⏱️ Ritmo perfecto

- Perfección combinada- 💫 Práctica perfecta

- 📢 Orador resistente (>3 min)

**Rachas**: Días consecutivos practicando- 🎙️ Conferenciante (>5 min)



## 🛠️ Stack Técnico## 🛠️ Arquitectura



| Componente | Tecnología | Versión |### Stack Tecnológico

|------------|------------|---------|- **Backend**: FastAPI 0.104.1 + Uvicorn

| Backend | FastAPI | 0.104.1 |- **Base de Datos**: PostgreSQL 15 + SQLAlchemy ORM

| Base de Datos | PostgreSQL | 15 |- **Autenticación**: JWT con python-jose

| ORM | SQLAlchemy | 2.0.23 |- **Procesamiento**: MediaPipe + OpenCV + SpeechRecognition

| Análisis Video | MediaPipe | 0.10.21 |- **Containerización**: Docker Compose

| Análisis Audio | SpeechRecognition | 3.10.0 |- **Reverse Proxy**: Caddy con SSL automático (producción)

| Reverse Proxy | Caddy | 2.7 |

| Autenticación | JWT | python-jose 3.3.0 |### Seguridad

- ✅ HTTPS/TLS 1.3 

## 📁 Estructura del Proyecto- ✅ JWT para autenticación

- ✅ CORS configurado

```- ✅ Persistencia en PostgreSQL

proyecto-grupal-sw1/

├── backend/### Base de Datos (PostgreSQL)

│   ├── main.py              # API completa (1200+ líneas)- **usuarios**: Gestión de cuentas

│   ├── services/- **practicas**: Historial completo con métricas JSON

│   │   ├── audio_analyzer.py- **insignias**: Sistema de logros dinámico

│   │   ├── video_analyzer.py- **rachas**: Tracking de constancia

│   │   └── av_processor.py

│   ├── Dockerfile## 🧪 Testing

│   └── requirements.txt

├── infra/caddy/### Script de Prueba Completo

│   └── Caddyfile            # Config HTTPS```bash

├── docker-compose.dev.yml   # Desarrollo./test_api_complete_v2.sh

├── docker-compose.caddy.yml # Producción```

├── deploy.sh                # Deploy automático

├── test_api_complete_v2.sh  # Tests + limpieza BD### Ejemplos de Uso

└── README.md

```1. **Iniciar práctica**:

```bash

## 🔧 Variables de Entornocurl -X POST "http://localhost:8000/practica/iniciar"

```

### Desarrollo (`docker-compose.dev.yml`)

```env2. **Finalizar con video**:

ENVIRONMENT=development       # Deshabilita autenticación```bash

DATABASE_URL=postgresql://practica_user:practica_pass@db:5432/practica_dbcurl -X POST "http://localhost:8000/practica/finalizar" \

JWT_SECRET_KEY=dev-secret-key  -H "Content-Type: application/json" \

OPENAI_API_KEY=opcional  -d '{"idSesion": "abc123", "urlArchivo": "https://url-del-video.mp4"}'

``````



### Producción (`docker-compose.caddy.yml`)3. **Ver análisis detallado**:

```env```bash

ENVIRONMENT=production        # Habilita autenticacióncurl "http://localhost:8000/practica/1/analisis"

DATABASE_URL=postgresql://practica_user:practica_secure_password_2025@postgres:5432/practica_db```

JWT_SECRET_KEY=practica-oral-jwt-secret-prod-2025-ultra-secure

DOMAIN=softwaredlv.duckdns.org4. **Obtener plan personalizado**:

``````bash

curl "http://localhost:8000/plan/actual"

## 🚢 Despliegue```



### Manual### Documentación Interactiva

```bash

# En el servidorVisita http://localhost:8000/docs para:

cd /root/proyecto-grupal-sw1- ✅ Probar todos los endpoints en vivo

git pull origin main- ✅ Ver esquemas completos de request/response  

export DOMAIN=softwaredlv.duckdns.org- ✅ Modelos Pydantic correctamente definidos

docker compose -f docker-compose.caddy.yml up -d --build

```## 📋 Estado Actual



### Automático### ✅ Implementado y Funcional

```bash- ✅ Análisis completo de video con MediaPipe

./deploy.sh- ✅ Análisis de audio con transcripción

```- ✅ Sistema de insignias dinámico (23 tipos)

- ✅ Generación de planes personalizados

El script:- ✅ Comentarios de retroalimentación con IA (preparado para OpenAI)

1. Sube cambios a GitHub- ✅ Persistencia en PostgreSQL

2. Se conecta vía SSH al servidor- ✅ Documentación Swagger completa

3. Actualiza código- ✅ Tendencias y progreso temporal

4. Reconstruye contenedores

5. Verifica que todo funcione### 🔜 Mejoras Sugeridas

- [ ] Integración real con OpenAI API (código preparado)

## 🧪 Testing- [ ] Procesamiento asíncrono para videos largos

- [ ] Rate limiting y validación de URLs

### Flujo Completo- [ ] Storage dedicado para videos (S3)

```bash- [ ] Métricas adicionales (tono de voz, pausas estratégicas)

./test_api_complete_v2.sh

```## � Deployment



### Pruebas Individuales### Despliegue Automático en Producción

```bash

# Health check```bash

curl https://softwaredlv.duckdns.org/health# Ejecutar script de despliegue

./deploy.sh

# Iniciar práctica```

curl -X POST https://softwaredlv.duckdns.org/practica/iniciar

Este script:

# Plan personalizado1. Sube cambios a GitHub

curl https://softwaredlv.duckdns.org/plan/actual -H "user-id: 1"2. Se conecta al servidor vía SSH

```3. Actualiza el código

4. Reconstruye y levanta contenedores

### Limpieza de BD5. Verifica que la API responda correctamente

```bash

curl -X POST https://softwaredlv.duckdns.org/admin/limpiar-bd### Despliegue Manual

```

```bash

## 📈 Plan Personalizado# En el servidor de producción

cd /root/proyecto-grupal-sw1

El sistema genera planes semanales dinámicos basados en:git pull origin main

- Debilidades detectadas (contacto visual, muletillas, expresividad)export DOMAIN=softwaredlv.duckdns.org

- Nivel de usuariodocker compose -f docker-compose.caddy.yml up -d --build

- Historial de prácticas```



**Estructura**: 8 tareas distribuidas en 7 días con evaluaciones inicial y final.## 🏗️ Estructura del Proyecto



## 🔐 Autenticación```

proyecto-grupal-sw1/

### Producción (HTTPS)├── backend/              # API FastAPI

1. Registrar: `POST /auth/registrar`│   ├── main.py          # Lógica principal + endpoints

2. Login: `POST /auth/login` → recibir JWT│   ├── services/        # Análisis de audio/video

3. Usar JWT en header: `Authorization: Bearer {token}`│   ├── Dockerfile       # Container backend

│   └── requirements.txt # Dependencias Python

### Desarrollo (HTTP)├── infra/

Autenticación deshabilitada. No requiere JWT.│   └── caddy/

│       └── Caddyfile    # Configuración HTTPS

## 🐳 Docker├── docker-compose.dev.yml      # Desarrollo local

├── docker-compose.caddy.yml    # Producción con HTTPS

### Servicios en Desarrollo├── deploy.sh                   # Script de despliegue

- `db`: PostgreSQL 15├── test_api_complete_v2.sh     # Suite de tests

- `api`: Backend FastAPI con hot-reload└── README.md

```

### Servicios en Producción

- `postgres`: PostgreSQL 15 con volumen persistente## 🤝 Contribución

- `backend`: API FastAPI optimizada

- `caddy`: Reverse proxy con SSL automáticoEste proyecto es un MVP completo y funcional para análisis de oratoria con IA.



## 📞 Comandos ÚtilesProyecto académico - Software 1 - Universidad Mayor de San Simón



```bash## 📞 Soporte

# Ver logs

docker compose -f docker-compose.dev.yml logs -f api- 🐛 **Issues**: [GitHub Issues](https://github.com/daviddlv007/proyecto-grupal-sw1/issues)

- 🔗 **Repositorio**: https://github.com/daviddlv007/proyecto-grupal-sw1

# Reiniciar servicios- 🌐 **API en Producción**: https://softwaredlv.duckdns.org

docker compose -f docker-compose.dev.yml restart

---

# Acceder a BD

docker exec -it practica_postgres psql -U practica_user -d practica_db**Última actualización**: Octubre 2025

**Estado**: ✅ MVP Completo - Sistema funcional con PostgreSQL, análisis real de audio/video, y despliegue automático
# Ver tablas
docker exec -it practica_postgres psql -U practica_user -d practica_db -c '\dt'

# Limpiar todo
docker compose -f docker-compose.dev.yml down -v
```

## 🎯 Estado del Proyecto

✅ **Completado y Funcional**
- Sistema de análisis completo
- Base de datos persistente
- Autenticación JWT en producción
- HTTPS con certificado válido
- 12 endpoints funcionales
- 23 tipos de insignias
- Planes personalizados dinámicos
- Deploy automatizado

## 🔗 Enlaces

- **GitHub**: https://github.com/daviddlv007/proyecto-grupal-sw1
- **Producción**: https://softwaredlv.duckdns.org
- **Swagger Docs**: https://softwaredlv.duckdns.org/docs

---

**Proyecto académico** - Universidad Mayor de San Simón - Software 1 - 2025
