from odoo import models


class TwelveModel(models.Model):
    _name = "twelve.model"

    def name_get(self):
        # do staff
        return super().name_get()
    
    def name_get2(self):
        return super().name_get()  # Should be super().name_get2()
