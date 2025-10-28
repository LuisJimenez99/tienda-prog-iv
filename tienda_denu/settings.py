from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+isv)*q2+5^l_(c&qmkhc-#k9gy3sy3$*zwyv%0leamtwe&rp7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
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
        'DIRS': [BASE_DIR / 'templates'], # Correcto
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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# --- CAMBIO AQUÍ: Usamos pathlib también para los archivos estáticos ---
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
PRECIO_CONSULTA = 1500.00


LOGIN_URL = 'account_login'
SITE_ID = 1

LOGIN_REDIRECT_URL = '/'  
LOGOUT_REDIRECT_URL = '/' 
AUTHENTICATION_BACKENDS = [
   
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGIN_METHODS = {"username", "email"}  # permite login con usuario o email
ACCOUNT_SIGNUP_FIELDS = [
    "username*",   # el * indica que es obligatorio
    "email*", 
    "password1*", 
    "password2*",
]

ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # o 'mandatory' si querés verificar
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_SESSION_REMEMBER = True
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"