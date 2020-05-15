"""
Django settings for otrtools project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', default='pvw@df5r2*xi#b(boz)acdo6a#&qcmk@=kzeszdw5q51710mrj')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', default=False)

DOMAIN = os.environ.get("DOMAIN")
if DOMAIN:
    ALLOWED_HOSTS = [DOMAIN]
else:
    ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'django_celery_results',
    'downloader',
    'searcher',
    'crispy_forms',
    'django_icons',
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

ROOT_URLCONF = 'otrtools.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['searcher/templates'],
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

WSGI_APPLICATION = 'otrtools.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

import djcelery
djcelery.setup_loader()

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(BASE_DIR, 'static'))

STATIC_URL = '/static/'

WWW_DIR = os.path.join(BASE_DIR, 'www/')

# Searching
MIRROR_PRIORITIES = [
    'datenkeller.net',
    'simple-otr-mirror.de',
]

FORMAT_PRIORITIES = [
    'HD',
    'HQ',
    'AVI',
    'MP4',
]

# Workers / Message Queue
#CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'amqp://my_user:YiMkX-8xwew_Uqp9m9_GGTkCMHMV7p3@localhost:5672/vhost'
CELERY_BROKER_URL = 'amqp://my_user:YiMkX-8xwew_Uqp9m9_GGTkCMHMV7p3@localhost:5672/vhost'
CELERY_BROKER_URL  = 'amqp://guest:guest@localhost:5672//'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Downloading
DATENKELLER_QUEUE_REFRESH = 20
DATENKELLER_INVALID_STATE_WAIT = 60
DATENKELLER_INVALID_STATE_RETRY = 10
DATENKELLER_INVALID_STATE_REQUEUE = 20

DATENKELLER_USER = os.environ.get('DATENKELLER_USER')
DATENKELLER_PASSWORD = os.environ.get('DATENKELLER_PASSWORD')

# Decryption
OTRKEY_CACHE = os.path.join(os.environ['HOME'], ".otrkey_cache")

OTR_USERNAME = os.environ.get('OTR_USERNAME')
OTR_PASSWORD = os.environ.get('OTR_PASSWORD')

OTRKEY_CACHE = os.environ.get('OTRKEY_CACHE')

DEST_DIR = os.environ.get("DEST_DIR")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "amqp://guest:guest@localhost:5672//")

FLOWER_HOST = os.environ.get("FLOWER_HOST", "localhost:5555")

# Cutting
CUT_ENCODER = "ffmpeg"
CUT_KEYFRAME_LISTER = "keyframe-list"
CUT_EXT = "avi"  # might work better with mkv
CUT_DIR = os.environ.get("CUT_DIR", os.path.join(WWW_DIR, 'temp'))

# Saving video files
DEST_DIR = os.environ.get('DEST_DIR', os.path.join(WWW_DIR, 'videos'))
DEST_EXT = "avi"
SERIES_NAME_FORMAT = '{series} s{season:02}e{episode:02} - {title}.{extension}'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(WWW_DIR, 'www/'))
DEST_CHOWN_USER, DEST_CHOWN_GROUP = os.environ.get('DEST_CHOWN_USER'), os.environ.get('DEST_CHOWN_GROUP')
DEST_CHMOD = os.environ.get('DEST_CHMOD')

# Logging
LOG_DIR = os.path.join(WWW_DIR, 'logs/')

# Production settings (keep at the end)
PRODUCTION_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "production.py")
if os.path.isfile(PRODUCTION_SETTINGS_PATH):
    print("Loading production settings..")
    from .production import *
