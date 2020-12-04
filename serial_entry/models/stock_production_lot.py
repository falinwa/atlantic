from odoo import fields, models, api


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    log_entries = fields.One2many("log.entry", "serial_number_ref")
    delivery_address = fields.Many2one(
        "res.partner", related="purchase_order_ids.dest_address_id"
    )
