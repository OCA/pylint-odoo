from odoo.tests.common import TransactionCase


class TestModel(TransactionCase):
    def setUp(self):
        super(TestModel, self).setUp()

    def method1(self, example_var):
        return example_var

    def test_1(self):
        self.partner.message_post(body="Test", subtype="mail.mt_comment")
        self.partner.message_post("Test", subtype="mail.mt_comment")
