# coding: utf-8

from openerp import models
from .no_exists import package


class TestModel(models.Model):
    _inherit = 'res.company'

    def method(self):
        return package


class TestModel2(models.Model):
    _inherit = 'model.no.duplicated'
