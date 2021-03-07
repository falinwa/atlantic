from odoo import models, fields


class ActivityType(models.Model):
    """ Class to define the Product Segments of the company

    This class has it's own view in Sale>configuration>Product Segment.
    It also has it's own role to assign to users to be able to manage them
    """

    _name = "activity.type"
    _description = "Product Segment"

    name = fields.Char("Activity Name", required=True)
    code = fields.Char("Activity code", required=True)
    companies = fields.Many2many("res.company")


# TODO: Change to it's own file
class ProductInherit(models.Model):
    _inherit = "product.product"
    _name = "product.product"

    standard_price = fields.Monetary(compute="_compute_cost")

    def _compute_cost(self):
        """
        Fix for a problem where the cost doesn't get set automatically based on vendor price
        """
        for record in self:
            if record.seller_ids:
                record.standard_price = record.seller_ids[0].price
            else:
                record.standard_price = 0
