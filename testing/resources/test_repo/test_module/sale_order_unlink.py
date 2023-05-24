import platform
from odoo.models import Model

if platform.system() == 'Windows':
    raise OSError


class SaleOrder(Model):
    _name = 'sale.order'

    def unlink(self):
        if self.name == 'maybe':
            if self.status == 'explosive':
                raise Exception()

        return super().unlink()
