from odoo import http
import sys
import json
import pandas as pd
import datetime
from datetime import timedelta
import locale
import pytz

from . import meeting_type_handler
from . import user_handler
from . import google_calendar_handler

def meeting_event_submit(kw):

    meetingTypeId = kw.get('meetingTypeId')
    meetingDescription = kw.get('meetingDescription')
    meetingDuration = kw.get('meetingDuration')
    meetingLocation = kw.get('meetingLocation')
    meetingAddress = kw.get('meetingAddress')
    selectedDate = kw.get('date')
    attendeeEmail = kw.get('email')

    selectedTime = user_handler.time_to_decimal(kw.get('time-select'))
    # locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
    selectedDay = datetime.datetime.strptime(
        selectedDate, "%Y-%m-%d").weekday()

    # Get meeting type data from database
    odoo_meetings_meeting_type = meeting_type_handler.get_meeting_type(meetingTypeId)

    # Get the ID of the last employee who attended the meeting
    last_employee = odoo_meetings_meeting_type.last_employee

    # Get the information of the employees assigned to the meeting type from database
    resource_resource = user_handler.get_resource_resource(
        odoo_meetings_meeting_type)

    # Get information about the type of working hours of the employees from the resource_calendar_attendance table
    resource_calendar_attendance_sorted = user_handler.get_resource_calendar_attendance_sorted(
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
    with open('meeting_event_handler.txt', 'w') as f:
        # Change the standard output to the file we created.
        sys.stdout = f
        print('\n', employee_attendance_order)
        print('\n', selectedTime)
        print('\n', selectedDay)

        # Get the ID of the first employee available
        assigned_employee_id = user_handler.get_first_available_employee(
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
        res_users_id = user_handler.get_res_users_id(
            assigned_employee_id, resource_resource)
        print('\n\n\n res_users_id: \n', res_users_id)

        # A partner is a employee registered on the website (it has an account and password to access back office).
        partner_id = user_handler.get_partner_id(
            assigned_employee_id, resource_resource)
        print('\n\n\n partner_id: \n', partner_id)

        # Get date time with the format '%Y-%m-%d %H:%M:%S'
        start_time = kw.get('time-select') + ':00'
        start_date_time_str = kw.get('date') + ' ' + start_time
        start_date_time_obj = user_handler.time_to_utc(start_date_time_str)

        end_time = user_handler.decimal_to_time(
            selectedTime + float(meetingDuration)/60) + ':00'
        end_date_time_str = kw.get('date') + ' ' + end_time
        end_date_time_obj = user_handler.time_to_utc(end_date_time_str)

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
        client_event_name = 'Reunión con ' + user_handler.get_employee_name(assigned_employee_id, resource_resource)

        start_date_time_with_tz = start_date_time_obj.replace(tzinfo=pytz.utc)
        end_date_time_with_tz = end_date_time_obj.replace(tzinfo=pytz.utc)
        # Google calendar date time uses RFC 3339 format
        start_date_time_with_tz_iso = start_date_time_with_tz.isoformat()
        end_date_time_with_tz_iso = end_date_time_with_tz.isoformat()

        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        delete_event_url = base_url + '/odoo-meetings/event/' + str(meeting.id)
        google_calendar_event_description = meetingDescription + '\n\nSi quieres cancelar/modificar la reunión, haz clic en el siguiente enlace: ' + delete_event_url
        # print(google_calendar_event_description)
        
        # Create Google Calendar event
        google_calendar_event = google_calendar_handler.create_google_calendar_event(client_event_name, google_calendar_event_description, start_date_time_with_tz_iso, end_date_time_with_tz_iso, attendeeEmail, employee_email, meetingLocation, meetingAddress)

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
        calendar_event = http.request.env['calendar.event'].sudo().create({
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
        odoo_meetings_meeting_type.sudo().write({ 'num_meetings': odoo_meetings_meeting_type.num_meetings + 1 })     

    return http.request.render('odoo_meetings.form_success', {})

def update_meeting_event_index(action, obj):
    
    if action == 'update': # Delete/Update calendar event
        return delete_meeting_event(obj)
    else:  # Show update meeting screen    
        return show_update_meeting_event_screen(obj)

def show_update_meeting_event_screen(meetingEvent):
    return http.request.render('odoo_meetings.update_delete_event', {
        'event_id': meetingEvent.id,
        'assistant_name': meetingEvent.assistant_name,
        'employee_name': meetingEvent.employee.name,
        'meeting_type_name': meetingEvent.meeting_type.name,
        'date': meetingEvent.date,
        'hour': meetingEvent.hour,
        'address': meetingEvent.meeting_type.address
    })


def delete_meeting_event(meetingEvent):
    # Remove google calendar event
    google_calendar_handler.delete_google_calendar_event(meetingEvent.google_calendar_event_id)
    
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