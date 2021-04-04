# -*- coding: utf-8 -*-
from odoo import http

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
        MeetingTypes = http.request.env['odoo_meetings.meeting_type']
        return http.request.render('odoo_meetings.index', {
            'meetingTypes': MeetingTypes.search([]),
        })

    @http.route('/odoo-meetings/<model("odoo_meetings.meeting_type"):obj>/', auth='public', website=True)
    def form_submittt(self, **kw):
        # print(obj.get('name'))
        # print(kw.get('meetingTypeSelect'))
        # # employee_ids = [20]
        # meeting = http.request.env['odoo_meetings.meeting_event'].create({
        #     'assistant_name': kw.get('name'),
        #     'assistant_email': kw.get('email'),
        #     'comments': kw.get('comments'),
        #     'date': kw.get('date'),
        #     'hour': kw.get('hour'),
        #     # 'state': 'TODO: add state',
        #     # 'meeting_type': 'TODO: add meeting type',
        #     # 'employee': [(6, 0, employee_ids)]
        # })
        return http.request.render('odoo_meetings.select_time', {})


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
