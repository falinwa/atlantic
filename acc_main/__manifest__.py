{
    'name': "Atlantic",
    'version': '0.0.1',
    'depends': ['base', 'sales'],
    'author': "Ruben Hias",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'data/hs_prices.xlsx',
        'views/DSSaleOrder.xml'
    ],
    'depends':["base", "sale"],

}
