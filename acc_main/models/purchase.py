from odoo import fields, models, api


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    customer_ref = fields.Char()

    @api.model
    def create(self, vals):
        if vals['origin']:
            origin_id = self.env['sale.order'].search([("name", "=", vals['origin'])])
            vals['customer_ref'] = origin_id.customer_reference
        return super(PurchaseOrderInherit, self).create(vals)




class PurchaseLineInherit(models.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    delivery_date = fields.Date()

    @api.model
    def create(self, vals_list):
        result = super(PurchaseLineInherit, self).create(vals_list)
        result.delivery_date = result.sale_line_id.delivery_date
        return result
