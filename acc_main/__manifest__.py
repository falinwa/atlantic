{
    'name': "Atlantic",
    'version': '0.0.2',
    'depends': ['base', 'sale', 'purchase', 'account', 'stock', 'contacts', 'sale_purchase'],
    'author': "Ruben Hias",
    'category': 'Category',
    'description': """
    Atlantic Compressors and Atlantic Cool Components main module
    """,
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/activity_types.xml',
        'data/sequences.xml',
        'wizards/ocr_fix.xml',
        'views/DSSaleOrder.xml',
        'views/templates.xml',
        'views/reports.xml',
        'views/activity_type_form.xml',
        'views/purchase.xml',
        'views/lost_reason.xml'
    ],

}
