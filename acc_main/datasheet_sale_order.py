from odoo import models, fields, api, _
from base64 import b64decode
import logging
from odoo.addons.acc_main.hs_cooler_calculator import hs_ocr, calculator

log = logging.getLogger(__name__)
from pdf2image import convert_from_bytes

class DSSaleOrder(models.Model):
    _inherit = "sale.order"
    _name = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    order_type = fields.Selection([("type01", "01 Compressors"),("type02","02 HS-Cooler"),("type03","03 SAV"),("type04","04 Divers"),("type05","05 HAP"),("type07","07 Cool Partners"),("type08", "08 Cabero")], 'Activity Type', required=True)

    @api.model
    @api.onchange('datasheet')
    def add_product_datasheet(self, data=None):
        """
        Function to add sale order line from HS-Cooler datasheet
        :param data: Optional field to fill in data (when function called externally)
        :return: None
        """
        log.warning("It's doing something, just not so much.")
        for rec in self:
            if rec.datasheet or data:
                log.warning("It's doing something.")
                if data:
                    bytes = data
                else:
                    b64 = rec.datasheet
                    bytes = b64decode(b64, validate=True)
                if bytes[0:4] != b'%PDF':
                    raise ValueError('Not a PDF file.')
                images = convert_from_bytes(bytes, 600)
                img = images[0]
                product_name = hs_ocr(img)
                if not product_name:
                    rec.datasheet = None
                    return {'warning':{'title':'Invalid Document','message':"Can't recognise datasheet. Please try again with another datasheet."}}
                price, weight = calculator(product_name)
                if self.env['product.product'].search([('name','=',product_name)]):
                    product = self.env['product.product'].search([('name', '=', product_name)])
                    if product.list_price != price:
                        product.write({'list_price': price,
                                       'weight': weight,
                                       })
                else:
                    product = self.env["product.product"].create({'name': product_name,
                                                                  'list_price': price,
                                                                  'weight': weight,
                                                                  })
                if rec._origin.id:
                    self.env['sale.order.line'].create({'order_id': rec._origin.id,
                                                        'product_uom_qty': 1,
                                                        'product_id': product.id
                                                        })
                    rec.datasheet = None


    @api.model
    def create(self, vals):
        """
        Inheriting create function to customize quotation name
        """
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
        if vals['datasheet']:
            result.add_product_datasheet()
        return result
    
    
    def action_confirm(self):
        """
        Inheriting confirm function to customize sale order name
        """
        result = super(DSSaleOrder, self).action_confirm()
        name = self.name
        code = self.env['ir.sequence'].next_by_code('confirmed.sale')
        name = 'ARC' + name[3:-5] + code
        self.write({'name': name})
        return result


