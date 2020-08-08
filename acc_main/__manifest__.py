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
        'security/ir.model.access.csv',
        'data/activity_types.xml',
        'views/DSSaleOrder.xml',
        'views/sequences.xml',
        'views/templates.xml',
        'views/reports.xml',
        'views/activity_type_form.xml'
    ],

}
