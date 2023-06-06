"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import json, logging, os
from typing import Any, Dict, Tuple, Union

import hjson
from django.core.management.utils import get_random_secret_key


logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv('ROOT_LOG_LEVEL', 'INFO'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."),
)


def apply_env_overrides(env: Dict[str, Any], environ: os._Environ) -> Dict[str, Any]:
    """
    Replaces values for any keys in env found in the environment
    """
    env_copy = env.copy()
    for key in env_copy.keys():
        if key in environ:
            os_value = environ[key]
            try:
                os_value = json.loads(os_value)
                logger.debug('Value was valid JSON; replaced value with parsed data.')
            except json.JSONDecodeError:
                logger.debug('Value was not JSON; kept the value as is.')
            env_copy[key] = os_value
            logger.debug(f'ENV value for "{key}" overridden')
            logger.debug(f'key: {key}; os_value: {os_value}')
    return env_copy


env_json: Union[str, None] = os.getenv('ENV_JSON')
if env_json:
    # optionally load settings from an environment variable
    ENV = hjson.loads(env_json)
else:
    # else try loading settings from the json config file
    try:
        with open(os.getenv("ENV_FILE", "/secrets/env.hjson")) as f:
            ENV = hjson.load(f)
        ENV = apply_env_overrides(ENV, os.environ)
    except FileNotFoundError as fnfe:
        logger.warn(
            "Default config file or one defined in environment variable ENV_FILE not found. " +
            "This is normal for the build; it should be defined when running the server."
        )
        # Set ENV so collectstatic will still run in the build
        ENV = os.environ

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
HELP_URL = ENV.get("HELP_URL", "https://its.umich.edu/academics-research/teaching-learning/my-learning-analytics")

URL_VIEW_RESOURCES_ACCESSED = ENV.get("URL_VIEW_RESOURCES_ACCESSED", "https://its.umich.edu/academics-research/teaching-learning/my-learning-analytics/support/resources-accessed")
URL_VIEW_ASSIGNMENT_PLANNING_V1 = ENV.get("URL_VIEW_ASSIGNMENT_PLANNING_V1", "https://its.umich.edu/academics-research/teaching-learning/my-learning-analytics/support/assignment-planning")
URL_VIEW_ASSIGNMENT_PLANNING = ENV.get("URL_VIEW_ASSIGNMENT_PLANNING", "https://its.umich.edu/academics-research/teaching-learning/my-learning-analytics/support/assignment-planning-goals")
URL_VIEW_GRADE_DISTRIBUTION = ENV.get("URL_VIEW_GRADE_DISTRIBUTION", "https://its.umich.edu/academics-research/teaching-learning/my-learning-analytics/support/grade-distribution")

# Google Analytics ID
GA_ID = ENV.get('GA_ID', '')

# Resource values from env
RESOURCE_VALUES = ENV.get("RESOURCE_VALUES", {"files": {"types": ["canvas"], "icon": "fas fa-file fa-lg"}})

# Convience map to be able to get from types
RESOURCE_VALUES_MAP = {
    resource_type : resource_value
    for resource_value in RESOURCE_VALUES
    for resource_type in RESOURCE_VALUES.get(resource_value).get('types')
}

