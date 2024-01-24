from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    code = fields.Char(string='Tax code')
