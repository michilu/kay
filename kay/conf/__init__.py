"""
Settings and configuration for Kay.

Values will be read from the module passed when initialization and
then, kay.conf.global_settings; see the global settings file for a
list of all possible variables.

Taken from django.
"""

import os
import re
import time     # Needed for Windows

from kay.conf import global_settings
from kay.utils.lazy import LazyObject
from kay.utils import importlib

class LazySettings(LazyObject):
  """
  A lazy proxy for either global Django settings or a app local
  settings object.  The user can manually configure settings prior to
  using them. Otherwise, Django uses the settings module passed to
  __init__ medthod.
  """
  def __init__(self, settings_module=None):
    super(LazySettings, self).__init__()
    self.settings_module = settings_module or 'settings'

  def __getattr__(self, name):
    if name == 'settigns_module':
      return self.__dict__["settings_module"]
    return super(LazySettings, self).__getattr__(name)

  def __setattr__(self, name, value):
    if name == 'settings_module':
      self.__dict__["settings_module"] = value
    else:
      super(LazySettings, self).__setattr__(name, value)

  def _setup(self):
    """
    Load the settings module pointed to by the environment
    variable. This is used the first time we need any settings at all,
    if the user has not previously configured the settings manually.
    """
    try:
      if not self.settings_module: # If it's set but is an empty string.
        raise KeyError
    except KeyError:
      # NOTE: This is arguably an EnvironmentError, but that causes
      # problems with Python's interactive help.
      raise ImportError("Settings cannot be imported, because environment variable %s is undefined." % ENVIRONMENT_VARIABLE)

    self._wrapped = Settings(self.settings_module)
    del self.settings_module

  def configured(self):
    """
    Returns True if the settings have already been configured.
    """
    return bool(self._wrapped)
  configured = property(configured)


class Settings(object):
  def __init__(self, settings_module):
    # update this dict from global settings (but only for ALL_CAPS settings)
    for setting in dir(global_settings):
      if setting == setting.upper():
        setattr(self, setting, getattr(global_settings, setting))

    # store the settings module in case someone later cares
    self.SETTINGS_MODULE = settings_module

    try:
      mod = importlib.import_module(self.SETTINGS_MODULE)
    except ImportError, e:
      raise ImportError, ("Could not import settings '%s' (Is it on sys.path?"
                          " Does it have syntax errors?): %s"
                          % (self.SETTINGS_MODULE, e))

    # Settings that should be converted into tuples if they're
    # mistakenly entered as strings.

    tuple_settings = ("INSTALLED_APPS", "TEMPLATE_DIRS")

    for setting in dir(mod):
      if setting == setting.upper():
        setting_value = getattr(mod, setting)
        if setting in tuple_settings and type(setting_value) == str:
          setting_value = (setting_value,) # In case the user forgot the comma.
        setattr(self, setting, setting_value)

    # Expand entries in INSTALLED_APPS like "django.contrib.*" to a list
    # of all those apps.
    new_installed_apps = []
    for app in self.INSTALLED_APPS:
      if app.endswith('.*'):
        app_mod = importlib.import_module(app[:-2])
        appdir = os.path.dirname(app_mod.__file__)
        app_subdirs = os.listdir(appdir)
        app_subdirs.sort()
        name_pattern = re.compile(r'[a-zA-Z]\w*')
        for d in app_subdirs:
          if name_pattern.match(d) and os.path.isdir(os.path.join(appdir, d)):
            new_installed_apps.append('%s.%s' % (app[:-2], d))
      else:
        new_installed_apps.append(app)
    self.INSTALLED_APPS = new_installed_apps

  def get_all_members(self):
    return dir(self)

settings = LazySettings()