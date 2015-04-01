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
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCES_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_CALLING_FORMAT = os.environ.get("AWS_CALLING_FORMAT")
SITE_URL = 'howso.co'
STATICFILES_STORAGE = os.environ.get("S3_STORAGE")
DEFAULT_FILE_STORAGE = os.environ.get("S3_STORAGE")
DEBUG = bool_env("DEBUG")
STATIC_URL = 'http://s3-us-west-2.amazonaws.com/creatorguides/'
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
LOGIN_URL = "/user/login/"
AUTH_USER_MODEL = 'custom_users.CustomUser'
# Quick-start development settings - unsuitable for productionN
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
SITE_ID = 1
DOMAIN = "howso.co"

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['projects.howso.co', 'www.projects.howso.co', 'howso.co', 'www.howso.co']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'storages',
    'haystack',
    'nodes',
    'custom_users',
    'subdomains',
)

MIDDLEWARE_CLASSES = (
    'subdomains.middleware.SubdomainURLRoutingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lg1.urls'

SUBDOMAIN_URLCONFS = {
    'projects':'nodes.urls',
    }


WSGI_APPLICATION = 'lg1.wsgi.application'


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
        'URL': 'http://127.0.0.1:8983/solr'
    },
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

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.static",
    "lg1.context_processors.get_current_path",
    "lg1.context_processors.request_is_ajax", 
)
