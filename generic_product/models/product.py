from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_product = fields.Boolean(
        string='Stockable?',
        default=False)

    is_generic_product = fields.Boolean(string='Generic?', default=False)
    property_account_income_id = fields.Many2one(copy=True)
    property_account_expense_id = fields.Many2one(copy=True)
