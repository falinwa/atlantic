from odoo import fields, models, api
import datetime

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    customer_ref = fields.Char()

    @api.model
    def create(self, vals):
        if vals['origin']:
            origin_id = self.env['sale.order'].search([("name", "=", vals['origin'])])
            vals['customer_ref'] = origin_id.customer_reference
            vals['user_id'] = origin_id.user_id.id
            vals['dest_address_id'] = origin_id.partner_shipping_id.id
        return super(PurchaseOrderInherit, self).create(vals)


class PurchaseLineInherit(models.Model):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    delivery_date = fields.Date()

    @api.model
    def create(self, vals_list):
        result = super(PurchaseLineInherit, self).create(vals_list)
        customer_lead = datetime.timedelta(result.sale_line_id.product_id.sale_delay)
        result.delivery_date = result.sale_line_id.delivery_date - customer_lead

        return result
