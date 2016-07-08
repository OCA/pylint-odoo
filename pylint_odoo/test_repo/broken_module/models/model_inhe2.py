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
