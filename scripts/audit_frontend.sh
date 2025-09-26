#!/bin/bash
# Script para auditoría de dependencias del frontend

echo "🔍 AUDITORÍA DE DEPENDENCIAS FRONTEND - MEDICLAB"
echo "================================================"

# Cambiar al directorio frontend
cd "$(dirname "$0")/../frontend" || exit 1

echo "📁 Directorio actual: $(pwd)"
echo ""

# Verificar que package.json existe
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json no encontrado"
    exit 1
fi

echo "1. Ejecutando npm audit..."
echo "=========================="

# Ejecutar npm audit y guardar resultado
npm audit > npm_audit_report.txt 2>&1
audit_exit_code=$?

# Mostrar resultado en pantalla
cat npm_audit_report.txt

echo ""
echo "2. Ejecutando npm audit --json..."
echo "================================="

# Generar reporte JSON
npm audit --json > npm_audit_report.json 2>&1

echo "✅ Reporte JSON generado: npm_audit_report.json"

echo ""
echo "3. Verificando fixes disponibles..."
echo "==================================="

# Verificar qué se puede arreglar automáticamente
npm audit fix --dry-run

echo ""
echo "4. Analizando dependencias outdated..."
echo "======================================"

# Verificar dependencias desactualizadas
npm outdated || true

echo ""
echo "📊 RESUMEN DE AUDITORÍA FRONTEND"
echo "================================"

if [ $audit_exit_code -eq 0 ]; then
    echo "✅ npm audit: Sin vulnerabilidades encontradas"
else
    echo "⚠️  npm audit: Se encontraron vulnerabilidades (código: $audit_exit_code)"
fi

echo ""
echo "📄 Archivos generados:"
echo "- npm_audit_report.txt (reporte legible)"
echo "- npm_audit_report.json (reporte estructurado)"

echo ""
echo "🔧 Para aplicar fixes automáticos:"
echo "   npm audit fix"
echo ""
echo "⚠️  Para fixes que requieren cambios breaking:"
echo "   npm audit fix --force"

echo ""
echo "✅ Auditoría frontend completada"