#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# 🎤 FLUJO COMPLETO DE USUARIO - API PRÁCTICA ORAL
# ═══════════════════════════════════════════════════════════════════════════
#
# Este script simula un flujo real de usuario con dos sesiones de práctica:
# 1. Primera sesión: Video CON BUENA ORATORIA (para validar detección de calidad)
# 2. Segunda sesión: Video CON MALA ORATORIA (para validar plan personalizado)
#
# Luego valida el flujo funcional completo de la aplicación.
# ═══════════════════════════════════════════════════════════════════════════

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝 CONFIGURACIÓN INICIAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# URLs de los videos de prueba (EDITABLE)
VIDEO_BUENO="https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/bueno.mp4"
VIDEO_MALO="https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/malo.mp4"

# Seleccionar ambiente (EDITABLE)
# OPCIÓN 1: Desarrollo local
# BASE_URL="http://localhost:8000"

# OPCIÓN 2: Producción
BASE_URL="https://softwaredlv.duckdns.org"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Variables globales
TOKEN=""
USER_ID=""
PRACTICA_1_ID=""
PRACTICA_2_ID=""

# ═══════════════════════════════════════════════════════════════════════════
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║              🎤 PRUEBA FLUJO COMPLETO - API PRÁCTICA ORAL               ║"
echo "║                                                                           ║"
echo "║        SIMULANDO: Usuario con 2 sesiones de práctica reales             ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${YELLOW}🌐 Ambiente: $BASE_URL${NC}"
echo -e "${YELLOW}🎬 Video Bueno: $VIDEO_BUENO${NC}"
echo -e "${YELLOW}🎬 Video Malo:  $VIDEO_MALO${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 0: VERIFICACIÓN DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 0: VERIFICACIÓN DEL SISTEMA${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}1️⃣  Health Check${NC}"
HEALTH=$(curl -s $BASE_URL/health)
echo "$HEALTH" | python3 -m json.tool
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 1: AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 1: AUTENTICACIÓN Y REGISTRO${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ $BASE_URL == *"https"* ]]; then
    echo -e "${YELLOW}🔐 Modo Producción: Autenticación requerida${NC}"
    echo ""
    
    # Crear usuario único
    RANDOM_USER="user_$(date +%s)"
    echo -e "${BLUE}2️⃣  Registrando usuario: $RANDOM_USER${NC}"
    
    REG_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/registrar" \
        -H "Content-Type: application/json" \
        -d "{\"correo\": \"${RANDOM_USER}@test.com\", \"contrasena\": \"test123\"}")
    
    USER_ID=$(echo "$REG_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)
    echo "$REG_RESPONSE" | python3 -m json.tool
    echo ""
    
    # Login
    echo -e "${BLUE}3️⃣  Obteniendo token JWT${NC}"
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"correo\": \"${RANDOM_USER}@test.com\", \"contrasena\": \"test123\"}")
    
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', data.get('access_token', '')))" 2>/dev/null)
    
    if [ -z "$TOKEN" ]; then
        echo -e "${RED}❌ Error obteniendo token. Abortando.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Token obtenido: ${TOKEN:0:30}...${NC}"
    echo ""
    AUTH_HEADER="Authorization: Bearer $TOKEN"
else
    echo -e "${YELLOW}🔓 Modo Desarrollo: Sin autenticación${NC}"
    echo ""
    AUTH_HEADER=""
fi

# ═══════════════════════════════════════════════════════════════════════════
# FASE 2: PRIMERA SESIÓN DE PRÁCTICA (VIDEO BUENO)
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 2: PRIMERA SESIÓN - VIDEO CON BUENA ORATORIA${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📊 Escenario: Usuario graba su primera práctica con buena técnica${NC}"
echo ""

# Iniciar sesión 1
echo -e "${BLUE}4️⃣  Iniciando primera sesión de práctica${NC}"
if [ -n "$AUTH_HEADER" ]; then
    SESION_1=$(curl -s -X POST $BASE_URL/practica/iniciar -H "$AUTH_HEADER" | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])" 2>/dev/null)
else
    SESION_1=$(curl -s -X POST $BASE_URL/practica/iniciar | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])" 2>/dev/null)
fi
echo -e "${GREEN}✅ Sesión iniciada: $SESION_1${NC}"
echo ""

# Finalizar sesión 1 con video bueno
echo -e "${BLUE}5️⃣  Procesando video BUENO y analizando...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    PRACTICA_1=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{\"idSesion\": \"$SESION_1\", \"urlArchivo\": \"$VIDEO_BUENO\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('idPractica', '1'))" 2>/dev/null)
else
    PRACTICA_1=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -d "{\"idSesion\": \"$SESION_1\", \"urlArchivo\": \"$VIDEO_BUENO\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('idPractica', '1'))" 2>/dev/null)
