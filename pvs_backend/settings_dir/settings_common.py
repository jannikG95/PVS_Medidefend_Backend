"""
Django common settings for aidjangoplatform project.
"""
import os
from pathlib import Path

# Core settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-insecure-ku428k6gv^%lv(94!bcazq&@x)@j7jeu9kxi@71@xk#@)$8q9y'
LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files and media settings
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'autoresponder',
    'drf_yasg',
]

# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]


# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Templates settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Application and routing
WSGI_APPLICATION = 'pvs_backend.wsgi.application'
ROOT_URLCONF = 'pvs_backend.urls'

POSTGRES_USER = os.environ.get('POSTGRES_USER', 'medidefenduser')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'mypassword') # Set your password here
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'medidefend')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,  # Name Ihrer PostgreSQL-Datenbank
        'USER': POSTGRES_USER,         # Ihr PostgreSQL-Benutzername
        'PASSWORD': POSTGRES_PASSWORD, # Ihr PostgreSQL-Passwort
        'HOST': POSTGRES_HOST,         # Ihr Datenbank-Host (oder '127.0.0.1')
        'PORT': '5432',              # Der Port Ihrer PostgreSQL-Instanz
    }
}

# Swagger settings
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'DEFAULT_INFO': 'pvs_backend.urls.api_info'
}

PINECONE_API_KEY = "49434cc5-3257-4091-bceb-958989eab291"

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
