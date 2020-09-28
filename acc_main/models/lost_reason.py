from odoo import models, fields


class LostReason(models.Model):
    _name = 'lost.reason'
    _description = 'Reasons for lost Sales Orders'

    name = fields.Char()
    description = fields.Char()