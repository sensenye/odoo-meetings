# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Meeting(models.Model):
    _name = 'odoo_meetings.meeting_event'
    _description = "Meeting Event"

    assistant_name = fields.Char(string="Nombre del asistente", required=True)
    assistant_email = fields.Char(string="Email del asistente", required=True)
    comments = fields.Text(string="Comentarios", required=True)
    date = fields.Date(string="Fecha", required=True)
    hour = fields.Char(string="Hora", required=True)
    # state = fields.Char(string="Estado", required=True)
    meeting_type = fields.Many2many('odoo_meetings.meeting_type', string="Tipo de reunión", relation="odoo_meetings_meeting_event_meeting_type_rel")
    employees = fields.Many2many('hr.employee.public', string="Empleado", relation="odoo_meetings_meeting_event_employee_rel")
    

# class odoo_meetings(models.Model):
#     _name = 'odoo_meetings.odoo_meetings'
#     _description = 'odoo_meetings.odoo_meetings'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
