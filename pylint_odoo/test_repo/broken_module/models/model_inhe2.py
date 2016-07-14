# coding: utf-8

from openerp import models


class TestModel(models.Model):
    _inherit = 'res.company'


class TestModel2(models.Model):
    _inherit = 'res.company'


class TestModel3(models.Model):
    _inherit = 'res.partner'


class TestModel4(models.Model):
    _inherit = 'res.partner'


class TestModel5(models.Model):
    _inherit = 'valid.duplicated'  # pylint: disable=R7980


class TestModel6(models.Model):
    _inherit = 'valid.duplicated'
