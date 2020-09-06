{
    'name': "Atlantic",
    'version': '0.0.1',
    'depends': ['base', 'sale'],
    'author': "Ruben Hias",
    'category': 'Category',
    'description': """
    Atlantic main module
    """,
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/activity_types.xml',
        'data/sequences.xml',
        'views/DSSaleOrder.xml',
        'views/templates.xml',
        'views/reports.xml',
        'views/activity_type_form.xml',
        'views/purchase.xml'
    ],

}
