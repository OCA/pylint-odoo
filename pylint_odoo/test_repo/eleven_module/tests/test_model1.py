
from odoo.tests.common import TransactionCase

# Even though astroid is not set as an external dependency, it should not fail,
# because this is a test file
import astroid
from astroid import Const
from astroid import BinOp as bo


class TestModel(TransactionCase):
    def setUp(self):
        super(TestModel, self).setUp()
        self.const = isinstance(astroid.Const, Const)
        self.bo = isinstance(astroid.BinOp, bo)
