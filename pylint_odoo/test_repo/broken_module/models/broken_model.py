# coding: utf-8

from openerp import fields, models, _
from openerp.exceptions import Warning as UserError
from openerp import exceptions

# Relatives import for odoo addons
from openerp.addons.broken_module import broken_model as broken_model1
from openerp.addons import broken_module as broken_module1
import openerp.addons.broken_module as broken_module2
import openerp.addons.broken_module.broken_model as broken_model2


other_field = fields.Char()


def function_no_method():
    return broken_model1, broken_module1, broken_module2, broken_model2


class TestModel(models.Model):
    _name = 'test.model'

    _columns = {}  # deprecated columns
    _defaults = {}  # deprecated defaults
    length = fields.Integer()  # Deprecated length by js errors

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
    compute_none = fields.Char(compute=None)

    other_field2 = fields.char(
        'Other Field2',
        copy=True,
    )

    # This is a inherit overwrite field then don't should show errors related
    # with creation of fields.
    def method_date(self):
        date = fields.Date.to_string(
            fields.Datetime.context_timestamp(self,
                                              timestamp=fields.Datetime.now())
        )
        return date

    my_ok_field = fields.Float(
        "My correctly named field",
        digits=(6, 6),  # OK: Valid field parameter
        index=True,  # OK: Valid field parameter
        help="My ok field",
    )

    my_ko_field = fields.Float(
        digits_compute=lambda cr: (6, 6),  # Deprecated field parameter
        select=True,  # Deprecated field parameter
        help="My ko field",
        string="My Ko Field",  # String parameter equal to name of variable
    )

    """The name of the variable is equal to the string parameter
    Tested all fields.*"""

    boolean_variable_1 = fields.Boolean(string='Boolean Variable 1',
                                        help="Help")
    boolean_variable_2 = fields.Boolean("Boolean Variable 2", help="Help")

    char_variable_1 = fields.Char(string='Char Variable 1', help="Help")
    char_variable_2 = fields.Char("Char Variable 2", help="Help")

    text_variable_1 = fields.Text(string='Text Variable 1', help="Help")
    text_variable_2 = fields.Text("Text Variable 2", help="Help")

    html_variable_1 = fields.Html(string='Html Variable 1', help="Help")
    html_variable_2 = fields.Html("Html Variable 2", help="Help")

    integer_variable_1 = fields.Integer(string='Integer Variable 1',
                                        help="Help")
    integer_variable_2 = fields.Integer("Integer Variable 2", help="Help")

    float_variable_1 = fields.Float(string='Float Variable 1', help="Help")
    float_variable_2 = fields.Float("Float Variable 2", help="Help")

    date_variable_1 = fields.Date(string='Date Variable 1', help="Help")
    date_variable_2 = fields.Date("Date Variable 2", help="Help")

    date_time_variable_1 = fields.DateTime(string='Date Time Variable 1',
                                           help="Help")
    date_time_variable_2 = fields.DateTime("Date Time Variable 2", help="Help")

    binary_variable_1 = fields.Binary(string='Binary Variable 1', help="Help")
    binary_variable_2 = fields.Binary("Binary Variable 2", help="Help")

    selection_variable_1 = fields.Selection(selection=[('a', 'A')],
                                            string='Selection Variable 1',
                                            help="Help")
    selection_variable_2 = fields.Selection([('a', 'A')],
                                            "Selection Variable 2",
                                            help="Help")

    reference_variable_1 = fields.Reference(selection=[('res.user', 'User')],
                                            string="Reference Variable 1",
                                            help="Help")
    reference_variable_2 = fields.Reference([('res.user', 'User')],
                                            "Reference Variable 2",
                                            help="Help")

    many_2_one_variable_1 = fields.Many2one(comodel_name='res.users',
                                            string='Many 2 One Variable 1',
                                            help="Help")
    many_2_one_variable_2 = fields.Many2one('res.users',
                                            "Many 2 One Variable 2",
                                            help="Help")

    one_2_many_variable_1 = fields.One2many(comodel_name='res.users',
                                            inverse_name='rel_id',
                                            string='One 2 Many Variable 1',
                                            help="Help")
    one_2_many_variable_2 = fields.One2many('res.users',
                                            'rel_id',
                                            "One 2 Many Variable 2",
                                            help="Help")

    many_2_many_variable_1 = fields.Many2many(comodel_name='res.users',
                                              relation='table_name',
                                              column1='col_name',
                                              column2='other_col_name',
                                              string='Many 2 Many Variable 1',
                                              help="Help")
    many_2_many_variable_2 = fields.Many2many('res.users',
                                              'table_name',
                                              'col_name',
                                              'other_col_name',
                                              "Many 2 Many Variable 2",
                                              help="Help")

    field_case_sensitive = fields.Char(
        'Field Case SENSITIVE',
        help="Field case sensitive"
    )

    name_equal_to_string = fields.Float(
        "Name equal to string",
        help="Name Equal To String"
    )

    many_2_one = fields.Many2one(
        'res.users',
        "Many 2 One",
        help="Many 2 one"
    )

    many_2_many = fields.Many2many(
        'res.users',
        'relation',
        'fk_column_from',
        'fk_column_to',
        "Many 2 many",
        help="Many 2 Many"
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
        # Shouldn't show error from lint
        raise ZeroDivisionError
        raise ZeroDivisionError()

    def my_method11(self):
        # A example of built-in raise with parameters
        # Shouldn't show error from lint
        raise ZeroDivisionError("String without translation")
        # raise without class-exception to increase coverage
        raise
        raise "obsolete case"

    def my_method12(self):
        # Should show error
        raise exceptions.Warning(
            'String with params format {p1}'.format(p1='v1'))
        raise exceptions.Warning(
            'qp2w String with params format %(p1)s' % {'p1': 'v1'})

    def my_method13(self):
        # Shouldn't show error
        raise exceptions.Warning(_(
            'String with params format {p1}').format(p1='v1'))
        raise exceptions.Warning(_(
            'String with params format {p1}'.format(p1='v1')))
        raise exceptions.Warning(_(
            'String with params format %(p1)s') % {'p1': 'v1'})
        raise exceptions.Warning(_(
            'String with params format %(p1)s' % {'p1': 'v1'}))

    def old_api_method_alias(self, cursor, user, ids, context=None):  # old api
        pass

    def sql_method(self, ids, cr):
        # Use of query parameters: nothing wrong here
        self._cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        self.env.cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))
        self.cr.execute(
            'SELECT name FROM account WHERE id IN %s', (tuple(ids),))

    def sql_injection_ignored_cases(self, ids, cr2):
        # This cr.execute2 or cr2.execute should not be detected
        self._cr.execute2(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        cr2.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))

        # Ignore when the query is built using private attributes
        self._cr.execute(
            'DELETE FROM %s WHERE id IN %%s' % self._table, (tuple(ids),))

    # old api
    def sql_injection_modulo_operator(self, cr, uid, ids, context=None):
        # Use of % operator: risky
        self._cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        self.env.cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))
        self.cr.execute(
            'SELECT name FROM account WHERE id IN %s' % (tuple(ids),))

        operator = 'WHERE'
        self._cr.execute(
            'SELECT name FROM account %s id IN %%s' % operator, ids)

        var = 'SELECT name FROM account WHERE id IN %s'
        values = ([1, 2, 3, ], )
        self._cr.execute(var % values)

    def sql_injection_executemany(self, ids, cr, v1, v2):
        # Check executemany() as well
        self.cr.executemany(
            'INSERT INTO account VALUES (%s, %s)' % (v1, v2))

    def sql_injection_format(self, ids, cr):
        # Use of .format(): risky
        self.cr.execute(
            'SELECT name FROM account WHERE id IN {}'.format(ids))

    def sql_injection_plus_operator(self, ids, cr):
        # Use of +: risky
        self.cr.execute(
            'SELECT name FROM account WHERE id IN ' + str(tuple(ids)))

        operator = 'WHERE'
        self._cr.execute(
            'SELECT name FROM account ' + operator + ' id IN %s', ids)
        self.cr.execute(
            ('SELECT name FROM account ' + operator + ' id IN (1)'))
        self.cr.execute(
            'SELECT name FROM account ' +
            operator +
            ' id IN %s' % (tuple(ids),))
        self.cr.execute(
            ('SELECT name FROM account ' +
             operator +
             ' id IN %s') % (tuple(ids),))

    def sql_injection_before(self, ids):
        # query built before execute: risky as well

        var = 'SELECT name FROM account WHERE id IN %s' % tuple(ids)
        self._cr.execute(var)

        var[1] = 'SELECT name FROM account WHERE id IN %s' % tuple(ids)
        self._cr.execute(var[1])
