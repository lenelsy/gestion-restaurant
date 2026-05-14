import os
import pymysql
from pathlib import Path

# 1. Configuration pour MySQL (Indispensable pour éviter l'erreur mysqlclient)
pymysql.install_as_MySQLdb()

# 2. Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Sécurité
SECRET_KEY = 'django-insecure-votre-cle-de-test-uniquement'
DEBUG = True
ALLOWED_HOSTS = []

# 4. Définition des applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Restaurant',  # Ton application
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resto_groupe1.urls'

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

WSGI_APPLICATION = 'resto_groupe1.wsgi.application'

# 5. Connexion à ta base MySQL (Vérifie bien ton mot de passe Nelson1234)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Restaurant',
        'USER': 'root',
        'PASSWORD': 'myroot2sql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 6. Internationalisation (En français !)
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 7. Fichiers statiques
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/restaurant/catalogue/'
LOGIN_URL = '/restaurant/login/'