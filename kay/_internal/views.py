# -*- coding: utf-8 -*-

"""
Views of Kay internal applications.

:Copyright: (c) 2009 Accense Technology, Inc.,
                     Takashi Matsuo <tmatsuo@candit.jp>,
                     All rights reserved.
:license: BSD, see LICENSE for more details.
"""

import logging

from werkzeug import Response
from google.appengine.ext import db

from kay.utils import (
  render_to_response, render_to_string
)
from kay.sessions.decorators import no_session
from kay.i18n import gettext as _

# TODO implement

@no_session
def cron_frequent(request):
  logging.debug("cron frequent handler called.")
  return Response("OK")

@no_session
def cron_hourly(request):
  logging.debug("cron hourly handler called.")
  return Response("OK")

@no_session
def maintenance_page(request):
  return render_to_response("_internal/maintenance.html",
                            {"message": _('Now it\'s under maintenance.')})

@no_session
def expire_registration(request, registration_key):
  from kay.registration.models import RegistrationProfile
  p = db.get(registration_key)
  def txn():
    if not p.activated:
      p.user.delete()
    p.delete()
  db.run_in_transaction(txn)
  return Response("OK")

@no_session
def send_registration_confirm(request, registration_key):
  logging.debug(registration_key)
  from kay.registration.models import RegistrationProfile
  from google.appengine.api import mail
  from kay.conf import settings
  p = db.get(registration_key)
  subject = render_to_string('registration/activation_email_subject.txt',
                             {'appname': settings.APP_NAME})
  subject = ''.join(subject.splitlines())
  message = render_to_string(
    'registration/activation_email.txt',
    {'activation_key': registration_key,
     'appname': settings.APP_NAME})
  mail.send_mail(subject=subject, body=message,
                 sender=settings.DEFAULT_MAIL_FROM, to=p.parent().email)
  return Response("OK")
