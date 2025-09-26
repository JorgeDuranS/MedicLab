#!/usr/bin/env python3
"""
Script simplificado para auditoría de dependencias
Compatible con Windows y sistemas Unix
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

def run_command_simple(command, description, capture_output=True):
    """Ejecuta un comando de forma simple"""
    print(f"\n{'='*50}")
    print(f"Ejecutando: {description}")
    print(f"Comando: {' '.join(command)}")
    print(f"{'='*50}")
    
    try:
        if capture_output:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            if result.stdout:
                print("SALIDA:")
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print("ERRORES:")
                print(result.stderr)
            
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, check=False)
            return result.returncode == 0, "", ""
            
    except FileNotFoundError:
        print(f"❌ Error: Comando '{command[0]}' no encontrado")
        return False, "", f"Comando {command[0]} no encontrado"
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, "", str(e)

def audit_backend():
    """Audita el backend Python"""
    print("\n🔍 AUDITORÍA BACKEND PYTHON")
    print("="*40)
    
    # Cambiar al directorio backend
    backend_dir = Path(__file__).parent.parent / "backend"
    original_dir = os.getcwd()
    
    try:
        os.chdir(backend_dir)
        print(f"📁 Directorio: {backend_dir}")
        
        results = {}
        
        # 1. Safety check
        print("\n1. Safety Check - Vulnerabilidades conocidas")
        success, stdout, stderr = run_command_simple(
            ["safety", "check"], 
            "Escaneo de vulnerabilidades con Safety"
        )
        results['safety'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Guardar reporte de safety
        with open('safety_report.txt', 'w', encoding='utf-8') as f:
            f.write(f"Safety Check Report - {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(stdout)
            if stderr:
                f.write("\n\nErrores:\n")
                f.write(stderr)
        
        # 2. Bandit check
        print("\n2. Bandit - Análisis de código estático")
        success, stdout, stderr = run_command_simple(
            ["bandit", "-r", ".", "-ll"], 
            "Análisis estático con Bandit (medium/high)"
        )
        results['bandit'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Guardar reporte de bandit
        with open('bandit_report.txt', 'w', encoding='utf-8') as f:
            f.write(f"Bandit Analysis Report - {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(stdout)
            if stderr:
                f.write("\n\nErrores:\n")
                f.write(stderr)
        
        # 3. Verificar dependencias desactualizadas
        print("\n3. Dependencias desactualizadas")
        success, stdout, stderr = run_command_simple(
            ["pip", "list", "--outdated"], 
            "Verificar dependencias desactualizadas"
        )
        results['outdated'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        return results
        
    finally:
        os.chdir(original_dir)

def audit_frontend():
    """Audita el frontend Node.js"""
    print("\n🔍 AUDITORÍA FRONTEND NODE.JS")
    print("="*40)
    
    # Cambiar al directorio frontend
    frontend_dir = Path(__file__).parent.parent / "frontend"
    original_dir = os.getcwd()
    
    try:
        os.chdir(frontend_dir)
        print(f"📁 Directorio: {frontend_dir}")
        
        results = {}
        
        # Verificar si npm está disponible
        npm_available = subprocess.run(["npm", "--version"], capture_output=True).returncode == 0
        
        if not npm_available:
            print("⚠️  npm no está disponible. Saltando auditoría de frontend.")
            return {'npm_audit': {'success': False, 'output': '', 'error': 'npm no disponible'}}
        
        # 1. npm audit
        print("\n1. npm audit - Vulnerabilidades de dependencias")
        success, stdout, stderr = run_command_simple(
            ["npm", "audit"], 
            "Auditoría de dependencias npm"
        )
        results['npm_audit'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        # Guardar reporte de npm audit
        with open('npm_audit_report.txt', 'w', encoding='utf-8') as f:
            f.write(f"npm audit Report - {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            f.write(stdout)
            if stderr:
                f.write("\n\nErrores:\n")
                f.write(stderr)
        
        # 2. npm outdated
        print("\n2. Dependencias desactualizadas")
        success, stdout, stderr = run_command_simple(
            ["npm", "outdated"], 
            "Verificar dependencias desactualizadas"
        )
        results['npm_outdated'] = {
            'success': success,
            'output': stdout,
            'error': stderr
        }
        
        return results
        
    finally:
        os.chdir(original_dir)

def generate_summary_report(backend_results, frontend_results):
    """Genera un reporte resumen"""
    report_path = Path(__file__).parent.parent / "security_audit_summary.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Reporte de Auditoría de Seguridad - MedicLab\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Resumen Ejecutivo\n\n")
        
        # Backend
        f.write("### Backend (Python)\n\n")
        if backend_results:
            safety_status = "✅ PASS" if backend_results.get('safety', {}).get('success', False) else "⚠️ ISSUES"
            bandit_status = "✅ PASS" if backend_results.get('bandit', {}).get('success', False) else "⚠️ ISSUES"
            
            f.write(f"- **Safety Check:** {safety_status}\n")
            f.write(f"- **Bandit Analysis:** {bandit_status}\n")
            f.write("- **Reportes:** `backend/safety_report.txt`, `backend/bandit_report.txt`\n")
        else:
            f.write("- **Estado:** ❌ ERROR EN AUDITORÍA\n")
        
        f.write("\n### Frontend (Node.js)\n\n")
        if frontend_results:
            npm_status = "✅ PASS" if frontend_results.get('npm_audit', {}).get('success', False) else "⚠️ ISSUES"
            f.write(f"- **npm audit:** {npm_status}\n")
            f.write("- **Reportes:** `frontend/npm_audit_report.txt`\n")
        else:
            f.write("- **Estado:** ❌ ERROR EN AUDITORÍA\n")
        
        f.write("\n## Próximos Pasos\n\n")
        f.write("1. **Revisar reportes detallados** en directorios backend/ y frontend/\n")
        f.write("2. **Actualizar dependencias** con vulnerabilidades:\n")
        f.write("   - Backend: Actualizar versions en requirements.txt\n")
        f.write("   - Frontend: `cd frontend && npm audit fix`\n")
        f.write("3. **Corregir issues de código** identificados por Bandit\n")
        f.write("4. **Re-ejecutar auditoría** después de aplicar correcciones\n")
        
        f.write("\n## Comandos de Corrección\n\n")
        f.write("### Frontend\n")
        f.write("```bash\n")
        f.write("cd frontend\n")
        f.write("npm audit fix                # Fixes automáticos\n")
        f.write("npm audit fix --force       # Fixes con breaking changes\n")
        f.write("```\n\n")
        
        f.write("### Backend\n")
        f.write("```bash\n")
        f.write("cd backend\n")
        f.write("pip install --upgrade safety bandit\n")
        f.write("# Actualizar dependencias específicas según reportes\n")
        f.write("```\n")
    
    print(f"\n📄 Reporte resumen generado: {report_path}")
    return report_path

def main():
    """Función principal"""
    print("🛡️  AUDITORÍA DE SEGURIDAD SIMPLIFICADA - MEDICLAB")
    print("="*60)
    
    # Verificar estructura del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if not (project_root / "backend").exists():
        print("❌ Error: Directorio backend no encontrado")
        sys.exit(1)
    
    if not (project_root / "frontend").exists():
        print("❌ Error: Directorio frontend no encontrado")
        sys.exit(1)
    
    # Ejecutar auditorías
    backend_results = audit_backend()
    frontend_results = audit_frontend()
    
    # Generar reporte
    report_path = generate_summary_report(backend_results, frontend_results)
    
    # Resumen final
    print("\n" + "="*60)
    print("🏁 AUDITORÍA COMPLETADA")
    print("="*60)
    
    # Determinar estado general
    backend_ok = backend_results and backend_results.get('safety', {}).get('success', False)
    frontend_ok = frontend_results and frontend_results.get('npm_audit', {}).get('success', False)
    
    if backend_ok and frontend_ok:
        print("✅ Estado general: AUDITORÍAS COMPLETADAS SIN ISSUES CRÍTICOS")
        exit_code = 0
    else:
        print("⚠️  Estado general: SE ENCONTRARON ISSUES DE SEGURIDAD")
        exit_code = 1
    
    print(f"\n📄 Reporte completo: {report_path}")
    print("📁 Reportes detallados en directorios backend/ y frontend/")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()