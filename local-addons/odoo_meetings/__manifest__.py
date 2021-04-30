# -*- coding: utf-8 -*-
{
    'name': "Odoo Meetings",

    'summary': """
        Manage meetings""",

    'description': """
        The module will let companies manage more efficiently the meetings with the customers
    """,

    'author': "Sensen Ye",
    'website': "https://www.odoomeetings.tk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity/Calendar',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','website','calendar','hr','google_calendar'],

    # will appear on App menu
    'application': True,

    # always loaded
    'data': [
        'security/meeting_type_groups.xml',
        'security/calendar_event_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/meeting_event_templates.xml',
        'views/meeting_type_templates.xml',
        'views/meeting_type_views.xml',
    ],
    'css': [
        'static/src/css/style.css'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ]
}
