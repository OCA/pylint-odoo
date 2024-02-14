from odoo import fields, models


class FailWizard(models.AbstractModel):
    _name = "fail.wizard"

    name = fields.Char()
