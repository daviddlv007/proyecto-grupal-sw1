# 🔍 ANÁLISIS DE LÓGICA DE NEGOCIO - API PRÁCTICA ORAL

**Fecha**: 30 de octubre de 2025  
**Objetivo**: Validar coherencia de endpoints con la lógica real de entrenamiento de oratoria

---

## ✅ **ENDPOINTS CORRECTOS**

### 1. **Plan Personalizado** (`/plan/actual`)
**Lógica de negocio**: ✅ CORRECTO

- **Input real**: Video malo → contacto_visual=32% (bajo), expresividad=0.002 (baja), postura=mala
- **Función `_identificar_debilidades`**:
  - Contacto visual < 50% → debilidad ALTA prioridad 1 ✅
  - Expresividad < 0.06 → debilidad MEDIA prioridad 2 ✅
  - Postura mala > 50% prácticas → debilidad MEDIA prioridad 3 ✅
- **Output real**: `objetivos: [contacto_visual, expresividad, postura]`
- **Conclusión**: Sistema detecta correctamente las 3 debilidades principales

**Tareas generadas**:
- Día 1: Evaluación base ✅
- Días 2-3: Ejercicios de contacto visual ✅
- Días 4-5: Ejercicios de expresividad ✅
- Día 6: Ejercicios de postura ✅
- Día 7: Evaluación final + práctica libre ✅

**Veredicto**: Plan es lógico, progresivo y personalizado.

---

### 2. **Historial** (`/practica/historial`)
**Lógica de negocio**: ✅ CORRECTO

- **Orden**: DESC por fecha (más reciente primero)
- **Output real**:
  ```json
  [
    {"id": 9, "fecha": "2025-10-30T19:30:51", "puntuacion": "amarillo"},
    {"id": 8, "fecha": "2025-10-30T19:30:36", "puntuacion": "verde"}
  ]
  ```
- **Conclusión**: Orden correcto para UI (último resultado primero)

---

## ⚠️ **INCONSISTENCIAS DETECTADAS**

### 3. **Tendencias/Progreso** (`/progreso/resumen`)
**Lógica de negocio**: ❌ **PROBLEMA CONCEPTUAL**

**Implementación actual**:
```python
# Divide prácticas en DOS MITADES
mitad = max(1, total // 2)
practicas_antes = practicas[:mitad]      # Primera mitad
practicas_ahora = practicas[mitad:]      # Segunda mitad
```

**Con 2 prácticas**:
- `practicas_antes` = [práctica 1] → 87.6% contacto visual
- `practicas_ahora` = [práctica 2] → 32.1% contacto visual
- **Cambio calculado**: -63.4% ✅ (matemáticamente correcto)

**PROBLEMA**: ¿Qué pasa con 3 prácticas?
- `mitad = 3 // 2 = 1`
- `practicas_antes` = [práctica 1]
- `practicas_ahora` = [práctica 2, práctica 3]

**¿Qué pasa con 5 prácticas?**
- `mitad = 5 // 2 = 2`
- `practicas_antes` = [práctica 1, práctica 2]
- `practicas_ahora` = [práctica 3, práctica 4, práctica 5]

**INCONSISTENCIA DE LÓGICA DE NEGOCIO**:

Para una app de entrenamiento de oratoria, las tendencias deberían mostrar:

**OPCIÓN A**: Últimas N prácticas vs N prácticas anteriores
- Ejemplo: últimas 3 vs 3 previas
- **Lógica**: "¿Estoy mejorando en mis últimas sesiones comparado con antes?"

**OPCIÓN B**: Última práctica vs promedio histórico
- **Lógica**: "¿Mi última sesión fue mejor que mi promedio general?"

**OPCIÓN C**: Últimas N prácticas vs primeras N prácticas
- **Lógica**: "¿He mejorado desde que empecé?"

**PROBLEMA ACTUAL**: Con 2 prácticas funciona, pero con 3+ la lógica de "mitad" no tiene sentido pedagógico.

**RECOMENDACIÓN**:
```python
# Opción más lógica para entrenamiento:
# Comparar últimas 3 prácticas vs 3 anteriores
VENTANA_COMPARACION = 3

practicas_recientes = practicas[-VENTANA_COMPARACION:]  # Últimas 3
practicas_antiguas = practicas[-2*VENTANA_COMPARACION:-VENTANA_COMPARACION]  # 3 previas

# Si no hay suficientes, comparar con todas las anteriores
if len(practicas) < 2 * VENTANA_COMPARACION:
    practicas_antiguas = practicas[:-VENTANA_COMPARACION]
```

---

### 4. **Racha** (`/recompensas/racha`)
**Lógica de negocio**: ❌ **INCORRECTO SEMÁNTICAMENTE**

**Implementación actual**:
```python
# Línea 708 en main.py
racha.racha_actual = total_practicas  # ❌ PROBLEMA
```

**Output real**:
```json
{
  "rachaActual": 2,  // 2 prácticas
  "unidad": "dias"   // ❌ Dice "días" pero cuenta PRÁCTICAS
}
```

