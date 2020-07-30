from odoo import models, fields, api

class DSSaleOrder(models.Model):
    _inherit = "sale.order"
    _name = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    