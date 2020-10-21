from odoo import fields, models, api
import datetime


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    customer_ref = fields.Char()
    delivery_date = fields.Date(compute="_po_delivery_date")
    supp_order_conf = fields.Boolean("Supplier Order Confirmed")
    sale_order_ref = fields.Many2one("sale.order")
    dest_address_id = fields.Many2one("res.partner", related="sale_order_ref.partner_shipping_id")
    dest_internal_address_id = fields.Many2one("res.partner")

    @api.model
    def create(self, vals):
        if vals['origin']:
            origin_id = self.env['sale.order'].search([("name", "=", vals['origin'])])
            vals["sale_order_ref"] = origin_id.id
            vals['customer_ref'] = origin_id.customer_reference
            vals['user_id'] = origin_id.user_id.id
            vals['dest_address_id'] = origin_id.partner_shipping_id.id
        sofie_id = self.env['res.users'].search([('name', '=', 'Sofie Yserbyt')])
        vals['user_id'] = sofie_id.id
        return super(PurchaseOrderInherit, self).create(vals)

    @api.depends('order_line.delivery_date')
    def _po_delivery_date(self):
        for order in self:
            min_date = None
            for line in order.order_line:
                if line.delivery_date and (min_date is None or line.delivery_date < min_date):
                    min_date = line.delivery_date
            order.delivery_date = min_date


class PurchaseLineInherit(models.Model):
    _inherit = "purchase.order.line"

    delivery_date = fields.Date(compute='_set_delivery_date_po', inverse='_set_delivery_date_so')

    @api.model
    def create(self, vals_list):
        result = super(PurchaseLineInherit, self).create(vals_list)
        customer_lead = datetime.timedelta(result.sale_line_id.product_id.sale_delay)
        if result.sale_line_id.delivery_date:
            result.delivery_date = result.sale_line_id.delivery_date - customer_lead

        return result

    @api.depends('sale_line_id.delivery_date')
    def _set_delivery_date_po(self):
        for rec in self:
            customer_lead = datetime.timedelta(rec.sale_line_id.product_id.sale_delay)
            if rec.sale_line_id.delivery_date:
                rec.delivery_date = rec.sale_line_id.delivery_date - customer_lead
            else:
                rec.delivery_date = datetime.date.today()


    def _set_delivery_date_so(self):
        for rec in self:
            customer_lead = datetime.timedelta(rec.sale_line_id.product_id.sale_delay)
            if not rec.delivery_date or customer_lead:
                rec.sale_line_id.delivery_date = datetime.date.today() + datetime.timedelta(days=365)
            else:
                rec.sale_line_id.delivery_date = rec.delivery_date + customer_lead

