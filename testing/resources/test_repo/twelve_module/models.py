from odoo import models


class TwelveModel(models.Model):
    _name = "twelve.model"

    def name_get(self):
        # do staff
        return super().name_get()
