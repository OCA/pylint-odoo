# 'missing-return' not necessary inside compute methods, even if super is called
# we can only make sure the method is used to compute fields if said fields/methods
# are declared in the same python module (file)
from odoo import api, fields, models


class MissingReturnCompute(models.Model):

    discount = fields.Float(compute="_compute_discount", store=True)

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        if hasattr(super(), "_compute_discount"):
            super()._compute_discount()
        for line in self:
            line.discount = line.order_id.general_discount
