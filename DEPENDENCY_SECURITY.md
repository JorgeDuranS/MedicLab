# [⬅️ Volver al README principal](README.md)
# Guía de Seguridad de Dependencias - MedicLab

## Resumen

Este documento describe las medidas implementadas para asegurar la integridad y seguridad de las dependencias del proyecto MedicLab, incluyendo version pinning, verificación de integridad y auditorías de seguridad.

## Version Pinning (Fijación de Versiones)

### Backend (Python)

#### Archivos de Dependencias

1. **`requirements.in`** - Archivo fuente con versiones específicas
2. **`requirements.txt`** - Archivo generado con hashes para verificación de integridad
3. **`requirements_secure.txt`** - Versiones actualizadas sin vulnerabilidades conocidas

#### Versiones Actualizadas por Seguridad

Las siguientes dependencias fueron actualizadas para corregir vulnerabilidades:

```
python-multipart: 0.0.6 → 0.0.18
- CVE-2024-53981: Allocation of Resources Without Limits
- PVE-2024-99762: Regular Expression Denial of Service (ReDoS)

python-jose[cryptography]: 3.3.0 → 3.4.0
- CVE-2024-33663: Algorithm confusion vulnerability
- CVE-2024-33664: Denial of service via crafted decode

safety: 2.3.5 → 3.2.11
- Versión actualizada con mejores capacidades de detección

bandit: 1.7.5 → 1.7.7
- PVE-2024-64484: Identificación mejorada de riesgos de inyección SQL
```

#### Generación de Requirements con Hashes

```bash
# Instalar pip-tools
pip install pip-tools

# Generar requirements.txt con hashes
pip-compile --generate-hashes requirements.in

# Instalar con verificación de integridad
pip install -r requirements.txt
```

### Frontend (Node.js)

#### Version Pinning en package.json

Se removieron los prefijos `^` y `~` para fijar versiones exactas:

```json
{
  "dependencies": {
    "react": "18.2.0",           // Fijado (era ^18.2.0)
    "react-dom": "18.2.0",       // Fijado (era ^18.2.0)
    "react-router-dom": "6.8.1", // Fijado (era ^6.8.1)
    "axios": "1.6.2"             // Actualizado y fijado (era ^1.6.0)
  }
}
```

#### Verificación de Integridad

```bash
# Generar package-lock.json con hashes
npm install

# Verificar integridad en CI/CD
npm ci
```

## Auditorías de Seguridad

### Scripts de Auditoría Automatizada

#### 1. Script Principal: `run_security_audit.sh`

Ejecuta auditoría completa de backend y frontend:

```bash
./scripts/run_security_audit.sh
```

#### 2. Script de Backend: `audit_backend.sh`

Audita dependencias Python:

```bash
./scripts/audit_backend.sh
```

#### 3. Script de Frontend: `audit_frontend.sh`

Audita dependencias Node.js:

```bash
./scripts/audit_frontend.sh
```

#### 4. Script Python Simplificado: `simple_audit.py`

Compatible con Windows y Unix:

```bash
python scripts/simple_audit.py
```

### Herramientas de Auditoría

#### Backend Python

1. **Safety** - Escaneo de vulnerabilidades conocidas
   ```bash
   safety check
   safety check --json --output safety_report.json
   ```

2. **Bandit** - Análisis de código estático
   ```bash
   bandit -r . -ll  # Solo medium/high severity
   bandit -r . -f json -o bandit_report.json
   ```

3. **pip-audit** (Opcional)
   ```bash
   pip install pip-audit
   pip-audit --format=json --output=pip_audit_report.json
   ```

#### Frontend Node.js

1. **npm audit** - Auditoría de dependencias
   ```bash
   npm audit
   npm audit --json > npm_audit_report.json
   ```

2. **npm audit fix** - Corrección automática
   ```bash
   npm audit fix                # Fixes seguros
   npm audit fix --force       # Fixes con breaking changes
   ```

## Proceso de Verificación de Integridad

### 1. Verificación de Hashes (Python)

```bash
# Los hashes en requirements.txt verifican la integridad
pip install -r requirements.txt
# pip verificará automáticamente los hashes SHA256
```

### 2. Verificación de package-lock.json (Node.js)

```bash
# npm ci verifica integridad usando package-lock.json
npm ci
```

### 3. Verificación Manual de Hashes

```python
# Ejemplo de verificación manual
import hashlib

def verify_package_hash(file_path, expected_hash):
    with open(file_path, 'rb') as f:
        content = f.read()
        actual_hash = hashlib.sha256(content).hexdigest()
        return actual_hash == expected_hash
```

## Automatización en CI/CD

### GitHub Actions / CI Pipeline

```yaml
name: Security Audit
on: [push, pull_request]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Install Node.js dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run security audit
        run: ./scripts/run_security_audit.sh
      
      - name: Upload audit reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            backend/*_report.*
            frontend/*_report.*
            security_audit_*.md
```

## Monitoreo Continuo

### 1. Auditorías Programadas

```bash
# Crontab para auditorías diarias
0 2 * * * /path/to/project/scripts/run_security_audit.sh
```

### 2. Alertas de Vulnerabilidades

- Configurar GitHub Dependabot
- Usar herramientas como Snyk o WhiteSource
- Monitorear CVE databases

### 3. Actualizaciones Regulares

```bash
# Verificar dependencias desactualizadas
pip list --outdated
npm outdated

# Actualizar requirements.in y regenerar requirements.txt
pip-compile --upgrade requirements.in
```

## Mejores Prácticas

### 1. Version Pinning

- ✅ Fijar versiones exactas en producción
- ✅ Usar rangos de versiones solo en desarrollo
- ✅ Documentar razones para versiones específicas

### 2. Verificación de Integridad

- ✅ Usar hashes SHA256 para Python
- ✅ Usar package-lock.json para Node.js
- ✅ Verificar firmas digitales cuando estén disponibles

### 3. Auditorías Regulares

- ✅ Ejecutar auditorías en cada commit
- ✅ Revisar reportes de vulnerabilidades
- ✅ Actualizar dependencias vulnerables inmediatamente

### 4. Gestión de Vulnerabilidades

- ✅ Priorizar vulnerabilidades críticas y altas
- ✅ Evaluar impacto antes de actualizar
- ✅ Mantener registro de cambios de seguridad

## Comandos de Referencia Rápida

```bash
# Auditoría completa
./scripts/run_security_audit.sh

# Solo backend
./scripts/audit_backend.sh

# Solo frontend
./scripts/audit_frontend.sh

# Actualizar dependencias Python
cd backend
pip-compile --upgrade requirements.in

# Actualizar dependencias Node.js
cd frontend
npm update
npm audit fix

# Verificar integridad
pip install -r requirements.txt  # Python
npm ci                           # Node.js
```

## Resolución de Problemas

### Errores Comunes

1. **Hash mismatch en pip**
   ```bash
   # Regenerar requirements.txt
   pip-compile --generate-hashes requirements.in
   ```

2. **Vulnerabilidades en npm**
   ```bash
   # Intentar fix automático
   npm audit fix
   # Si no funciona, actualizar manualmente
   npm install package@latest
   ```

3. **Dependencias conflictivas**
   ```bash
   # Resolver conflictos Python
   pip-compile --resolver=backtracking requirements.in
   ```

## Contacto y Soporte

Para preguntas sobre seguridad de dependencias:
- Revisar logs de auditoría en `security_reports/`
- Consultar documentación de herramientas específicas
- Seguir proceso de actualización documentado