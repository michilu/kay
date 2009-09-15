# -*- coding: utf-8 -*-

"""
Kay utilities.

:Copyright: (c) 2009 Accense Technology, Inc. All rights reserved.
:license: BSD, see LICENSE for more details.
"""

import os
import logging
from datetime import datetime

from google.appengine.api import users
from google.appengine.api import memcache

from werkzeug import (
  Local, LocalManager, Response
)
from werkzeug.exceptions import NotFound
from werkzeug.urls import url_quote
from pytz import timezone, UTC

from kay.conf import settings
from kay.utils.importlib import import_module

local = Local()
local_manager = LocalManager([local])

_translations_cache = {}
_default_translations = None
_standard_context_processors = None

_timezone_cache = {}

def set_trace():
  import pdb, sys
  debugger = pdb.Pdb(stdin=sys.__stdin__, 
                     stdout=sys.__stdout__)
  debugger.set_trace(sys._getframe().f_back)

def get_project_path():
  return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_kay_locale_path():
  return os.path.join(get_project_path(), 'kay', 'i18n')


def get_timezone(tzname):
  """
  Method to get timezone with memcached enhancement.
  """
  global _timezone_cache
  if hasattr(_timezone_cache, 'tzname'):
    tz = _timezone_cache['tzname']
  else:
    try:
      tz = memcache.get("tz:%s" % tzname)
    except:
      tz = None
      logging.debug("timezone get failed: %s" % tzname)
  if tz is None:
    tz = timezone(tzname)
    memcache.add("tz:%s" % tzname, tz, 86400)
    _timezone_cache['tzname'] = tz
  return tz


def raise_on_dev():
  if 'SERVER_SOFTWARE' in os.environ and \
        os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    raise RuntimeError("Just for debugging.")
  else:
    pass


def get_request():
  return getattr(local, 'request', None)


def url_for(endpoint, **args):
  """Get the URL to an endpoint.  The keyword arguments provided are used
  as URL values.  Unknown URL values are used as keyword argument.
  Additionally there are some special keyword arguments:

  `_anchor`
    This string is used as URL anchor.

  `_external`
    If set to `True` the URL will be generated with the full server name
    and `http://` prefix.
  """
  if hasattr(endpoint, 'get_url_values'):
    rv = endpoint.get_url_values()
    if rv is not None:
      if isinstance(rv, basestring):
        return make_external_url(rv)
      endpoint, updated_args = rv
      args.update(updated_args)
  anchor = args.pop('_anchor', None)
  external = args.pop('_external', False)
  rv = local.url_adapter.build(endpoint, args,
                               force_external=external)
  if anchor is not None:
    rv += '#' + url_quote(anchor)
  return rv


def create_auth_url(url, action):
  # TODO: Change implementation according to auth backend settings.
  if url is None:
    url = local.request.url
  method_name = 'create_%s_url' % action
  if 'kay.auth.middleware.GoogleAuthenticationMiddleware' in \
        settings.MIDDLEWARE_CLASSES:
    from google.appengine.api import users
    method = getattr(users, method_name)
  elif 'kay.auth.middleware.AuthenticationMiddleware' in \
        settings.MIDDLEWARE_CLASSES:
    method = getattr(local.app.auth_backend, method_name)
  return method(url)
      

def create_logout_url(url=None):
  """
  An utility function for jinja2.
  """
  return create_auth_url(url, 'logout')
    

def create_login_url(url=None):
  """
  An utility function for jinja2.
  """
  return create_auth_url(url, 'login')


def reverse(endpoint, _external=False, method='GET', **values):
  """
  An utility function for jinja2.
  """
  return local.url_adapter.build(endpoint, values, method=method,
      force_external=_external)


def render_to_string(template, context={}, processors=None):
  """
  A function for template rendering adding useful variables to context
  automatically, according to the CONTEXT_PROCESSORS settings.
  """
  if processors is None:
    processors = ()
  else:
    processors = tuple(processors)
  for processor in get_standard_processors() + processors:
    context.update(processor(get_request()))
  template = local.app.jinja2_env.get_template(template)
  return template.render(context)


def render_to_response(template, context, mimetype='text/html',
                       processors=None):
  """
  A function for render html pages.
  """
  return Response(render_to_string(template, context, processors),
                  mimetype=mimetype)

def get_standard_processors():
  from kay.conf import settings
  global _standard_context_processors
  if _standard_context_processors is None:
    processors = []
    for path in settings.CONTEXT_PROCESSORS:
      i = path.rfind('.')
      module, attr = path[:i], path[i+1:]
      try:
        mod = import_module(module)
      except ImportError, e:
        raise ImproperlyConfigured('Error importing request processor module'
                                   ' %s: "%s"' % (module, e))
      try:
        func = getattr(mod, attr)
      except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'callable request processor' %
                                   (module, attr))
      processors.append(func)
    _standard_context_processors = tuple(processors)
  return _standard_context_processors


def to_local_timezone(datetime, tzname=settings.DEFAULT_TIMEZONE):
  """Convert a datetime object to the local timezone."""
  if datetime.tzinfo is None:
    datetime = datetime.replace(tzinfo=UTC)
  tzinfo = get_timezone(tzname)
  return tzinfo.normalize(datetime.astimezone(tzinfo))


def to_utc(datetime, tzname=settings.DEFAULT_TIMEZONE):
  """Convert a datetime object to UTC and drop tzinfo."""
  if datetime.tzinfo is None:
    datetime = get_timezone(tzname).localize(datetime)
  return datetime.astimezone(UTC).replace(tzinfo=None)


def get_by_key_name_or_404(model_class, key_name):
  obj = model_class.get_by_key_name(key_name)
  if not obj:
    raise NotFound
  return obj


def get_by_id_or_404(model_class, id):
  obj = model_class.get_by_id(id)
  if not obj:
    raise NotFound
  return obj


def get_or_404(model_class, key):
  obj = model_class.get(key)
  if not obj:
    raise NotFound
  return obj
