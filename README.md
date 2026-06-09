# 🍗 Asadero Rossy Pollo - Blog CMS con Flask

Una aplicación web completa de Blog/CMS desarrollada con **Flask**, **SQLAlchemy** y **Bootstrap 5**.

## 🚀 Características

✅ **Autenticación de usuarios** - Login y registro  
✅ **Panel de administración** - Crear, editar y publicar posts  
✅ **Sistema de categorías** - Organiza tus artículos
✅ **Búsqueda** - Encuentra posts rápidamente
✅ **Contador de vistas** - Estadísticas de popularidad
✅ **Resultados personales** - Cada usuario puede ver sus propios registros
✅ **Panel de administradores** - Ver ganadores y todos los resultados
✅ **Diseño responsive** - Se adapta a todos los dispositivos
✅ **Base de datos SQLite** - Fácil de configurar  
✅ **Bootstrap 5** - Interfaz moderna y limpia  

## 📁 Estructura del Proyecto

```
asadero_rossypollo/
├── app/
│   ├── __init__.py           # Factory de la aplicación
│   ├── config.py             # Configuración
│   ├── models.py             # Modelos (User, Post, Category, Result)
│   ├── routes.py             # Rutas principales
│   ├── auth_routes.py        # Rutas de autenticación
│   ├── templates/
│   │   ├── base.html         # Template base
│   │   ├── index.html        # Página principal
│   │   ├── login.html        # Iniciar sesión
│   │   ├── register.html     # Registrarse
│   │   ├── post.html         # Ver un post
│   │   ├── results.html      # Ver resultados personales
│   │   ├── dashboard.html    # Panel del usuario
│   │   ├── category.html     # Ver categoría
│   │   ├── profile.html      # Perfil del usuario
│   │   ├── edit_profile.html # Editar perfil
│   │   └── admin/
│   │       ├── create_post.html
│   │       ├── edit_post.html
│   │       └── results.html  # Panel de resultados para admin
│   └── static/
│       ├── css/style.css     # Estilos personalizados
│       └── js/main.js        # JavaScript
├── run.py                    # Punto de entrada
├── requirements.txt          # Dependencias Python
├── Dockerfile                # Configuración para Docker
├── docker-compose.yml        # Orquestación de contenedores
├── .env                      # Variables de entorno (no versionar)
├── .env.example              # Ejemplo de variables de entorno
├── .dockerignore              # Archivos a ignorar en build Docker
├── .gitignore                # Archivos a ignorar en git
├── README.md                 # Este archivo
└── DEVELOPMENT.md            # Guía de desarrollo
```

## 🛠️ Instalación

### Opción 1: Instalación Local

#### 1. Clonar o descargar el proyecto
```bash
cd asadero_rossypollo
```

#### 2. Crear entorno virtual
```bash
python -m venv venv
```

#### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 5. Ejecutar la aplicación
```bash
python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

#### 6. Ejecutar tests
```bash
pytest
```

Si deseas ejecutar una prueba específica:
```bash
pytest tests/test_app.py
```

---

### Opción 2: Instalación con Docker

#### Requisitos previos
- Docker instalado
- Docker Compose instalado

#### 1. Copiar archivo de entorno
```bash
cp .env.example .env
```

*En Windows PowerShell:*
```powershell
Copy-Item .env.example .env
```

#### 2. Personalizar `.env`
Asegúrate de ajustar:
- `SECRET_KEY`
- `DATABASE_URL`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`

#### 3. Levantar los contenedores
```bash
docker-compose up -d --build
```

#### 4. Verificar que el contenedor esté listo
```bash
docker-compose logs -f app
```

#### 5. Acceder a la aplicación
```
http://localhost:5000
```

#### 6. Migraciones y mantenimiento
El `entrypoint.sh` ejecuta `flask db upgrade` automáticamente cuando `FLASK_ENV=production`.
Si necesitas forzar una migración manualmente:
```bash
docker-compose exec app flask db upgrade
```

Para resetear el volumen de la base de datos y volver a iniciar desde cero:
```bash
docker-compose down -v
```

