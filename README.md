
# 🚩 Cómo clonar este repositorio (principiantes)

Sigue estos pasos para obtener una copia de este proyecto en tu computadora:

1. **Abre una terminal o PowerShell** en la carpeta donde quieras guardar el proyecto.
2. **Clona el repositorio usando HTTPS:**
   ```bash
   git clone https://github.com/JorgeDuranS/MedicLab.git
   ```
3. **Entra a la carpeta del proyecto:**
   ```bash
   cd MedicLab/mediclab
   ```
4. ¡Listo! Ahora puedes seguir las instrucciones de instalación más abajo.

> 💡 Si nunca has usado Git, solo copia y pega los comandos uno por uno en tu terminal.

# 📚 Documentación y Recursos Importantes

Para aprender y profundizar en la seguridad y pruebas de este proyecto, revisa los siguientes documentos incluidos en el repositorio:

- [Resumen de Implementación de Seguridad](SECURITY_IMPLEMENTATION_SUMMARY.md)
- [Guía de Testing de Seguridad](SECURITY_TESTING_GUIDE.md)
- [Guía de Seguridad de Dependencias](DEPENDENCY_SECURITY.md)
- [Reporte de Auditoría de Seguridad](security_audit_report.md)
- [Resumen de Pruebas de Integración](test_integration_summary.md)
- [Resumen de Pruebas OWASP Top 10](test_owasp_summary.md)

# MedicLab 🏥

Sistema de gestión de citas médicas con implementación completa de seguridad OWASP Top 10.

## 🚀 Características

### ✨ Funcionalidades Principales
- **Sistema de autenticación JWT** con roles (Paciente, Médico, Administrador)
- **Gestión de citas médicas** con interfaz diferenciada por rol
- **Dashboard administrativo** con logs de seguridad en tiempo real
- **Protección SSRF** para avatares de usuario
- **Rate limiting** y logging de seguridad completo

### 🎯 Roles de Usuario
- **Pacientes**: Pueden agendar citas seleccionando médicos
- **Médicos**: Pueden crear citas para pacientes específicos
- **Administradores**: Acceso completo + dashboard de logs de seguridad

### 🔒 Seguridad Implementada
- Autenticación JWT con expiración
- Validación de roles y permisos
- Protección contra SSRF en avatares
- Rate limiting por endpoint
- Logging completo de eventos de seguridad
- Validación de entrada con Pydantic
- Consultas parametrizadas (SQLAlchemy)

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos ligera
- **Pydantic** - Validación de datos
- **JWT** - Autenticación
- **Bcrypt** - Hashing de contraseñas

### Frontend
- **React** - Biblioteca de UI
- **Tailwind CSS** - Framework de estilos
- **Vite** - Build tool
- **Axios** - Cliente HTTP

## 📦 Instalación

---

## 🗄️ ¿Cómo funciona la base de datos SQLite?

MedicLab utiliza SQLite como base de datos local, lo que significa que no necesitas instalar ni configurar un servidor de base de datos externo. El archivo de la base de datos se llama `database.db` y se encuentra en la carpeta `backend/`.

**¿Qué debes saber como principiante?**

- **Creación automática:** La base de datos y sus tablas se crean automáticamente al ejecutar el comando de inicialización (`python -c "from app.database import init_db; init_db()"`).
- **Usuarios y datos de prueba:** Al inicializar, se crean usuarios de ejemplo (admin, médicos y pacientes) y citas de muestra para que puedas probar la aplicación sin registrar nada manualmente.
- **Inspección:** Puedes abrir el archivo `database.db` con herramientas como [DB Browser for SQLite](https://sqlitebrowser.org/) para ver y modificar los datos de manera visual.
- **Persistencia:** Todos los datos que crees o modifiques desde la app se guardan en este archivo.
- **Restablecer datos:** Si quieres empezar de cero, puedes borrar el archivo `database.db` y volver a ejecutar el comando de inicialización.

**Estructura básica de la base de datos:**

- Tabla `users`: almacena usuarios, roles, contraseñas hasheadas y datos personales.
- Tabla `appointments`: almacena citas médicas, fechas, descripciones y relaciones paciente/médico.

---

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- npm o yarn

### Backend Setup

1. **Navegar al directorio backend**
   ```bash
   cd backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Inicializar base de datos**
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

6. **Ejecutar servidor**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navegar al directorio frontend**
   ```bash
   cd frontend
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Ejecutar aplicación**
   ```bash
   npm run dev
   ```

## 🚀 Uso

1. **Acceder a la aplicación**: http://localhost:3000
2. **API Documentation**: http://localhost:8000/docs
3. **Crear usuarios** a través del registro o usar usuarios de prueba

### Usuarios de Prueba
- **Paciente**: `patient@mediclab.com` / `password123`
- **Médico**: `doctor@mediclab.com` / `password123`
- **Admin**: `admin@mediclab.com` / `password123`

## 📊 Dashboard de Administrador

El dashboard de admin incluye:
- **Gestión de usuarios** - Ver todos los usuarios del sistema
- **Gestión de citas** - Ver todas las citas programadas
- **Logs de seguridad** - Monitoreo en tiempo real con filtros avanzados

### Filtros de Logs Disponibles
- Tipo de acción (LOGIN_ATTEMPT, UNAUTHORIZED_ACCESS, etc.)
- Usuario específico
- Rango de fechas
- Dirección IP
- Estado (éxito/fallo)

## 🔧 Estructura del Proyecto

```
mediclab/
├── backend/
│   ├── app/
│   │   ├── routers/          # Endpoints de la API
│   │   ├── models.py         # Modelos de base de datos
│   │   ├── schemas.py        # Esquemas de validación
│   │   ├── security.py       # Autenticación y autorización
│   │   ├── logging_config.py # Configuración de logs
│   │   └── main.py          # Aplicación principal
│   ├── logs/                # Logs de seguridad
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── pages/          # Páginas principales
│   │   ├── services/       # Servicios API
│   │   └── utils/          # Utilidades
│   └── package.json        # Dependencias Node.js
└── README.md
```

## 🛡️ Seguridad

### Medidas Implementadas
- **Autenticación JWT** con tokens de corta duración
- **Hashing de contraseñas** con bcrypt
- **Validación de roles** en cada endpoint
- **Rate limiting** para prevenir ataques de fuerza bruta
- **Protección SSRF** en carga de avatares
- **Logging de seguridad** completo
- **Validación de entrada** estricta

### Logs de Seguridad
Todos los eventos de seguridad se registran automáticamente:
- Intentos de login (exitosos y fallidos)
- Accesos no autorizados
- Creación y modificación de citas
- Accesos administrativos
- Intentos de SSRF

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Jorge Durán** - [JorgeDuranS](https://github.com/JorgeDuranS)

## 🙏 Agradecimientos

- Implementación de seguridad basada en OWASP Top 10
- Diseño de UI/UX moderno y responsivo
- Arquitectura escalable y mantenible