# coding: utf-8

from openerp import fields, models, _


def function_no_method():
    pass


class TestModel(models.Model):
    _name = 'test.model'

    _fields = {}  # deprecated fields
    _defaults = {}  # deprecated defaults

    name = fields.Char(
        _(u"Näme"),  # Don't need translate
        help=u"My hëlp",
        required=False)

    # Imported openerp.fields use Char (Upper case)
    other_field = fields.char(
        name=_("Other field"),
        copy=True,
    )

    other_field2 = fields.char(
        'Other Field2',
        copy=True,
    )

    def my_method1(self, variable1):
        #  Shouldn't show error of field-argument-translate
        self.my_method2(_('hello world'))

    def my_method2(self, variable2):
        return variable2
