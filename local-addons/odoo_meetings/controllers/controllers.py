# -*- coding: utf-8 -*-
# from odoo import http


# class OdooMeetings(http.Controller):
#     @http.route('/odoo_meetings/odoo_meetings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_meetings/odoo_meetings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_meetings.listing', {
#             'root': '/odoo_meetings/odoo_meetings',
#             'objects': http.request.env['odoo_meetings.odoo_meetings'].search([]),
#         })

#     @http.route('/odoo_meetings/odoo_meetings/objects/<model("odoo_meetings.odoo_meetings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_meetings.object', {
#             'object': obj
#         })
