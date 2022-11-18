from odoo.models import AbstractModel
from odoo import fields

from .utils import func


class PassWizard(AbstractModel):
    _name = "pass.wizard"

    name = fields.Char(required=True)

    def foo(self):
        return func(self)
