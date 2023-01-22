"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import collections
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="django-insecure-rxo16nxf7l-ghxr%q)9-t9_5y%w5&^nj9i=vq9m0-f1%a4xo6v")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'more_admin_filters',
    'nested_admin',
    'sslserver',
    'social_django',
    'eligibility',
    'userprofile',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'querycount.middleware.QueryCountMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}


# Email
# https://docs.djangoproject.com/en/3.2/ref/settings/#email-backend

EMAIL = env.email_url("EMAIL_URL", default="consolemail://")

EMAIL_BACKEND = EMAIL["EMAIL_BACKEND"]
EMAIL_HOST = EMAIL["EMAIL_HOST"]
EMAIL_PORT = EMAIL["EMAIL_PORT"]
EMAIL_USE_TLS = EMAIL.get("EMAIL_USE_TLS", False)
EMAIL_HOST_USER = EMAIL["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = EMAIL["EMAIL_HOST_PASSWORD"]
EMAIL_FILE_PATH = EMAIL["EMAIL_FILE_PATH"]

EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="")

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@tournaments.fit")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Social Auth

SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_JSONFIELD_CUSTOM = 'django.db.models.JSONField'

SOCIAL_AUTH_FACEBOOK_KEY = env("FACEBOOK_KEY", default="")
SOCIAL_AUTH_FACEBOOK_SECRET = env("FACEBOOK_SECRET", default="")
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'en_AU',
    'fields': 'id, name, email, age_range',
}

SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = env("LINKEDIN_KEY", default="")
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = env("LINKEDIN_SECRET", default="")
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_liteprofile', 'r_emailaddress']
SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['emailAddress']
SOCIAL_AUTH_LINKEDIN_OAUTH2_EXTRA_DATA = [
    ('id', 'id'),
    ('firstName', 'first_name'),
    ('lastName', 'last_name'),
    ('emailAddress', 'email_address'),
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


# Logging

LOGGING_LEVELS = collections.defaultdict(
    lambda: env("LOGLEVEL", default="WARNING"),
    env.json("LOGLEVEL_LOGGERS", default={}),
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "formatters": {
        "verbose": {
            "format": 'timestamp="%(asctime)s" '
            'level="%(levelname)s" '
            'process="%(processName)s" '
            'thread="%(thread)d" '
            'logger="%(name)s" '
            'function="%(funcName)s" '
            'message="%(message)s"'
        },
        "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {"class": "logging.NullHandler"},
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django.db": {"handlers": ["console"], "level": LOGGING_LEVELS["django.db"]},
        "django.security.DisallowedHost": {"handlers": ["console"], "propagate": False},
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": LOGGING_LEVELS["django.request"],
            "propagate": True,
        },
        "": {"handlers": ["console"], "level": LOGGING_LEVELS[""]},
    },
}

for logger_name in LOGGING_LEVELS:
    LOGGING["loggers"][logger_name] = {
        "handlers": ["console"],
        "level": LOGGING_LEVELS[logger_name],
    }
