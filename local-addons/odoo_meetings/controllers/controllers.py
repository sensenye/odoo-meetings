# -*- coding: utf-8 -*-
from odoo import http
import sys
import json
import pandas as pd
import datetime
import locale

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
        resource_resource = self.get_resource_resource(odoo_meetings_meeting_type)

        # Get information about the type of working hours of the employees from the resource_calendar_attendance table
        resource_calendar_attendance_sorted = self.get_resource_calendar_attendance_sorted(resource_resource)

        availability = self.get_availability(
            resource_resource, resource_calendar_attendance_sorted, meetingDuration)

        return http.request.render('odoo_meetings.select_time', {
            'meetingType': obj,
            # 'employees': meeting_type_employees,
            'meetingTypeId': meetingTypeId,
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
        selectedTime = self.time_to_decimal(kw.get('time-select'))
        # locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        selectedDay = datetime.datetime.strptime(kw.get('date'), "%Y-%m-%d").weekday()

        # Get meeting type data from database
        odoo_meetings_meeting_type = self.get_meeting_type(meetingTypeId)

        # Get the ID of the last employee who attended the meeting
        last_employee = odoo_meetings_meeting_type.last_employee

        # Get the information of the employees assigned to the meeting type from database
        resource_resource = self.get_resource_resource(odoo_meetings_meeting_type)

        # Get information about the type of working hours of the employees from the resource_calendar_attendance table
        resource_calendar_attendance_sorted = self.get_resource_calendar_attendance_sorted(resource_resource)

        employee_attendance_order = []
        employee_attendance_recent = []
        # Get a list of employee ID by attendance order. The first ID will be the first employee assigned to the meeting if he is available. If not, the next one and so on. The ID of the first employee that can be assigned must be greater than the ID of the last employee (last_employee) in order to have a more equitative distribution. This way, the ID of the last employee will be at the end of the list, being the last one that can be considered.
        for res in resource_resource: # Sorted by id
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
            assigned_employee_id = self.get_first_available_employee(employee_attendance_order, resource_resource, resource_calendar_attendance_sorted, selectedDay, selectedTime)
            print('\n', '\n', 'assigned_employee_id', '\n', assigned_employee_id)

        meeting = http.request.env['odoo_meetings.meeting_event'].create({
            'assistant_name': kw.get('name'),
            'assistant_email': kw.get('email'),
            'comments': kw.get('comments'),
            'date': kw.get('date'),
            'hour': kw.get('time-select'),
            # 'state': 'TODO: add state',
            'meeting_type': [(4, kw.get('meetingTypeId'), 0)],
            'employee': [(4, assigned_employee_id, 0)]
        })

        # Save last_employee to the meeting_type table
        query = f"UPDATE odoo_meetings_meeting_type SET last_employee = {assigned_employee_id} WHERE id = {meetingTypeId}"
        # Because models use the same cursor and the Environment holds various caches, these caches must be invalidated when altering the database in raw SQL, or further uses of models may become incoherent
        http.request.env['odoo_meetings.meeting_type'].invalidate_cache()
        http.request.env.cr.execute(query)

        return http.request.render('odoo_meetings.form_success', {})

    def time_to_decimal(self, time):
        (h, m) = time.split(':')
        return int(h) + int(m) / 60
    def get_first_available_employee(self, employee_attendance_order, resource_resource, resource_calendar_attendance_sorted, selectedDay, selectedTime):
    # Get employee info according to employee_attendance_order
        for employee_id in employee_attendance_order:
            for res in resource_resource:
                if (employee_id == res.id): # Get employee
                    print('\n', res.id, '\t',res.name)
                    for calendar in resource_calendar_attendance_sorted:
                        # Get working type
                        if (calendar.calendar_id.id == res.calendar_id.id):
                            if (int(calendar.dayofweek) == int(selectedDay) and calendar.hour_from <= selectedTime <= calendar.hour_to):
                                print(calendar.dayofweek, "\t",calendar.name, "\t", calendar.hour_from," - ", calendar.hour_to)
                                return employee_id
