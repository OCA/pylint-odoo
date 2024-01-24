from odoo import api, fields, models


class ProductPartnerSku(models.Model):
    _name = 'product.partner.sku'
    _description = 'Relationship between product sku and partners'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    sku = fields.Char(string="SKU", required=True)
    internal_product_name = fields.Char(string="Product name")
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Client', required=True)

    @api.depends('sku', 'partner_id', 'product_id')
    def _compute_name(self):
        for record in self:
            record.name = '%s, %s, %s' % (record.sku, record.partner_id.name, record.product_id.name)
