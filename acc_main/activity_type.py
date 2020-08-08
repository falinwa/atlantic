from odoo import models, fields


class ActivityType(models.Model):
    _name = "activity.type"
    _description = "Activity Type Atlantic"

    name = fields.Char("Activity Name", required=True)
    code = fields.Char("Activity code (type##)", required=True)
