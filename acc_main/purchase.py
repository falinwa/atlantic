from odoo import fields, models



class PurchaseInherit(models.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    delivery_date = fields.Date()

    def create(self, vals_list):
        result = super(PurchaseInherit, self).create(vals_list)
        result.delivery_date = result.sale_line_id.delivery_date
