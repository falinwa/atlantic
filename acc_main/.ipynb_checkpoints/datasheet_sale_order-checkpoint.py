from odoo import models, fields, api, _

class DSSaleOrder(models.Model):
    _inherit = "sale.order"
    _name = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    order_type = fields.Selection([("type01", "01 Compressors"),("type02","02 HS-Cooler"),("type03","03 SAV"),("type04","04 Divers"),
