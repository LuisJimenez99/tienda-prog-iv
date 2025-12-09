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
# Definimos explícitamente los dominios permitidos para evitar errores 400 en prod
ALLOWED_HOSTS = ['luchy.pythonanywhere.com', 'localhost', '127.0.0.1']

# ===========================
# 📦 INSTALLED APPS
# ===========================
INSTALLED_APPS = [
    # 1. TUS APPS
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
    'django.contrib.sitemaps',
]

# ===========================
# 🧠 AUTH / MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # AllAuth middleware debe ir aquí, después de session
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
                # Nuestro motor de temas personalizado
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
LANGUAGE_CODE = 'es'
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
if DEBUG:
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_ROOT = '/home/luchy/tienda-prog-iv/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# 🎨 Jazzmin (PANEL ADMIN)
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
    
    # --- MENÚ PERSONALIZADO (AQUÍ ESTÁ EL DASHBOARD) ---
    "custom_links": {
        "carrito": [{
            # Nombre que verás en el menú
            "name": "Tablero de Ventas", 
            
            # El nombre de la URL definida en carrito/urls.py
            "url": "admin_dashboard", 
            
            # Icono visual
            "icon": "fas fa-chart-line",
            
            # Permisos (opcional)
            "permissions": ["carrito.view_pedido"]
        }]
    },
    # ---------------------------------------------------
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
# 👤 ALLAUTH (CONFIGURACIÓN MODERNA)
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

# Configuración limpia y sin warnings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
SOCIALACCOUNT_EMAIL_VERIFICATION = "none" 
SOCIALACCOUNT_AUTO_SIGNUP = True 
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_ADAPTER = 'usuarios.adapter.MyAccountAdapter'
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_SESSION_REMEMBER = True

# Plantillas de email personalizadas
ACCOUNT_EMAIL_TEMPLATES = {
    'email_confirmation': 'account/email/email_confirmation_message',
    'password_reset': 'account/email/password_reset_message',
}