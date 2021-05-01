from odoo import http
import sys
import pandas
import datetime
import pytz

def get_resource_resource(odoo_meetings_meeting_type):
    # List of employees from the hr.employee table that are assigned to the meeting type selected by user
    meeting_type_employees = odoo_meetings_meeting_type.employees.sorted(
        key='id', reverse=False)

    # List of the ids of the employees
    meeting_type_employees_id_list = []
    for employee in meeting_type_employees:
        meeting_type_employees_id_list.append(employee.id)

    # Get the info of the resource table of the employees above
    resource_resource = http.request.env['resource.resource'].sudo().search([
        ['id', 'in', meeting_type_employees_id_list]
    ])

    return resource_resource

def get_resource_calendar_attendance_sorted(resource_resource):
    # List of ids from the resource_calendar table
    resource_calendar_attendance_id_list = []
    for res in resource_resource:
        resource_calendar_attendance_id_list.append(res.calendar_id.id)

    # Type of working hours from the resource_calendar_attendance table
    resource_calendar_attendance = http.request.env['resource.calendar.attendance'].sudo().search([
        ['calendar_id', 'in', resource_calendar_attendance_id_list]
    ])

    # Sort by id
    resource_calendar_attendance_sorted = resource_calendar_attendance.sorted(
        key='id', reverse=False)

    return resource_calendar_attendance_sorted

def get_availability(resource_resource, resource_calendar_attendance_sorted, meetingDuration):
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
    # with open('getAvailability().txt', 'w') as f:
        # Change the standard output to the file we created.
        # sys.stdout = f
        # for res in resource_resource:
        #     # Employee name + type of working hours name
        #     print(res.name, "\t", res.calendar_id.name)
        #     # Print hours of each type
        #     for calendar in resource_calendar_attendance_sorted:
        #         if (calendar.calendar_id.id == res.calendar_id.id):
        #             print(calendar.name, "\t", calendar.hour_from,
        #                   " - ", calendar.hour_to)
        # print("\n", "\n")
        
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
    df = pandas.DataFrame(myDict)

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
                    hours_per_day.append(get_hours(
                        availability[i], availability[i+1], meetingDuration))
            else:
                # Save to the corresponding day
                temp += 4
                availabilityDict[day] = hours_per_day
                break

    print("\n\nAVAILABILITY DICTIONARY:\n", availabilityDict)
    # for a in availabilityDict:
    #     for b in a[b]
    #     print("\n\n", b)

    # sys.stdout = original_stdout  # Reset the standard output to its original value
    return availabilityDict

def get_hours(min_value, max_value, duration):
    original_stdout = sys.stdout
    hours = []
    value = min_value
    # with open('getHours().txt', 'w') as f:
        # Change the standard output to the file we created.
        # sys.stdout = f
    while value <= max_value:
        hours.append(decimal_to_time(value))
        value += (duration / 60)
    print(hours)
        # sys.stdout = original_stdout
    return hours

def get_first_available_employee(employee_attendance_order, resource_resource, resource_calendar_attendance_sorted, selectedDate, selectedDay, selectedTime, meetingDuration):
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

                            res_users_id = get_res_users_id(
                                employee_id, resource_resource)

                            # Check if employee is available on the day and time selected (check if it has another event on the calendar)
                            if is_available(res_users_id, selectedDate, selectedTime, meetingDuration):
                                return employee_id
    return -1  # No employee available

def is_available(res_users_id, date_selected, time_selected, meetingDuration):
    # Get all the calendar events of the employee in the date selected by the user
    today = datetime.datetime.today().date()
    calendar_event = http.request.env['calendar.event'].sudo().search([
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
        event_start_time_decimal = local_time_decimal(event.start)
        event_end_time_decimal = local_time_decimal(event.stop)
        # print(event.start.date(), ' | ', local_time_decimal(event.start), ' - ', local_time_decimal(event.stop))
        print(event.start.date(), ' | ', event_start_time_decimal,
              ' - ', event_end_time_decimal)
        print(event.partner_id.name, '\n')
        if (start_time_selected_decimal > event_end_time_decimal or end_time_selected_decimal < event_start_time_decimal):
            continue # Need to check all events
        else:
            return False # Employee not available
    return True

def get_partner_id(assigned_employee_id, resource_resource):
    for res in resource_resource:
        if assigned_employee_id == res.id:
            return res.user_id.partner_id.id

def get_res_users_id(assigned_employee_id, resource_resource):
    for res in resource_resource:
        if assigned_employee_id == res.id:
            return res.user_id.id

def get_employee_name(employee_id, resource_resource):
    for res in resource_resource:
        if (employee_id == res.id):  # Get employee
            return res.name

def get_employee_email(employee_id, resource_resource):
    for res in resource_resource:
        if (employee_id == res.id):  # Get employee
            return res.email

def local_time_decimal(timestamp):
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
    local_time_decimal = time_to_decimal(
        str(local_timestamp_obj.time()))

    return local_time_decimal

def time_to_utc(timestamp):
    # Odoo stores date in UTC format, so it is neccessary to convert it into UTC before saving to database
    local_timestamp = datetime.datetime.strptime(
        timestamp, "%Y-%m-%d %H:%M:%S")
    utc_timestamp = local_timestamp - \
        datetime.timedelta(hours=2)  # Current timezone is +2:00

    return utc_timestamp

def decimal_to_time(decimal):
    hours = int(decimal)
    minutes = int((decimal*60) % 60)
    return str(hours).zfill(2) + ':' + str(minutes).zfill(2)

def time_to_decimal(time):
    if len(time) < 6:  # Time without seconds
        (h, m) = time.split(':')
    else:  # Time with seconds
        (h, m, s) = time.split(':')
    return int(h) + int(m) / 60