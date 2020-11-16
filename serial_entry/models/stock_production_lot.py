from odoo import fields, models, api


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    log_entries = fields.One2many("log.entry", "serial_number_ref")
    delivery_address = fields.Many2one("res.partner", related="purchase_order_ids.dest_address_id")

    @api.onchange("sale_order_ids")
    def _add_so_log(self):
        for rec in self:
            raise ValueError
            values = {
                'sale_order_ref': rec.sale_order_ids[-1],
                'description': "Sale Order received.",
                'date': rec.sale_order_ids[-1].date_order,
            }
            rec.write({
                'log_entries': [(0, 0, values)]
            })


    @api.onchange("purchase_order_ids")
    def _add_po_log(self):
        for rec in self:
            raise ValueError
            values = {
                'purchase_order_ref': rec.purchase_order_ids[-1],
                'description': "Purchase Order Confirmed",
                'date': rec.purchase_order_ids[-1].date_approve
            }
            rec.write({
                'log_entries': [(0, 0, values)]
            })
