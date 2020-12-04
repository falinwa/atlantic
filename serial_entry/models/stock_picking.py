from odoo import models, fields
from datetime import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        rec = self.env["stock.picking"].search([("id", "=", self.id)])
        for move in rec.move_ids_without_package:
            for line in move.move_line_ids:
                so_id = move.sale_line_id.order_id
                po_id = move.purchase_line_id.order_id
                so_id.write({"state": "done"})
                po_id.write({"state": "done"})
                if line.lot_id:
                    log_entries = []
                    if so_id:
                        so_id.write({"state": "done"})
                        values_so = {
                            "sale_order_ref": so_id.id,
                            "description": "Sale Order received",
                            "date": so_id.date_order,
                        }
                        log_entries.append((0, 0, values_so))
                    if po_id:
                        values_po = {
                            "purchase_order_ref": po_id.id,
                            "description": "Purchase Order Confirmed",
                            "date": po_id.date_approve,
                        }
                        log_entries.append((0, 0, values_po))
                    values_shipped = {
                        "date": datetime.today(),
                        "description": "Order has been shipped",
                    }
                    log_entries.append((0, 0, values_shipped))
                    if log_entries:
                        line.lot_id.write({"log_entries": log_entries})

        return res
