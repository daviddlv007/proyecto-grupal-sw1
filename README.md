# API Práctica Oral 🎤

Sistema completo de análisis y entrenamiento de oratoria con IA, que procesa videos en tiempo real, 
extrae métricas avanzadas de audio y video, genera retroalimentación inteligente con IA, y crea 
planes de mejora personalizados.

## ✨ Características Principales

- 🎥 **Análisis de Video en Tiempo Real**: MediaPipe Face Mesh + Hands + Pose
- 🎙️ **Análisis de Audio**: Transcripción, detección de muletillas, velocidad de habla
- 🤖 **Retroalimentación con IA**: Comentarios personalizados (preparado para OpenAI)
- 📊 **Métricas Avanzadas**: Contacto visual, expresividad facial, gestos, postura
- 🏆 **Sistema de Gamificación**: 23 insignias dinámicas + rachas
- 📈 **Planes Personalizados**: Generación automática basada en debilidades detectadas
- 💾 **Persistencia de Datos**: PostgreSQL con SQLAlchemy ORM
- 📝 **Documentación Automática**: Swagger UI integrado

## 🌐 Enlaces Importantes

- **Documentación Swagger**: http://localhost:8000/docs (desarrollo)
- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Producción**: https://softwaredlv.duckdns.org

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/daviddlv007/proyecto-grupal-sw1.git
cd proyecto-grupal-sw1

# Levantar servicios (PostgreSQL + API)
docker-compose -f docker-compose.dev.yml up --build -d

# Ver logs
docker logs -f proyecto-grupal-sw1-api-1

# Ejecutar pruebas
./test_api_complete_v2.sh
```

La API estará disponible en: http://localhost:8000  
Swagger UI en: http://localhost:8000/docs

### Producción

```bash
# Desplegar en producción con Caddy (HTTPS automático)
docker-compose -f docker-compose.caddy.yml up -d
```

## 📚 API Endpoints Completos

### 🔐 Autenticación
- `POST /auth/registrar` - Registro de usuarios con hash de contraseña
- `POST /auth/login` - Login con JWT (válido 24 horas)
- `GET /auth/yo` - Información del usuario autenticado

### � Práctica y Análisis
- `POST /practica/iniciar` - Inicia sesión de grabación
- `POST /practica/finalizar` - **Procesa video completo** con análisis real de audio/video
- `GET /practica/{id}/analisis` - Análisis detallado con comentario de IA
- `GET /practica/historial` - Lista todas las prácticas del usuario
- `GET /practica/{id}` - Detalle completo de una práctica

### 📈 Progreso y Entrenamiento
- `GET /plan/actual` - **Plan semanal personalizado** basado en debilidades
- `GET /progreso/resumen` - Resumen de progreso con tendencias temporales

### 🏆 Recompensas
- `GET /recompensas/insignias` - Lista de 23 insignias obtenidas
- `GET /recompensas/racha` - Racha actual del usuario

### ⚙️ Administración
- `POST /admin/limpiar-bd` - Limpia toda la base de datos (⚠️ solo desarrollo)
- `GET /health` - Health check del sistema

## 📊 Métricas Implementadas

### Análisis de Video (MediaPipe)
- **Contacto Visual**: Orientación de mirada usando vectores faciales (alto >75%, medio 50-75%, bajo <50%)
- **Expresividad Facial**: Movimiento de boca (40%) + cejas (30%) + manos (30%)
- **Gestos de Manos**: Detección y frecuencia (frecuente >50%, moderado 20-50%, escaso <20%)
- **Postura Corporal**: Alineación de hombros (buena <0.015, regular 0.015-0.03, mala >0.03)
- **Orientación de Cabeza**: Estabilidad del movimiento cefálico

### Análisis de Audio
- **Transcripción**: Google Speech Recognition
- **Muletillas**: Detección de "eh", "este", "emm", "entonces", etc.
- **Velocidad**: Palabras/minuto (lenta <100, normal 100-160, rápida >160)
- **Conteo de Palabras**: Total pronunciadas

## 🏆 Sistema de Insignias (23 Tipos)

### Por Cantidad
- 🎯 Primera práctica (1) → 👑 Orador profesional (50)

### Por Métricas
- 🎤 Cero muletillas
- 👁️ Mirada profesional (>80%)
- 👀 Conexión total (>90%)
- 😊 Expresivo natural
- 👐 Manos comunicativas
- 🧍 Postura impecable
- ⏱️ Ritmo perfecto
- 💫 Práctica perfecta
- 📢 Orador resistente (>3 min)
- 🎙️ Conferenciante (>5 min)

## 🛠️ Arquitectura

### Stack Tecnológico
- **Backend**: FastAPI 0.104.1 + Uvicorn
- **Base de Datos**: PostgreSQL 15 + SQLAlchemy ORM
- **Autenticación**: JWT con python-jose
- **Procesamiento**: MediaPipe + OpenCV + SpeechRecognition
- **Containerización**: Docker Compose
- **Reverse Proxy**: Caddy con SSL automático (producción)

### Seguridad
- ✅ HTTPS/TLS 1.3 
- ✅ JWT para autenticación
- ✅ CORS configurado
- ✅ Persistencia en PostgreSQL

### Base de Datos (PostgreSQL)
- **usuarios**: Gestión de cuentas
- **practicas**: Historial completo con métricas JSON
- **insignias**: Sistema de logros dinámico
- **rachas**: Tracking de constancia

## 🧪 Testing

### Script de Prueba Completo
```bash
./test_api_complete_v2.sh
```

### Ejemplos de Uso

1. **Iniciar práctica**:
```bash
curl -X POST "http://localhost:8000/practica/iniciar"
```

2. **Finalizar con video**:
```bash
curl -X POST "http://localhost:8000/practica/finalizar" \
  -H "Content-Type: application/json" \
  -d '{"idSesion": "abc123", "urlArchivo": "https://url-del-video.mp4"}'
