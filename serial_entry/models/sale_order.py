from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    serial_number_ref = fields.Many2one("stock.production.lot")
    serial_entry_description = fields.Char("Log Description")


    @api.onchange('serial_number_ref', 'description')
    def _onchange_serial_num(self):
        for rec in self:
            so_id = rec._origin.id
            existing_ref = self.env["log.entry"].search([('sale_order_ref', '=', so_id)])

            # Only description has changed so the log entry only has to be updated
            if existing_ref and existing_ref.serial_number_ref == rec.serial_number_ref:
                rec.serial_number_ref.write({
                    'log_entries': [(1, existing_ref.id, {'description': rec.serial_entry_description})]
                })

            # The serial number has changed
            elif serial_number_ref:
                # Checking if the record already exists, if so first delete it
                if existing_ref:
                    existing_ref.serial_number_ref.write({
                        'log_entries': [(3, exiting_ref.id, 0)] 
                    })

                # Creating new record of 'log.entry' and adding it to the log entries of serial number
                rec.serial_number_ref.write({
                    'log_entries': [(0, 0, {'sale_order_ref': rec._origin.id,
                                            'description': rec.serial_entry_description})]
                })
            
