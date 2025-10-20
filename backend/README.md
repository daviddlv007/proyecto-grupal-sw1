# MVP Practica Oral - Backend FastAPI

Backend MVP para la aplicación de práctica oral con análisis de discursos.

## Funcionalidades implementadas

✅ **Autenticación completa**
- Registro de usuarios (`/auth/registrar`)
- Login (`/auth/login`) 
- Información del usuario (`/auth/yo`)
- JWT tokens

✅ **Gestión de prácticas**
- Iniciar sesión de grabación (`/practica/iniciar`)
- Finalizar y procesar (`/practica/finalizar`)
- Ver análisis (`/practica/{id}/analisis`)
- Historial de prácticas (`/practica/historial`)
- Detalle de práctica (`/practica/{id}`)

✅ **Funciones adicionales**
- Plan de estudios (`/plan/actual`)
- Resumen de progreso (`/progreso/resumen`)
- Insignias (`/recompensas/insignias`)
- Racha de días (`/recompensas/racha`)

## Arquitectura MVP

- **Base de datos**: En memoria (diccionarios Python)
- **Autenticación**: JWT simple con bcrypt
- **Análisis**: Datos mock para desarrollo rápido
- **CORS**: Configurado para desarrollo

## Instalación y uso

### Opción 1: Docker (Recomendado)
```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar (si ya está construido)
docker-compose up
```

### Opción 2: Instalación local
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Opción 3: Con uvicorn
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints disponibles

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Ejemplos de uso

**Registro:**
```bash
curl -X POST "http://localhost:8000/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{"correo": "juan@example.com", "contrasena": "Secreta123"}'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"correo": "juan@example.com", "contrasena": "Secreta123"}'
```

**Iniciar práctica:**
```bash
curl -X POST "http://localhost:8000/practica/iniciar" \
  -H "Authorization: Bearer TU_TOKEN"
```

## Escalabilidad

Este MVP está diseñado para crecer gradualmente:

1. **Base de datos real**: Cambiar diccionarios por PostgreSQL/MongoDB
2. **Análisis real**: Integrar APIs de transcripción y análisis de video
3. **Storage**: Añadir S3/MinIO para archivos de video
4. **Cache**: Redis para sesiones y datos frecuentes
5. **Monitoring**: Logs, métricas y health checks
6. **Tests**: Suite de testing automatizado

## Estructura del código

```
backend/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── Dockerfile          # Contenedor
└── .env.example        # Variables de entorno
```

El código está estructurado para facilitar la refactorización futura en módulos separados.