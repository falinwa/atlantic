from odoo import fields, models


class LogWizard(models.TransientModel):
    _name = "log.wizard"

    serial_number = fields.Many2one("stock.production.lot")
    description = fields.Char()
    sale_order_id = fields.Many2one("sale.order")

    def submit(self):
        values = {
            "description": self.description,
            "serial_number_ref": self.serial_number.id,
            "sale_order_ref": self.sale_order_id.id,
        }
        self.serial_number.write({"log_entries": [(0, 0, values)]})
        raise ValueError()
