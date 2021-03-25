# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MeetingType(models.Model):
    _name = "odoo_meetings.meeting_type"
    _description = "Meeting Type"

    name = fields.Char(string="Tipo de reunión", required=True)
    localization = fields.Char(string="Localización", required=True)
    description = fields.Char(string="Descripción", required=True)
    # employees =
    date_range = fields.Char(string="Rango", required=True)
    duration = fields.Integer(string="Duración", required=True)
    daily_limit = fields.Integer(string="Límite diario", required=True)
    url = fields.Char(string="URL", required=True)
    # localization_options = fields.Selection([
    #     ('normal', 'In Progress'),
    #     ('done', 'Ready for next stage'), 
    #     ('blocked', 'Blocked')], string='State')

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