```

3. **Ver análisis detallado**:
```bash
curl "http://localhost:8000/practica/1/analisis"
```

4. **Obtener plan personalizado**:
```bash
curl "http://localhost:8000/plan/actual"
```

### Documentación Interactiva

Visita http://localhost:8000/docs para:
- ✅ Probar todos los endpoints en vivo
- ✅ Ver esquemas completos de request/response  
- ✅ Modelos Pydantic correctamente definidos

## 📋 Estado Actual

### ✅ Implementado y Funcional
- ✅ Análisis completo de video con MediaPipe
- ✅ Análisis de audio con transcripción
- ✅ Sistema de insignias dinámico (23 tipos)
- ✅ Generación de planes personalizados
- ✅ Comentarios de retroalimentación con IA (preparado para OpenAI)
- ✅ Persistencia en PostgreSQL
- ✅ Documentación Swagger completa
- ✅ Tendencias y progreso temporal

### 🔜 Mejoras Sugeridas
- [ ] Integración real con OpenAI API (código preparado)
- [ ] Procesamiento asíncrono para videos largos
- [ ] Rate limiting y validación de URLs
- [ ] Storage dedicado para videos (S3)
- [ ] Métricas adicionales (tono de voz, pausas estratégicas)

## � Deployment

### Despliegue Automático en Producción

```bash
# Ejecutar script de despliegue
./deploy.sh
```

Este script:
1. Sube cambios a GitHub
2. Se conecta al servidor vía SSH
3. Actualiza el código
4. Reconstruye y levanta contenedores
5. Verifica que la API responda correctamente

### Despliegue Manual

```bash
# En el servidor de producción
cd /root/proyecto-grupal-sw1
git pull origin main
export DOMAIN=softwaredlv.duckdns.org
docker compose -f docker-compose.caddy.yml up -d --build
```

## 🏗️ Estructura del Proyecto

```
proyecto-grupal-sw1/
├── backend/              # API FastAPI
│   ├── main.py          # Lógica principal + endpoints
│   ├── services/        # Análisis de audio/video
│   ├── Dockerfile       # Container backend
│   └── requirements.txt # Dependencias Python
├── infra/
│   └── caddy/
│       └── Caddyfile    # Configuración HTTPS
├── docker-compose.dev.yml      # Desarrollo local
├── docker-compose.caddy.yml    # Producción con HTTPS
├── deploy.sh                   # Script de despliegue
├── test_api_complete_v2.sh     # Suite de tests
└── README.md
```

## 🤝 Contribución

Este proyecto es un MVP completo y funcional para análisis de oratoria con IA.

Proyecto académico - Software 1 - Universidad Mayor de San Simón

## 📞 Soporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/daviddlv007/proyecto-grupal-sw1/issues)
- 🔗 **Repositorio**: https://github.com/daviddlv007/proyecto-grupal-sw1
- 🌐 **API en Producción**: https://softwaredlv.duckdns.org

---

**Última actualización**: Octubre 2025
**Estado**: ✅ MVP Completo - Sistema funcional con PostgreSQL, análisis real de audio/video, y despliegue automático