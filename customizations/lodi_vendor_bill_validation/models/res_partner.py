from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_bill_validation = fields.Boolean(string='Bill validation is not mandatory')
