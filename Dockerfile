# Imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Limpiar cualquier cache de Python compilado
RUN find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
RUN find /app -name "*.pyc" -delete 2>/dev/null || true
RUN find /app -name "*.pyo" -delete 2>/dev/null || true

# Crear directorio para la base de datos
RUN mkdir -p /app/instance

# Exponer puerto
EXPOSE 5000

# Variable de entorno para evitar buffering de stdout
ENV PYTHONUNBUFFERED=1

# Evitar que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Copiar entrypoint y otorgar permisos
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponer comando por defecto (gunicorn en producción)
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4"]
