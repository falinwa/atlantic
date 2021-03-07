from odoo import models, fields, api, _
from base64 import b64decode
import logging
from odoo.addons.acc_main.models.hs_cooler_calculator import hs_ocr, calculator
from odoo.exceptions import Warning, UserError
from pdf2image import convert_from_bytes
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """ 
    Extending the Sale Order Model

    Extra Fields:
    -----
    datasheet: Field to upload file of datasheet
    datasheet_name: File field always need to be accompanied by a char field because odoo
    activity_type: Which Product Segment the order falls under
    delivery_date: Date field because Odoo's delivery date system doesn't work
    customer_reference: Field for customer reference
    purchase_order_ref: Reference to PO (only available once SO confirmed)
    supp_order_conf: Boolean/checkbox if supplier has confirmed the order
                        Related field with PO
    reason_lost: Field to have the ability to say why the order was lost
    temp_product_name: Field where the name comes after OCR, 
                        user is then able to edit it if there are mistakes
    """

    _inherit = "sale.order"

    datasheet = fields.Binary("Upload Datasheet")
    datasheet_name = fields.Char("File name")
    activity_type = fields.Many2one("activity.type", required=True)
    delivery_date = fields.Date(compute="_so_delivery_date")
    # TODO: Delete if no errors occur
    # order_type = fields.Selection(
    #     [
    #         ("type01", "01 Compressors"),
    #         ("type02", "02 HS-Cooler"),
    #         ("type03", "03 SAV"),
    #         ("type04", "04 Divers"),
    #         ("type05", "05 HAP"),
    #         ("type07", "07 Cool Partners"),
    #         ("type08", "08 Cabero"),
    #     ],
    #     "Activity Type",
    # )
    # TODO: Combine with customer ref from odoo?
    customer_reference = fields.Char("Customer Reference")
    purchase_order_ref = fields.Many2one("purchase.order")
    supp_order_conf = fields.Boolean(related="purchase_order_ref.supp_order_conf")
    reason_lost = fields.Many2one("lost.reason")
    temp_product_name = fields.Char()

    @api.depends("order_line.delivery_date")
    def _so_delivery_date(self):
        """Sets SO delivery date as earliest of the delivery date of the SO lines"""
        for order in self:
            min_date = None
            for line in order.order_line:
                if line.delivery_date and (
                    min_date is None or line.delivery_date < min_date
                ):
                    min_date = line.delivery_date
            order.delivery_date = min_date

    # TODO: Able to change with related field???
    @api.onchange("customer_reference")
    def _sync_purchase_order(self):
        for rec in self:
            if rec.state == "sale":
                order = self.env["purchase.order"].search([("origin", "=", self.name)])
                if order:
                    order.write({"customer_ref": rec.customer_reference})

    @api.onchange("partner_shipping_id")
    def _sync_delivery_address_po(self):
        """Syncs delivery address with PO"""

        for rec in self:
            if rec.state == "sale":
                order = self.env["purchase.order"].search(
                    [("origin", "=", self.origin)]
                )
                if order:
                    order.write({"dest_address_id": rec.partner_shipping_id})

    @api.model
    def add_product_name(self, product_name, rec):
        """Add product to SO based on name of HS Cooler product"""

        # Defining ids and constants for the sale order line
        price, weight = calculator(product_name)
        product = self.env["product.product"].search([("name", "=", product_name)])
        product_exists = bool(product)
        categ = self.env["product.category"].search([("name", "=", "HS Cooler HEX")])
        vendor = self.env["res.partner"].search([("name", "=", "HS Cooler")])
        intrastat_id = self.env["hs.code"].search([("local_code", "=", "84195080")])
        route = self.env["stock.location.route"].search([("name", "=", "Dropship")])
        if not route:
            route = self.env["stock.location.route"].search([("id", "=", 9)])
            if not route:
                route = self.env["stock.location.route"].search([("id", "=", 10)])
        country = self.env["res.country"].search([("name", "=", "Germany")])
        company_id = self.env["res.company"].search(
            [("name", "=", "Atlantic Cool Components")]
        )

        supplierinfo_args = {"name": vendor.id, "price": price, "delay": 56}
        product_args = {
            "name": product_name,
            "lst_price": price * 2.052,
            "weight": weight,
            "categ_id": categ.id,
            "hs_code_id": intrastat_id.id,
            "sale_delay": 7,
            "route_ids": [route.id],
            "origin_country_id": country.id,
            "company_id": company_id.id,
            "type": "product",
            "tracking": "serial",
        }

        # If the product is not yet in the database, it is created
        if product_exists:
            supplierinfo = product.seller_ids[0]
            supplierinfo.write(supplierinfo_args)
            product.write(product_args)
        else:
            supplier = self.env["product.supplierinfo"].create(supplierinfo_args)
            product_args["seller_ids"] = [supplier.id]
            product = self.env["product.product"].create(product_args)
        if rec._origin.id:
            self.env["sale.order.line"].create(
                {
                    "order_id": rec._origin.id,
                    "product_uom_qty": 1,
                    "product_id": product.id,
                }
            )
            self.env.cr.commit()
            rec.datasheet = None

    @api.model
    @api.onchange("datasheet")
    def add_product_datasheet(self, data=None, res_id=None):
        """
        Function to add sale order line from HS-Cooler datasheet
        :param data: Optional field to fill in data (when function called externally)
        :return: None
        """
        # Needed fix to be able to call method from Javascript code (Drag&Drop)
        if res_id:
            self = self.env["sale.order"].search([("id", "=", res_id)])
        for rec in self:
            if rec.datasheet or data:
                # Getting the datasheet from the datasheet file field
                if data:
                    b64 = data
                else:
                    b64 = rec.datasheet
                file_bytes = b64decode(b64, validate=True)
                if file_bytes[0:4] != b"%PDF":
                    raise Warning(
                        "Not a PDF file, please upload datasheet in pdf format."
                    )
                # Converting PDF to Image
                images = convert_from_bytes(file_bytes, 600)
                img = images[0]

                # Using OCR
                ocr = hs_ocr(img)
                print(ocr)
                product_name, success = ocr
                if success:
                    self.add_product_name(product_name, rec)
                else:
                    rec.temp_product_name = product_name
                    return {
                        "warning": {
                            "title": "OCR Failed",
                            "message": "The OCR recognised "
                            + product_name
                            + ", you can also enter the "
                            "product name manually by "
                            "clicking the button "
                            "below.",
                        }
                    }

    @api.model
    def create(self, vals):
        """
        Inheriting create function to customize SO name
        """
        if vals.get("name", _("New")) == _("New"):
            seq_date = None
            if "date_order" in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals["date_order"])
                )
            if "company_id" in vals:
                vals["name"] = self.env["ir.sequence"].with_context(
                    force_company=vals["company_id"]
                ).next_by_code("sale.order", sequence_date=seq_date) or _("New")
            else:
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "sale.order", sequence_date=seq_date
                ) or _("New")
        if vals["activity_type"]:
            og_name = str(vals["name"])
            activity_type = self.env["activity.type"].search(
                [("id", "=", vals["activity_type"])]
            )
            vals["name"] = og_name[:7] + str(activity_type.code) + "." + og_name[7:]
        result = super(SaleOrder, self).create(vals)
        if vals["datasheet"]:
            result.add_product_datasheet()
        return result

    def action_confirm(self):
        """
        When confirming order changing SO name, add PO ref and some security features
        """
        # Check if customer in France or EU and making sure taxes are correct
        if self.partner_id.country_id.name != "France":
            if self.amount_tax > 0:
                raise UserError("Orders outside of France can't have taxes.")
        elif self.amount_tax == 0 and self.amount_total != 0:
            raise UserError("Orders in France must have taxes")
                

        # Check if there aren't any more individuals on the sale order (Only companies allowed)
        contact_fields = [
            self.partner_id,
            self.partner_invoice_id,
            self.partner_shipping_id,
        ]
        for field in contact_fields:
            if field.company_type != "company" and field.type == "contact":
                raise UserError(
                    "Please change all contact fields to companies instead of individuals."
                )

        result = super(SaleOrder, self).action_confirm()

        # Updating delivery_date
        timediff = self.date_order.date() - self.create_date.date()
        for line in self.order_line:
            if line.delivery_date:
                line.delivery_date = line.delivery_date + timediff

        # Updating name
        self.origin = self.name
        name = self.name
        code = self.env["ir.sequence"].next_by_code("confirmed.sale")
        name = "ARC " + str(datetime.now().year)[2:] + name[6:10] + code

        # Setting reference to Purchase Order
        po = self.env["purchase.order"].search([("origin", "=", self.origin)])
        if po:
            po.origin = name
            po_id = po[-1].id
        else:
            po_id = False
        self.write(
            {"name": name, "customer_reference": False, "purchase_order_ref": po_id}
        )

        return result

    def redirect_po(self):
        """Method called by button to go to related PO from SO"""
        if self.origin:
            new_order = self.env["purchase.order"].search([("origin", "=", self.name)])
            if not new_order:
                return {
                    "warning": {
                        "title": "No Source Document",
                        "message": "No source document could be found, please try again with another order.",
                    }
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "name": "purchase.view_order_form",
                    "res_model": "purchase.order",
                    "res_id": new_order[-1].id,
                    "view_type": "form",
                    "view_mode": "form",
                    "target": "self",
                }
        else:
            return {
                "warning": {
                    "title": "No Source Document",
                    "message": "No source document could be found, please try again with another order.",
                }
            }


