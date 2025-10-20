# 🔐 CONFIGURACIÓN DE GITHUB SECRETS PARA AUTO-DEPLOY

## 📋 Secrets necesarios en GitHub

Para que el workflow de deploy automático funcione, necesitas configurar estos secrets en tu repositorio de GitHub:

### 🔑 Opción 1: Autenticación por contraseña (más fácil)
Usar el archivo: `deploy-password.yml`

**Secrets requeridos:**
- `SERVER_HOST` = `165.22.47.1`
- `SERVER_USER` = `root` 
- `SERVER_PASSWORD` = `softWare_1fin`

### 🔐 Opción 2: Autenticación por SSH key (más segura)
Usar el archivo: `deploy.yml`

**Secrets requeridos:**
- `SERVER_HOST` = `165.22.47.1`
- `SERVER_USER` = `root`
- `SSH_PRIVATE_KEY` = [Tu clave SSH privada]

## 🛠️ PASOS PARA CONFIGURAR SECRETS EN GITHUB

### 1️⃣ Ir a tu repositorio en GitHub
```
https://github.com/daviddlv007/proyecto-grupal-sw1
```

### 2️⃣ Navegar a Settings > Secrets and variables > Actions

### 3️⃣ Hacer click en "New repository secret"

### 4️⃣ Agregar cada secret:

**Para opción con contraseña:**
```
Name: SERVER_HOST
Value: 165.22.47.1

Name: SERVER_USER  
Value: root

Name: SERVER_PASSWORD
Value: softWare_1fin
```

## 🚀 CÓMO USAR

### Opción A: Deploy con contraseña (recomendado para empezar)
1. Configurar los 3 secrets de contraseña
2. Renombrar `deploy-password.yml` a `deploy.yml`
3. Eliminar el otro archivo de workflow
4. Hacer push a main

### Opción B: Deploy con SSH key (más seguro)
1. Generar SSH key pair en tu máquina local:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions"
   ```
2. Copiar la clave pública al servidor:
   ```bash
   ssh-copy-id -i ~/.ssh/id_rsa.pub root@165.22.47.1
   ```
3. Copiar la clave privada a GitHub Secrets
4. Configurar los secrets de SSH
5. Hacer push a main

## ⚡ QUÉ HACE EL WORKFLOW

🔄 **Se ejecuta automáticamente cuando:**
- Haces push a la rama `main`
- Cambias archivos en `backend/`, `docker-compose.caddy.yml`, o `infra/caddy/`
- Lo ejecutas manualmente desde GitHub Actions

📋 **Pasos del deployment:**
1. Descarga el código del repositorio
2. Se conecta al servidor vía SSH
3. Actualiza el código con `git pull`
4. Detiene los contenedores actuales
5. Construye y ejecuta la nueva versión
6. Verifica que todo funcione
7. Muestra resumen del deployment

## 🎯 BENEFICIOS

✅ **Deploy automático** en cada cambio
✅ **Verificación automática** de que la API funciona
✅ **Logs detallados** de cada deployment
✅ **Rollback fácil** si algo falla
✅ **Notificaciones** del estado del deploy

## 🔍 VERIFICAR DEPLOYMENT

Después de cada push, puedes:
1. Ver el progreso en la pestaña "Actions" de GitHub
2. Verificar que la API funciona: https://softwaredlv.duckdns.org/health
3. Revisar logs si hay problemas

## 🚨 TROUBLESHOOTING

### Si el workflow falla:
1. Revisar logs en GitHub Actions
2. Verificar que los secrets estén configurados correctamente
3. Asegurarse de que el servidor esté accesible
4. Verificar que Docker esté funcionando en el servidor

### Comandos útiles para debug en el servidor:
```bash
# Ver estado de contenedores
docker compose -f docker-compose.caddy.yml ps

# Ver logs
docker compose -f docker-compose.caddy.yml logs -f

# Restart manual
docker compose -f docker-compose.caddy.yml restart
```