# This is required by flatpages flow. For Example Copyright information in the footer populated from flatpages
SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.get('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.get('DJANGO_DEBUG', False)

ALLOWED_HOSTS = ENV.get("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])

WATCHMAN_TOKEN = ENV.get('DJANGO_WATCHMAN_TOKEN', None)

WATCHMAN_TOKEN_NAME = ENV.get('DJANGO_WATCHMAN_TOKEN_NAME', 'token')

# Only report on the default database
WATCHMAN_DATABASES = ('default',)

# courses_enabled api
COURSES_ENABLED = ENV.get('COURSES_ENABLED', False)
# Fall back to the old config name
ENABLE_LTI = ENV.get('ENABLE_LTI', ENV.get('STUDENT_DASHBOARD_LTI', False))

# Defaults for DEBUGPY
DEBUGPY_ENABLE = ENV.get("DEBUGPY_ENABLE", False)
DEBUGPY_REMOTE_ADDRESS = ENV.get("DEBUGPY_REMOTE_ADDRESS", "0.0.0.0")
DEBUGPY_REMOTE_PORT = ENV.get("DEBUGPY_REMOTE_PORT", 3000)
DEBUGPY_WAIT_FOR_ATTACH = ENV.get("DEBUGPY_WAIT_FOR_ATTACH", False)

LOGIN_REDIRECT_URL = ENV.get('DJANGO_LOGIN_REDIRECT_URL', '/')
LOGOUT_REDIRECT_URL = ENV.get('DJANGO_LOGOUT_REDIRECT_URL', '/')

# Application definition

INSTALLED_APPS = [
    'dashboard',
    'django_su',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'graphene_django',
    'django_cron',
    'watchman',
    'pinax.eventlog',
    'webpack_loader',
    'rules.apps.AutodiscoverRulesConfig',
    'django_mysql',
    'constance',
    'constance.backends.database',
    'import_export',
    'rangefilter',
    'fontawesomefree'
]

# The order of this MIDDLEWARE is important
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

CRON_CLASSES = [
    "dashboard.cron.DashboardCronJob",
]
# the cron_udp.hjson file contains queries run by MyLA cron job
CRON_QUERY_FILE = os.path.join(BASE_DIR, ENV.get('CRON_QUERY_FILE', 'config/cron_udp.hjson'))


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django_su.context_processors.is_su',
    'dashboard.context_processors.get_git_version_info',
    'dashboard.context_processors.get_myla_globals',
    'dashboard.context_processors.last_updated'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(APPLICATION_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': CONTEXT_PROCESSORS,
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)

GRAPHENE = {
    'SCHEMA': 'dashboard.graphql.schema.schema'
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

ROOT_URLCONF = 'dashboard.urls'

WSGI_APPLICATION = 'dashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        **{
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'student_dashboard',
            'USER': 'student_dashboard_user',
            'PASSWORD': 'student_dashboard_password',
            'HOST': 'localhost',
            'PORT': 3306,
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        },
        **ENV.get('MYSQL', {})
    },
    'DATA_WAREHOUSE': {
        **{
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': 5432,
            'OPTIONS': {},
            'IS_UNIZIN': True
        },
        **ENV.get('DATA_WAREHOUSE', {})
    },
}
# optionally set LRS data source
LRS_IS_BIGQUERY = ENV.get('LRS', {}).get('ENGINE', 'google.cloud.bigquery') == 'google.cloud.bigquery'
if not LRS_IS_BIGQUERY:
    DATABASES['LRS'] = {
        **{
            'ENGINE': '',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': 5432,
            'OPTIONS': {},
        },
        **ENV.get('LRS', {})
    }

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = ENV.get("TIME_ZONE", os.getenv("TZ", "America/Detroit"))

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# The hex value to be used in the front end for the "primary" color of the palette and theme.
PRIMARY_UI_COLOR = ENV.get("PRIMARY_UI_COLOR", None)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # Gunicorns logging format https://github.com/benoitc/gunicorn/blob/19.x/gunicorn/glogging.py
    'formatters': {
        "generic": {
            "format": "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': ENV.get('DJANGO_LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO'),
        },
        'rules': {
            'handlers': ['console'],
            'propagate': False,
            'level': ENV.get('RULES_LOG_LEVEL', 'INFO'),
        },
        '': {
            'level': 'WARNING',
            'handlers': ['console'],
        },

    },
    'root': {
        'level': ENV.get('ROOT_LOG_LEVEL', 'INFO'),
        'handlers': ['console']
    },
}
RANDOM_PASSWORD_DEFAULT_LENGTH = ENV.get('RANDOM_PASSWORD_DEFAULT_LENGTH', 32)
DB_CACHE_CONFIGS = ENV.get('DB_CACHE_CONFIGS',
                           {'CACHE_TTL': 600, 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
                            'LOCATION': 'django_myla_cache',
                            'CACHE_KEY_PREFIX': 'myla',
                            'CACHE_OPTIONS': {'COMPRESS_MIN_LENGTH': 5000, 'COMPRESS_LEVEL': 6}
                            })

CACHES = {
    'default': {
        'BACKEND': DB_CACHE_CONFIGS['BACKEND'],
        'LOCATION': DB_CACHE_CONFIGS['LOCATION'],
        'OPTIONS': DB_CACHE_CONFIGS['CACHE_OPTIONS'],
        "KEY_PREFIX": DB_CACHE_CONFIGS['CACHE_KEY_PREFIX'],
        "TIMEOUT": DB_CACHE_CONFIGS['CACHE_TTL']
    }
}

# IMPORT LOCAL ENV
# =====================
try:
    from settings_local import *
except ImportError:
    pass

AUTHENTICATION_BACKENDS: Tuple[str, ...] = (
    'rules.permissions.ObjectPermissionBackend',
    'django_su.backends.SuBackend',
)

