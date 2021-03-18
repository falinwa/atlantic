# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)
        moves = values.get('move_dest_ids')
        if moves:
            for move in moves:
                if product_id.is_generic_product and move.sale_line_id.name:
                    res.update({'name': move.sale_line_id.name})
        else:
            sale_line_id = values.get('sale_line_id')
            sale_line = self.env['sale.order.line'].browse(sale_line_id)
            if product_id.is_generic_product and sale_line.name:
                res.update({'name': sale_line.name})
        return res
