from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    so_invoice_id = fields.Many2one('res.partner', compute='_get_so_invoice_id')

    @api.model
    @api.depends('invoice_origin')
    def _get_so_invoice_id(self):
        for rec in self:
            res = rec.env['sale.order'].search([('name', '=', rec.invoice_origin)])
            rec.so_invoice_id = res.partner_invoice_id