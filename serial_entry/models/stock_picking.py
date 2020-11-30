from odoo import models, fields


class StockPicking(models.Model):
    _inherit='stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        rec = self.env["stock.picking"].search([("id","=",self.id)])
        for move in rec.move_ids_without_package:
            for line in move.move_line_ids:
                if line.lot_id:
                    log_entries = []
                    so_id = move.sale_line_id.order_id
                    if so_id:
                        values_so = {
                            'sale_order_ref': so_id.id,
                            'description': "Sale Order received",
                            'date': so_id.date_order,
                        }
                        log_entries.append((0, 0, values_so))
                    po_id = move.purchase_line_id.order_id
                    if po_id:
                        values_po= {
                            'purchase_order_ref': po_id.id,
                            'description': "Purchase Order Confirmed",
                            'date': po_id.date_approve,
                        }
                        log_entries.append((0, 0, values_po))
                    if log_entries:
                        line.lot_id.write({
                            'log_entries': log_entries
                        })

        return res
