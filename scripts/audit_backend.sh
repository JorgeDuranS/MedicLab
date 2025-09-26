#!/bin/bash
# Script para auditoría de dependencias del backend Python

echo "🔍 AUDITORÍA DE DEPENDENCIAS BACKEND - MEDICLAB"
echo "==============================================="

# Cambiar al directorio backend
cd "$(dirname "$0")/../backend" || exit 1

echo "📁 Directorio actual: $(pwd)"
echo ""

# Verificar que requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    exit 1
fi

echo "1. Ejecutando Safety check..."
echo "============================="

# Verificar si safety está instalado
if ! command -v safety &> /dev/null; then
    echo "⚠️  Safety no está instalado. Instalando..."
    pip install safety
fi

# Ejecutar safety check
echo "Escaneando vulnerabilidades conocidas..."
safety check --json --output safety_report.json
safety_exit_code=$?

# También generar reporte legible
safety check > safety_report.txt 2>&1

# Mostrar resultado
if [ $safety_exit_code -eq 0 ]; then
    echo "✅ Safety check: Sin vulnerabilidades conocidas"
else
    echo "⚠️  Safety check: Vulnerabilidades encontradas"
    cat safety_report.txt
fi

echo ""
echo "2. Ejecutando Bandit (análisis estático)..."
echo "==========================================="

# Verificar si bandit está instalado
if ! command -v bandit &> /dev/null; then
    echo "⚠️  Bandit no está instalado. Instalando..."
    pip install bandit
fi

# Ejecutar bandit
echo "Analizando código para issues de seguridad..."
bandit -r . -f json -o bandit_report.json
bandit_exit_code=$?

# También generar reporte legible (solo medium y high)
bandit -r . -ll > bandit_report.txt 2>&1

# Mostrar resultado
if [ $bandit_exit_code -eq 0 ]; then
    echo "✅ Bandit: Sin issues de seguridad críticos"
else
    echo "⚠️  Bandit: Issues de seguridad encontrados"
    echo "Mostrando issues de nivel medium/high:"
    cat bandit_report.txt
fi

echo ""
echo "3. Verificando dependencias desactualizadas..."
echo "=============================================="

# Verificar dependencias desactualizadas con pip
echo "Dependencias que pueden ser actualizadas:"
pip list --outdated || true

echo ""
echo "4. Ejecutando pip-audit (si está disponible)..."
echo "==============================================="

# Verificar si pip-audit está disponible
if command -v pip-audit &> /dev/null; then
    echo "Ejecutando pip-audit..."
    pip-audit --format=json --output=pip_audit_report.json
    pip-audit > pip_audit_report.txt 2>&1
    pip_audit_exit_code=$?
    
    if [ $pip_audit_exit_code -eq 0 ]; then
        echo "✅ pip-audit: Sin vulnerabilidades"
    else
        echo "⚠️  pip-audit: Vulnerabilidades encontradas"
        cat pip_audit_report.txt
    fi
else
    echo "ℹ️  pip-audit no está instalado. Para instalarlo:"
    echo "   pip install pip-audit"
fi

echo ""
echo "📊 RESUMEN DE AUDITORÍA BACKEND"
echo "==============================="

echo "Safety check: $([ $safety_exit_code -eq 0 ] && echo "✅ PASS" || echo "❌ ISSUES")"
echo "Bandit analysis: $([ $bandit_exit_code -eq 0 ] && echo "✅ PASS" || echo "❌ ISSUES")"

echo ""
echo "📄 Archivos generados:"
echo "- safety_report.json / safety_report.txt"
echo "- bandit_report.json / bandit_report.txt"
if command -v pip-audit &> /dev/null; then
    echo "- pip_audit_report.json / pip_audit_report.txt"
fi

echo ""
echo "✅ Auditoría backend completada"