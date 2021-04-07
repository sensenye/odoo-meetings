# -*- coding: utf-8 -*-
from odoo import http
import sys
import json
import pandas as pd

# https://odoo-development.readthedocs.io/en/latest/dev/frontend/webpage.html
# https://kanakinfosystems.com/blog/create-form-in-odoo-website


class OdooMeetings(http.Controller):
    # @http.route('/odoo-meetings/<model("odoo_meetings.meeting_type"):meeting_types>', auth='public', website=True)
    # def index(self, **kw):
    #     # MeetingTypes = http.request.env['odoo_meetings.meeting_type']
    #     return http.request.render('odoo_meetings.index', {
    #         'meetingTypes': meeting_types,
    #     })

    @http.route('/odoo-meetings/', auth='public', website=True)
    def index(self, **kw):
        meetingTypes = http.request.env['odoo_meetings.meeting_type']
        return http.request.render('odoo_meetings.index', {
            'meetingTypes': meetingTypes.search([]),
        })

    @http.route('/odoo-meetings/<model("odoo_meetings.meeting_type"):obj>/', auth='public', website=True)
    def form_submittt(self, obj, **kw):

        original_stdout = sys.stdout # Save a reference to the original standard output
        
        # Id of the meeting type selected by user
        meetingTypeId = obj.id

        # Duration of each meeting within the meeting type
        meetingDuration = obj.duration

        # Object from db of the meeting type with the id above
        odoo_meetings_meeting_type = http.request.env['odoo_meetings.meeting_type'].search([
            ['id','=',meetingTypeId]
        ])

        # List of employees from the hr.employee table that are assigned to the meeting type selected by user
        meeting_type_employees = odoo_meetings_meeting_type.employees.sorted(key='id', reverse=False)

        # List of the ids of the employees
        meeting_type_employees_id_list = []
        for employee in meeting_type_employees:
            meeting_type_employees_id_list.append(employee.id)

        # Get the info of the resource table of the employees above
        resource_resource = http.request.env['resource.resource'].search([
            ['id','in',meeting_type_employees_id_list]
        ])

        # The employees are saved on resource_resource. The attribute calendar_id indicates the type of working hours and is related with the rsource_calendar_attendance table.
        print(resource_resource[0].calendar_id.name)

        # List of ids from the resource_calendar table
        resource_calendar_attendance_id_list = []
        for res in resource_resource:
            resource_calendar_attendance_id_list.append(res.calendar_id.id)
        
        # Type of working hours from the resource_calendar_attendance table
        resource_calendar_attendance = http.request.env['resource.calendar.attendance'].search([
            ['calendar_id','in',resource_calendar_attendance_id_list]
        ])

        resource_calendar_attendance_sorted = resource_calendar_attendance.sorted(key='id', reverse=False)

        print('\n\n')
        # Rows from the resource_calendar_attendance table. Contains info about the type of working hours (hours/day/week)
        print(resource_calendar_attendance_sorted[0].name)
        print('\n\n')


        availability = self.get_availability(resource_resource, resource_calendar_attendance_sorted, meetingDuration)

        return http.request.render('odoo_meetings.select_time', {
            'meetingType': obj,
            'employees': meeting_type_employees,
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

        # if "key1" in d
        # a if condition else b
    
    def print_to_file(self, elem):
        original_stdout = sys.stdout # Save a reference to the original standard output
        with open('filename.txt', 'w') as f:
            sys.stdout = f # Change the standard output to the file we created.
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
        res_cal_att_sorted_by_dayofweek = resource_calendar_attendance_sorted.sorted(key='name', reverse=False)

        # Print to file
        with open('filename.txt', 'w') as f:
            sys.stdout = f # Change the standard output to the file we created.
            for res in resource_resource:
                # Employee name + type of working hours name
                print(res.name,"\t",res.calendar_id.name)
                # Print hours of each type
                for calendar in resource_calendar_attendance_sorted:
                    if (calendar.calendar_id.id == res.calendar_id.id):
                        print(calendar.name,"\t",calendar.hour_from," - ",calendar.hour_to)

            print("\n","\n")
            # Get all type of working hours
            for calendar in resource_calendar_attendance_sorted:
                hour_from.append(calendar.hour_from)
                hour_to.append(calendar.hour_to)
                calendar_id.append(calendar.calendar_id.id)
                dayofweek.append(calendar.dayofweek)
                type_name.append(calendar.name)
                print(calendar.calendar_id.name,"\t",calendar.name,"\t",calendar.hour_from," - ",calendar.hour_to)

            # Create dictionary with all needed data
            myDict["calendar_id"]=calendar_id
            myDict["type_name"]=type_name
            myDict["dayofweek"]=dayofweek
            myDict["hour_from"]=hour_from
            myDict["hour_to"]=hour_to
            
            print("\n",myDict)

            # Create dataframe from Pandas library
            df = pd.DataFrame(myDict)

            print("\n",df)

            df_dayofweek = df.groupby("dayofweek")
            print("\n",df_dayofweek.first())
            print("\n",df_dayofweek.get_group('0'))

            # Get min hour from and max hour to for each type and for each day. This will be the availability of the entire team
            df_min_hour_from_by_type = df.groupby(['type_name'], sort=False).hour_from.min()
            df_max_hour_to_by_type = df.groupby(['type_name'], sort=False).hour_to.max()

            # Create list from dataframe
            list_min_hour_from_by_type = df_min_hour_from_by_type.values.tolist()
            list_max_hour_to_by_type = df_max_hour_to_by_type.values.tolist()

            print("\ndf_min_hour_from_by_type \n",df_min_hour_from_by_type)
            print("\nlist_min_hour_from_by_type \n",list_min_hour_from_by_type)
            print("\ndf_max_hour_to_by_type \n",df_max_hour_to_by_type)
            print("\nlist_max_hour_to_by_type \n",list_max_hour_to_by_type)

            # Add min hour from and max hour to to the list
            for min_value, max_value in zip(list_min_hour_from_by_type, list_max_hour_to_by_type):
                availability.append(min_value)
                availability.append(max_value)

            print("\n\nAVAILABILITY:\n", availability)    

            print("\n\nDAYS:\n", myDict["dayofweek"])  

            # Get unique values of dayofweek
            unique_dayofweek = df.groupby("dayofweek").dayofweek.min().values.tolist()
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
                            hours_per_day.append(self.get_hours(availability[i], availability[i+1], meetingDuration))
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
            

        sys.stdout = original_stdout # Reset the standard output to its original value
        return availabilityDict


    def get_hours(self, min_value, max_value, duration):
        original_stdout = sys.stdout
        hours = []
        value = min_value
        with open('filename2.txt', 'w') as f:
            sys.stdout = f # Change the standard output to the file we created.
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

    @http.route('/odoo-meetings/meeting-type/submit/', auth='public', website=True)
    def form_submit(self, **kw):
        print('Hola')
        print(kw.get('meetingTypeSelect'))
        # employee_ids = [20]
        meeting = http.request.env['odoo_meetings.meeting_event'].create({
            'assistant_name': kw.get('name'),
            'assistant_email': kw.get('email'),
            'comments': kw.get('comments'),
            'date': kw.get('date'),
            'hour': kw.get('hour'),
            # 'state': 'TODO: add state',
            # 'meeting_type': 'TODO: add meeting type',
            # 'employee': [(6, 0, employee_ids)]
        })
        return http.request.render('odoo_meetings.form_success', {})

        # @http.route('/odoo-meetings/', authhttp.request.render('newpage.index')
    # def index(self, **kw):
        # return "Hello, world"

    # @http.route('/odoo_meetings/odoo_meetings/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('odoo_meetings.listing', {
    #         'root': '/odoo_meetings/odoo_meetings',
    #         'objects': http.request.env['odoo_meetings.odoo_meetings'].search([]),
    #     })

    # @http.route('/odoo_meetings/odoo_meetings/objects/<model("odoo_meetings.odoo_meetings"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('odoo_meetings.object', {
    #         'object': obj
    #     })
