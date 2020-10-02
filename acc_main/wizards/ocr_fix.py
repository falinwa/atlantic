from odoo import models, fields
from ..models.hs_cooler_calculator import name_test


class OCRFix(models.TransientModel):
    _name = "ocr.fix"

    product_name = fields.Char()
    so = fields.Many2one("sale.order")

    def action_name_fix(self):
        for record in self:
            if name_test(record.product_name):
                self.env['sale.order'].add_product_name(record.product_name, record.so)
            else:
                raise Warning("You entered an invalid product name.")

