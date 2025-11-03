from pathlib import Path
import os
import dj_database_url # <-- Añadido
from dotenv import load_dotenv
from decimal import Decimal
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN DE PRODUCCIÓN ---
# 1. SECRET_KEY
# Lee la SECRET_KEY desde las variables de entorno de Render.
# Debes añadir tu clave al .env para que funcione localmente.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-+isv)*q2+5^l_(c&qmkhc-#k9gy3sy3$*zwyv%0leamtwe&rp7') # El default es solo para que no falle

# 2. DEBUG
# Render pondrá esto en 'False' automáticamente.
# 'False' es más seguro.
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 3. ALLOWED_HOSTS
# Render necesita que su dominio esté aquí.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    # Para desarrollo, permitimos localhost
    ALLOWED_HOSTS.append('127.0.0.1')


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # <-- Añadido (para estáticos)
    'django.contrib.staticfiles',
    # Mis Apps
    'core',
    'productos',
    'recetas',
    'turnos',
    'paginas',
    'configuracion',
    'usuarios',
    'django.contrib.sites', 
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'carrito',
    'envios',
    'colorfield',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <-- Añadido (para estáticos)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tienda_denu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'configuracion.context_processors.apariencia_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'tienda_denu.wsgi.application'


# --- Base de Datos (¡MODIFICADO!) ---
# Render nos da una URL de PostgreSQL. dj-database-url la lee.
# Ya no usaremos db.sqlite3 en producción.
DATABASES = {
    'default': dj_database_url.config(
        # Fallback a tu sqlite3 si DATABASE_URL no está definida (para desarrollo)
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600 # Mantiene las conexiones activas
    )
}


# Password validation
# ... (sin cambios)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# ... (sin cambios)
LANGUAGE_CODE = 'en-ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript) (¡MODIFICADO!) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
# 1. Dónde 'collectstatic' pondrá todos los archivos
STATIC_ROOT = BASE_DIR / 'staticfiles'
# 2. El motor de almacenamiento de WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Media files (Fotos de productos) (¡MODIFICADO!) ---
MEDIA_URL = '/media/'
# Render usará un "Disco Persistente" en esta ruta.
# Para desarrollo, usará tu carpeta 'media' local.
MEDIA_ROOT = os.getenv('RENDER_DISK_MOUNT_PATH', BASE_DIR / 'media')


# Default primary key field type
# ... (sin cambios)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Jazzmin Settings
# ... (sin cambios)
JAZZMIN_SETTINGS = {
    "site_title": "NutriTienda Admin",
    "site_header": "NutriTienda",
    "welcome_sign": "Bienvenida al Panel de NutriTienda",
    "copyright": "NutriTienda Ltd.",
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
        {"model": "auth.User"},
    ],
    "icons": {
        "auth.user": "fas fa-user",
        "productos.Producto": "fas fa-shopping-basket",
        "recetas.Receta": "fas fa-utensils",
        "turnos.TurnoReservado": "fas fa-calendar-check",
        "turnos.ReglaDisponibilidad": "fas fa-calendar-alt",
        "paginas.Pagina": "fas fa-file-alt",
        "configuracion.DatosPago": "fas fa-credit-card",
    },
    "hide_models": ["auth.group"],
}

# --- Email Settings (¡MODIFICADO!) ---
# Usamos el backend de Consola si DEBUG es True
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # EN PRODUCCIÓN (Render): Debes configurar esto
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST') # ej: 'smtp.sendgrid.net'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') # ej: 'apikey'
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # La clave de tu proveedor
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@mitienda.com')

# --- Claves de APIs (Leídas desde variables de entorno) ---
MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
PRECIO_CONSULTA = Decimal(os.getenv('PRECIO_CONSULTA', '1500.00'))
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')


# --- Configuración de AllAuth ---
LOGIN_URL = 'account_login'
SITE_ID = 1

LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/' 
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
# Configuración específica de Google
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_SECRET_KEY,
            'key': ''
        }
    }
}
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_SESSION_REMEMBER = True
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"