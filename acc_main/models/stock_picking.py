from odoo import models, api


class StockPickingInherit(models.Model):
    """
    Extension of Stock Picking model
    """
    _inherit = 'stock.picking'

    # TODO: Can go????
    @api.model
    def create(self, vals):
        """Sets reference to PO"""
        result = super(StockPickingInherit, self).create(vals)
        if result.group_id:
            source_po = self.env['purchase.order'].search([("name", "=", result.origin)])
            result.group_id.name = source_po.origin
        return result
