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


# https://odoo-development.readthedocs.io/en/latest/dev/frontend/webpage.html
# https://kanakinfosystems.com/blog/create-form-in-odoo-website


class OdooMeetings(http.Controller):
    @http.route('/odoo-meetings/', auth='public', website=True)
    def index(self, **kw):
        meetingTypes = http.request.env['odoo_meetings.meeting_type']
        return http.request.render('odoo_meetings.index', {
            'meetingTypes': meetingTypes.search([]),
        })

    @http.route('/odoo-meetings/<model("odoo_meetings.meeting_type"):obj>/', auth='public', website=True)
    def form_submittt(self, obj, **kw):

        # Id of the meeting type selected by user
        meetingTypeId = obj.id

        # Duration of each meeting within the meeting type
        meetingDuration = obj.duration

        # Get meeting type data from database
        odoo_meetings_meeting_type = self.get_meeting_type(meetingTypeId)

        # Get the information of the employees assigned to the meeting type from database
        resource_resource = self.get_resource_resource(
            odoo_meetings_meeting_type)

        # Get information about the type of working hours of the employees from the resource_calendar_attendance table
        resource_calendar_attendance_sorted = self.get_resource_calendar_attendance_sorted(
            resource_resource)

        availability = self.get_availability(
            resource_resource, resource_calendar_attendance_sorted, meetingDuration)

        return http.request.render('odoo_meetings.select_time', {
            'meetingType': obj,
            'today': datetime.datetime.today().date(),
            # 'employees': meeting_type_employees,
            'meetingTypeId': meetingTypeId,
            'meetingDuration': meetingDuration,
            'meetingDescription': obj.description,
            'meetingLocation': obj.location,
            'meetingAddress': obj.address,
            'resources': resource_resource,
            # Check key in dictionary
            'monday': availability['0'] if '0' in availability else [],
            'tuesday': availability['1'] if '1' in availability else [],
            'wednesday': availability['2'] if '2' in availability else [],
            'thursday': availability['3'] if '3' in availability else [],
            'friday': availability['4'] if '4' in availability else [],
            'saturday': availability['5'] if '5' in availability else [],
            'sunday': availability['6'] if '6' in availability else []
        })

    def get_meeting_type(self, meetingTypeId):
        return http.request.env['odoo_meetings.meeting_type'].search([
            ['id', '=', meetingTypeId]
        ])

    def get_resource_resource(self, odoo_meetings_meeting_type):
        # List of employees from the hr.employee table that are assigned to the meeting type selected by user
        meeting_type_employees = odoo_meetings_meeting_type.employees.sorted(
            key='id', reverse=False)

        # List of the ids of the employees
        meeting_type_employees_id_list = []
        for employee in meeting_type_employees:
            meeting_type_employees_id_list.append(employee.id)

        # Get the info of the resource table of the employees above
        resource_resource = http.request.env['resource.resource'].search([
            ['id', 'in', meeting_type_employees_id_list]
        ])

        return resource_resource

    def get_resource_calendar_attendance_sorted(self, resource_resource):
        # List of ids from the resource_calendar table
        resource_calendar_attendance_id_list = []
        for res in resource_resource:
            resource_calendar_attendance_id_list.append(res.calendar_id.id)

        # Type of working hours from the resource_calendar_attendance table
        resource_calendar_attendance = http.request.env['resource.calendar.attendance'].search([
            ['calendar_id', 'in', resource_calendar_attendance_id_list]
        ])

        # Sort by id
        resource_calendar_attendance_sorted = resource_calendar_attendance.sorted(
            key='id', reverse=False)

        return resource_calendar_attendance_sorted

    def print_to_file(self, elem):
        original_stdout = sys.stdout  # Save a reference to the original standard output
        with open('filename.txt', 'w') as f:
            # Change the standard output to the file we created.
            sys.stdout = f
            print(elem)
        sys.stdout = original_stdout

    def get_availability(self, resource_resource, resource_calendar_attendance_sorted, meetingDuration):
        myDict = {}
        hour_from = []
        hour_to = []
        calendar_id = []
        dayofweek = []
        type_name = []

        temp = 0
        availabilityDict = {}
        availability = []

        original_stdout = sys.stdout

        # Sort by name
        res_cal_att_sorted_by_dayofweek = resource_calendar_attendance_sorted.sorted(
            key='name', reverse=False)

        # Print to file
        with open('filename.txt', 'w') as f:
            # Change the standard output to the file we created.
            sys.stdout = f
            for res in resource_resource:
                # Employee name + type of working hours name
                print(res.name, "\t", res.calendar_id.name)
                # Print hours of each type
                for calendar in resource_calendar_attendance_sorted:
                    if (calendar.calendar_id.id == res.calendar_id.id):
                        print(calendar.name, "\t", calendar.hour_from,
                              " - ", calendar.hour_to)

            print("\n", "\n")
            # Get all type of working hours
            for calendar in resource_calendar_attendance_sorted:
                hour_from.append(calendar.hour_from)
                hour_to.append(calendar.hour_to)
                calendar_id.append(calendar.calendar_id.id)
                dayofweek.append(calendar.dayofweek)
                type_name.append(calendar.name)
                print(calendar.calendar_id.name, "\t", calendar.name,
                      "\t", calendar.hour_from, " - ", calendar.hour_to)

            # Create dictionary with all needed data
            myDict["calendar_id"] = calendar_id
            myDict["type_name"] = type_name
            myDict["dayofweek"] = dayofweek
            myDict["hour_from"] = hour_from
            myDict["hour_to"] = hour_to

            print("\n", myDict)

            # Create dataframe from Pandas library
            df = pd.DataFrame(myDict)

            print("\n", df)

            df_dayofweek = df.groupby("dayofweek")
            print("\n", df_dayofweek.first())
            print("\n", df_dayofweek.get_group('0'))

            # Get min hour from and max hour to for each type and for each day. This will be the availability of the entire team
            df_min_hour_from_by_type = df.groupby(
                ['type_name'], sort=False).hour_from.min()
            df_max_hour_to_by_type = df.groupby(
                ['type_name'], sort=False).hour_to.max()

            # Create list from dataframe
            list_min_hour_from_by_type = df_min_hour_from_by_type.values.tolist()
            list_max_hour_to_by_type = df_max_hour_to_by_type.values.tolist()

            print("\ndf_min_hour_from_by_type \n", df_min_hour_from_by_type)
            print("\nlist_min_hour_from_by_type \n",
                  list_min_hour_from_by_type)
            print("\ndf_max_hour_to_by_type \n", df_max_hour_to_by_type)
            print("\nlist_max_hour_to_by_type \n", list_max_hour_to_by_type)

            # Add min hour from and max hour to to the list
            for min_value, max_value in zip(list_min_hour_from_by_type, list_max_hour_to_by_type):
                availability.append(min_value)
                availability.append(max_value)

            print("\n\nAVAILABILITY:\n", availability)

            print("\n\nDAYS:\n", myDict["dayofweek"])

            # Get unique values of dayofweek
            unique_dayofweek = df.groupby(
                "dayofweek").dayofweek.min().values.tolist()
            print("\n\nDAYS:\n", unique_dayofweek)

            # Save availability on a dictionary. Each key will represent a day (0 will be monday, 1 tuesday and so on until 6 which will be sunday) and it will store a list with the availability. The format will be:
            # availabilityDict {
            #     "0": [hour_from_morning, hour_to_morning, hour_from_afternoon, hour_to_afternoon]
            #     "1": [hour_from_morning, hour_to_morning, hour_from_afternoon, hour_to_afternoon]
            # }
            for day in unique_dayofweek:
                hours_per_day = []
                for i, hours in enumerate(availability, start=temp):
                    # Get 4 hours (morning start time and end time & afternoon start time and end time)
                    if ((i == temp) or (i % 4 != 0)):
                        # hours_per_day.append(availability[i])
                        if ((i+1) < len(availability) and i % 2 == 0):
                            hours_per_day.append(self.get_hours(
                                availability[i], availability[i+1], meetingDuration))
                            # i += 1
                    else:
                        # Save to the corresponding day
                        temp += 4
                        availabilityDict[day] = hours_per_day
                        break

            print("\n\nAVAILABILITY DICTIONARY:\n", availabilityDict)
            # for a in availabilityDict:
            #     for b in a[b]
            #     print("\n\n", b)

        sys.stdout = original_stdout  # Reset the standard output to its original value
        return availabilityDict

    def get_hours(self, min_value, max_value, duration):
        original_stdout = sys.stdout
        hours = []
        value = min_value
        with open('filename2.txt', 'w') as f:
            # Change the standard output to the file we created.
            sys.stdout = f
            while value <= max_value:
                hours.append(self.decimal_to_time(value))
                value += (duration / 60)
            print(hours)
            sys.stdout = original_stdout
        return hours

    def decimal_to_time(self, decimal):
        hours = int(decimal)
        minutes = int((decimal*60) % 60)
        return str(hours).zfill(2) + ':' + str(minutes).zfill(2)

    @http.route('/odoo-meetings/submit/', auth='public', website=True)
    def form_submit(self, **kw):

        meetingTypeId = kw.get('meetingTypeId')
        meetingDescription = kw.get('meetingDescription')
        meetingDuration = kw.get('meetingDuration')
        meetingLocation = kw.get('meetingLocation')
        meetingAddress = kw.get('meetingAddress')
        selectedDate = kw.get('date')
        attendeeEmail = kw.get('email')

        selectedTime = self.time_to_decimal(kw.get('time-select'))
        # locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        selectedDay = datetime.datetime.strptime(
            selectedDate, "%Y-%m-%d").weekday()

        # Get meeting type data from database
        odoo_meetings_meeting_type = self.get_meeting_type(meetingTypeId)

        # Get the ID of the last employee who attended the meeting
        last_employee = odoo_meetings_meeting_type.last_employee

        # Get the information of the employees assigned to the meeting type from database
        resource_resource = self.get_resource_resource(
            odoo_meetings_meeting_type)

        # Get information about the type of working hours of the employees from the resource_calendar_attendance table
        resource_calendar_attendance_sorted = self.get_resource_calendar_attendance_sorted(
            resource_resource)

        employee_attendance_order = []
        employee_attendance_recent = []
        # Get a list of employee ID by attendance order. The first ID will be the first employee assigned to the meeting if he is available. If not, the next one and so on. The ID of the first employee that can be assigned must be greater than the ID of the last employee (last_employee) in order to have a more equitative distribution. This way, the ID of the last employee will be at the end of the list, being the last one that can be considered.
        for res in resource_resource:  # Sorted by id
            if res.id > last_employee:
                employee_attendance_order.append(res.id)
            else:
                employee_attendance_recent.append(res.id)

        employee_attendance_order += employee_attendance_recent

        # Print to file
        with open('employees.txt', 'w') as f:
            # Change the standard output to the file we created.
            sys.stdout = f
            print('\n', employee_attendance_order)
            print('\n', selectedTime)
            print('\n', selectedDay)

            # Get the ID of the first employee available
            assigned_employee_id = self.get_first_available_employee(
                employee_attendance_order, resource_resource, resource_calendar_attendance_sorted, selectedDate, selectedDay, selectedTime, meetingDuration)
            print('\n', '\n', 'assigned_employee_id',
                  '\n', assigned_employee_id)

            if -1 == assigned_employee_id:  # No employees available
                return http.request.render('odoo_meetings.form_failure', {})

            employee_email = odoo_meetings_meeting_type.employees.search([
                ['id', '=', assigned_employee_id],
            ]).work_email

            # Save last_employee to the meeting_type table
            query = f"UPDATE odoo_meetings_meeting_type SET last_employee = {assigned_employee_id} WHERE id = {meetingTypeId}"
            # Because models use the same cursor and the Environment holds various caches, these caches must be invalidated when altering the database in raw SQL, or further uses of models may become incoherent
            http.request.env['odoo_meetings.meeting_type'].invalidate_cache()
            http.request.env.cr.execute(query)

            # The user login info is stored on the res_users_id
            res_users_id = self.get_res_users_id(
                assigned_employee_id, resource_resource)
            print('\n\n\n res_users_id: \n', res_users_id)

            # A partner is a employee registered on the website (it has an account and password to access back office).
            partner_id = self.get_partner_id(
                assigned_employee_id, resource_resource)
            print('\n\n\n partner_id: \n', partner_id)

            # Get date time with the format '%Y-%m-%d %H:%M:%S'
            start_time = kw.get('time-select') + ':00'
            start_date_time_str = kw.get('date') + ' ' + start_time
            start_date_time_obj = self.time_to_utc(start_date_time_str)

            end_time = self.decimal_to_time(
                selectedTime + float(meetingDuration)/60) + ':00'
            end_date_time_str = kw.get('date') + ' ' + end_time
            end_date_time_obj = self.time_to_utc(end_date_time_str)

            print('timestamp: \n', start_date_time_obj, ' - ', end_date_time_obj)

            # Save meeting event to db
            meeting = http.request.env['odoo_meetings.meeting_event'].create({
                'assistant_name': kw.get('name'),
                'assistant_email': kw.get('email'),
                'comments': kw.get('comments'),
                'date': kw.get('date'),
                'hour': kw.get('time-select'),
                # 'state': 'TODO: add state',
                'meeting_type': [(4, kw.get('meetingTypeId'), 0)],
                'employee': [(4, assigned_employee_id, 0)],
                # 'google_calendar_event_id': google_calendar_event_id
            })

            # Google Calendar event parameters
            client_event_name = 'Reunión con ' + self.get_employee_name(assigned_employee_id, resource_resource)

            start_date_time_with_tz = start_date_time_obj.replace(tzinfo=pytz.utc)
            end_date_time_with_tz = end_date_time_obj.replace(tzinfo=pytz.utc)
            # Google calendar date time uses RFC 3339 format
            start_date_time_with_tz_iso = start_date_time_with_tz.isoformat()
            end_date_time_with_tz_iso = end_date_time_with_tz.isoformat()

            base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')
            delete_event_url = base_url + '/odoo-meetings/event/' + str(meeting.id)
            google_calendar_event_description = meetingDescription + '\n\nSi quieres cancelar/modificar la reunión, haz clic en el siguiente enlace: ' + delete_event_url
            # print(google_calendar_event_description)
            
            # Create Google Calendar event
            google_calendar_event = self.create_google_calendar_event(client_event_name, google_calendar_event_description, start_date_time_with_tz_iso, end_date_time_with_tz_iso, attendeeEmail, employee_email, meetingLocation, meetingAddress)

            google_calendar_event_id = google_calendar_event.get('id')

            # Update google_calendar_event_id on the meeting
            meeting.write({ 'google_calendar_event_id': google_calendar_event_id })

            google_meet_msg = '\n'
            
            # If the meeting is on Google Meet, save the link in the Odoo Calendar of the employee
            if (meetingLocation == 'google_meet'):
                google_meet_url = google_calendar_event.get('conferenceData').get('entryPoints')[0].get('label')
                google_meet_msg = 'Para conectarte a la reunión de Google Meet, haz clic en el siguiente enlace: ' + google_meet_url + '\n'

            odoo_calendar_event_description = meetingDescription + '\n' + google_meet_msg + 'Si quieres cancelar/modificar la reunión, haz clic en el siguiente enlace: ' + delete_event_url

            # print(odoo_calendar_event_description)

            # Save calendar event to DB. Employees will be able to see them on the Odoo Calendar Module
            calendar_event = http.request.env['calendar.event'].create({
                'name': 'Reunión con ' + kw.get('name'),
                'start': start_date_time_obj,
                'stop': end_date_time_obj,
                'start_date': kw.get('date'),
                'stop_date': kw.get('date'),
                'privacy': 'public',
                'show_as': 'busy',
                'user_id': res_users_id, # Responsible
                'partner_id': [(4, partner_id, 0)], # Responsible Contact
                'partner_ids': [(4, partner_id, 0)], # Attendees
                'location': meetingAddress,
                'description': odoo_calendar_event_description
            })

            # Update google_calendar_event_id on the meeting
            meeting.write({ 'calendar_event': [(4, calendar_event.id, 0)] })
            # Increase in 1 the number of meetings of the meeting type
            odoo_meetings_meeting_type.write({ 'num_meetings': odoo_meetings_meeting_type.num_meetings + 1 })     

        return http.request.render('odoo_meetings.form_success', {})

    def time_to_decimal(self, time):
        if len(time) < 6:  # Time without seconds
            (h, m) = time.split(':')
        else:  # Time with seconds
            (h, m, s) = time.split(':')
        return int(h) + int(m) / 60

    def get_first_available_employee(self, employee_attendance_order, resource_resource, resource_calendar_attendance_sorted, selectedDate, selectedDay, selectedTime, meetingDuration):
        # Get employee info according to employee_attendance_order
        for employee_id in employee_attendance_order:
            for res in resource_resource:
                if (employee_id == res.id):  # Get employee
                    print('\n', res.id, '\t', res.name)
                    for calendar in resource_calendar_attendance_sorted:
                        # Get working type
                        if (calendar.calendar_id.id == res.calendar_id.id):
                            # Check if employee is working on the day and time selected by user
                            if (int(calendar.dayofweek) == int(selectedDay) and calendar.hour_from <= selectedTime <= calendar.hour_to):
                                print(calendar.dayofweek, "\t", calendar.name,
                                      "\t", calendar.hour_from, " - ", calendar.hour_to)

                                res_users_id = self.get_res_users_id(
                                    employee_id, resource_resource)

                                # Check if employee is available on the day and time selected (check if it has another event on the calendar)
                                if self.is_available(res_users_id, selectedDate, selectedTime, meetingDuration):
                                    return employee_id
        return -1  # No employee available

    def is_available(self, res_users_id, date_selected, time_selected, meetingDuration):
        # Get all the calendar events of the employee in the date selected by the user
        today = datetime.datetime.today().date()
        calendar_event = http.request.env['calendar.event'].search([
            ['start_date', '=', date_selected],
            ['user_id', '=', res_users_id]
        ])

        start_time_selected_decimal = time_selected
        end_time_selected_decimal = start_time_selected_decimal + \
            float(meetingDuration)/60
        print('\n\n', 'Time selected by user:',
              start_time_selected_decimal, ' - ', end_time_selected_decimal)

        # Check if the employee is available in the date and time selected by user
        for event in calendar_event:
            event_start_time_decimal = self.local_time_decimal(event.start)
            event_end_time_decimal = self.local_time_decimal(event.stop)
            # print(event.start.date(), ' | ', self.local_time_decimal(event.start), ' - ', self.local_time_decimal(event.stop))
            print(event.start.date(), ' | ', event_start_time_decimal,
                  ' - ', event_end_time_decimal)
            print(event.partner_id.name, '\n')
            if (start_time_selected_decimal > event_end_time_decimal or end_time_selected_decimal < event_start_time_decimal):
                continue # Need to check all events
            else:
                return False # Employee not available
        return True

    def get_partner_id(self, assigned_employee_id, resource_resource):
        for res in resource_resource:
            if assigned_employee_id == res.id:
                return res.user_id.partner_id.id

    def get_res_users_id(self, assigned_employee_id, resource_resource):
        for res in resource_resource:
            if assigned_employee_id == res.id:
                return res.user_id.id
    
    def get_employee_name(self, employee_id, resource_resource):
        for res in resource_resource:
            if (employee_id == res.id):  # Get employee
                return res.name

    def get_employee_email(self, employee_id, resource_resource):
        for res in resource_resource:
            if (employee_id == res.id):  # Get employee
                return res.email

    def local_time_decimal(self, timestamp):
        # Odoo stores date in UTC format, so it is neccessary to convert it into local format
        user_tz = http.request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)

        # Timestamp on local format (string)
        local_timestamp_str = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(
            str(timestamp), '%Y-%m-%d %H:%M:%S')).astimezone(local), '%Y-%m-%d %H:%M:%S')

        # Timestamp object
        local_timestamp_obj = datetime.datetime.strptime(
            local_timestamp_str, '%Y-%m-%d %H:%M:%S')

        # Local time
        local_time_decimal = self.time_to_decimal(
            str(local_timestamp_obj.time()))

        return local_time_decimal

    def time_to_utc(self, timestamp):
        # Odoo stores date in UTC format, so it is neccessary to convert it into UTC before saving to database
        local_timestamp = datetime.datetime.strptime(
            timestamp, "%Y-%m-%d %H:%M:%S")
        utc_timestamp = local_timestamp - \
            datetime.timedelta(hours=2)  # Current timezone is +2:00

        return utc_timestamp

    def get_google_calendar_service(self):
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

    def create_google_calendar_event(self, event_name, meetingDescription, start_date_time, end_date_time, attendeeEmail, employeeEmail, meetingLocation, meetingAddress):

        service = self.get_google_calendar_service()

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

    @http.route('/odoo-meetings/event/<model("odoo_meetings.meeting_event"):obj>/', auth='public', website=True)
    def update_meeting_event_index(self, obj, **kw):
        action = kw.get('action')
        if action == 'update': # Delete/Update calendar event
            return self.delete_meeting_event(obj)
        else:  # Show update meeting screen    
            return self.show_update_meeting_event_screen(obj)

    def show_update_meeting_event_screen(self, meetingEvent):
        return http.request.render('odoo_meetings.update_delete_event', {
            'event_id': meetingEvent.id,
            'assistant_name': meetingEvent.assistant_name,
            'employee_name': meetingEvent.employee.name,
            'meeting_type_name': meetingEvent.meeting_type.name,
            'date': meetingEvent.date,
            'hour': meetingEvent.hour,
            'address': meetingEvent.meeting_type.address
        })
    

    def delete_meeting_event(self, meetingEvent):
        # Remove google calendar event
        service = self.get_google_calendar_service()
        service.events().delete(calendarId='primary', eventId=meetingEvent.google_calendar_event_id, sendUpdates="all").execute()
        
        # Decrease in 1 the number of meetings of the meeting type
        odoo_meetings_meeting_type = http.request.env['odoo_meetings.meeting_type'].search([
            ['id', '=', meetingEvent.meeting_type.id]
        ])
        odoo_meetings_meeting_type.write({ 'num_meetings': odoo_meetings_meeting_type.num_meetings - 1 })
        
        meeting_event = http.request.env['odoo_meetings.meeting_event'].search([
            ['id', '=', meetingEvent.id]
        ])
        # Remove event from meeting_event & calendar_event tables
        meeting_event.calendar_event.unlink()
        meeting_event.unlink()

        
        
        return http.request.render('odoo_meetings.delete_event_success')