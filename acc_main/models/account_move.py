from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    so_invoice_id = fields.Many2one('res.partner', compute='_get_so_invoice_id')

    @api.model
    def create(self, vals):
        print(vals['invoice_origin'])
        so = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])])
        if so:
            vals['partner_shipping_id'] = so.partner_shipping_id
        else:
            po = self.env['purchase.order'].search([('name', '=', vals['invoice_origin'])])
            vals['partner_shipping_id'] = po.dest_address_id.id
        print(vals['partner_shipping_id'])
        return super(AccountMoveInherit, self).create(vals)

    @api.model
    @api.depends('invoice_origin')
    def _get_so_invoice_id(self):
        for rec in self:
            res = rec.env['sale.order'].search([('name', '=', rec.invoice_origin)])
            rec.so_invoice_id = res.partner_invoice_id