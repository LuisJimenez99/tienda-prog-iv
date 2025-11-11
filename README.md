Este proyecto es una plataforma web integral de e-commerce y gestión de servicios, desarrollada con Django. Está diseñada para un profesional de la nutrición, permitiendo la venta de productos físicos (viandas) y la gestión de servicios (reserva de turnos y venta de contenido digital).

El pilar del proyecto es un panel de administración (Django Admin + Jazzmin) profundamente personalizado, que permite al propietario modificar el contenido, la lógica de negocio y la apariencia visual completa del sitio (colores, fuentes y estilos de componentes) sin escribir una sola línea de código.

**Sitio en Producción:** [https://luchy.pythonanywhere.com](https://luchy.pythonanywhere.com)

---

## 🚀 Tecnologías Clave

* **Backend:** Python 3.10, Django 5.x
* **Servidor (Producción):** Gunicorn (en PythonAnywhere)
* **Base de Datos (Producción):** MySQL (provista por PythonAnywhere)
* **Base de Datos (Local):** SQLite 3
* **Frontend:** JavaScript (ES6+ modularizado), CSS3 (con Variables CSS)
* **Admin:** `django-jazzmin`
* **Autenticación:** `django-allauth` (Email, Contraseña y Google OAuth2)
* **Pagos:** SDK de `mercadopago` (Checkout Pro + Webhooks)
* **Emails HTML:** `pynliner` (para aplicar CSS inline)
* **Gestión de Secretos:** `python-dotenv`

---

## 🛠️ Cómo Iniciar el Proyecto (Instalación Local)

Sigue estos pasos para correr el proyecto en tu computadora local (ej. VS Code) para desarrollo y pruebas.

### 1. Prerrequisitos

* Python 3.10 o superior
* Git

### 2. Clonar el Repositorio

```bash
git clone [https://github.com/LuisJimenez99/tienda-prog-iv.git](https://github.com/LuisJimenez99/tienda-prog-iv.git)
cd tienda-prog-iv

3. Configurar el Entorno Virtual (venv)


# Crear un nuevo entorno virtual
python -m venv venv

# Activar el venv
# En Windows (Powershell):
.\venv\Scripts\activate
# En Mac/Linux:
# source venv/bin/activate


4. Instalar Dependencias
Asegúrate de que tu venv esté activado.


pip install -r requirements.txt
