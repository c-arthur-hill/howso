"""
Django settings for lc1 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def bool_env(val):
    """Replaces string based environment values with Python booleans"""
    return True if os.environ.get(val, False) == "True" else False

SECRET_KEY = os.environ.get("SECRET_KEY")
#AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCES_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_CALLING_FORMAT = os.environ.get("AWS_CALLING_FORMAT")
#SITE_URL = 'http://sciguides.com/'
STATICFILES_STORAGE = os.environ.get("S3_STORAGE")
DEFAULT_FILE_STORAGE = os.environ.get("S3_STORAGE")
DEBUG = bool_env("DEBUG")
STATIC_URL = 'https://s3-us-west-2.amazonaws.com/creatorguides/'
#LOGIN_URL = "/users/login/"
#LOGIN_REDIRECT_URL = "/guides/"
#AUTH_USER_MODEL = 'auth.user'

# Quick-start development settings - unsuitable for productionN
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/



TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',
    'core',
    'stripe_transactions',
    'addresses',
    'events',
    'cities_light',
    'phonenumber_field',
    'listings',
    'users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lc1.urls'

WSGI_APPLICATION = 'lc1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
     'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.  '
          'NAME': DB_NAME,
          'USER': DB_USER,
          'PASSWORD': DB_PASSWORD,
          'HOST': DB_HOST,
          'PORT': DB_PORT,
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
