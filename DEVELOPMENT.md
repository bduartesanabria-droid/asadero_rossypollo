# 📚 Guía de Desarrollo - Asadero Rossy Pollo

## 🐳 Ejecutar con Docker

### Requisitos previos
- Docker instalado
- Docker Compose instalado

### Configuración inicial

1. **Copiar archivo de entorno:**
```bash
cp .env.example .env
```

2. **Editar `.env` con tus valores** (especialmente `SECRET_KEY`)

### Ejecutar la aplicación

**Opción 1: Con docker-compose (recomendado)**
```bash
# Iniciar contenedor en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f app

# Detener el contenedor
docker-compose down
```

**Opción 2: Sin docker-compose**
```bash
# Construir imagen
docker build -t asadero_rossypollo .

# Ejecutar contenedor
docker run -p 5000:5000 -v $(pwd):/app --env-file .env asadero_rossypollo
```

### Acceder a la aplicación

```
http://localhost:5000
```

### Comandos útiles

```bash
# Ver contenedor corriendo
docker ps

# Ejecutar comando dentro del contenedor
docker-compose exec app python -c "from app import create_app, db; app = create_app(); print('OK')"

# Reconstruir imagen
docker-compose build --no-cache

# Eliminar todo (contenedores, imágenes, volúmenes)
docker-compose down -v
```

---

## 🎯 Cómo Agregar Funcionalidades

### Agregar un nuevo modelo

1. **Edita `app/models.py`:**
```python
class MiModelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    # ... más campos
    
    def __repr__(self):
        return f'<MiModelo {self.nombre}>'
```

2. **Crea una migración** (en futuro con Alembic)

3. **Reinicia la app** - Las tablas se crean automáticamente

### Agregar una nueva ruta

1. **Opción A: En `app/routes.py`** (rutas públicas)
```python
@main_bp.route('/mi-ruta')
def mi_funcion():
    return render_template('mi_template.html')
```

2. **Opción B: En `app/auth_routes.py`** (rutas con autenticación)
```python
@auth_bp.route('/mi-ruta')
@login_required
def mi_funcion():
    return render_template('mi_template.html')
```

### Crear un nuevo template

1. **Crea el archivo en `app/templates/`**
2. **Extiende `base.html`:**
```html
{% extends "base.html" %}

{% block title %}Mi Página{% endblock %}

{% block content %}
    <h1>¡Hola!</h1>
{% endblock %}
```

## 🔑 Variables útiles en templates

```html
<!-- Usuario actual -->
{{ current_user.username }}
{{ current_user.email }}
{{ current_user.is_admin }}
{{ current_user.is_authenticated }}

<!-- URLs -->
{{ url_for('main.index') }}
{{ url_for('auth.login') }}

<!-- Flash messages -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        {{ message }}
    {% endfor %}
{% endwith %}
```

## 💾 Trabajar con la Base de Datos

### Acceder a la BD desde consola Python

```python
from app import create_app, db
from app.models import User, Post, Category

app = create_app()
with app.app_context():
    # Crear
    post = Post(title="Mi post", slug="mi-post", content="...")
    db.session.add(post)
    db.session.commit()
    
    # Leer
    posts = Post.query.all()
    post = Post.query.filter_by(id=1).first()
    
    # Actualizar
    post.title = "Nuevo título"
    db.session.commit()
    
    # Eliminar
    db.session.delete(post)
    db.session.commit()
```

### Resetear la base de datos
```python
from app import create_app, db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
```

## 🎨 Personalizar estilos

**Archivo:** `app/static/css/style.css`

Variables CSS disponibles:
```css
:root {
    --primary-color: #d4714d;      /* Naranja principal */
    --secondary-color: #f4a74f;    /* Naranja secundario */
}
```

## 🧪 Comando de prueba rápida

```bash
# Ejecutar app en modo debug
python run.py

# Ejecutar consola Python con contexto de app
python -c "from app import create_app, db; app = create_app(); print('App lista')"
```

## 📝 Casos de uso comunes

### 1. Crear un post programáticamente
```python
from app import create_app, db
from app.models import Post, User

app = create_app()
with app.app_context():
    user = User.query.first()
    post = Post(
        title="Mi primer post",
        slug="mi-primer-post",
        content="Contenido del post...",
        user_id=user.id,
        is_published=True
    )
    db.session.add(post)
    db.session.commit()
```

### 2. Crear una categoría
```python
from app.models import Category

category = Category(
    name="Recetas",
    slug="recetas",
    description="Posts sobre recetas"
)
db.session.add(category)
db.session.commit()
```

### 3. Listar posts de un usuario
```python
user_posts = Post.query.filter_by(user_id=1).all()
for post in user_posts:
    print(f"{post.title} ({post.views} vistas)")
```

## 🐛 Debugging

### Habilitar logs en Flask
```python
# En run.py
app.config['DEBUG'] = True
app.logger.setLevel('DEBUG')
```

### Ver queries SQL
```python
import logging
from flask import Flask

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 📦 Añadir nuevas dependencias

```bash
pip install nombre_paquete
pip freeze > requirements.txt
```

## 🚀 Desplegar en producción

1. **Cambiar configuración:**
   - Editar `app/config.py` a `ProductionConfig`
   - Cambiar `SECRET_KEY` a una clave segura
   - Usar base de datos PostgreSQL o similar

2. **Usar servidor WSGI:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **Configurar variables de entorno:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=tu-clave-secreta-aqui
   ```

## 📞 Soporte

Para dudas o problemas, revisar:
- [Documentación Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

---

**Happy coding! 🚀**
