from odoo.tests.common import TransactionCase


class TestModel(TransactionCase):
    def setUp(self):
        super(TestModel, self).setUp()

    def method1(self, example_var):
        return example_var

    def test_1(self):
        self.partner.message_post(body="Test", subtype="mail.mt_comment")
        self.partner.message_post("Test", subtype="mail.mt_comment")

    def test_base_method_1(self):
        # Override prohibited, should fail
        super().test_base_method_1()
        # No override applied, should not fail
        super().test_base_method_2()
        return super().test_base_method_3()

    def test_base_method_2(self):
        # No override applied, should not fail
        super(TestModel, self).test_base_method_1()
        # Override allowed, should not fail
        super(TestModel, self).test_base_method_2()
        # No override applied, should not fail
        return super(TestModel, self).test_base_method_3()

    def test_base_method_3(self):
        some_obj = TransactionCase()
        # No override applied, should not fail
        super(TestModel, self).test_base_method_1()
        super(TestModel, self).test_base_method_2()
        some_obj.test_base_method_3()
        # Override prohibited, should fail
        return super(TestModel, self).test_base_method_3()
