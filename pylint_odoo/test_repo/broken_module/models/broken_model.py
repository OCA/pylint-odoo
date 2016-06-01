# coding: utf-8

from openerp import fields, models, _
from openerp.exceptions import Warning as UserError


def function_no_method():
    pass


class TestModel(models.Model):
    _name = 'test.model'

    _columns = {}  # deprecated columns
    _defaults = {}  # deprecated defaults

    name = fields.Char(
        _(u"Näme"),  # Don't need translate
        help=u"My hëlp",
        required=False,
        compute='_compute_name',  # good compute method name
        search='_search_name',  # good search method name
        inverse='_inverse_name',  # good inverse method name
    )

    # Imported openerp.fields use Char (Upper case)
    other_field = fields.char(
        name=_("Other field"),
        copy=True,
        compute='my_method_compute',  # bad compute method name
        search='my_method_search',  # bad search method name
        inverse='my_method_inverse',  # bad inverse method name
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

    def my_method3(self, cr):
        cr.commit()  # Dangerous use of commit old api
        self.env.cr.commit()  # Dangerous use of commit
        self._cr.commit()  # Dangerous use of commit
        self.cr.commit()  # Dangerous use of commit
        return cr

    def my_method4(self, variable2):
        self.env.cr2.commit()  # This should not be detected
        return variable2

    def my_method5(self, variable2):
        self.env.cr.commit2()  # This should not be detected
        return variable2

    def my_method6(self):
        user_id = 1
        if user_id != 99:
            # Method without translation
            raise UserError('String without translation')

    def my_method7(self):
        user_id = 1
        if user_id != 99:
            # Method with translation
            raise UserError(_('String with translation'))

    def my_method8(self):
        user_id = 1
        if user_id != 99:
            str_error = 'String with translation 2'  # Don't check
            raise UserError(str_error)

    def my_method9(self):
        user_id = 1
        if user_id != 99:
            # Method without translation
            raise UserError("String without translation 2")

    def my_method10(self):
        # A example of built-in raise without parameters
        raise ZeroDivisionError

    def sql_method(self, ids, cr):
        # This is the better way and should not be detected
        self._cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        self.env.cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        self.cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))

    def sql_injection_method(self, cr, ids):
        # SQL injection, bad way
        self._cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        self.env.cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        self.cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))

    def sql_injection_method3(self, ids, cr2):
        # This cr.execute2 or cr2.execute should not be detected
        self._cr.execute2(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        cr2.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))

    def sql_injection_method5(self, ids):
        var = 'SELECT name FROM account WHERE id IN %s'
        values = ([1, 2, 3, ], )
        self._cr.execute(var % values)  # sql injection too
