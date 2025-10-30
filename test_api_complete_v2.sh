#!/bin/bash

# Script de prueba completa de la API
# Demuestra el flujo completo del usuario

echo "========================================="
echo "🎤 PRUEBA COMPLETA DE API PRÁCTICA ORAL"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Health check
echo -e "${BLUE}1. Verificando salud del sistema...${NC}"
curl -s $BASE_URL/health | python3 -m json.tool
echo ""

# 2. Registrar usuario (opcional, ya que auth está deshabilitada)
echo -e "${BLUE}2. Iniciando sesión de práctica...${NC}"
SESSION=$(curl -s -X POST $BASE_URL/practica/iniciar | python3 -c "import sys, json; print(json.load(sys.stdin)['idSesion'])")
echo -e "${GREEN}Sesión iniciada: $SESSION${NC}"
echo ""

# 3. Finalizar práctica con video bueno
echo -e "${BLUE}3. Procesando video de práctica (BUENO)...${NC}"
PRACTICA_ID=$(curl -s -X POST $BASE_URL/practica/finalizar \
  -H "Content-Type: application/json" \
  -d "{\"idSesion\": \"$SESSION\", \"urlArchivo\": \"https://bwduexqzhjolwfxupvco.supabase.co/storage/v1/object/public/imagenes/bueno.mp4\"}" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(data['idPractica']); print('Puntuación:', data.get('resumen', 'N/A'))")
echo ""

# 4. Ver análisis detallado
echo -e "${BLUE}4. Consultando análisis detallado...${NC}"
curl -s $BASE_URL/practica/1/analisis | python3 -m json.tool | head -30
echo ""

# 5. Ver historial
echo -e "${BLUE}5. Consultando historial de prácticas...${NC}"
curl -s $BASE_URL/practica/historial | python3 -m json.tool
echo ""

# 6. Ver plan personalizado
echo -e "${BLUE}6. Obteniendo plan de entrenamiento personalizado...${NC}"
curl -s $BASE_URL/plan/actual | python3 -m json.tool | head -40
echo ""

# 7. Ver progreso
echo -e "${BLUE}7. Consultando progreso y tendencias...${NC}"
curl -s $BASE_URL/progreso/resumen | python3 -m json.tool
echo ""

# 8. Ver insignias
echo -e "${BLUE}8. Consultando insignias obtenidas...${NC}"
curl -s $BASE_URL/recompensas/insignias | python3 -m json.tool | head -30
echo ""

# 9. Ver racha
echo -e "${BLUE}9. Consultando racha actual...${NC}"
curl -s $BASE_URL/recompensas/racha | python3 -m json.tool
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ PRUEBA COMPLETA FINALIZADA${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Para ver la documentación Swagger:"
echo "  👉 http://localhost:8000/docs"
echo ""
echo "Para acceder a la API:"
echo "  👉 http://localhost:8000"
echo ""
