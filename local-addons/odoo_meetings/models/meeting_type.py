# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MeetingType(models.Model):
    _name = "odoo_meetings.meeting_type"
    _description = "Meeting Type"

    # LOCALIZATION_STATES = [
    #     ('physical', 'Físico'),
    #     ('google_meet', 'Google Meet'),
    # ]

    name = fields.Char(string="Tipo de reunión *", required=True)
    location = fields.Selection([
        ('physical', 'Físico'),
        ('google_meet', 'Google Meet'),
    ], default='google_meet', required=True, string="Localización *")
    address = fields.Char(string="Dirección", help="Es la ubicación que se le mostrará al usuario. Puedes poner Google Meet, videoconferencia, una dirección física...", required=True)
    description = fields.Char(string="Descripción *", required=True)
    employees = fields.Many2many('hr.employee.public', string="Empleado", relation="odoo_meetings_meeting_type_employee_rel")
    # date_range = fields.Char(string="Rango", required=True)
    # date_range = fields.Selection([
    #     ('next_days', 'Dentro de los próximos'),
    #     ('range', 'Dentro de un rango de fechas'),
    #     ('infinite', 'De manera indefinida'),
    # ], default='google_meet', required=True)
    duration = fields.Integer(string="Duración *", required=True, default=30)
    daily_limit = fields.Integer(string="Límite diario *", required=True)
    url = fields.Char()

    start_date = fields.Date(string='Fecha de inicio *', default=fields.Date.today())
    end_date = fields.Date(string='Fecha de fin *', default=fields.Date.today())

    last_employee = fields.Integer(default=0, invisible=True)

    # localization_options = fields.Selection([
    #     ('normal', 'In Progress'),
    #     ('done', 'Ready for next stage'),
    #     ('blocked', 'Blocked')], string='State')

    def get_description(self):
        return self.description

    def open_calendar(self):
        print("Hola")
        return {
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "views": [[False, "calendar"]],
            # "search_view_id": ["view_calendar_event_search_external","view_calendar_event_search_external"]
            # "domain": [["active", "=", 1]],
        }


# class odoo_meetings(models.Model):
#     _name = "odoo_meetings.odoo_meetings"
#     _description = "odoo_meetings.odoo_meetings"

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends("value")
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

    # @api.constrains('field_name')
    #  def field_name_constratints(self):
        # if condition:
        # raise Warning(message)

    # @api.constrains('start_date','end_date')
    # def _check_end_date(self):
        # for record in self:
        # if self.start_date > self.end_date:
            # print('asdfasdfasdf')
            # raise ValidationError("La fecha de fin tiene que ser mayor que la fecha de inicio")

    @api.onchange('end_date','start_date')
    def _onchange_date(self):
        if self.start_date > self.end_date:
            self.start_date = fields.Date.today()
            self.end_date = fields.Date.today()
            return {
            'warning': {'title': "Warning", 'message': "La fecha de inicio tiene que ser menor que la fecha de fin", 'type': 'notification'},
            }

    # @api.onchange('start_date', 'end_date')
    # def cheking_field_date(self):
    #     if self.start_date and self.end_date:
    #         if self.start_date > self.end_date:
    #             print('asdfasdfasdf')
    #             print(self.end_date)
    #             self.end_date = fields.Date.today()
    #             print(self.end_date)
    #             raise ValidationError('The Deadline Date is Invalid')


    # @api.onchange('end_date', 'start_date')
    # def date_constrains(self):
    #     for rec in self:
    #         if rec.end_date < rec.start_date:
    #             rec.end_date = fields.Date.today()
    #             raise ValidationError(  'Sorry, End Date Must be greater Than Start Date...')

    # pname = fields.Char(compute='_compute_pname')

    # @api.depends('partner_id.start_date', 'partner_id.end_date')
    # def _compute_pname(self):
    #     for record in self:
    #         if record.partner_id.start_date > record.partner_id.start_date:
    #             record.pname = (record.partner_id.name or "").upper()
    #         else:
    #             record.pname = record.partner_id.name