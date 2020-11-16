from odoo import models, fields


class StockPicking(models.Model):
    _inherit='stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        rec = self.env["stock.picking"].search([("id","=",self.id)])
        for move in rec.move_ids_without_package:
            for line in move.move_line_ids:
                if line.lot_id:
                    ... 
        return res
