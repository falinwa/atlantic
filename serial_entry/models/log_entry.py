from odoo import fields, models, api
from datetime import date


class LogEntry(models.Model):
    _name = "log.entry"
    _description = """
        Log entries for serial numbers.
    """

    date = fields.Date(default=date.today())
    description = fields.Char()
    serial_number_ref = fields.Many2one("stock.production.lot")

    @api.model
    def create(self, vals):
        result = super(LogEntry, self).create(vals)
        result.date = date.today()
        return result

