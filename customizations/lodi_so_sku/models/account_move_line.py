from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sku = fields.Char('SKU', compute='_compute_product_sku')
    internal_product_name = fields.Char('Internal product name', compute='_compute_internal_product_name')

    @api.depends('product_id', 'move_id.partner_id')
    def _compute_product_sku(self):
        for line in self:
            line.sku = line.product_id.get_sku_by_partner_id(line.move_id.partner_id.id).sku

    @api.depends('product_id', 'move_id.partner_id')
    def _compute_internal_product_name(self):
        for line in self:
            line.internal_product_name = line.product_id.get_sku_by_partner_id(
                line.move_id.partner_id.id).internal_product_name