if ENABLE_LTI:
    LTI_CONFIG = ENV.get('LTI_CONFIG', {})
    LTI_CONFIG_TEMPLATE_PATH = ENV.get('LTI_CONFIG_TEMPLATE_PATH')
    LTI_CONFIG_DISABLE_DEPLOYMENT_ID_VALIDATION = ENV.get('LTI_CONFIG_DISABLE_DEPLOYMENT_ID_VALIDATION', False)

# This is used to fix ids from Canvas Data which are incremented by some large number
CANVAS_DATA_ID_INCREMENT = ENV.get("CANVAS_DATA_ID_INCREMENT", 17700000000000000)

# Allow enabling/disabling the View options globally
VIEWS_DISABLED = ENV.get('VIEWS_DISABLED', [])

# Time to run cron
RUN_AT_TIMES = ENV.get('RUN_AT_TIMES', [])

# Number of weeks max to allow by default. some begin/end dates in Canvas aren't correct
MAX_DEFAULT_WEEKS = ENV.get("MAX_DEFAULT_WEEKS", 16)

CLIENT_CACHE_TIME = ENV.get("CLIENT_CACHE_TIME", 3600)

CRON_BQ_IN_LIMIT = ENV.get("CRON_BQ_IN_LIMIT", 1000)

CANVAS_FILE_PREFIX = ENV.get("CANVAS_FILE_PREFIX", "")
CANVAS_FILE_POSTFIX = ENV.get("CANVAS_FILE_POSTFIX", "")

# strings for construct file download url

CANVAS_FILE_ID_NAME_SEPARATOR = "|"

RESOURCE_ACCESS_CONFIG = ENV.get("RESOURCE_ACCESS_CONFIG", {})

# Git info settings
SHA_ABBREV_LENGTH = 7

# Django CSP Settings, load up from file if set
if "CSP" in ENV:
    MIDDLEWARE += ['csp.middleware.CSPMiddleware',]
    for csp_key, csp_val in ENV.get("CSP").items():
        # If there's a value set for this CSP config, set it as a global
        if (csp_val):
            globals()["CSP_"+csp_key] = csp_val
# If CSP not set, add in XFrameOptionsMiddleware
else:
    MIDDLEWARE += ['django.middleware.clickjacking.XFrameOptionsMiddleware',]

# These are mostly needed by Canvas but it should also be in on general
CSRF_COOKIE_SECURE = ENV.get("CSRF_COOKIE_SECURE", False)
if CSRF_COOKIE_SECURE:
    CSRF_TRUSTED_ORIGINS = ENV.get("CSRF_TRUSTED_ORIGINS", [])
    SESSION_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = ENV.get('USE_X_FORWARDED_HOST', False)

# When using the application with iframes (e.g. with LTI), these need to be set to None. However, we'll need to update
# this when new browser versions expect (and the Django version allows) the string "None".
SESSION_COOKIE_SAMESITE = ENV.get("SESSION_COOKIE_SAMESITE", 'None')
CSRF_COOKIE_SAMESITE = ENV.get("CSRF_COOKIE_SAMESITE", 'None')

SESSION_COOKIE_AGE = ENV.get('SESSION_COOKIE_AGE', 86400)
SESSION_EXPIRE_AT_BROWSER_CLOSE = ENV.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', True)

CHECK_ENABLE_BACKEND_LOGIN = False if ENABLE_LTI else True

# Allow for ENABLE_BACKEND_LOGIN override
ENABLE_BACKEND_LOGIN = ENV.get("ENABLE_BACKEND_LOGIN", CHECK_ENABLE_BACKEND_LOGIN)
# only show logout URL with backend enabled
SHOW_LOGOUT_LINK = True if ENABLE_BACKEND_LOGIN else False

# If backend login is still enabled or LTI is used (since it uses this), enable the ModelBackend
if ENABLE_BACKEND_LOGIN or ENABLE_LTI:
    AUTHENTICATION_BACKENDS += (
        'django.contrib.auth.backends.ModelBackend',
    )

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'SURVEY_URL': ('', 'Full URL to Qualtrics survey. If left blank no survey link will display.', str),
    'SURVEY_TEXT': ('Take Survey', 'Custom text for Qualtrics survey link and title. If left blank will default to "Take Survey". Must also configure SURVEY_URL. For best mobile fit keep this text to under 6 words/30 characters.', str),
    'RESOURCE_LIMIT': (100, 'Maximum number of resources shown in the Resources Accessed visualization.', int)
}

# the url strings for Canvas Caliper events
CANVAS_EVENT_URLS = ENV.get("CANVAS_EVENT_URLS", [])

# Only need view permission for exports
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'

# IMPORT LOCAL ENV
# =====================
try:
    from settings_local import *
except ImportError:
    pass
