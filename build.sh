#!/usr/bin/env bash

# Salir si un comando falla
set -o errexit

# 1. Instalar todos los paquetes de Python
pip install -r requirements.txt

# 2. Recolectar todos los archivos estáticos (CSS, JS) en la carpeta /staticfiles/
python manage.py collectstatic --no-input

# 3. Correr las migraciones de la base de datos
python manage.py migrate