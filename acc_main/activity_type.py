from odoo import models, fields


class ActivityType(models.Model):
    _name = "activity.type"
    _description = "Activity Type Atlantic"

    name = fields.Char("Activity Name", required=True)
    code = fields.Char("Activity code", required=True)


class ProductInherit(models.Model):
    _inherit = "product.product"
    _name = "product.product"

    standard_price = fields.Monetary(compute="_compute_cost")

    def _compute_cost(self):
        for record in self:
            if record.seller_ids:
                record.standard_price = record.seller_ids[0].price
            else:
                record.standard_price = 0
