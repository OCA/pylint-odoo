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


class TestModel41(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'


class TestModel5(models.Model):
    _inherit = 'valid.duplicated'  # pylint: disable=R7980


class TestModel6(models.Model):
    _inherit = 'valid.duplicated'


class TestModel7(models.Model):
    _name = 'valid.duplicated.2'
    _inherit = 'valid.duplicated'


class TestModel8(models.Model):
    _inherit = ['valid.duplicated', 'valid.duplicated2']

    def method_1(self):
        _inherit = 'not-class-attribute'
        return _inherit

    def method_2(self):
        _inherit = 'not-class-attribute'
        return _inherit
