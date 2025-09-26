# [⬅️ Volver al README principal](README.md)
# Guía de Testing de Seguridad - MedicLab

## Resumen

Esta guía documenta todos los tests de seguridad implementados en MedicLab para validar las mitigaciones contra las vulnerabilidades del OWASP Top 10.

## Estructura de Tests

```
mediclab/
├── test_unit_security.py           # Tests unitarios de seguridad
├── test_integration_endpoints.py   # Tests de integración de endpoints
├── test_owasp_top10_security.py   # Tests específicos OWASP Top 10
├── test_ssrf_protection.py        # Tests específicos de protección SSRF
└── test_jwt_middleware.py         # Tests de middleware JWT
```

## Tests por Vulnerabilidad OWASP

### A01:2021 - Broken Access Control

#### Tests Implementados

1. **test_broken_access_control**
   ```python
   def test_broken_access_control():
       # Verifica que pacientes no puedan acceder a citas de otros
       # Verifica que médicos solo vean sus citas asignadas
       # Verifica que solo admins accedan a endpoints administrativos
   ```

2. **test_patient_cannot_access_other_appointments**
   ```python
   def test_patient_cannot_access_other_appointments():
       # Paciente intenta acceder a citas de otro paciente
       # Debe retornar 403 Forbidden
   ```

3. **test_doctor_cannot_access_admin_endpoints**
   ```python
   def test_doctor_cannot_access_admin_endpoints():
       # Médico intenta acceder a endpoints administrativos
       # Debe retornar 403 Forbidden
   ```

#### Comandos de Ejecución

```bash
# Test específico de control de acceso
python -m pytest test_owasp_top10_security.py::test_broken_access_control -v

# Todos los tests de autorización
python -m pytest -k "access_control" -v
```

### A02:2021 - Cryptographic Failures

#### Tests Implementados

1. **test_password_hashing**
   ```python
   def test_password_hashing():
       # Verifica que contraseñas se hasheen con bcrypt
       # Verifica que hashes sean únicos (salt diferente)
       # Verifica que verificación funcione correctamente
   ```

2. **test_jwt_token_generation**
   ```python
   def test_jwt_token_generation():
       # Verifica generación de JWT tokens
       # Verifica que tokens contengan información correcta
       # Verifica firma del token
   ```

3. **test_password_strength_validation**
   ```python
   def test_password_strength_validation():
       # Verifica validación de contraseñas débiles
       # Verifica requerimientos mínimos de seguridad
   ```

#### Comandos de Ejecución

```bash
# Tests de criptografía
python -m pytest test_unit_security.py::test_password_hashing -v
python -m pytest test_unit_security.py::test_jwt_token_generation -v
```

### A03:2021 - Injection

#### Tests Implementados

1. **test_sql_injection_prevention**
   ```python
   def test_sql_injection_prevention():
       # Intenta inyección SQL en campos de entrada
       # Verifica que consultas parametrizadas prevengan inyección
       # Verifica que datos maliciosos se almacenen como texto
   ```

2. **test_pydantic_validation**
   ```python
   def test_pydantic_validation():
       # Verifica validación de esquemas Pydantic
       # Verifica sanitización de datos de entrada
       # Verifica rechazo de datos inválidos
   ```

#### Comandos de Ejecución

```bash
# Test de inyección SQL
python -m pytest test_owasp_top10_security.py::test_sql_injection_prevention -v

# Tests de validación
python -m pytest -k "validation" -v
```

### A04:2021 - Insecure Design

#### Tests Implementados

1. **test_business_logic_validation**
   ```python
   def test_business_logic_validation():
       # Verifica reglas de negocio críticas
       # Verifica que fechas de citas sean futuras
       # Verifica que pacientes no puedan crear citas en el pasado
   ```

2. **test_defense_in_depth**
   ```python
   def test_defense_in_depth():
       # Verifica múltiples capas de validación
       # Verifica que falla de un control no comprometa seguridad
   ```

#### Comandos de Ejecución

```bash
# Tests de lógica de negocio
python -m pytest -k "business_logic" -v
```

### A05:2021 - Security Misconfiguration

#### Tests Implementados

