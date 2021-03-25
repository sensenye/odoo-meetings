# -*- coding: utf-8 -*-
{
    'name': "Odoo Meetings",

    'summary': """
        Manage meetings""",

    'description': """
        The module will let companies manage more efficiently the meetings with the customers
    """,

    'author': "Sensen Ye",
    'website': "http://www.odoomeetings.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity/Calendar',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','calendar'],

    # will appear on App menu
    'application': True,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
        'views/meetings.xml',
    ],
    'css': [
        'static/src/css/style.css'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]
}
