# Guía para Desarrolladores Frontend

Este documento está dirigido a Aldair y Chris, responsables del desarrollo del frontend. Aquí encontrarán una descripción clara de los casos de uso, flujos, ejemplos de request/response y recomendaciones para integrar el frontend con el backend.

---

## 1. Autenticación y Registro

### Registro de Usuario
- **Endpoint:** `POST /auth/registrar`
- **Request:**
```json
{
  "correo": "usuario@email.com",
  "contrasena": "password123"
}
```
- **Response:**
```json
{
  "id": 1,
  "correo": "usuario@email.com",
  "token": "<jwt-token>"
}
```

### Login
- **Endpoint:** `POST /auth/login`
- **Request:**
```json
{
  "correo": "usuario@email.com",
  "contrasena": "password123"
}
```
- **Response:**
```json
{
  "token": "<jwt-token>"
}
```

### Obtener Usuario Autenticado
- **Endpoint:** `GET /auth/yo`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "id": 1,
  "correo": "usuario@email.com"
}
```

---

## 2. Prácticas y Análisis

### Iniciar Práctica
- **Endpoint:** `POST /practica/iniciar`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "idSesion": "abc123",
  "estado": "iniciada"
}
```

### Finalizar Práctica
- **Endpoint:** `POST /practica/finalizar`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Request:**
```json
{
  "idSesion": "abc123",
  "urlArchivo": "https://url-del-video.mp4"
}
```
- **Response:**
```json
{
  "idPractica": 5,
  "estado": "finalizada",
  "resumen": "Buen contacto visual",
  "comentario": "Evita muletillas",
  "metricas": { ... }
}
```

### Consultar Análisis de Práctica
- **Endpoint:** `GET /practica/{id}/analisis`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "idPractica": 5,
  "transcripcion": "Texto completo...",
  "metricas": { ... },
  "puntuacion": "A",
  "resumen": "Buen contacto visual",
  "comentario": "Evita muletillas"
}
```

### Consultar Historial de Prácticas
- **Endpoint:** `GET /practica/historial`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
[
  {
    "id": 5,
    "fecha": "2025-10-29",
    "puntuacion": "A",
    "urlArchivo": "https://url-del-video.mp4"
  },
  ...
]
```

---

## 3. Plan Semanal

### Consultar Plan Actual
- **Endpoint:** `GET /plan/actual`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "id": 12,
  "objetivos": ["Mejorar contacto visual", "Reducir muletillas"],
  "tareas": [
    {"dia": 1, "tarea": "Practica contacto visual", "completada": false},
    {"dia": 2, "tarea": "Evita muletillas", "completada": true}
  ],
  "creadoEn": "2025-10-28T10:00:00"
}
```

### Marcar Tarea como Completada
- **Endpoint:** `POST /plan/tarea/completar`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Request:**
```json
{
  "planId": 12,
  "dia": 1
}
```
- **Response:**
```json
{
  "success": true
}
```

### Consultar Historial de Planes
- **Endpoint:** `GET /plan/historial`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
[
  {
    "id": 10,
    "objetivos": ["Expresividad"],
    "tareas": [...],
    "creadoEn": "2025-10-21T10:00:00"
  },
  {
    "id": 12,
    "objetivos": ["Contacto visual", "Muletillas"],
    "tareas": [...],
    "creadoEn": "2025-10-28T10:00:00"
  }
]
```

---

## 4. Progreso y Recompensas

### Consultar Progreso
- **Endpoint:** `GET /progreso/resumen`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "totalPracticas": 8,
  "puntuacionPromedio": "B+",
  "tendencias": { ... },
  "ultimaPractica": "2025-10-29"
}
```

### Consultar Insignias
- **Endpoint:** `GET /recompensas/insignias`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
[
  {"id": 1, "nombre": "Primera práctica", "obtenidaEn": "2025-10-20"},
  {"id": 2, "nombre": "Mirada profesional", "obtenidaEn": "2025-10-22"}
]
```

### Consultar Racha
- **Endpoint:** `GET /recompensas/racha`
- **Headers:** `Authorization: Bearer <jwt-token>`
- **Response:**
```json
{
  "id": 1,
  "rachaActual": 5,
  "unidad": "días"
}
```

---

## 5. Administración y Health

### Limpiar Base de Datos (solo desarrollo)
- **Endpoint:** `POST /admin/limpiar-bd`
- **Response:**
```json
{
  "success": true
}
```

### Health Check
- **Endpoint:** `GET /health`
- **Response:**
```json
{
  "status": "ok"
}
```

---

## 6. Recursos Útiles
- Script de prueba: `/home/ubuntu/proyectos/proyecto-grupal-sw1/test_api_complete_v2.sh`
- Videos de ejemplo:
  - Oratoria buena: https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/bueno.mp4
  - Oratoria mala: https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/malo.mp4

---

## 7. Notas y Buenas Prácticas
- Todos los endpoints (excepto registro/login/health) requieren JWT en el header.
- La generación del plan es automática al consultar `/plan/actual` y se regenera cada 7 días.
- Hay un endpoint para limpiar (vaciar) la Base de Datos