class OrderLineInherit(models.Model):
    """
    Extending Sale Order Line model

    Extra Fields
    ----
    delivery_date: Delivery date for each line
    total_lead: Added to be able to show the Customer Lead Time in list view
    """
    _inherit = "sale.order.line"
    _name = "sale.order.line"

    delivery_date = fields.Date()
    total_lead = fields.Integer()

    @api.model
    def create(self, vals):
        """
        Setting customer_lead, total_lead and delivery_date on creation
        """
        order = self.env["sale.order"].search([("id", "=", vals["order_id"])])
        order_date = order.date_order
        product = self.env["product.product"].search([("id", "=", vals["product_id"])])
        try:
            lead_time = vals["customer_lead"]
        except KeyError:
            lead_time = product.sale_delay

        # Check to make sure that there are sellers of the product in the database
        if product.seller_ids:
            supplier_delay = product.seller_ids[0].delay
            vals["total_lead"] = lead_time + supplier_delay
            vals["delivery_date"] = order_date + timedelta(vals["total_lead"])
        return super(OrderLineInherit, self).create(vals)


class InvoiceInherit(models.Model):
    """
    Extending the Account Move (Invoice) model

    Extra Fields
    ----
    customer_reference: Added own customer reference field
    partner_invoice_id: There were some issues with odoo setting invoice address
    """
    _inherit = "account.move"
    _name = "account.move"

    customer_reference = fields.Char()
    partner_invoice_id = fields.Many2one("res.partner")

    @api.model
    def create(self, vals_list):
        # TODO: Can't this all just be deleted?
        result = super(InvoiceInherit, self).create(vals_list)
        source = self.env["sale.order"].search([("name", "=", result.invoice_origin)])
        result.customer_reference = source.customer_reference
        result.ref = source.customer_reference
        result.partner_invoice_id = source.partner_invoice_id
        return result
