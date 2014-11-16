"""Django settings for Genevieve project."""
import os

from django.conf import global_settings


# Paths should all be built from this base directory.
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'genevieve',
    'file_process',
    'genomes',
    'variants',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'genevieve.urls'

WSGI_APPLICATION = 'genevieve.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# Path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Directory that will hold data files imported by admin or Genevieve.
DATA_FILE_ROOT = os.path.join(BASE_DIR, 'data_files')

# Max Upload Size
MAX_UPLOAD_SIZE = "400000000"

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
) + global_settings.TEMPLATE_CONTEXT_PROCESSORS

LOGIN_REDIRECT_URL = "file_process/"

# Import settings last. These override anything defined above.
try:
    from settings_local import *
except ImportError:
    pass