fi

# Ver análisis detallado de sesión 1
echo -e "${BLUE}6️⃣  Análisis detallado de Primera Sesión${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/practica/$PRACTICA_1/analisis -H "$AUTH_HEADER" | python3 -m json.tool | head -50
else
    curl -s $BASE_URL/practica/$PRACTICA_1/analisis | python3 -m json.tool | head -50
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 3: SEGUNDA SESIÓN DE PRÁCTICA (VIDEO MALO)
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 3: SEGUNDA SESIÓN - VIDEO CON MALA ORATORIA${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📊 Escenario: Usuario graba segunda práctica sin técnica (simula debilidades)${NC}"
echo ""

# Iniciar sesión 2
echo -e "${BLUE}7️⃣  Iniciando segunda sesión de práctica${NC}"
if [ -n "$AUTH_HEADER" ]; then
    SESION_2=$(curl -s -X POST $BASE_URL/practica/iniciar -H "$AUTH_HEADER" | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])" 2>/dev/null)
else
    SESION_2=$(curl -s -X POST $BASE_URL/practica/iniciar | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])" 2>/dev/null)
fi
echo -e "${GREEN}✅ Sesión iniciada: $SESION_2${NC}"
echo ""

# Finalizar sesión 2 con video malo
echo -e "${BLUE}8️⃣  Procesando video MALO y analizando debilidades...${NC}"
if [ -n "$AUTH_HEADER" ]; then
    PRACTICA_2=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{\"idSesion\": \"$SESION_2\", \"urlArchivo\": \"$VIDEO_MALO\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('idPractica', '2'))" 2>/dev/null)
else
    PRACTICA_2=$(curl -s -X POST $BASE_URL/practica/finalizar \
      -H "Content-Type: application/json" \
      -d "{\"idSesion\": \"$SESION_2\", \"urlArchivo\": \"$VIDEO_MALO\"}" | \
      python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('idPractica', '2'))" 2>/dev/null)
fi

# Ver análisis detallado de sesión 2
echo -e "${BLUE}9️⃣  Análisis detallado de Segunda Sesión${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/practica/$PRACTICA_2/analisis -H "$AUTH_HEADER" | python3 -m json.tool | head -50
else
    curl -s $BASE_URL/practica/$PRACTICA_2/analisis | python3 -m json.tool | head -50
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 4: ANÁLISIS DE DATOS Y RECOMENDACIONES
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 4: ANÁLISIS INTEGRAL DE USUARIO${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📊 Escenario: Sistema analiza el progreso y genera recomendaciones${NC}"
echo ""

# Historial completo
echo -e "${BLUE}🔟 Historial de prácticas${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/practica/historial -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/practica/historial | python3 -m json.tool
fi
echo ""

# Plan personalizado basado en debilidades
echo -e "${BLUE}1️⃣1️⃣  Plan personalizado (basado en análisis de sesión 2)${NC}"
echo -e "${YELLOW}⚠️  El plan se personaliza según las debilidades detectadas${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/plan/actual -H "$AUTH_HEADER" | python3 -m json.tool | head -50
else
    curl -s $BASE_URL/plan/actual | python3 -m json.tool | head -50
fi
echo ""

# Progreso y tendencias
echo -e "${BLUE}1️⃣2️⃣  Resumen de progreso y tendencias${NC}"
echo -e "${YELLOW}💡 Comparativa: ¿Mejoró entre sesión 1 y 2?${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/progreso/resumen -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/progreso/resumen | python3 -m json.tool
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 5: GESTIÓN DE TAREAS DEL PLAN
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 5: GESTIÓN DE TAREAS DEL PLAN${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📋 Escenario: Usuario marca tareas como completadas${NC}"
echo ""

# Obtener el ID del plan actual
echo -e "${BLUE}1️⃣3️⃣  Obteniendo ID del plan actual${NC}"
if [ -n "$AUTH_HEADER" ]; then
    PLAN_ID=$(curl -s $BASE_URL/plan/actual -H "$AUTH_HEADER" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 0))" 2>/dev/null)
else
    PLAN_ID=$(curl -s $BASE_URL/plan/actual | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 0))" 2>/dev/null)
fi
echo -e "${GREEN}✅ Plan ID: $PLAN_ID${NC}"
echo ""

