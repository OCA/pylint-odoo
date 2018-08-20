from odoo import models

# astroid is not set as an external Python dependency in the manifest,
# so all of the following imports should fail
import astroid
from astroid import Const
from astroid import BinOp as bo


class EleveModel(models.Model):
    _name = 'eleve.model'

    def method1(self):
        self.const = isinstance(astroid.Const, Const)
        self.bo = isinstance(astroid.BinOp, bo)
