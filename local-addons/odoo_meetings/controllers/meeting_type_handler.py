from odoo import http
import sys
import datetime

from . import user_handler

def meeting_type_index():
    # meetingTypes = http.request.env['odoo_meetings.meeting_type']
    meetingTypes = get_all_meeting_type()
    return http.request.render('odoo_meetings.index', {
        'meetingTypes': meetingTypes.search([]),
    })

def meeting_type_details_index(obj):

    # Id of the meeting type selected by user
    meetingTypeId = obj.id

    # Duration of each meeting within the meeting type
    meetingDuration = obj.duration

    # Get meeting type data from database
    odoo_meetings_meeting_type = get_meeting_type(meetingTypeId)

    # Get the information of the employees assigned to the meeting type from database
    resource_resource = user_handler.get_resource_resource(odoo_meetings_meeting_type)

    # Get information about the type of working hours of the employees from the resource_calendar_attendance table
    resource_calendar_attendance_sorted = user_handler.get_resource_calendar_attendance_sorted(resource_resource)

    availability = user_handler.get_availability(resource_resource, resource_calendar_attendance_sorted, meetingDuration)

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

def get_meeting_type(meetingTypeId):
    return http.request.env['odoo_meetings.meeting_type'].search([
        ['id', '=', meetingTypeId]
    ])

def get_all_meeting_type():
    return http.request.env['odoo_meetings.meeting_type'].search([])