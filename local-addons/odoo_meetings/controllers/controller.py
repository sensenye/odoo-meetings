# -*- coding: utf-8 -*-
from odoo import http
import sys
import json
import pandas as pd
import datetime
from datetime import timedelta
import locale
import pytz

# Google calendar
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from . import meeting_type_handler
from . import meeting_event_handler

# https://odoo-development.readthedocs.io/en/latest/dev/frontend/webpage.html
# https://kanakinfosystems.com/blog/create-form-in-odoo-website


class OdooMeetings(http.Controller):
    @http.route('/odoo-meetings/', auth='public', website=True)
    def index(self, **kw):
        return meeting_type_handler.meeting_type_index()

    @http.route('/odoo-meetings/<model("odoo_meetings.meeting_type"):obj>/', auth='public', website=True)
    def meeting_type_details_index(self, obj, **kw):
        return meeting_type_handler.meeting_type_details_index(obj)

    @http.route('/odoo-meetings/submit/', auth='public', website=True)
    def meeting_event_submit(self, **kw):
        return meeting_event_handler.meeting_event_submit(kw)

    @http.route('/odoo-meetings/event/<model("odoo_meetings.meeting_event"):obj>/', auth='public', website=True)
    def update_meeting_event_index(self, obj, **kw):
        return meeting_event_handler.update_meeting_event_index(kw.get('action'), obj)