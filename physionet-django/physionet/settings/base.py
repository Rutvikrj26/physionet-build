"""
Django settings for physionet project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from decouple import config

import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

SECRET_KEY = config('SECRET_KEY')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ckeditor',
    # 'django_cron',
    'background_task',

    'user',
    'project',
    'console',
    'export',
    'notification',
    'search',
    'lightwave',
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

CRON_CLASSES = [
    "physionet.cron.RemoveUnverifiedEmails",
    "physionet.cron.RemoveOutstandingInvites",
]

ROOT_URLCONF = 'physionet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'physionet.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'user.validators.ComplexityValidator',
    },
]

AUTHENTICATION_BACKENDS = ['user.models.DualAuthModelBackend']

AUTH_USER_MODEL = 'user.User'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/projects/'

LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]


# List of permitted HTML tags and attributes for rich text fields.
# The 'default' configuration permits all of the tags below.  Other
# configurations may be added that permit different sets of tags.

# Attributes that can be added to any HTML tag
_generic_attributes = ['lang', 'title']

# Inline/phrasing content
_inline_tags = {
    'a':      {'attributes': ['href']},
    'abbr':   True,
    'b':      True,
    'bdi':    True,
    'cite':   True,
    'code':   True,
    'dfn':    True,
    'em':     True,
    'i':      True,
    'kbd':    True,
    'q':      True,
    'rb':     True,
    'rp':     True,
    'rt':     True,
    'rtc':    True,
    'ruby':   True,
    's':      True,
    'samp':   True,
    'span':   True,
    'strong': True,
    'sub':    True,
    'sup':    True,
    'time':   True,
    'var':    True,
    'wbr':    True,
}
# Block/flow content
_block_tags = {
    # Paragraphs, lists, quotes, line breaks
    'blockquote': True,
    'br':         True,
    'dd':         True,
    'div':        True,
    'dl':         True,
    'dt':         True,
    'li':         {'attributes': ['value']},
    'ol':         {'attributes': ['start', 'type']},
    'p':          True,
    'pre':        True,
    'ul':         True,

    # Tables
    'caption':    True,
    'col':        {'attributes': ['span']},
    'colgroup':   {'attributes': ['span']},
    'table':      {'attributes': ['width']},
    'tbody':      True,
    'td':         {'attributes': ['colspan', 'headers', 'rowspan', 'style'],
                   'styles': ['text-align']},
    'tfoot':      True,
    'th':         {'attributes': ['abbr', 'colspan', 'headers', 'rowspan',
                                  'scope', 'sorted', 'style'],
                   'styles': ['text-align']},
    'thead':      True,
    'tr':         True,
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format'],
            ['Bold', 'Italic', 'Underline','Blockquote'],
            ['NumberedList', 'BulletedList'],
            ['CodeSnippet', 'Table'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
        ],
        'width': '100%',
        'format_tags': 'p;h3',
        'extraPlugins': 'codesnippet',
        'allowedContent': {
            **_inline_tags,
            **_block_tags,
            'h3': True,
            'h4': True,
            'h5': True,
            'h6': True,
            '*': {'attributes': _generic_attributes},
        },
    }

}

LOGGING_CONFIG = None
LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)-15s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'Custom_Logging': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/physionet.log',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }, 
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'user': {
            'level': 'INFO',
            'handlers': ['Custom_Logging'],
            'propagate': False,
        },
       'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'physionet.error': {
            'handlers': ['console', 'mail_admins', 'Custom_Logging'],
            'level': 'ERROR',
        }
    },
})
