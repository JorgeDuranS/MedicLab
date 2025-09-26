#!/usr/bin/env python3
"""
Script para auditoría automática de dependencias de seguridad
Ejecuta safety check y bandit para el backend Python
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n{'='*50}")
    print(f"Ejecutando: {description}")
    print(f"Comando: {' '.join(command)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"⚠️  Comando falló con código de salida: {result.returncode}")
            return False
        else:
            print("✅ Comando ejecutado exitosamente")
            return True
            
    except FileNotFoundError:
        print(f"❌ Error: Comando no encontrado. Asegúrate de que esté instalado.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def audit_python_dependencies():
    """Audita dependencias de Python usando safety y bandit"""
    print("\n🔍 AUDITORÍA DE DEPENDENCIAS PYTHON")
    
    # Cambiar al directorio backend
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    results = []
    
    # 1. Safety check para vulnerabilidades conocidas
    print("\n1. Ejecutando Safety check...")
    safety_result = run_command(
        ["safety", "check", "--json"],
        "Safety check para vulnerabilidades conocidas"
    )
    results.append(("Safety Check", safety_result))
    
    # También ejecutar safety en modo texto para ver resultados
    run_command(
        ["safety", "check"],
        "Safety check (salida de texto)"
    )
    
    # 2. Bandit para análisis de código estático
    print("\n2. Ejecutando Bandit...")
    bandit_result = run_command(
        ["bandit", "-r", ".", "-f", "json", "-o", "bandit_report.json"],
        "Bandit análisis de seguridad estática"
    )
    results.append(("Bandit Analysis", bandit_result))
    
    # También ejecutar bandit en modo texto
    run_command(
        ["bandit", "-r", ".", "-ll"],
        "Bandit análisis (salida de texto, solo medium/high)"
    )
    
    return results

def audit_npm_dependencies():
    """Audita dependencias de Node.js usando npm audit"""
    print("\n🔍 AUDITORÍA DE DEPENDENCIAS NODE.JS")
    
    # Cambiar al directorio frontend
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    results = []
    
    # 1. npm audit
    print("\n1. Ejecutando npm audit...")
    npm_audit_result = run_command(
        ["npm", "audit", "--json"],
        "npm audit para vulnerabilidades"
    )
    results.append(("npm audit", npm_audit_result))
    
    # También ejecutar en modo texto para ver resultados
    run_command(
        ["npm", "audit"],
        "npm audit (salida de texto)"
    )
    
    # 2. npm audit fix (solo mostrar qué se puede arreglar)
    print("\n2. Verificando fixes disponibles...")
    run_command(
        ["npm", "audit", "fix", "--dry-run"],
        "npm audit fix (dry run)"
    )
    
    return results

def generate_audit_report(python_results, npm_results):
    """Genera un reporte consolidado de auditoría"""
    report_path = Path(__file__).parent.parent / "security_audit_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Reporte de Auditoría de Seguridad - MedicLab\n\n")
        import datetime
        f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Resumen Ejecutivo\n\n")
        
        # Python results
        f.write("### Backend Python\n\n")
        for tool, success in python_results:
            status = "✅ PASS" if success else "❌ ISSUES FOUND"
            f.write(f"- **{tool}**: {status}\n")
        
        f.write("\n### Frontend Node.js\n\n")
        for tool, success in npm_results:
            status = "✅ PASS" if success else "❌ ISSUES FOUND"
            f.write(f"- **{tool}**: {status}\n")
        
        f.write("\n## Archivos de Reporte Detallado\n\n")
        f.write("- `backend/safety_report.json` - Vulnerabilidades de dependencias Python\n")
        f.write("- `backend/bandit_report.json` - Análisis de código estático Python\n")
        f.write("- Ejecutar `npm audit` en directorio frontend para detalles de Node.js\n")
        
        f.write("\n## Recomendaciones\n\n")
        f.write("1. Revisar todos los reportes detallados\n")
        f.write("2. Actualizar dependencias con vulnerabilidades conocidas\n")
        f.write("3. Ejecutar `npm audit fix` para arreglos automáticos en frontend\n")
        f.write("4. Revisar y corregir issues de Bandit en código Python\n")
        f.write("5. Re-ejecutar auditoría después de aplicar fixes\n")
    
    print(f"\n📄 Reporte consolidado generado: {report_path}")

def main():
    """Función principal"""
    print("🛡️  AUDITORÍA DE SEGURIDAD DE DEPENDENCIAS - MEDICLAB")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if not (project_root / "backend").exists() or not (project_root / "frontend").exists():
        print("❌ Error: No se encontraron directorios backend y frontend")
        print(f"Ejecutar desde: {project_root}")
        sys.exit(1)
    
    # Auditar dependencias Python
    python_results = audit_python_dependencies()
    
    # Auditar dependencias Node.js
    npm_results = audit_npm_dependencies()
    
    # Generar reporte consolidado
    generate_audit_report(python_results, npm_results)
    
    # Resumen final
    print("\n" + "="*60)
    print("🏁 AUDITORÍA COMPLETADA")
    print("="*60)
    
    all_passed = all(result[1] for result in python_results + npm_results)
    
    if all_passed:
        print("✅ Todas las auditorías pasaron sin issues críticos")
    else:
        print("⚠️  Se encontraron issues de seguridad. Revisar reportes detallados.")
    
    print("\nPróximos pasos:")
    print("1. Revisar security_audit_report.md")
    print("2. Revisar reportes JSON detallados")
    print("3. Aplicar fixes necesarios")
    print("4. Re-ejecutar auditoría")

if __name__ == "__main__":
    main()