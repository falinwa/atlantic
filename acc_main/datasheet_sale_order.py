from odoo import models, fields, api, _
from base64 import b64decode
import logging
from odoo.addons.acc_main.hs_cooler_calculator import hs_ocr, calculator
from odoo.exceptions import Warning
import datetime

log = logging.getLogger(__name__)
from pdf2image import convert_from_bytes

class DSSaleOrder(models.Model):
    _inherit = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    activity_type = fields.Many2one("activity.type",required=True)
    order_type = fields.Selection([("type01", "01 Compressors"),("type02","02 HS-Cooler"),("type03","03 SAV"),("type04","04 Divers"),("type05","05 HAP"),("type07","07 Cool Partners"),("type08", "08 Cabero")], 'Activity Type', required=True)
    customer_reference = fields.Char("Customer Reference")

    @api.onchange('customer_reference')
    def _sync_purchase_order(self):
        for rec in self:
            if rec.state == 'sale' and rec.origin:
                order = self.env['purchase.order'].search([('origin', '=', self.origin)])
                if order:
                    order.write({'customer_ref': rec.customer_reference})

    @api.onchange('partner_shipping_id')
    def _sync_delivery_address_po(self):
        for rec in self:
            if rec.state == 'sale':
                order = self.env['purchase.order'].search([('origin', '=', self.origin)])
                if order:
                    order.write({'dest_address_id': rec.partner_shipping_id})

    @api.model
    @api.onchange('datasheet')
    def add_product_datasheet(self, data=None, res_id=None):
        """
        Function to add sale order line from HS-Cooler datasheet
        :param data: Optional field to fill in data (when function called externally)
        :return: None
        """
        if res_id:
            self = self.env['sale.order'].search([('id','=',res_id)])
        for rec in self:
            if rec.datasheet or data:
                if data:
                    b64 = data
                else:
                    b64 = rec.datasheet
                file_bytes = b64decode(b64, validate=True)
                if file_bytes[0:4] != b'%PDF':
                    raise Warning("Not a PDF file, please upload datasheet in pdf format.")
                images = convert_from_bytes(file_bytes, 600)
                img = images[0]
                product_name = hs_ocr(img)
                if not product_name:
                    rec.datasheet = None
                    raise Warning("Can't recognise datasheet. Please try again with another datasheet.")
                price, weight = calculator(product_name)
                if self.env['product.product'].search([('name','=',product_name)]):
                    product = self.env['product.product'].search([('name', '=', product_name)])
                    if round(product.lst_price) != round(price*2.052):
                        product.seller_ids[0].write({'price': price})
                        categ = self.env['product.category'].search([('name', '=', 'HS Cooler HEX')])
                        product.write({'lst_price': price*2.052,
                                       'weight': weight,
                                       'categ_id': categ.id,
                                       })
                else:
                    categ = self.env['product.category'].search([('name', '=', 'HS Cooler HEX')])
                    vendor = self.env['res.partner'].search([('name', '=', 'HS Cooler')])
                    intrastat_id = self.env['account.intrastat.code'].search([('code', '=', '84195080')])
                    supplier = self.env['product.supplierinfo'].create({'name': vendor.id,
                                                                        'price': price})
                    product = self.env["product.product"].create({'name': product_name,
                                                                  'lst_price': price*2.052,
                                                                  'weight': weight,
                                                                  'categ_id': categ.id,
                                                                  'seller_ids': [supplier.id],
                                                                  'intrastat_id': intrastat_id.id,
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
        if vals['activity_type']:
            og_name = str(vals['name'])
            activity_type = self.env['activity.type'].search([('id','=',vals['activity_type'])])
            vals['name'] = og_name[:7] + str(activity_type.code) + '.' + og_name[7:]
        result = super(DSSaleOrder, self).create(vals)
        if vals['datasheet']:
            result.add_product_datasheet()
        return result
    
    def action_confirm(self):
        """
        Inheriting confirm function to customize sale order name
        """
        result = super(DSSaleOrder, self).action_confirm()
        self.origin = self.name
        name = self.name
        code = self.env['ir.sequence'].next_by_code('confirmed.sale')
        name = 'ARC' + name[3:10] + code
        self.write({'name': name,
                    'customer_reference': False,
                    })

        return result

    def redirect_po(self):
        if self.origin:
            new_order = self.env['purchase.order'].search([('origin', '=', self.origin)])
            if not new_order:
                return {'warning': {'title': 'No Source Document',
                                    'message': "No source document could be found, please try again with another order."}}
            return {
                'type': 'ir.actions.act_window',
                'name': 'purchase.view_order_form',
                'res_model': 'purchase.order',
                'res_id': new_order.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'self',
            }
        else:
            return {'warning': {'title': 'No Source Document',
                                'message': "No source document could be found, please try again with another order."}}


class OrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    _name = "sale.order.line"

    delivery_date = fields.Date()

    @api.model
    def create(self, vals):
        order = self.env['sale.order'].search([('id', '=', vals['order_id'])])
        order_date = order.date_order
        lead_time = vals['customer_lead']
        delivery_date = order_date + datetime.timedelta(lead_time)
        vals['delivery_date'] = delivery_date
        return super(OrderLineInherit, self).create(vals)


class InvoiceInherit(models.Model):
    _inherit = "account.move"
    _name = "account.move"

    customer_reference = fields.Char()
    partner_invoice_id = fields.Many2one('res.partner')

    @api.model
    def create(self, vals_list):
        result = super(InvoiceInherit, self).create(vals_list)
        source = self.env['sale.order'].search([('name','=',result.invoice_origin)])
        result.customer_reference = source.customer_reference
        log.warning(result.customer_reference)
        result.partner_invoice_id = source.partner_invoice_id
        return result