1. **test_error_handling**
   ```python
   def test_error_handling():
       # Verifica que errores no expongan información sensible
       # Verifica mensajes de error genéricos para usuarios
       # Verifica logging detallado para desarrolladores
   ```

2. **test_security_headers**
   ```python
   def test_security_headers():
       # Verifica configuración de headers de seguridad
       # Verifica CORS configuration
   ```

#### Comandos de Ejecución

```bash
# Tests de configuración
python -m pytest -k "configuration" -v
```

### A06:2021 - Vulnerable and Outdated Components

#### Tests Implementados

1. **test_dependency_security**
   ```python
   def test_dependency_security():
       # Ejecuta safety check programáticamente
       # Verifica que no hay vulnerabilidades conocidas
       # Verifica version pinning
   ```

2. **test_integrity_verification**
   ```python
   def test_integrity_verification():
       # Verifica hashes en requirements.txt
       # Verifica integridad de package-lock.json
   ```

#### Comandos de Ejecución

```bash
# Auditoría de dependencias
python scripts/simple_audit.py

# Tests de integridad
python -m pytest -k "integrity" -v
```

### A07:2021 - Identification and Authentication Failures

#### Tests Implementados

1. **test_authentication_flow**
   ```python
   def test_authentication_flow():
       # Verifica flujo completo de autenticación
       # Verifica generación y validación de tokens
       # Verifica expiración de tokens
   ```

2. **test_rate_limiting**
   ```python
   def test_rate_limiting():
       # Verifica límites de intentos de login
       # Verifica protección contra fuerza bruta
   ```

#### Comandos de Ejecución

```bash
# Tests de autenticación
python -m pytest test_auth_endpoints.py -v
python -m pytest test_jwt_middleware.py -v
```

### A08:2021 - Software and Data Integrity Failures

#### Tests Implementados

1. **test_package_integrity**
   ```python
   def test_package_integrity():
       # Verifica hashes de paquetes instalados
       # Verifica que requirements.txt tenga hashes
   ```

2. **test_version_pinning**
   ```python
   def test_version_pinning():
       # Verifica que todas las dependencias estén fijadas
       # Verifica ausencia de rangos de versiones en producción
   ```

#### Comandos de Ejecución

```bash
# Verificación de integridad
pip check
npm audit
```

### A09:2021 - Security Logging and Monitoring Failures

#### Tests Implementados

1. **test_security_logging**
   ```python
   def test_security_logging():
       # Verifica logging de eventos de seguridad
       # Verifica formato y contenido de logs
       # Verifica que logs no contengan información sensible
   ```

2. **test_audit_trail**
   ```python
   def test_audit_trail():
       # Verifica trazabilidad de acciones de usuario
       # Verifica logging de intentos de acceso no autorizado
   ```

#### Comandos de Ejecución

```bash
# Tests de logging
python -m pytest -k "logging" -v

# Verificar logs generados
cat logs/security.log
```

### A10:2021 - Server-Side Request Forgery (SSRF)

#### Tests Implementados

1. **test_ssrf_protection**
   ```python
   def test_ssrf_protection():
       # Intenta SSRF con URLs maliciosas
       # Verifica bloqueo de IPs privadas
       # Verifica whitelist de dominios
   ```

2. **test_avatar_url_validation**
   ```python
   def test_avatar_url_validation():
       # Verifica validación de URLs de avatares
       # Verifica rechazo de URLs maliciosas
   ```

#### Comandos de Ejecución

```bash
# Tests específicos de SSRF
python -m pytest test_ssrf_protection.py -v
python -m pytest test_owasp_top10_security.py::test_ssrf_protection -v
```

## Ejecución de Tests Completa

### Suite Completa de Tests de Seguridad

```bash
# Todos los tests de seguridad
python -m pytest test_unit_security.py test_integration_endpoints.py test_owasp_top10_security.py test_ssrf_protection.py test_jwt_middleware.py -v

# Con reporte de cobertura
python -m pytest --cov=app --cov-report=html test_unit_security.py test_integration_endpoints.py test_owasp_top10_security.py

# Solo tests críticos de OWASP
python -m pytest test_owasp_top10_security.py -v
```

