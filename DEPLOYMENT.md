# 🚀 Guía de Despliegue - API Práctica Oral

## ✅ Estado Actual

**Última actualización**: 30 de Octubre 2025

- ✅ Proyecto limpio (eliminados archivos MD y scripts redundantes)
- ✅ PostgreSQL integrado en producción
- ✅ Despliegue automático configurado
- ✅ Sistema funcionando en: https://softwaredlv.duckdns.org
- ✅ HTTPS habilitado con Caddy

## 📦 Estructura Final del Proyecto

```
proyecto-grupal-sw1/
├── backend/                          # API FastAPI
│   ├── main.py                       # Lógica principal + endpoints
│   ├── services/                     # Análisis audio/video
│   │   ├── audio_analyzer.py        # Transcripción y muletillas
│   │   ├── video_analyzer.py        # MediaPipe para video
│   │   └── av_processor.py          # Procesamiento AV
│   ├── Dockerfile                    # Container backend
│   └── requirements.txt              # Dependencias Python
├── infra/
│   └── caddy/
│       └── Caddyfile                 # Configuración HTTPS
├── docker-compose.dev.yml            # Desarrollo local
├── docker-compose.caddy.yml          # Producción con Caddy + PostgreSQL
├── deploy.sh                         # Script de despliegue automático
├── test_api_complete_v2.sh           # Suite completa de tests
└── README.md                         # Documentación principal
```

## 🔧 Servicios en Producción

### 1. PostgreSQL
- **Imagen**: postgres:15-alpine
- **Base de datos**: practica_db
- **Usuario**: practica_user
- **Puerto interno**: 5432
- **Volumen persistente**: postgres_data

### 2. Backend FastAPI
- **Puerto interno**: 8000
- **Variables de entorno**:
  - `DATABASE_URL`: Conexión a PostgreSQL
  - `SECRET_KEY`: Para JWT
  - `ENVIRONMENT`: production

### 3. Caddy (Reverse Proxy)
- **Puertos**: 80 (HTTP), 443 (HTTPS)
- **SSL/TLS**: Automático con Let's Encrypt
- **Dominio**: softwaredlv.duckdns.org
- **Volúmenes**: caddy_data, caddy_config

## 🚀 Despliegue

### Método 1: Script Automático (Recomendado)

```bash
./deploy.sh
```

Este script:
1. Hace commit y push de los cambios a GitHub
2. Se conecta al servidor vía SSH
3. Actualiza el código desde el repositorio
4. Reconstruye y levanta los contenedores
5. Verifica que la API responda correctamente

### Método 2: Manual

```bash
# Conectarse al servidor
ssh root@165.22.47.1

# Navegar al proyecto
cd /root/proyecto-grupal-sw1

# Actualizar código
git pull origin main

# Configurar dominio
export DOMAIN=softwaredlv.duckdns.org

# Levantar servicios
docker compose -f docker-compose.caddy.yml up -d --build

# Verificar estado
docker compose -f docker-compose.caddy.yml ps

# Ver logs
docker compose -f docker-compose.caddy.yml logs -f backend
```

## 🧪 Verificación Post-Despliegue

```bash
# 1. Health check
curl https://softwaredlv.duckdns.org/health

# 2. Documentación Swagger
curl -I https://softwaredlv.duckdns.org/docs

# 3. Iniciar práctica
curl -X POST https://softwaredlv.duckdns.org/practica/iniciar

# 4. Ver contenedores
docker compose -f docker-compose.caddy.yml ps

# 5. Ver logs
docker compose -f docker-compose.caddy.yml logs --tail=50 backend
```

## 📊 Endpoints Disponibles

- `GET /health` - Health check
- `GET /docs` - Documentación Swagger
- `POST /practica/iniciar` - Inicia sesión de grabación
- `POST /practica/finalizar` - Procesa video y genera análisis
- `GET /practica/{id}/analisis` - Análisis detallado
- `GET /practica/historial` - Historial de prácticas
- `GET /plan/actual` - Plan personalizado
- `GET /progreso/resumen` - Resumen de progreso
- `GET /recompensas/insignias` - Insignias obtenidas
- `GET /recompensas/racha` - Racha actual
- `POST /admin/limpiar-bd` - Limpia BD (solo desarrollo)

## 🔐 Credenciales del Servidor