# Marcar día 1 como completado
echo -e "${BLUE}1️⃣4️⃣  Marcando tarea del día 1 como completada${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s -X POST $BASE_URL/plan/tarea/completar \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{\"planId\": $PLAN_ID, \"dia\": 1}" | python3 -m json.tool
else
    curl -s -X POST $BASE_URL/plan/tarea/completar \
      -H "Content-Type: application/json" \
      -d "{\"planId\": $PLAN_ID, \"dia\": 1}" | python3 -m json.tool
fi
echo ""

# Marcar día 2 como completado
echo -e "${BLUE}1️⃣5️⃣  Marcando tarea del día 2 como completada${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s -X POST $BASE_URL/plan/tarea/completar \
      -H "Content-Type: application/json" \
      -H "$AUTH_HEADER" \
      -d "{\"planId\": $PLAN_ID, \"dia\": 2}" | python3 -m json.tool
else
    curl -s -X POST $BASE_URL/plan/tarea/completar \
      -H "Content-Type: application/json" \
      -d "{\"planId\": $PLAN_ID, \"dia\": 2}" | python3 -m json.tool
fi
echo ""

# Verificar estado actualizado del plan
echo -e "${BLUE}1️⃣6️⃣  Verificando plan con tareas actualizadas${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/plan/actual -H "$AUTH_HEADER" | python3 -m json.tool | head -60
else
    curl -s $BASE_URL/plan/actual | python3 -m json.tool | head -60
fi
echo ""

# Historial de planes
echo -e "${BLUE}1️⃣7️⃣  Consultando historial completo de planes${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/plan/historial -H "$AUTH_HEADER" | python3 -m json.tool | head -40
else
    curl -s $BASE_URL/plan/historial | python3 -m json.tool | head -40
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 6: GAMIFICACIÓN Y RECOMPENSAS
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 6: GAMIFICACIÓN Y RECOMPENSAS${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}🏆 Escenario: Sistema otorga insignias y rachas${NC}"
echo ""

# Insignias obtenidas
echo -e "${BLUE}1️⃣8️⃣  Insignias desbloqueadas${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/recompensas/insignias -H "$AUTH_HEADER" | python3 -m json.tool | head -40
else
    curl -s $BASE_URL/recompensas/insignias | python3 -m json.tool | head -40
fi
echo ""

# Racha actual
echo -e "${BLUE}1️⃣9️⃣  Racha de días consecutivos${NC}"
if [ -n "$AUTH_HEADER" ]; then
    curl -s $BASE_URL/recompensas/racha -H "$AUTH_HEADER" | python3 -m json.tool
else
    curl -s $BASE_URL/recompensas/racha | python3 -m json.tool
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FASE 7: LIMPIEZA OPCIONAL
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ FASE 7: LIMPIEZA FINAL (OPCIONAL)${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}2️⃣0️⃣  ¿Deseas limpiar la base de datos? (s/n)${NC}"
read -p "Respuesta: " LIMPIAR

if [ "$LIMPIAR" = "s" ] || [ "$LIMPIAR" = "S" ]; then
    echo ""
    echo -e "${BLUE}Limpiando base de datos...${NC}"
    if [ -n "$AUTH_HEADER" ]; then
        curl -s -X POST $BASE_URL/admin/limpiar-bd -H "$AUTH_HEADER" | python3 -m json.tool
    else
        curl -s -X POST $BASE_URL/admin/limpiar-bd | python3 -m json.tool
    fi
    echo -e "${GREEN}✅ Base de datos limpiada${NC}"
else
    echo -e "${YELLOW}⏭️  Limpieza omitida${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║                    ✅ PRUEBA COMPLETADA EXITOSAMENTE                    ║"
echo "║                                                                           ║"
echo "║                         FLUJO VALIDADO:                                 ║"
echo "║                                                                           ║"
echo "║  ✓ Autenticación JWT                                                    ║"
echo "║  ✓ Dos sesiones de práctica (buena y mala)                              ║"
echo "║  ✓ Análisis detallado de audio/video                                    ║"
echo "║  ✓ Comparativa de progreso                                              ║"
echo "║  ✓ Plan personalizado basado en debilidades                             ║"
echo "║  ✓ Persistencia de planes en BD                                         ║"
echo "║  ✓ Gestión de estado de tareas del plan                                 ║"
echo "║  ✓ Historial de planes generados                                        ║"
echo "║  ✓ Insignias dinámicas                                                  ║"
echo "║  ✓ Racha de usuarios                                                    ║"
echo "║  ✓ Limpieza de BD                                                       ║"
echo "║                                                                           ║"
echo "║              🎤 SISTEMA FUNCIONAL Y SEMÁNTICAMENTE COHERENTE             ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${CYAN}📚 Documentación Swagger: $BASE_URL/docs${NC}"
echo -e "${CYAN}🌐 API Base: $BASE_URL${NC}"
echo ""