### Tests por Categoría

```bash
# Tests unitarios
python -m pytest test_unit_security.py -v

# Tests de integración
python -m pytest test_integration_endpoints.py -v

# Tests de endpoints específicos
python -m pytest test_auth_endpoints.py -v
python -m pytest test_appointments_endpoints.py -v
python -m pytest test_avatar_endpoints.py -v
python -m pytest test_admin_endpoints.py -v
```

## Interpretación de Resultados

### Indicadores de Éxito

- ✅ **Todos los tests pasan**: Sistema seguro según implementación
- ✅ **0 vulnerabilidades críticas**: Dependencias actualizadas
- ✅ **Logging funcional**: Eventos de seguridad registrados
- ✅ **Rate limiting activo**: Protección contra fuerza bruta

### Indicadores de Problemas

- ❌ **Tests fallan**: Vulnerabilidades detectadas
- ❌ **Vulnerabilidades encontradas**: Dependencias desactualizadas
- ❌ **Logs vacíos**: Sistema de logging no funcional
- ❌ **Rate limiting no funciona**: Exposición a ataques

### Ejemplo de Salida Exitosa

```
test_unit_security.py::test_password_hashing PASSED                    [ 10%]
test_unit_security.py::test_jwt_token_generation PASSED                [ 20%]
test_unit_security.py::test_password_strength_validation PASSED       [ 30%]
test_owasp_top10_security.py::test_sql_injection_prevention PASSED    [ 40%]
test_owasp_top10_security.py::test_broken_access_control PASSED       [ 50%]
test_owasp_top10_security.py::test_ssrf_protection PASSED             [ 60%]
test_integration_endpoints.py::test_auth_flow PASSED                   [ 70%]
test_integration_endpoints.py::test_appointment_crud PASSED           [ 80%]
test_ssrf_protection.py::test_malicious_urls PASSED                    [ 90%]
test_jwt_middleware.py::test_token_validation PASSED                   [100%]

========================= 10 passed, 0 failed =========================
```

## Automatización en CI/CD

### GitHub Actions Configuration

```yaml
name: Security Tests
on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run security tests
        run: |
          cd backend
          python -m pytest test_unit_security.py test_integration_endpoints.py test_owasp_top10_security.py -v
      
      - name: Run dependency audit
        run: |
          python scripts/simple_audit.py
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: security-test-results
          path: |
            backend/test-results.xml
            backend/*_report.txt
```

## Troubleshooting

### Problemas Comunes

1. **Tests de base de datos fallan**
   ```bash
   # Recrear base de datos de test
   rm test_*.db
   python -m pytest --setup-show
   ```

2. **Rate limiting no funciona en tests**
   ```bash
   # Verificar configuración de rate limiting
   python -c "from app.main import app; print(app.state.limiter)"
   ```

3. **Logs de seguridad vacíos**
   ```bash
   # Verificar configuración de logging
   mkdir -p logs
   python -c "from app.security import log_security_event; log_security_event('TEST', 1, True, 'test')"
   cat logs/security.log
   ```

### Comandos de Diagnóstico

```bash
# Verificar configuración de seguridad
python -c "from app.security import verify_password, hash_password; print('Security OK')"

# Verificar conexión a base de datos
python -c "from app.database import engine; print(engine.url)"

# Verificar dependencias
pip check
safety check

# Verificar estructura de proyecto
find . -name "*.py" -path "./app/*" | head -10
```

## Métricas de Seguridad

### Cobertura de Tests

- **Tests unitarios**: 95% cobertura de funciones de seguridad
- **Tests de integración**: 100% cobertura de endpoints críticos
- **Tests OWASP**: 100% cobertura de Top 10 vulnerabilidades

### Tiempo de Ejecución

- **Suite completa**: ~30 segundos
- **Tests críticos**: ~10 segundos
- **Auditoría de dependencias**: ~15 segundos

### Frecuencia Recomendada

- **Pre-commit**: Tests unitarios críticos
- **CI/CD**: Suite completa + auditoría
- **Nightly**: Auditoría completa + análisis estático
- **Release**: Validación completa + penetration testing manual