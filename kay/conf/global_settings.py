# -*- coding: utf-8 -*-

"""
Kay default settings.

:Copyright: (c) 2009 Accense Technology, Inc. 
                     Takashi Matsuo <tmatsuo@candit.jp>,
                     All rights reserved.
:license: BSD, see LICENSE for more details.
"""

import os

APP_NAME = 'kay_main'
DEFAULT_TIMEZONE = 'Asia/Tokyo'
DEBUG = True
PROFILE = False
PRINNT_CALLERS_ON_PROFILING = False
PRINNT_CALLEES_ON_PROFILING = False
SECRET_KEY = 'please set secret keys here'
SESSION_PREFIX = 'gaesess:'
COOKIE_AGE = 1209600 # 2 weeks
COOKIE_NAME = 'KAY_SID'
SESSION_MEMCACHE_AGE = 3600
LANG_COOKIE_AGE = COOKIE_AGE
LANG_COOKIE_NAME = 'hl'

CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_NAMESPACE = 'CACHE_MIDDLEWARE'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

ADD_APP_PREFIX_TO_KIND = True

ROOT_URL_MODULE = 'urls'

MEDIA_URL = '/media'
INTERNAL_MEDIA_URL = '/_media'

ADMINS = (
)

TEMPLATE_DIRS = (
)

USE_I18N = True
DEFAULT_LANG = 'en'

INSTALLED_APPS = (
)

APP_MOUNT_POINTS = {
}

CONTEXT_PROCESSORS = (
  'kay.context_processors.request',
  'kay.context_processors.url_functions',
  'kay.context_processors.media_url',
)

JINJA2_FILTERS = {
  'nl2br': 'kay.utils.filters.nl2br',
}

SUBMOUNT_APPS = (
)

MIDDLEWARE_CLASSES = (
  'kay.sessions.middleware.SessionMiddleware',
  'kay.auth.middleware.GoogleAuthenticationMiddleware',
)

AUTH_USER_BACKEND = 'kay.auth.backend.DatastoreBackend'
AUTH_USER_MODEL = 'kay.auth.models.GoogleUser'
USE_DB_HOOK = False
