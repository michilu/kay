# -*- coding: utf-8 -*-

"""
kay.ext.gaema.utils

:Copyright: (c) 2009 Takashi Matsuo <tmatsuo@candit.jp>
                     All rights reserved.
:license: BSD, see LICENSE for more details.
"""

from kay.utils import (
  set_cookie, url_for, local
)
from kay.conf import settings
from kay.ext.gaema import (
  NEXT_URL_KEY_FORMAT, GAEMA_USER_KEY_FORMAT
)

def create_gaema_login_url(name, nexturl):
  next_url_key = NEXT_URL_KEY_FORMAT % name
  set_cookie(next_url_key, nexturl)
  return url_for("gaema/%s_login" % name)

def create_gaema_logout_url(name, nexturl):
  next_url_key = NEXT_URL_KEY_FORMAT % name
  set_cookie(next_url_key, nexturl)
  return url_for("gaema/%s_logout" % name)

def get_gaema_user(name):
  gaema_user_key = GAEMA_USER_KEY_FORMAT % name
  if hasattr(settings, "GAEMA_STORAGE") and settings.GAEMA_STORAGE == "cookie":
    return local.request.cookies.get(gaema_user_key, None)
  else:
    return local.request.session.get(gaema_user_key, None)

def set_gaema_user(name, user):
  gaema_user_key = GAEMA_USER_KEY_FORMAT % name
  if hasattr(settings, "GAEMA_STORAGE") and settings.GAEMA_STORAGE == "cookie":
    set_cookie(gaema_user_key, user)
  else:
    local.request.session[gaema_user_key] = user
  
