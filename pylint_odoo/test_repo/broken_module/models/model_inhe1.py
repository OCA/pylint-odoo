# coding: utf-8

from openerp import models

# to tests a suppression of a import-error
from odoo import tools
import odoo
import odoo.addons as addons
from odoo.addons.module.models import partner

import no_exists
from no_exists import package


class TestModel(models.Model):
    _inherit = 'res.company'

    def method(self):
        return tools, odoo, addons, partner, no_exists, package


class TestModel2(models.Model):
    _inherit = 'model.no.duplicated'
