{
    "name": "Serial Number Followup",
    "version": "0.0.2",
    "depends": ["base", "stock", "sale", "sale_stock"],
    "author": "Ruben Hias",
    "category": "Category",
    "description": """
        Module to track the lifespan of a sold product.
        Adds to possibility to add log entries in the serial number form and from the Sale Order view.
    """,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/log_wizard.xml",
        "views/stock_production.xml",
        "views/log_entry_views.xml",
        "views/sale_order_views.xml",
    ],
}
