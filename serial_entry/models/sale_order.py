from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    log_entries = fields.One2many("log.entry", "sale_order_ref")
