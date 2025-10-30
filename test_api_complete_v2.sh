#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🎤 SCRIPT DE PRUEBA COMPLETA - API PRÁCTICA ORAL
# ═══════════════════════════════════════════════════════════════
# 
# CONFIGURACIÓN: Comenta/Descomenta la URL que deseas usar
# ───────────────────────────────────────────────────────────────

# OPCIÓN 1: Desarrollo local
# BASE_URL="http://localhost:8000"

# OPCIÓN 2: Producción (descomenta la siguiente línea para usar)
BASE_URL="https://softwaredlv.duckdns.org"

# ───────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════"
echo "🎤 PRUEBA COMPLETA DE API PRÁCTICA ORAL"
echo "═══════════════════════════════════════════════════════════"
echo "🌐 URL Base: $BASE_URL"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variable para token JWT (solo en producción)
TOKEN=""

# 1. Health check
echo -e "${BLUE}1. Verificando salud del sistema...${NC}"
curl -s $BASE_URL/health | python3 -m json.tool
echo ""

# 2. Autenticación (solo si es producción)
if [[ $BASE_URL == *"https"* ]]; then
    echo -e "${YELLOW}🔐 Autenticación requerida (producción)${NC}"
    
    # Registrar usuario de prueba
    echo -e "${BLUE}2a. Registrando usuario de prueba...${NC}"
    RANDOM_USER="test_$(date +%s)"
    curl -s -X POST "$BASE_URL/auth/registrar" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"${RANDOM_USER}@test.com\", \"password\": \"test123\", \"nombre\": \"Usuario Test\"}" | python3 -m json.tool
    echo ""
    
    # Login y obtener token
    echo -e "${BLUE}2b. Obteniendo token JWT...${NC}"
    TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"${RANDOM_USER}@test.com\", \"password\": \"test123\"}" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))")
    
    if [ -z "$TOKEN" ]; then
        echo -e "${RED}❌ Error obteniendo token. Abortando.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Token obtenido: ${TOKEN:0:20}...${NC}"
    echo ""
    AUTH_HEADER="Authorization: Bearer $TOKEN"
else
    echo -e "${YELLOW}🔓 Modo desarrollo - Sin autenticación${NC}"
    echo ""
    AUTH_HEADER=""
fi

# 3. Iniciar práctica
echo -e "${BLUE}3. Iniciando sesión de práctica...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    SESSION=$(curl -s -X POST $BASE_URL/practica/iniciar -H "$AUTH_HEADER" | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])")
else
    SESSION=$(curl -s -X POST $BASE_URL/practica/iniciar | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])")
fi
echo -e "${GREEN}Sesión iniciada: $SESSION${NC}"
echo ""

# 4. Finalizar práctica con video bueno
echo -e "${BLUE}4. Procesando video de práctica (BUENO)...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    PRACTICA_ID=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{\"idSesion\": \"$SESSION\", \"urlArchivo\": \"https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/bueno.mp4\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data['idPractica']); print('Puntuación:', data.get('resumen', 'N/A'))")
else
    PRACTICA_ID=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -d "{\"idSesion\": \"$SESSION\", \"urlArchivo\": \"https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/bueno.mp4\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data['idPractica']); print('Puntuación:', data.get('resumen', 'N/A'))")
fi
echo ""

# 5. Ver análisis detallado
echo -e "${BLUE}5. Consultando análisis detallado...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/practica/1/analisis -H "$AUTH_HEADER" | python3 -m json.tool | head -30
else
    curl -s $BASE_URL/practica/1/analisis | python3 -m json.tool | head -30
fi
echo ""

# 6. Ver historial
echo -e "${BLUE}6. Consultando historial de prácticas...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/practica/historial -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/practica/historial | python3 -m json.tool
fi
echo ""

# 7. Ver plan personalizado
echo -e "${BLUE}7. Obteniendo plan de entrenamiento personalizado...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/plan/actual -H "$AUTH_HEADER" | python3 -m json.tool | head -40
else
    curl -s $BASE_URL/plan/actual | python3 -m json.tool | head -40
fi
echo ""

# 8. Ver progreso
echo -e "${BLUE}8. Consultando progreso y tendencias...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/progreso/resumen -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/progreso/resumen | python3 -m json.tool
fi
echo ""

# 9. Ver insignias
echo -e "${BLUE}9. Consultando insignias obtenidas...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/recompensas/insignias -H "$AUTH_HEADER" | python3 -m json.tool | head -30
else
    curl -s $BASE_URL/recompensas/insignias | python3 -m json.tool | head -30
fi
echo ""

# 10. Ver racha
echo -e "${BLUE}10. Consultando racha actual...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/recompensas/racha -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/recompensas/racha | python3 -m json.tool
fi
echo ""

# 11. Limpieza de base de datos (opcional)
echo -e "${YELLOW}11. ¿Deseas limpiar la base de datos? (s/n)${NC}"
read -p "Respuesta: " LIMPIAR

if [ "$LIMPIAR" = "s" ] || [ "$LIMPIAR" = "S" ]; then
    echo -e "${BLUE}Limpiando base de datos...${NC}"
    if [ -n "$AUTH_HEADER" ]; then
        RESULTADO=$(curl -s -X POST $BASE_URL/admin/limpiar-bd -H "$AUTH_HEADER")
    else
        RESULTADO=$(curl -s -X POST $BASE_URL/admin/limpiar-bd)
    fi
    echo "$RESULTADO" | python3 -m json.tool
    echo -e "${GREEN}✅ Base de datos limpiada exitosamente${NC}"
else
    echo -e "${YELLOW}⏭️  Limpieza de BD omitida${NC}"
fi
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ PRUEBA COMPLETA FINALIZADA${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "📚 Documentación Swagger:"
echo "  👉 $BASE_URL/docs"
echo ""
echo "🌐 API Base:"
echo "  👉 $BASE_URL"
echo ""
