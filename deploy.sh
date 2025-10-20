#!/bin/bash

# 🚀 Script de Deploy Manual para API Práctica Oral
# Usar mientras se resuelve el tema de GitHub Actions

echo "🔄 Iniciando deploy manual..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para logs con color
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.caddy.yml" ]; then
    log_error "No se encuentra docker-compose.caddy.yml. ¿Estás en el directorio correcto?"
    exit 1
fi

# 1. Actualizar código
log_info "Subiendo cambios a GitHub..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || log_warn "No hay cambios para commitear"
git push origin main

# 2. Deploy en servidor
log_info "Conectando al servidor para deploy..."

ssh root@165.22.47.1 << 'EOF'
    set -e
    echo "🔄 Iniciando deploy en servidor..."
    
    cd /root/proyecto-grupal-sw1
    
    echo "📥 Actualizando código..."
    git pull origin main
    
    echo "⏹️ Deteniendo contenedores actuales..."
    docker compose -f docker-compose.caddy.yml down || true
    
    echo "🧹 Limpiando imágenes antiguas..."
    docker system prune -f || true
    
    echo "🏗️ Construyendo y ejecutando..."
    export DOMAIN=softwaredlv.duckdns.org
    docker compose -f docker-compose.caddy.yml up -d --build
    
    echo "🔍 Verificando deployment..."
    sleep 10
    
    if docker compose -f docker-compose.caddy.yml ps | grep -q "Up"; then
        echo "✅ Contenedores funcionando!"
        
        # Verificar API
        if curl -f -s https://softwaredlv.duckdns.org/health > /dev/null; then
            echo "✅ API respondiendo correctamente!"
        else
            echo "⚠️ API aún iniciando, dale unos segundos más..."
        fi
    else
        echo "❌ Error en deployment"
        docker compose -f docker-compose.caddy.yml logs --tail=20
        exit 1
    fi
    
    echo "🎉 Deploy completado!"
EOF

if [ $? -eq 0 ]; then
    log_info "🎉 Deploy exitoso!"
    echo ""
    echo "🔗 Tu API está disponible en:"
    echo "   📚 Docs: https://softwaredlv.duckdns.org/docs"
    echo "   🩺 Health: https://softwaredlv.duckdns.org/health"
    echo ""
else
    log_error "Deploy falló. Revisa los logs arriba."
    exit 1
fi