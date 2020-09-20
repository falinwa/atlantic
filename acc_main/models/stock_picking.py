from odoo import models, api


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        result = super(StockPickingInherit, self).create(vals)
        if result.group_id:
            source_po = self.env['purchase.order'].search([("name", "=", result.origin)])
            result.group_id.name = source_po.origin
        return result
