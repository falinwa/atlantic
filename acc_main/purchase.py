from odoo import fields, models, api



class PurchaseInherit(models.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    delivery_date = fields.Date()

    @api.model
    def create(self, vals_list):
        result = super(PurchaseInherit, self).create(vals_list)
        result.delivery_date = self.sale_line_id.delivery_date
