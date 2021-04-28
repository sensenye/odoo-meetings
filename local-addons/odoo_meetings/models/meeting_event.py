# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MeetingEvent(models.Model):
    _name = 'odoo_meetings.meeting_event'
    _description = "Meeting Event"

    assistant_name = fields.Char(string="Nombre del asistente", required=True)
    assistant_email = fields.Char(string="Email del asistente", required=True)
    comments = fields.Text(string="Comentarios", required=True)
    date = fields.Date(string="Fecha", required=True)
    hour = fields.Char(string="Hora", required=True)
    meeting_type = fields.Many2many('odoo_meetings.meeting_type', string="Tipo de reunión", relation="odoo_meetings_meeting_event_meeting_type_rel")
    employee = fields.Many2many('hr.employee.public', string="Empleado", relation="odoo_meetings_meeting_event_employee_rel")
    calendar_event = fields.Many2many('calendar.event', string="Evento de calendario", relation="odoo_meetings_meeting_event_calendar_event_rel")
    google_calendar_event_id = fields.Char()