**INCONSISTENCIA**: 
- Variable dice `rachaActual` (implica días consecutivos)
- Unidad dice `"dias"`
- Pero **realmente cuenta número de prácticas, no días**

**Escenario problemático**:
1. Usuario hace 5 prácticas **el mismo día**
2. Sistema muestra: `rachaActual: 5 dias` ❌
3. **INCOHERENTE**: No son 5 días, es 1 día con 5 prácticas

**LÓGICA CORRECTA DE NEGOCIO**:

Una racha de días consecutivos en apps de entrenamiento significa:
- **Día 1**: Practicaste → Racha = 1 día
- **Día 2**: Practicaste → Racha = 2 días
- **Día 3**: NO practicaste → Racha = 0 días (se reinicia)
- **Día 4**: Practicaste → Racha = 1 día (empieza nueva racha)

**IMPLEMENTACIÓN CORRECTA**:
```python
# Calcular racha de días ÚNICOS con prácticas
fechas_unicas = set(p.fecha.date() for p in practicas)
fechas_ordenadas = sorted(fechas_unicas, reverse=True)

racha_dias = 0
fecha_esperada = datetime.now().date()

for fecha in fechas_ordenadas:
    if fecha == fecha_esperada:
        racha_dias += 1
        fecha_esperada -= timedelta(days=1)
    else:
        break  # Se rompió la racha

racha.racha_actual = racha_dias
```

**Ejemplo coherente**:
- 3 prácticas hoy + 2 prácticas ayer + 1 práctica anteayer → **Racha: 3 días** ✅
- 10 prácticas hoy → **Racha: 1 día** ✅

---

### 5. **Insignias** (`/recompensas/insignias`)
**Lógica de negocio**: ⚠️ **ACEPTABLE pero mejorable**

**Otorgadas en primera práctica**:
1. ✅ "🎯 Primera práctica" (coherente: es su primera vez)
2. ✅ "🎤 Cero muletillas" (coherente: 0 muletillas detectadas)
3. ✅ "👁️ Mirada profesional" (coherente: 87.6% contacto visual > 80%)
4. ✅ "😊 Expresivo natural" (coherente: expresividad_nivel = "alta")
5. ✅ "👐 Manos comunicativas" (coherente: gestos_manos = "frecuente")
6. ✅ "⏱️ Ritmo perfecto" (coherente: velocidad = "normal")

**Observación**:
- En primera práctica se otorgan 6 insignias
- **¿Es motivador o abrumador?**

**Desde lógica de negocio de gamificación**:
- ✅ **CORRECTO**: Refuerzo positivo inicial es clave para engagement
- ✅ Criterios son objetivos (basados en métricas reales)
- ⚠️ Considerar: ¿Debería haber insignias "progresivas"?
  - Ejemplo: "Primera práctica" → "3 prácticas" → "10 prácticas"
  - Actualmente: Primera (1) → Constancia (3) → Dedicado (5) → Orador (10)
  - **ESTÁ BIEN IMPLEMENTADO** ✅

**Insignias que NO se otorgan** (correctamente):
- ❌ "🧍 Postura impecable" → NO se otorga porque postura = "mala" ✅
- ❌ "🔥 Constancia" → NO se otorga porque total_practicas = 1 < 3 ✅

**Veredicto**: Lógica de insignias es coherente.

---

## 📊 **RESUMEN DE CONSISTENCIA**

| Endpoint | Lógica de Negocio | Estado | Prioridad de Corrección |
|----------|-------------------|--------|-------------------------|
| `/plan/actual` | Detecta debilidades y genera ejercicios personalizados | ✅ CORRECTO | - |
| `/practica/historial` | Ordena por fecha DESC | ✅ CORRECTO | - |
| `/progreso/resumen` | División en mitades | ⚠️ CONCEPTUAL | 🟡 MEDIA |
| `/recompensas/racha` | Cuenta prácticas en vez de días | ❌ INCORRECTO | 🔴 ALTA |
| `/recompensas/insignias` | Criterios objetivos y motivadores | ✅ CORRECTO | - |

---

## 🎯 **RECOMENDACIONES**

### **Prioridad ALTA** (Corregir YA):
1. **Racha**: Cambiar lógica para contar días consecutivos con al menos 1 práctica
   - Impacto: Alta inconsistencia semántica
   - Usuario ve "5 días" pero solo practicó 1 día

### **Prioridad MEDIA** (Mejorar después):
2. **Tendencias**: Usar ventana deslizante (últimas N vs N previas)
   - Impacto: Con 2 prácticas funciona, con 10+ la lógica es confusa
   - Pedagogía: "últimas 3 sesiones" es más claro que "segunda mitad"

### **Mantener**:
3. Plan personalizado ✅
4. Sistema de insignias ✅
5. Historial ✅

---

## 🔧 **CÓDIGO PROPUESTO**

Ver archivo: `backend/main.py` líneas a modificar:
- **Racha**: Línea 702-709
- **Tendencias**: Línea 720-820

