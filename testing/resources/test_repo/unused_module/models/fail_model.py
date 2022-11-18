from odoo.models import BaseModel

class FailModel(BaseModel):
    _name = "fail.model"

    not_imported = fields.Boolean(default=True)
