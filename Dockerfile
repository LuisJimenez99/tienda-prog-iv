# 1. Base Image: Usa la versión de Python 3.13 (la que usas en tu venv)
FROM python:3.13-slim-bookworm

# 2. Variables de Entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Instalar dependencias del sistema
# (libpq-dev es para conectarse a PostgreSQL, el resto es para Pillow)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       libjpeg-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Crear un usuario no-root para más seguridad
RUN addgroup --system app && adduser --system --group app

# 5. Crear el directorio de trabajo
WORKDIR /app

# 6. Instalar dependencias de Python (en una capa separada para caché)
# Copia solo el archivo de requisitos primero
COPY requirements.txt .
# Instala los paquetes
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiar el resto del código del proyecto
COPY . .

# 8. Correr collectstatic
# Esto agrupa todos tus archivos (CSS, JS, etc.) en la carpeta /staticfiles/
# WhiteNoise (que ya instalamos) los usará desde allí.
RUN python manage.py collectstatic --no-input

# 9. Cambiar al usuario no-root que creamos
USER app

# 10. Comando para correr la aplicación
# Gunicorn es el servidor de producción (reemplaza a runserver)
# Se enlazará al puerto ($PORT) que Google Cloud Run le asigne automáticamente.
CMD ["gunicorn", "tienda_denu.wsgi", "--bind", "0.0.0.0:$PORT", "--workers", "4"]