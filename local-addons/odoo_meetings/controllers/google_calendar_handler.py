import datetime
import pytz
# Google calendar
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def get_google_calendar_service():
    # If modifying these scopes, delete the file token.json.
    # https://developers.google.com/calendar/quickstart/python
    # SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'local-addons/odoo_meetings/static/google_calendar/credentials.json', SCOPES)
            creds = flow.run_local_server(port=51989)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    return service

def create_google_calendar_event(event_name, meetingDescription, start_date_time, end_date_time, attendeeEmail, employeeEmail, meetingLocation, meetingAddress):

    service = get_google_calendar_service()

    if (meetingLocation == 'google_meet'):
        conferenceData = { # Add Google meet to Google Calendar event
            'createRequest': {
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'requestId': 'requestId'
            },
            'entryPoints': [{'entryPointType': 'video'}]
        }
    else: 
        conferenceData = {}

    event = { # Google Calendar event JSON
        'summary': event_name,
        'location': meetingAddress,
        'description': meetingDescription,
        'start': {
            'dateTime': start_date_time,
            'timeZone': pytz.utc.zone, # UTC timezone
        },
        'end': {
            'dateTime': end_date_time,
            'timeZone': pytz.utc.zone, # UTC timezone
        },
        # 'recurrence': [
        #     'RRULE:FREQ=DAILY;COUNT=2'
        # ],
        'attendees': [
            {'email': 'sensen.yechen@gmail.com'},
            # {'email': '100349203@alumnos.uc3m.es'},
            {'email': attendeeEmail},
            {'email': employeeEmail}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'conferenceData': conferenceData
    }

    event = service.events().insert(
        calendarId='primary',
        conferenceDataVersion=1, # Allow google meet/hangouts
        sendNotifications=True,
        sendUpdates='all',
        body=event).execute()
    # return event.get('id')
    return event
    # print('Event created: ', event.get('htmlLink'))

def delete_google_calendar_event(eventId):
    service = get_google_calendar_service()
    service.events().delete(calendarId='primary', eventId=eventId, sendUpdates="all").execute()