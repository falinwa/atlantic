from odoo import models, fields


class Reports(models.Model):
    _inherit = "ir.actions.report"

    company_id = fields.Many2one("res.company")
