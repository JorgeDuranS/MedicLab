@echo off
REM Script maestro para ejecutar auditoría completa de seguridad en Windows

echo 🛡️  AUDITORÍA COMPLETA DE SEGURIDAD - MEDICLAB
echo ==============================================
echo Fecha: %date% %time%
echo.

REM Obtener directorio del proyecto
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo 📁 Directorio del proyecto: %PROJECT_ROOT%
echo.

REM Verificar estructura del proyecto
if not exist "%PROJECT_ROOT%\backend" (
    echo ❌ Error: Directorio backend no encontrado
    exit /b 1
)
if not exist "%PROJECT_ROOT%\frontend" (
    echo ❌ Error: Directorio frontend no encontrado
    exit /b 1
)

REM Crear directorio para reportes si no existe
if not exist "%PROJECT_ROOT%\security_reports" mkdir "%PROJECT_ROOT%\security_reports"

echo 🔍 FASE 1: AUDITORÍA BACKEND (Python)
echo =====================================

REM Cambiar al directorio backend
cd /d "%PROJECT_ROOT%\backend"

echo Ejecutando Safety check...
safety check > safety_report.txt 2>&1
if %errorlevel% equ 0 (
    echo ✅ Safety check: Sin vulnerabilidades conocidas
) else (
    echo ⚠️  Safety check: Vulnerabilidades encontradas
)

safety check --json --output safety_report.json 2>nul

echo.
echo Ejecutando Bandit...
bandit -r . -ll > bandit_report.txt 2>&1
if %errorlevel% equ 0 (
    echo ✅ Bandit: Sin issues críticos
) else (
    echo ⚠️  Bandit: Issues encontrados
)

bandit -r . -f json -o bandit_report.json 2>nul

set backend_result=%errorlevel%

echo.
echo 🔍 FASE 2: AUDITORÍA FRONTEND (Node.js)
echo ======================================

REM Cambiar al directorio frontend
cd /d "%PROJECT_ROOT%\frontend"

echo Ejecutando npm audit...
npm audit > npm_audit_report.txt 2>&1
set frontend_result=%errorlevel%

if %frontend_result% equ 0 (
    echo ✅ npm audit: Sin vulnerabilidades
) else (
    echo ⚠️  npm audit: Vulnerabilidades encontradas
)

npm audit --json > npm_audit_report.json 2>nul

echo.
echo 📊 GENERANDO REPORTE CONSOLIDADO
echo ================================

REM Generar timestamp para el archivo
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set "report_file=%PROJECT_ROOT%\security_reports\security_audit_%timestamp%.md"

REM Crear reporte consolidado
(
echo # Reporte de Auditoría de Seguridad - MedicLab
echo.
echo **Fecha:** %date% %time%
echo **Sistema:** Windows
echo.
echo ## Resumen Ejecutivo
echo.
echo ### Backend (Python^)
if %backend_result% equ 0 (
    echo - **Estado:** ✅ PASS
) else (
    echo - **Estado:** ⚠️ ISSUES ENCONTRADOS
)
echo - **Herramientas:** Safety, Bandit
echo - **Archivos:** backend/safety_report.*, backend/bandit_report.*
echo.
echo ### Frontend (Node.js^)
if %frontend_result% equ 0 (
    echo - **Estado:** ✅ PASS
) else (
    echo - **Estado:** ⚠️ ISSUES ENCONTRADOS
)
echo - **Herramientas:** npm audit
echo - **Archivos:** frontend/npm_audit_report.*
echo.
echo ## Próximos Pasos
echo.
echo 1. Revisar reportes detallados en backend/ y frontend/
echo 2. Aplicar fixes: `cd frontend ^&^& npm audit fix`
echo 3. Actualizar dependencias de Python según reportes
echo 4. Re-ejecutar auditoría después de correcciones
echo.
echo ## Comandos de Corrección
echo.
echo ### Frontend
echo ```
echo cd frontend
echo npm audit fix
echo npm audit fix --force
echo ```
echo.
echo ### Backend
echo ```
echo cd backend
echo pip install --upgrade safety bandit
echo pip install --upgrade ^<package_name^>
echo ```
) > "%report_file%"

echo ✅ Reporte consolidado generado: %report_file%

echo.
echo 🏁 AUDITORÍA COMPLETA FINALIZADA
echo ================================

if %backend_result% equ 0 if %frontend_result% equ 0 (
    echo ✅ Estado general: TODAS LAS AUDITORÍAS PASARON
    set exit_code=0
) else (
    echo ⚠️  Estado general: SE ENCONTRARON ISSUES DE SEGURIDAD
    set exit_code=1
)

echo.
echo 📄 Reporte completo: %report_file%
echo 📁 Reportes detallados en directorios backend/ y frontend/

cd /d "%PROJECT_ROOT%"
exit /b %exit_code%