#!/bin/bash
# Script maestro para ejecutar auditoría completa de seguridad

echo "🛡️  AUDITORÍA COMPLETA DE SEGURIDAD - MEDICLAB"
echo "=============================================="
echo "Fecha: $(date)"
echo ""

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Directorio del proyecto: $PROJECT_ROOT"
echo ""

# Verificar estructura del proyecto
if [ ! -d "$PROJECT_ROOT/backend" ] || [ ! -d "$PROJECT_ROOT/frontend" ]; then
    echo "❌ Error: Estructura del proyecto no encontrada"
    echo "Asegúrate de ejecutar desde el directorio correcto"
    exit 1
fi

# Crear directorio para reportes si no existe
mkdir -p "$PROJECT_ROOT/security_reports"

echo "🔍 FASE 1: AUDITORÍA BACKEND (Python)"
echo "====================================="

# Ejecutar auditoría del backend
bash "$SCRIPT_DIR/audit_backend.sh"
backend_result=$?

echo ""
echo "🔍 FASE 2: AUDITORÍA FRONTEND (Node.js)"
echo "======================================"

# Ejecutar auditoría del frontend
bash "$SCRIPT_DIR/audit_frontend.sh"
frontend_result=$?

echo ""
echo "📊 GENERANDO REPORTE CONSOLIDADO"
echo "================================"

# Generar reporte consolidado
report_file="$PROJECT_ROOT/security_reports/security_audit_$(date +%Y%m%d_%H%M%S).md"

cat > "$report_file" << EOF
# Reporte de Auditoría de Seguridad - MedicLab

**Fecha:** $(date)
**Ejecutado por:** $(whoami)

## Resumen Ejecutivo

### Backend (Python)
- **Estado:** $([ $backend_result -eq 0 ] && echo "✅ PASS" || echo "⚠️ ISSUES ENCONTRADOS")
- **Herramientas:** Safety, Bandit, pip-audit
- **Archivos:** backend/safety_report.*, backend/bandit_report.*

### Frontend (Node.js)
- **Estado:** $([ $frontend_result -eq 0 ] && echo "✅ PASS" || echo "⚠️ ISSUES ENCONTRADOS")
- **Herramientas:** npm audit
- **Archivos:** frontend/npm_audit_report.*

## Archivos de Reporte Detallado

### Backend
- \`backend/safety_report.json\` - Vulnerabilidades conocidas (JSON)
- \`backend/safety_report.txt\` - Vulnerabilidades conocidas (texto)
- \`backend/bandit_report.json\` - Análisis estático (JSON)
- \`backend/bandit_report.txt\` - Análisis estático (texto)

### Frontend
- \`frontend/npm_audit_report.json\` - Auditoría npm (JSON)
- \`frontend/npm_audit_report.txt\` - Auditoría npm (texto)

## Próximos Pasos

1. **Revisar reportes detallados** en los archivos generados
2. **Actualizar dependencias** con vulnerabilidades conocidas
3. **Aplicar fixes automáticos:**
   - Frontend: \`cd frontend && npm audit fix\`
   - Backend: Actualizar versions en requirements.txt
4. **Corregir issues de código** identificados por Bandit
5. **Re-ejecutar auditoría** después de aplicar correcciones

## Comandos de Corrección

### Frontend
\`\`\`bash
cd frontend
npm audit fix                    # Fixes automáticos
npm audit fix --force           # Fixes que requieren breaking changes
npm update                       # Actualizar a versiones compatibles
\`\`\`

### Backend
\`\`\`bash
cd backend
pip install --upgrade safety bandit pip-audit
# Actualizar dependencias específicas según reportes
pip install --upgrade <package_name>
\`\`\`

## Automatización

Para ejecutar esta auditoría regularmente:

\`\`\`bash
# Ejecutar auditoría completa
./scripts/run_security_audit.sh

# Solo backend
./scripts/audit_backend.sh

# Solo frontend
./scripts/audit_frontend.sh
\`\`\`

---
*Reporte generado automáticamente por el sistema de auditoría de MedicLab*
EOF

echo "✅ Reporte consolidado generado: $report_file"

echo ""
echo "🏁 AUDITORÍA COMPLETA FINALIZADA"
echo "================================"

if [ $backend_result -eq 0 ] && [ $frontend_result -eq 0 ]; then
    echo "✅ Estado general: TODAS LAS AUDITORÍAS PASARON"
    exit_code=0
else
    echo "⚠️  Estado general: SE ENCONTRARON ISSUES DE SEGURIDAD"
    echo ""
    echo "Revisar:"
    [ $backend_result -ne 0 ] && echo "- Issues en backend (Python)"
    [ $frontend_result -ne 0 ] && echo "- Issues en frontend (Node.js)"
    exit_code=1
fi

echo ""
echo "📄 Reporte completo: $report_file"
echo "📁 Reportes detallados en directorios backend/ y frontend/"

exit $exit_code