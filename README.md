# API Práctica Oral 🎤

API backend para aplicación de práctica de comunicación oral con análisis automático y gamificación.

## 🌐 Enlaces Importantes

- **API Base URL**: https://softwaredlv.duckdns.org
- **Documentación Interactiva**: https://softwaredlv.duckdns.org/docs
- **Health Check**: https://softwaredlv.duckdns.org/health

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/daviddlv007/proyecto-grupal-sw1.git
cd proyecto-grupal-sw1

# Ejecutar en desarrollo
docker-compose -f docker-compose.dev.yml up --build
```

La API estará disponible en: http://localhost:8000

### Producción

```bash
# Desplegar en producción
docker-compose -f docker-compose.caddy.yml up -d
```

## 📚 Estado de Endpoints

### ✅ Endpoints Funcionando (Implementación Real)

#### 🔐 Autenticación
- `POST /auth/registrar` - Registro de usuarios con validación
- `POST /auth/login` - Login con JWT válido por 24 horas  
- `GET /auth/yo` - Información del usuario autenticado

#### 🎮 Gestión de Sesiones
- `POST /practica/iniciar` - Inicia sesión de práctica con UUID real

### 🎭 Endpoints con Datos Mock (Para Desarrollo)

#### 📊 Análisis de Prácticas
- `POST /practica/finalizar` - Finaliza práctica con métricas simuladas
- `GET /practica/{id}/analisis` - Análisis detallado (datos mock)
- `GET /practica/historial` - Historial de prácticas
- `GET /practica/{id}` - Detalle de práctica específica

#### 📈 Progreso y Planificación  
- `GET /plan/actual` - Plan de estudios personalizado (mock)
- `GET /progreso/resumen` - Resumen de progreso con tendencias

#### 🏆 Gamificación
- `GET /recompensas/insignias` - Sistema de insignias
- `GET /recompensas/racha` - Racha de días consecutivos

## 🛠️ Arquitectura

### Stack Tecnológico
- **Backend**: FastAPI + Python 3.9+
- **Autenticación**: JWT con SHA256
- **Containerización**: Docker + Docker Compose
- **Reverse Proxy**: Caddy con SSL automático
- **Dominio**: DuckDNS (softwaredlv.duckdns.org)

### Seguridad
- ✅ HTTPS/TLS 1.3 
- ✅ Headers de seguridad (HSTS, XSS Protection)
- ✅ CORS configurado
- ✅ JWT para autenticación

### Base de Datos
- **Actual**: En memoria (diccionarios Python)
- **⚠️ Para Producción**: Migrar a PostgreSQL/MongoDB

## 🧪 Testing

### Probar la API

1. **Registrar usuario**:
```bash
curl -X POST "https://softwaredlv.duckdns.org/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{"correo": "test@example.com", "contrasena": "password123"}'
```

2. **Hacer login**:
```bash
curl -X POST "https://softwaredlv.duckdns.org/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"correo": "test@example.com", "contrasena": "password123"}'
```

3. **Usar endpoints protegidos**:
```bash
curl -X GET "https://softwaredlv.duckdns.org/auth/yo" \
  -H "Authorization: Bearer <tu-token-jwt>"
```

### Documentación Interactiva

Visita https://softwaredlv.duckdns.org/docs para:
- ✅ Probar todos los endpoints en vivo
- ✅ Ver esquemas de request/response  
- ✅ Generar tokens JWT para testing

## 📋 Roadmap

### Por Implementar
- [ ] Integración con APIs de transcripción (Whisper)
- [ ] Análisis de video para gestos y expresión corporal
- [ ] Algoritmos de análisis de comunicación oral
- [ ] Base de datos persistente
- [ ] Sistema de logros dinámico
- [ ] Generador de planes personalizados

### Próximas Versiones
- [ ] Análisis de sentimientos en audio
- [ ] Recomendaciones de mejora basadas en IA
- [ ] Sistema de feedback colaborativo
- [ ] Integración con plataformas de videoconferencia

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Deployment Manual

Para desplegar manualmente usar el script incluido:

```bash
./deploy.sh
```

## 📞 Soporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/daviddlv007/proyecto-grupal-sw1/issues)
- 📧 **Dudas técnicas**: Consultar documentación en `/docs`
- 🔗 **Repositorio**: https://github.com/daviddlv007/proyecto-grupal-sw1

---

**Última actualización**: Octubre 2025 - API desplegada con HTTPS y 12 endpoints (4 reales, 8 mock)