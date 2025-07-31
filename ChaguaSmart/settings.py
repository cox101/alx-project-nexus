INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_yasg',
    'users',
    'polls',
]
INSTALLED_APPS = [
    #...
    'rest_framework',
    'rest_framework_simplejwt',
    'users',
]


AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

import environ
import os

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("chaguasmart_db"),
        'USER': env("ChaguaSmart_db_user"),
        'PASSWORD': env("hpVI6FKvleBgubB21jG0k7HKfjYbHrci"),
        'HOST': env("Render"),
        'PORT': env("5432"),
    }
}

import dj_database_url
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Add allowed host
ALLOWED_HOSTS = ['chaguasmart.onrender.com']

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

import dj_database_url
import os

DEBUG = False

ALLOWED_HOSTS = ['chaguasmart.onrender.com', 'localhost', '127.0.0.1']

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise settings
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-key")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

INSTALLED_APPS = [
    # Add your Django apps here
    'rest_framework',
    'drf_yasg',
    'polls',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 🧊 WhiteNoise for static
    ...
]

DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

import dj_database_url
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get("DATABASE_URL"))
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChaguaSmart.settings')
