from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
# ===========================
# 🔑 SECRET KEY & DEBUG
# ===========================
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ===========================
# 🌍 ALLOWED HOSTS
# ===========================
ALLOWED_HOSTS = []

# Leemos el dominio de producción de PythonAnywhere (desde el .env)
PA_DOMAIN = os.getenv("PYTHONANYWHERE_DOMAIN")
if PA_DOMAIN:
    ALLOWED_HOSTS.append(PA_DOMAIN)

# Leemos el dominio de Render (si lo volvemos a usar)
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ¡LÍNEA CLAVE! Si estamos en modo DEBUG (local),
# añadimos los hosts de desarrollo automáticamente.
if DEBUG:
    ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS.append('localhost')

# ===========================
# 📦 INSTALLED APPS (¡ORDEN CORREGIDO!)
# ===========================
INSTALLED_APPS = [
    # 1. TUS APPS (Tienen que cargarse primero)
    'core',
    'productos',
    'recetas',
    'turnos',
    'paginas',
    'configuracion',
    'usuarios',
    'carrito',
    'envios',

    # 2. Paquetes de Terceros
    'jazzmin',
    'colorfield',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'imagekit',

    # 3. Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

# ===========================
# 🧠 AUTH / MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware', # <-- Mover aquí
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

# ===========================
# 🗄️ DATABASE CONFIG
# ===========================
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST") 

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
elif DB_HOST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': DB_HOST,
            'PORT': os.getenv("DB_PORT", '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4'
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===========================
# 🔒 PASSWORDS
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# 🌐 LANGUAGE / TIME
# ===========================
LANGUAGE_CODE = 'en-ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# 📁 STATIC & MEDIA
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
# Ruta de media actualizada para desarrollo local
if DEBUG:
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_ROOT = '/home/luchy/tienda-prog-iv/media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# 🎨 Jazzmin
# ===========================
JAZZMIN_SETTINGS = {
    "site_title": "NutriTienda Admin",
    "site_header": "NutriTienda",
    "welcome_sign": "Bienvenida al Panel de NutriTienda",
    "copyright": "NutriTienda",
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index"},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
        {"model": "auth.User"},
    ],
    "hide_models": ["auth.group"],
}

# ===========================
# ✉️ EMAIL SETTINGS
# ===========================
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@mitienda.com')

# ===========================
# 💳 MERCADO PAGO + GOOGLE
# ===========================
MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
PRECIO_CONSULTA = Decimal(os.getenv('PRECIO_CONSULTA', '1500.00'))
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')

# ===========================
# 👤 ALLAUTH (BLOQUE ACTUALIZADO Y CORREGIDO)
# ===========================
SITE_ID = 1
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

# --- CONFIGURACIÓN MODERNA DE ALLAUTH ---

# 1. El email es el método de login
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# 2. El email es obligatorio y debe ser único
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# 3. Verificación de Email
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# 4. Confía en Google (no pide verificar email si vienes de Google)
SOCIALACCOUNT_EMAIL_VERIFICATION = "none" 
SOCIALACCOUNT_AUTO_SIGNUP = True 

# 5. Campos de Registro (solo pide email y passwords)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# 6. Adaptador para copiar email a username
ACCOUNT_ADAPTER = 'usuarios.adapter.MyAccountAdapter'

# 7. Opcional: seguridad
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_SESSION_REMEMBER = True

# 8. Forzar el uso de nuestras plantillas de email personalizadas
ACCOUNT_EMAIL_TEMPLATES = {
    'email_confirmation': 'account/email/email_confirmation_message',
    'password_reset': 'account/email/password_reset_message',
}