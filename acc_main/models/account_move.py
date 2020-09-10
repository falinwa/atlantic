from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    saleorder_id = fields.Many2one('sale.order')
    purchaseorder_id = fields.Many2one('purchase.order')

    @api.model
    def create(self, vals):
        journal = self.env['account.journal'].search([('id', '=', vals['journal_id'])])
        if journal.name == 'Vendor Bills':
            vals['ref'] = ""
            vals['invoice_payment_ref'] = ""

        so = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])])
        if so:
            vals['saleorder_id'] = so.id
            vals['partner_shipping_id'] = so.partner_shipping_id
        else:
            po = self.env['purchase.order'].search([('name', '=', vals['invoice_origin'])])
            vals['purchaseorder_id'] = po.id
            vals['partner_shipping_id'] = po.dest_address_id.id
        return super(AccountMoveInherit, self).create(vals)
