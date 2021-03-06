from odoo import fields, models, api

# TODO: Verify that this really is not applicable anymore

class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    saleorder_id = fields.Many2one('sale.order')
    purchaseorder_id = fields.Many2one('purchase.order')

    @api.model
    def create(self, vals):
        try:
            journal = self.env['account.journal'].search([('id', '=', vals['journal_id'])])
            if journal.name == 'Vendor Bills':
                vals['ref'] = ""
                vals['invoice_payment_ref'] = ""
        except KeyError:
            pass

        try:
            so = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])])
        except KeyError:
            so = None
        if so:
            vals['saleorder_id'] = so.id
            vals['partner_shipping_id'] = so.partner_shipping_id
            vals['ref'] = so.customer_reference
        else:
            try:
                po = self.env['purchase.order'].search([('name', '=', vals['invoice_origin'])])
                vals['purchaseorder_id'] = po.id
                vals['partner_shipping_id'] = po.dest_address_id.id
            except KeyError:
                pass
        return super(AccountMoveInherit, self).create(vals)