**Servidor**: 165.22.47.1  
**Usuario**: root  
**Contraseña**: softWare_1fin  
**Repositorio**: https://github.com/daviddlv007/proyecto-grupal-sw1.git  
**Dominio**: softwaredlv.duckdns.org

## 🗃️ Base de Datos

### Acceso a PostgreSQL en Producción

```bash
# Conectarse a la BD
docker exec -it practica_postgres_prod psql -U practica_user -d practica_db

# Verificar tablas
\dt

# Ver usuarios
SELECT * FROM usuarios;

# Ver prácticas
SELECT id, usuario_id, fecha_inicio, duracion_segundos FROM practicas;

# Ver insignias
SELECT * FROM insignias ORDER BY fecha_obtencion DESC LIMIT 10;

# Salir
\q
```

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Ver logs en tiempo real
docker compose -f docker-compose.caddy.yml logs -f

# Reiniciar un servicio específico
docker compose -f docker-compose.caddy.yml restart backend

# Detener todo
docker compose -f docker-compose.caddy.yml down

# Detener y eliminar volúmenes (⚠️ cuidado, borra la BD)
docker compose -f docker-compose.caddy.yml down -v

# Reconstruir sin caché
docker compose -f docker-compose.caddy.yml build --no-cache backend
```

### Debugging

```bash
# Entrar al contenedor del backend
docker exec -it practica_backend_prod bash

# Ver uso de recursos
docker stats

# Ver espacio en disco
df -h
docker system df

# Limpiar imágenes no usadas
docker system prune -a
```

## 📈 Monitoreo

### Verificar Certificado SSL

```bash
curl -I https://softwaredlv.duckdns.org
```

### Ver Logs de Caddy

```bash
docker compose -f docker-compose.caddy.yml logs caddy
```

### Verificar Salud de PostgreSQL

```bash
docker exec practica_postgres_prod pg_isready -U practica_user
```

## 🔄 Actualización del Sistema

Cuando hagas cambios en el código:

```bash
# Local
git add .
git commit -m "Descripción del cambio"
git push origin main

# Ejecutar deploy
./deploy.sh
```

## 🆘 Troubleshooting

### Error: API no responde

```bash
# Ver logs del backend
docker compose -f docker-compose.caddy.yml logs backend

# Reiniciar backend
docker compose -f docker-compose.caddy.yml restart backend
```

### Error: PostgreSQL no conecta

```bash
# Ver logs de PostgreSQL
docker compose -f docker-compose.caddy.yml logs postgres

# Verificar salud
docker exec practica_postgres_prod pg_isready -U practica_user
```

### Error: Caddy no sirve HTTPS

```bash
# Ver logs de Caddy
docker compose -f docker-compose.caddy.yml logs caddy

# Verificar certificados
docker exec practica_caddy_prod ls -la /data/caddy/certificates/
```

### Error: Puerto ocupado

```bash
# Ver qué proceso usa el puerto 80 o 443
sudo lsof -i :80
sudo lsof -i :443

# Detener servicios previos
docker compose -f docker-compose.caddy.yml down
```

## 📝 Notas Importantes

1. **Volumen de PostgreSQL**: Los datos persisten entre reinicios gracias al volumen `postgres_data`
2. **Certificados SSL**: Caddy los renueva automáticamente
3. **Logs**: Se almacenan dentro de los contenedores, acceder con `docker logs`
4. **Backups**: Considera configurar backups automáticos de PostgreSQL

## ✅ Checklist de Despliegue Exitoso

- [x] Código subido a GitHub
- [x] Contenedores levantados en producción
- [x] PostgreSQL funcionando y saludable
- [x] Backend respondiendo en puerto 8000
- [x] Caddy sirviendo HTTPS correctamente
- [x] Endpoint `/health` responde OK
- [x] Swagger UI accesible en `/docs`
- [x] Certificado SSL válido

## 🎯 Próximos Pasos (Opcionales)

- [ ] Configurar backups automáticos de PostgreSQL
- [ ] Integrar monitoreo con Prometheus/Grafana
- [ ] Añadir rate limiting con Redis
- [ ] Implementar CI/CD con GitHub Actions
- [ ] Configurar logs centralizados

---

**Estado**: ✅ Sistema desplegado y funcional  
**Última verificación**: 30 de Octubre 2025, 18:33 UTC  
**URL Producción**: https://softwaredlv.duckdns.org
