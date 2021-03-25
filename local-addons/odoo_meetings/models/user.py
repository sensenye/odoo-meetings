# -*- coding: utf-8 -*-

from odoo import models, fields, api

class User(models.Model):
    _name = 'odoo_meetings.user'
    _description = "User"

    name = fields.Char(string="Nombre", required=True)
    email = fields.Char(string="Email", required=True)
    password = fields.Char(string="Contraseña", required=True)
    availability = fields.Char(string="Disponibilidad", required=True)
    rol = fields.Char(string="Rol", required=True)
    

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
