from odoo import fields, models, api
import datetime


class PurchaseOrderInherit(models.Model):
    """
    Extending the Purchase order model

    Extra fields
    ----
    customer_ref: Copy of the customer reference from the SO 
    delivery_date: new field for delivery date because the system from odoo is not compatible
                    with the workings of Atlantic.
    supp_order_conf: Checkbox of whether or not the supplier has confirmed the order
    sale_order_ref: Reference to preceding sale order
    dest_address_id: Also here was a problem with Odoo's dropshipping system so related it to SO
    dest_internal_address_id: Extra field for if the bill gets created without the usual business flow
                                Because normal delivery address is related to SO.
    """
    _inherit = "purchase.order"

    # TODO: Make related fields of a lot of these
    customer_ref = fields.Char()
    delivery_date = fields.Date(compute="_po_delivery_date")
    supp_order_conf = fields.Boolean("Supplier Order Confirmed")
    sale_order_ref = fields.Many2one("sale.order")
    dest_address_id = fields.Many2one("res.partner", related="sale_order_ref.partner_shipping_id")
    dest_internal_address_id = fields.Many2one("res.partner")
    po_confirmation_ref = fields.Char(string="Supplier Order Reference")

    @api.model
    def create(self, vals):
        """Copying over values from SO to PO"""
        if vals['origin']:
            origin_id = self.env['sale.order'].search([("name", "=", vals['origin'])])
            vals["sale_order_ref"] = origin_id.id
            vals['customer_ref'] = origin_id.customer_reference
        return super(PurchaseOrderInherit, self).create(vals)

    @api.depends('order_line.delivery_date')
    def _po_delivery_date(self):
        """Calculates the earliest delivery date from all the lines
         and sets it as delivery date of PO"""
        for order in self:
            min_date = None
            for line in order.order_line:
                # Fix for error with notes, because a note evidently does not have a delivery date.
                if line.display_type != 'line_note' and (min_date is None or line.delivery_date < min_date):
                    min_date = line.delivery_date
            order.delivery_date = min_date


class PurchaseLineInherit(models.Model):
    """
    Extending Purchase Order Line
    
    Extra Fields
    -----
    delivery_date: Added extra field for delivery_date per line because Odoos system doesn't work
                    REMARK: Not able to use related field because of substraction of customer lead
                            odoo doesn't support calculations inside of related fields.
    """
    _inherit = "purchase.order.line"

    delivery_date = fields.Date(compute='_set_delivery_date_po', inverse='_set_delivery_date_so')

    # TODO: Test if this can go, but should be okay because of next method
    # @api.model
    # def create(self, vals_list):
    #     """Copies the delivery dates from SO lines to the corresponding PO lines"""
    #     result = super(PurchaseLineInherit, self).create(vals_list)
    #     customer_lead = datetime.timedelta(result.sale_line_id.product_id.sale_delay)
    #     if result.sale_line_id.delivery_date:
    #         result.delivery_date = result.sale_line_id.delivery_date - customer_lead
    #     return result

    @api.depends('sale_line_id.delivery_date')
    def _set_delivery_date_po(self):
        """Copies the delivery dates from SO lines to the corresponding PO lines"""
        for rec in self:
            # Customer lead has to be subtracted as this delivery date is
            # when it departs at the vendor factory.
            customer_lead = datetime.timedelta(rec.sale_line_id.product_id.sale_delay)
            if rec.sale_line_id.delivery_date:
                rec.delivery_date = rec.sale_line_id.delivery_date - customer_lead
            else:
                rec.delivery_date = datetime.date.today()


    def _set_delivery_date_so(self):
        """Sets the corresponding delivery date on SO lines when PO line date changed"""
        for rec in self:
            customer_lead = datetime.timedelta(rec.sale_line_id.product_id.sale_delay)
            if rec.display_type == 'line_note' or not customer_lead:
                rec.sale_line_id.delivery_date = datetime.date.today() + datetime.timedelta(days=365)
            else:
                rec.sale_line_id.delivery_date = rec.delivery_date + customer_lead