#### Comandos útiles
```bash
# Ver logs de la app
docker-compose logs -f app

# Ver logs de MySQL
docker-compose logs -f db

# Detener la aplicación
docker-compose down

# Reconstruir imágenes
docker-compose build --no-cache
```

---

## 👤 Crear Usuario Administrador

### Localmente

Abre Python en la terminal:

```bash
python
```

Luego ejecuta:

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Crear usuario admin
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('password123')
    db.session.add(admin)
    db.session.commit()
    print("¡Usuario administrador creado!")
```

### Con Docker

```bash
docker-compose exec app python -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('password123')
    db.session.add(admin)
    db.session.commit()
    print('¡Usuario administrador creado!')
"
```

## 📊 Modelos de Base de Datos

### User (Usuario)
- `id` - ID único
- `username` - Nombre de usuario único
- `email` - Correo electrónico único
- `password_hash` - Contraseña encriptada
- `is_admin` - ¿Es administrador?
- `created_at` - Fecha de creación
- `posts` - Relación con posts del usuario

### Post (Artículo)
- `id` - ID único
- `title` - Título del post
- `slug` - URL amigable (único)
- `content` - Contenido del post
- `excerpt` - Resumen corto
- `user_id` - Autor del post (FK)
- `category_id` - Categoría (FK)
- `created_at` - Fecha de creación
- `updated_at` - Última actualización
- `is_published` - ¿Está publicado?
- `views` - Contador de vistas

### Category (Categoría)
- `id` - ID único
- `name` - Nombre de la categoría
- `slug` - URL amigable
- `description` - Descripción
- `created_at` - Fecha de creación

## 🗺️ Rutas Principales

### Públicas
- `/` - Página principal (lista de posts)
- `/post/<slug>` - Ver post completo
- `/category/<slug>` - Ver posts por categoría
- `/auth/login` - Iniciar sesión
- `/auth/register` - Registrarse

### Privadas (requieren login)
- `/dashboard` - Panel del usuario
- `/results` - Ver resultados personales
- `/auth/profile` - Ver perfil
- `/auth/edit-profile` - Editar perfil
- `/auth/logout` - Cerrar sesión

### Administrador
- `/admin` - Panel principal del administrador
- `/admin/matches` - Gestionar partidos
- `/admin/match/new` - Crear partido
- `/admin/match/<id>/edit` - Editar partido y resultados
- `/admin/prizes` - Gestionar premios
- `/admin/prize/new` - Crear premio
- `/admin/prize/<id>/edit` - Editar premio
- `/admin/results` - Ver ganadores y todos los resultados
- `/admin/post/new` - Crear nuevo post
- `/admin/post/<id>/edit` - Editar post

### API
- `/api/search?q=<query>` - Buscar posts

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y personaliza según sea necesario:

```bash
cp .env.example .env
```

**Variables principales:**
- `FLASK_ENV` - Entorno (`development` o `production`)
- `SECRET_KEY` - Clave secreta para sesiones (⚠️ **cambiar en producción**)
- `DEBUG` - Activar modo debug
- `PORT` - Puerto de la aplicación (default: 5000)
- `DATABASE_URL` - URL de la base de datos (default: SQLite local)

**Nota:** El archivo `.env` NO se versionará (está en `.gitignore`)

### Configuración avanzada

Edita `app/config.py` para cambiar parámetros adicionales como:
- `SQLALCHEMY_TRACK_MODIFICATIONS` - Rastreo de modificaciones ORM
- Configuración de email (SMTP)
- Configuración de almacenamiento en la nube (AWS S3)

## 📦 Dependencias

- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM para base de datos
- **Flask-Login** - Manejo de sesiones
- **Werkzeug** - Utilidades de seguridad
- **Python 3.11+** - Intérprete de Python

## 🚀 Próximas Mejoras

- [ ] Upload de imágenes
- [ ] Sistema de comentarios
- [ ] Tags para posts
- [ ] Exportar a PDF
- [ ] Email de confirmación
- [ ] API REST completa
- [ ] Tests unitarios

## 📝 Licencia

Este proyecto es de uso libre.

## 👨‍💻 Desarrollo

Para contribuir o reportar bugs, crea un issue en el repositorio.

---

**¡Feliz blogging! 🍗**
