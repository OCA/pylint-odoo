from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_partner_sku_ids = fields.Many2many(comodel_name='product.partner.sku', string='SKUs', ondelete='cascade')

    def get_sku_by_partner_id(self, partner_id):
        return self.product_partner_sku_ids.filtered(lambda _sku: _sku.partner_id.id == partner_id)[:1]
