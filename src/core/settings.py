"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
<<<<<<< HEAD
import sys
=======
from decouple import config
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676

import dj_database_url
from decouple import config

try:
    from psycopg2cffi import compat

    DISABLE_SERVER_SIDE_CURSORS = True
    compat.register()
except ImportError:
    pass

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
<<<<<<< HEAD
SECRET_KEY = config('SECRET_KEY', 'upmxof7pp2h78tbtp9e3=q5#-%_7#rf@1!f#1r7&o#wieketxr')
=======
SECRET_KEY = config(
    'SECRET_KEY', 'upmxof7pp2h78tbtp9e3=q5#-%_7#rf@1!f#1r7&o#wieketxr'
)
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', True, cast=bool)

<<<<<<< HEAD
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

=======
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676
SECURE_SSL_REDIRECT = config('SSL', False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', '*')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'iot',
    'aquaponic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ATOMIC_REQUESTS': True,
    }
}

DATABASES['default'].update(dj_database_url.config())

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config('TIMEZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    )
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/py-aquaponic-cache/',
    }
}

if config('MEMCACHED_URL', False):
    CACHES['default'] = {
        'backend': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config('REDIS_URL', cast=lambda v: [v.strip() for v in v.split(',')])
    }

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

if config('REDIS_URL', False):
<<<<<<< HEAD
    CHANNEL_LAYERS['default']['BACKEND'] = 'channels_redis.core.RedisChannelLayer'
    CHANNEL_LAYERS['default']['CONFIG'] = {
        'hosts': config('REDIS_URL', cast=lambda v: [v.strip() for v in v.split(',')])
=======
    CHANNEL_LAYERS['default']['BACKEND'] = 'asgi_redis.RedisChannelLayer'
    CHANNEL_LAYERS['default']['CONFIG'] = {
        'hosts': [config('REDIS_URL')]
>>>>>>> 6101720d5b73be9a3257384bf71dee7668701676
    }
elif not DEBUG:
    CHANNEL_LAYERS['default']['BACKEND'] = 'asgi_ipc.IPCChannelLayer'
