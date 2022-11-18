from odoo import fields
from odoo.models import BaseModel

from ..useful import USEFUL
import foo


class ResPartner(BaseModel):
    _name = "res.partner"

    random_field = fields.Char(string=USEFUL, size=foo.THREE)
