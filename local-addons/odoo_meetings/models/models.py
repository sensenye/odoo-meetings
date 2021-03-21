# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Meetings(models.Model):
    _name = 'odoo_meetings.meeting'
    _description = "Reunion"

    name = fields.Char(string="Title", required=True)
    value = fields.Text()

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
