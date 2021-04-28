# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MeetingType(models.Model):
    _name = "odoo_meetings.meeting_type"
    _description = "Meeting Type"

    name = fields.Char(string="Tipo de reunión *", required=True)
    location = fields.Selection([
        ('physical', 'Físico'),
        ('google_meet', 'Google Meet'),
    ], default='google_meet', required=True, string="Localización *")
    address = fields.Char(
        string="Dirección", help="Es la ubicación que se le mostrará al usuario. Puedes poner Google Meet, videoconferencia, una dirección física...", required=True)
    description = fields.Char(string="Descripción *", required=True)
    employees = fields.Many2many(
        'hr.employee.public', string="Empleado", relation="odoo_meetings_meeting_type_employee_rel")
    duration = fields.Integer(string="Duración *", required=True, default=30)
    url = fields.Char()
    start_date = fields.Date(string='Fecha de inicio *',
                             default=fields.Date.today())
    end_date = fields.Date(string='Fecha de fin *',
                           default=fields.Date.today())
    last_employee = fields.Integer(default=0, invisible=True)
    num_meetings = fields.Integer()

    def get_description(self):
        return self.description

    def open_calendar(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "views": [[False, "calendar"]],
        }

    @api.onchange('end_date', 'start_date')
    def _onchange_date(self):
        if self.start_date > self.end_date:
            self.start_date = fields.Date.today()
            self.end_date = fields.Date.today()
            return {
                'warning': {'title': "Warning", 'message': "La fecha de inicio tiene que ser menor que la fecha de fin", 'type': 'notification'},
            }
