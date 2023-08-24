from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def unlink(self):
        if self.name == 'explode':
            raise RuntimeError()

        return super().unlink()
