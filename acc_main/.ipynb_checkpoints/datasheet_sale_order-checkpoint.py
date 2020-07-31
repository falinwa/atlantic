from odoo import models, fields, api, _

class DSSaleOrder(models.Model):
    _inherit = "sale.order"
    _name = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    order_type = fields.Selection([("type01", "01 Compressors"),("type02","02 HS-Cooler"),("type03","03 SAV"),("type04","04 Divers"),
                                  ("type05","05 HAP"),("type07","07 Cool Partners"),("type08", "08 Cabero")], 'Type')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')
        if vals['order_type']:
            og_name = str(vals['name'])
            vals['name'] = og_name[:7] + str(vals['order_type'])[-2:] + '.' + og_name[7:]
        result = super(DSSaleOrder, self).create(vals)
        return result
    
    
    def action_confirm(self):
        result = super(DSSaleOrder, self).action_confirm()
        name = self.name
        code = self.env['ir.sequence'].next_by_code('confirmed.sale')
        name = 'ARC' + name[3:]
        self.write({'name': name})
        return result
