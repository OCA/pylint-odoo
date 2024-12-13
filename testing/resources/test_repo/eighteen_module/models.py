from odoo import models, _, fields
from odoo.exceptions import UserError


class EighteenModel(models.Model):
    _name = "eighteen.model"

    name = fields.Char(_("Näme"))

    def my_method7(self):
        user_id = 1
        if user_id != 99:
            # Method with translation
            raise UserError(_("String with translation"))
