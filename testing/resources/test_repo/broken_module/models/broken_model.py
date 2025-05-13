# coding: utf-8

import psycopg2
from psycopg2 import sql
from psycopg2.sql import SQL, Identifier
import requests
from requests import (
    delete, get, head, options, patch, post, put, request)
from requests import (
    delete as delete_r, get as get_r, head as head_r,
    options as options_r, patch as patch_r, post as post_r,
    put as put_r, request as request_r)

import urllib
from urllib.request import urlopen
from urllib.request import urlopen as urlopen_r

import suds.client
from suds.client import Client
from suds.client import Client as Client_r

import http.client
from http.client import HTTPConnection, HTTPSConnection
from http.client import (
    HTTPConnection as HTTPConnection_r,
    HTTPSConnection as HTTPSConnection_r,
)

import smtplib
import smtplib as smtplib_r
from smtplib import SMTP
from smtplib import SMTP as SMTP_r

import serial
import serial as serial_r
from serial import Serial
from serial import Serial as Serial_r

import ftplib
import ftplib as ftplib_r
from ftplib import FTP
from ftplib import FTP as ftp_r

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo import exceptions
from odoo.tools.translate import LazyTranslate


# Relatives import for odoo addons
from odoo.addons.broken_module import broken_model as broken_model1
from odoo.addons import broken_module as broken_module1
import odoo.addons.broken_module as broken_module2
import odoo.addons.broken_module.broken_model as broken_model2

import odoo.addons.iap.models.iap.jsonrpc
from odoo.addons.iap.models.iap import jsonrpc
from odoo.addons.iap.models import iap

import odoo.models
from odoo import tools

import itertools
from itertools import groupby

_lt = LazyTranslate(__name__)
other_field = fields.Char()

DOMAIN_GOOD = '[("type", "=", "Product")]'


def function_no_method():
    return broken_model1, broken_module1, broken_module2, broken_model2


def fields_view_get():
    return "Not part of a model, i'm free"

class TestModel2(odoo.models.Model):
    def _compute_name2(self):
        # Compute called from string with write defined before
        self.write({"name": "hello"})
        for rec in self:
            rec.write({"name": "world"})
        users = self.env["res.users"].browse([1,2,3])
        for user in users:
            user.write({"name": "moy6"})
        users.write({"name": "moy8"})
        with open("file.txt", "w") as f_obj:
            f_obj.write("write file allowed")
        unknown_type_object = self._get_object()
        unknown_type_object.write('write not self.browse allowed')

    def _default(self):
        pass

    def _domain(self):
        pass

    name2 = fields.Char(compute='_compute_name2')

    default1 = fields.Char(default='good_default')  # good default
    default2 = fields.Char(default=lambda self: self._default())  # good default
    default3 = fields.Char(default=_default)  # bad default
    default4 = fields.Date(default=fields.Date.context_today)  # good default

    domain1 = fields.Many2one("res.partner", domain=_domain)  # bad domain
    domain2 = fields.Many2one("res.partner", domain=lambda self: self._domain())  # good domain
    domain3 = fields.Many2one("res.partner", domain=[("type", "=", "Product")])  # good domain
    domain4 = fields.Many2one("res.partner", domain='[("type", "=", "Product")]')  # good domain
    domain5 = fields.Many2one("res.partner", domain='[("type", "=", "Product")]')  # good domain
    domain6 = fields.Many2one("res.partner", domain=DOMAIN_GOOD)  # good domain

    def fields_view_get(self):
        return "Deprecated in Odoo 16.0!!!"

    def custom_deprecated_method_just_because(self):
        return "this method is deprecated because i said so in the options" + self.name2

    def another_deprecated_model_method(self):
        return self.name2

class TestModel(models.Model):
    _name = 'test.model'

    _inherit = ['mail.thread']

    _columns = {}  # deprecated columns
    _defaults = {}  # deprecated defaults
    length = fields.Integer()  # Deprecated length by js errors

    def _compute_name(self):
        var = itertools.groupby([(1,2,3), (3,4,5)], key=lambda x: x[0])
        var2 = groupby([(1,2,3), (3,4,5)], key=lambda x: x[0])
        var3 = tools.groupby([(1,2,3), (3,4,5)], key=lambda x: x[0])
        # Compute called from string with write defined before
        self.write({"name": "hello"})
        for rec in self:
            rec.write({"name": "world"})
        users = self.env["res.users"].browse([1,2,3])
        for user in users:
            user.write({"name": "moy6"})
        users.write({"name": "moy8"})
        with open("file.txt", "w") as f_obj:
            f_obj.write("write file allowed")
        unknown_type_object = self._get_object()
        unknown_type_object.write('write not self.browse allowed')
        self.write({"name": "hello"})  # pylint: disable=no-write-in-compute

    def _search_name(self):
        pass

    def _inverse_name(self):
        pass

    def _compute_with_method_def(self):
        # Compute called from funct-def with write
        self.write({"name": "hello"})
        for rec in self:
            rec.write({"name": "world"})
        users = self.env["res.users"].browse([1,2,3])
        for user in users:
            user.write({"name": "moy6"})
        with open("file.txt", "w") as f_obj:
            f_obj.write("write file allowed")
        users.write({"name": "moy8"})
        unknown_type_object = self._get_object()
        unknown_type_object.write('write not self.browse allowed')
        self.write({"name": "hello"})  # pylint: disable=no-write-in-compute

    name = fields.Char(
        _(u"Näme"),  # Don't need translate
        help=u"My hëlp",
        required=False,
        compute='_compute_name',  # good compute method name
        search='_search_name',  # good search method name
        inverse='_inverse_name',  # good inverse method name
    )

    name2 = fields.Char(
        compute=_compute_name,  # bad string-method-name
        search=_search_name,  # bad string-method-name
        inverse=_inverse_name,  # bad string-method-name
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
    field_related = fields.Char('Field Related', related='model_id.related_field')
    other_field_related = fields.Char(
        related='model_id.related_field', string='Other Field Related')
    compute_with_method_def = fields.Char(compute=_compute_with_method_def)

    def my_method_compute(self):
        # Compute called from string with write defined after
        self.write({"name": "hello"})
        for rec in self:
            rec.write({"name": "world"})
        users = self.env["res.users"].browse([1,2,3])
        for user in users:
            user.write({"name": "moy6"})
        users.write({"name": "moy8"})
        with open("file.txt", "w") as f_obj:
            f_obj.write("write file allowed")
        unknown_type_object = self._get_object()
        unknown_type_object.write('write not self.browse allowed')
        self.write({"name": "hello"})  # pylint: disable=no-write-in-compute

    # This is a inherit overwrite field then don't should show errors related
    # with creation of fields.
    def method_date(self):
        date = fields.Date.to_string(
            fields.Datetime.context_timestamp(self,
                                              timestamp=fields.Datetime.now())
        )
        self.with_context({'overwrite_context': True}).write({})
        ctx = {'overwrite_context': True}
        self.with_context(ctx).write({})
        ctx2 = ctx
        self.with_context(ctx2).write({})

        self.with_context(**ctx).write({})
        self.with_context(overwrite_context=False).write({})
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

        # Message post without translation function
        self.message_post(subject='Subject not translatable',
                          body='Body not translatable %s' % variable1)
        self.message_post(subject='Subject not translatable %(variable)s' %
                          {'variable': variable1},
                          body='Body not translatable {}'.format(variable1),
                          message_type='notification')
        self.message_post('Body not translatable',
                          'Subject not translatable {a}'.format(a=variable1))
        self.message_post('Body not translatable %s' % variable1,
                          'Subject not translatable %(variable)s' %
                          {'variable': variable1})
        self.message_post('Body not translatable',
                          subject='Subject not translatable')
        self.message_post(body='<h1>%s</h1><p>%s</p>' % (
            _('Paragraph translatable'), 'Paragraph not translatable'))

        # Message post with translation function
        self.message_post(subject=_('Subject translatable'),
                          body=_('Body translatable'))
        self.message_post(_('Body translatable'),
                          _('Subject translatable'))
        self.message_post(_('Body translatable'),
                          subject=_('Subject translatable'))
        self.message_post(_('A CDR has been recovered for %s') % (variable1,))
        self.message_post(_('A CDR has been recovered for %s') % variable1)
        self.message_post(_('Var {a}').format(a=variable1))
        self.message_post(_('Var %(variable)s') % {'variable': variable1})
        self.message_post(subject=_('Subject translatable'),
                          body=_('Body translatable %s') % variable1)
        self.message_post(subject=_('Subject translatable %(variable)s') %
                          {'variable': variable1},
                          message_type='notification')
        self.message_post(_('Body translatable'),
                          _('Subject translatable {a}').format(a=variable1))
        self.message_post(_('Body translatable %s') % variable1,
                          _('Subject translatable %(variable)s') %
                          {'variable': variable1})
        self.message_post('<p>%s</p>' % _('Body translatable'))
        self.message_post(body='<p>%s</p>' % _('Body translatable'))

        # There is no way to know if the variable is translated, then ignoring
        self.message_post(variable1)
        self.message_post(body=variable1 + variable1)
        self.message_post(body=(variable1 + variable1))
        self.message_post(body=variable1 % variable1)
        self.message_post(body=(variable1 % variable1))

        # translation function with variables in the term
        variable2 = variable1
        self.message_post(_('Variable not translatable: %s' % variable1))
        self.message_post(_('Variables not translatable: %s, %s' % (
            variable1, variable2)))
        self.message_post(body=_('Variable not translatable: %s' % variable1))
        self.message_post(body=_('Variables not translatable: %s %s' % (
            variable1, variable2)))
        error_msg = _('Variable not translatable: %s' % variable1)
        error_msg = _('Variables not translatable: %s, %s' % (
            variable1, variable2))
        error_msg = _('Variable not translatable: {}'.format(variable1))
        error_msg = _('Variables not translatable: {}, {variable2}'.format(
            variable1, variable2=variable2))

        # string with parameters without name
        # so you can't change the order in the translation
        _('%s %d') % ('hello', 3)
        _('%s %s') % ('hello', 'world')
        _('{} {}').format('hello', 3)
        _('{} {}').format('hello', 'world')

        # Valid cases
        _('%(strname)s') % {'strname': 'hello'}
        _('%(strname)s %(intname)d') % {'strname': 'hello', 'intname': 3}
        _('%s') % 'hello'
        _('%d') % 3
        _('{}').format('hello')
        _('{}').format(3)

        # It raised exception but it was already fixed
        msg = "Invalid not _ method %s".lstrip() % "value"
        # It should emit message but binop.left is showing "lstrip" only instead of "_"
        self.message_post(_('Double method _ and lstrtip %s').lstrip() % (variable1,))  # TODO: Emit message for this case
        return error_msg

    def my_method11(self, variable1):
        #  Shouldn't show error of field-argument-translate
        self.my_method2(self.env._('hello world'))

        # Message post with new translation function
        self.message_post(subject=self.env._('Subject translatable'),
                          body=self.env._('Body translatable'))
        self.message_post(self.env._('Body translatable'),
                          self.env._('Subject translatable'))
        self.message_post(self.env._('Body translatable'),
                          subject=self.env._('Subject translatable'))
        self.message_post(self.env._('A CDR has been recovered for %s') % (variable1,))
        self.message_post(self.env._('A CDR has been recovered for %s') % variable1)
        self.message_post(self.env._('Var {a}').format(a=variable1))
        self.message_post(self.env._('Var %(variable)s') % {'variable': variable1})
        self.message_post(subject=self.env._('Subject translatable'),
                          body=self.env._('Body translatable %s') % variable1)
        self.message_post(subject=self.env._('Subject translatable %(variable)s') %
                          {'variable': variable1},
                          message_type='notification')
        self.message_post(self.env._('Body translatable'),
                          self.env._('Subject translatable {a}').format(a=variable1))
        self.message_post(self.env._('Body translatable %s') % variable1,
                          self.env._('Subject translatable %(variable)s') %
                          {'variable': variable1})
        self.message_post('<p>%s</p>' % self.env._('Body translatable'))
        self.message_post(body='<p>%s</p>' % self.env._('Body translatable'))

        # translation new function with variables in the term
        variable2 = variable1
        self.message_post(self.env._('Variable not translatable: %s' % variable1))
        self.message_post(self.env._('Variables not translatable: %s, %s' % (
            variable1, variable2)))
        self.message_post(body=self.env._('Variable not translatable: %s' % variable1))
        self.message_post(body=self.env._('Variables not translatable: %s %s' % (
            variable1, variable2)))
        error_msg = self.env._('Variable not translatable: %s' % variable1)
        error_msg = self.env._('Variables not translatable: %s, %s' % (
            variable1, variable2))
        error_msg = self.env._('Variable not translatable: {}'.format(variable1))
        error_msg = self.env._('Variables not translatable: {}, {variable2}'.format(
            variable1, variable2=variable2))

        # string with parameters without name
        # so you can't change the order in the translation
        self.env._('%s %d') % ('hello', 3)
        self.env._('%s %s') % ('hello', 'world')
        self.env._('{} {}').format('hello', 3)
        self.env._('{} {}').format('hello', 'world')

        # Valid cases
        self.env._('%(strname)s') % {'strname': 'hello'}
        self.env._('%(strname)s %(intname)d') % {'strname': 'hello', 'intname': 3}
        self.env._('%s') % 'hello'
        self.env._('%d') % 3
        self.env._('{}').format('hello')
        self.env._('{}').format(3)

        # It raised exception but it was already fixed
        msg = "Invalid not _ method %s".lstrip() % "value"
        # It should emit message but binop.left is showing "lstrip" only instead of "_"
        self.message_post(self.env._('Double method _ and lstrtip %s').lstrip() % (variable1,))  # TODO: Emit message for this case
        return error_msg

    def my_method111(self, variable1):
        #  Shouldn't show error of field-argument-translate
        self.my_method2(_lt('hello world'))

        # Message post with new translation function
        self.message_post(subject=_lt('Subject translatable'),
                          body=_lt('Body translatable'))
        self.message_post(_lt('Body translatable'),
                          _lt('Subject translatable'))
        self.message_post(_lt('Body translatable'),
                          subject=_lt('Subject translatable'))
        self.message_post(_lt('A CDR has been recovered for %s') % (variable1,))
        self.message_post(_lt('A CDR has been recovered for %s') % variable1)
        self.message_post(_lt('Var {a}').format(a=variable1))
        self.message_post(_lt('Var %(variable)s') % {'variable': variable1})
        self.message_post(subject=_lt('Subject translatable'),
                          body=_lt('Body translatable %s') % variable1)
        self.message_post(subject=_lt('Subject translatable %(variable)s') %
                          {'variable': variable1},
                          message_type='notification')
        self.message_post(_lt('Body translatable'),
                          _lt('Subject translatable {a}').format(a=variable1))
        self.message_post(_lt('Body translatable %s') % variable1,
                          _lt('Subject translatable %(variable)s') %
                          {'variable': variable1})
        self.message_post('<p>%s</p>' % _lt('Body translatable'))
        self.message_post(body='<p>%s</p>' % _lt('Body translatable'))

        # translation new function with variables in the term
        variable2 = variable1
        self.message_post(_lt('Variable not translatable: %s' % variable1))
        self.message_post(_lt('Variables not translatable: %s, %s' % (
            variable1, variable2)))
        self.message_post(body=_lt('Variable not translatable: %s' % variable1))
        self.message_post(body=_lt('Variables not translatable: %s %s' % (
            variable1, variable2)))
        error_msg = _lt('Variable not translatable: %s' % variable1)
        error_msg = _lt('Variables not translatable: %s, %s' % (
            variable1, variable2))
        error_msg = _lt('Variable not translatable: {}'.format(variable1))
        error_msg = _lt('Variables not translatable: {}, {variable2}'.format(
            variable1, variable2=variable2))

        # string with parameters without name
        # so you can't change the order in the translation
        _lt('%s %d') % ('hello', 3)
        _lt('%s %s') % ('hello', 'world')
        _lt('{} {}').format('hello', 3)
        _lt('{} {}').format('hello', 'world')

        # Valid cases
        _lt('%(strname)s') % {'strname': 'hello'}
        _lt('%(strname)s %(intname)d') % {'strname': 'hello', 'intname': 3}
        _lt('%s') % 'hello'
        _lt('%d') % 3
        _lt('{}').format('hello')
        _lt('{}').format(3)

        # It raised exception but it was already fixed
        msg = "Invalid not _ method %s".lstrip() % "value"
        # It should emit message but binop.left is showing "lstrip" only instead of "_"
        self.message_post(_lt('Double method _ and lstrtip %s').lstrip() % (variable1,))  # TODO: Emit message for this case
        return error_msg

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

    def my_method71(self):
        user_id = 1
        if user_id != 99:
            # Method with translation
            raise UserError(self.env._('String with translation'))

    def my_method72(self):
        user_id = 1
        if user_id != 99:
            # Method with translation
            raise UserError(_lt('String with translation'))

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

    def my_method131(self):
        # Shouldn't show error
        raise exceptions.Warning(self.env._(
            'String with params format {p1}').format(p1='v1'))
        raise exceptions.Warning(self.env._(
            'String with params format {p1}'.format(p1='v1')))
        raise exceptions.Warning(self.env._(
            'String with params format %(p1)s') % {'p1': 'v1'})
        raise exceptions.Warning(self.env._(
            'String with params format %(p1)s' % {'p1': 'v1'}))

    def my_method132(self):
        # Shouldn't show error
        raise exceptions.Warning(_lt(
            'String with params format {p1}').format(p1='v1'))
        raise exceptions.Warning(_lt(
            'String with params format {p1}'.format(p1='v1')))
        raise exceptions.Warning(_lt(
            'String with params format %(p1)s') % {'p1': 'v1'})
        raise exceptions.Warning(_lt(
            'String with params format %(p1)s' % {'p1': 'v1'}))

    def my_method14(self):
        _("String with missing args %s %s", "param1")
        _("String with missing kwargs %(param1)s", param2="hola")
        _(f"String with f-interpolation {self.param1}")
        _("String unsupported character %y", "param1")
        _("format truncated %s%", 'param1')
        _("too many args %s", 'param1', 'param2')

        _("multi-positional args without placeholders %s %s", 'param1', 'param2')

        _("multi-positional args without placeholders {} {}".format('param1', 'param2'))

        _("String with correct args %s", "param1")
        _("String with correct kwargs %(param1)s", param1="hola")

    def my_method141(self):
        self.env._("String with missing args %s %s", "param1")
        self.env._("String with missing kwargs %(param1)s", param2="hola")
        self.env._(f"String with f-interpolation {self.param1}")
        self.env._("String unsupported character %y", "param1")
        self.env._("format truncated %s%", 'param1')
        self.env._("too many args %s", 'param1', 'param2')

        self.env._("multi-positional args without placeholders %s %s", 'param1', 'param2')

        self.env._("multi-positional args without placeholders {} {}".format('param1', 'param2'))

        self.env._("String with correct args %s", "param1")
        self.env._("String with correct kwargs %(param1)s", param1="hola")

    def my_method142(self):
        _lt("String with missing args %s %s", "param1")
        _lt("String with missing kwargs %(param1)s", param2="hola")
        _lt(f"String with f-interpolation {self.param1}")
        _lt("String unsupported character %y", "param1")
        _lt("format truncated %s%", 'param1')
        _lt("too many args %s", 'param1', 'param2')

        _lt("multi-positional args without placeholders %s %s", 'param1', 'param2')

        _lt("multi-positional args without placeholders {} {}".format('param1', 'param2'))

        _lt("String with correct args %s", "param1")
        _lt("String with correct kwargs %(param1)s", param1="hola")

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

        # Ignore string parsed with "".format() if args are psycopg2.sql.* calls
        query = "SELECT * FROM table"
        # imported from pyscopg2 import sql
        self._cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table),
                sql.SQL(query)
            ))
        self._cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {table} as ({query})""").format(
                table=sql.Identifier(self._table),
                query=sql.SQL(query),
            ))
        # imported from pyscopg2.sql import SQL, Identifier
        self._cr.execute(
            SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                Identifier(self._table),
                SQL(query),
            ))
        self._cr.execute(
            SQL("""CREATE or REPLACE VIEW {table} as ({query})""").format(
                table=Identifier(self._table),
                query=SQL(query),
            ))
        # imported from pyscopg2 direclty
        self._cr.execute(
            psycopg2.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                psycopg2.sql.Identifier(self._table),
                psycopg2.sql.SQL(query),
            ))
        self._cr.execute(
            psycopg2.sql.SQL("""CREATE or REPLACE VIEW {table} as ({query})""").format(
                table=Identifier(self._table),
                query=SQL(query),
            ))
        # Variables build using pyscopg2.sql.* callers
        table = Identifier('table_name')
        sql_query = SQL(query)
        # format params
        self._cr.execute(
            SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                table,
                sql_query,
            ))
        # format dict
        self._cr.execute(
            SQL("""CREATE or REPLACE VIEW {table} as ({query})""").format(
                table=table,
                query=sql_query,
            ))

        self._cr.execute(
            'SELECT name FROM %(table)s' % {'table': self._table})

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
        # Ignore sql-injection because of there is a parameter e.g. "ids"
        self._cr.execute(
            'SELECT name FROM account %s id IN %%s' % operator, ids)

        var = 'SELECT name FROM account WHERE id IN %s'
        values = ([1, 2, 3, ], )
        self._cr.execute(var % values)

        self._cr.execute(
            'SELECT name FROM account WHERE id IN %(ids)s' % {'ids': ids})

    def sql_injection_executemany(self, ids, cr, v1, v2):
        # Check executemany() as well
        self.cr.executemany(
            'INSERT INTO account VALUES (%s, %s)' % (v1, v2))

    def sql_injection_format(self, ids, cr):
        # Use of .format(): risky
        self.cr.execute(
            'SELECT name FROM account WHERE id IN {}'.format(ids))

        var = 'SELECT name FROM account WHERE id IN {}'
        values = (1, 2, 3)
        self._cr.execute(var.format(values))

        self.cr.execute(
            'SELECT name FROM account WHERE id IN {ids}'.format(ids=ids))

    def sql_injection_plus_operator(self, ids, cr):
        # Use of +: risky
        self.cr.execute(
            'SELECT name FROM account WHERE id IN ' + str(tuple(ids)))

        operator = 'WHERE'
        # Ignore sql-injection because of there is a parameter e.g. "ids"
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

        var = 'SELECT name FROM account WHERE id IN %(ids)s' % {'ids': tuple(ids)}
        self._cr.execute(var)

        var[1] = 'SELECT name FROM account WHERE id IN %(ids)s' % {'ids': tuple(ids)}
        self._cr.execute(var[1])

    def sql_no_injection_private_attributes(self, _variable, variable):
        # Skip sql-injection using private attributes
        self._cr.execute(
            "CREATE VIEW %s AS (SELECT * FROM res_partner)" % self._table)
        # Real sql-injection cases
        self._cr.execute(
            "CREATE VIEW %s AS (SELECT * FROM res_partner)" % self.table)
        self._cr.execute(
            "CREATE VIEW %s AS (SELECT * FROM res_partner)" % _variable)
        self._cr.execute(
            "CREATE VIEW %s AS (SELECT * FROM res_partner)" % variable)

    def sql_no_injection_private_methods(self):
        # Skip sql-injection using private methods
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW %s AS (
                %s %s %s %s
            )
        """
            % (
                self._table,
                self._select(),
                self._from(),
                self._where(),
                self._group_by(),
            )
        )

    def sql_no_injection_constants(self):
        self.env.cr.execute("SELECT * FROM %s" % 'table_constant')
        self.env.cr.execute("SELECT * FROM {}".format('table_constant'))
        self.env.cr.execute(
            "SELECT * FROM %(table_variable)s" % {'table_variable': 'table_constant'})

    def func(self, a):
        length = len(a)
        return length

    def requests_test(self):
        # requests without timeout
        requests.delete('http://localhost')
        requests.get('http://localhost')
        requests.head('http://localhost')
        requests.options('http://localhost')
        requests.patch('http://localhost')
        requests.post('http://localhost')
        requests.put('http://localhost')
        requests.request('call', 'http://localhost')

        delete_r('http://localhost')
        get_r('http://localhost')
        head_r('http://localhost')
        options_r('http://localhost')
        patch_r('http://localhost')
        post_r('http://localhost')
        put_r('http://localhost')
        request_r('call', 'http://localhost')

        delete('http://localhost')
        get('http://localhost')
        head('http://localhost')
        options('http://localhost')
        patch('http://localhost')
        post('http://localhost')
        put('http://localhost')
        request('call', 'http://localhost')

        # requests valid cases
        requests.delete('http://localhost', timeout=10)
        requests.get('http://localhost', timeout=10)
        requests.head('http://localhost', timeout=10)
        requests.options('http://localhost', timeout=10)
        requests.patch('http://localhost', timeout=10)
        requests.post('http://localhost', timeout=10)
        requests.put('http://localhost', timeout=10)
        requests.request('call', 'http://localhost', timeout=10)

        delete_r('http://localhost', timeout=10)
        get_r('http://localhost', timeout=10)
        head_r('http://localhost', timeout=10)
        options_r('http://localhost', timeout=10)
        patch_r('http://localhost', timeout=10)
        post_r('http://localhost', timeout=10)
        put_r('http://localhost', timeout=10)
        request_r('call', 'http://localhost', timeout=10)

        delete('http://localhost', timeout=10)
        get('http://localhost', timeout=10)
        head('http://localhost', timeout=10)
        options('http://localhost', timeout=10)
        patch('http://localhost', timeout=10)
        post('http://localhost', timeout=10)
        put('http://localhost', timeout=10)
        request('call', 'http://localhost', timeout=10)

        # urllib without timeout
        urllib.request.urlopen('http://localhost')
        urlopen('http://localhost')
        urlopen_r('http://localhost')

        # urllib valid cases
        urllib.request.urlopen('http://localhost', timeout=10)
        urlopen('http://localhost', timeout=10)
        urlopen_r('http://localhost', timeout=10)

        # suds without timeout
        suds.client.Client('http://localhost')
        Client('http://localhost')
        Client_r('http://localhost')

        # suds valid cases
        suds.client.Client('http://localhost', timeout=10)
        Client('http://localhost', timeout=10)
        Client_r('http://localhost', timeout=10)

        # http.client without timeout
        http.client.HTTPConnection('http://localhost')
        http.client.HTTPSConnection('http://localhost')
        HTTPConnection('http://localhost')
        HTTPSConnection('http://localhost')
        HTTPConnection_r('http://localhost')
        HTTPSConnection_r('http://localhost')

        # http.client valid cases
        http.client.HTTPConnection('http://localhost', timeout=10)
        http.client.HTTPSConnection('http://localhost', timeout=10)
        HTTPConnection('http://localhost', timeout=10)
        HTTPSConnection('http://localhost', timeout=10)
        HTTPConnection_r('http://localhost', timeout=10)
        HTTPSConnection_r('http://localhost', timeout=10)

        # smtplib without timeout
        smtplib.SMTP('http://localhost')
        smtplib_r.SMTP('http://localhost')
        SMTP('http://localhost')
        SMTP_r('http://localhost')

        # smtplib valid cases
        smtplib.SMTP('http://localhost', timeout=10)
        smtplib_r.SMTP('http://localhost', timeout=10)
        SMTP('http://localhost', timeout=10)
        SMTP_r('http://localhost', timeout=10)

        # Serial without timeout
        serial.Serial('/dev/ttyS1')
        serial_r.Serial('/dev/ttyS1')
        Serial('/dev/ttyS1')
        Serial_r('/dev/ttyS1')

        # serial valid cases
        serial.Serial('/dev/ttyS1', timeout=10)
        serial_r.Serial('/dev/ttyS1', timeout=10)
        Serial('/dev/ttyS1', timeout=10)
        Serial_r('/dev/ttyS1', timeout=10)

        # odoo.addons.iap without timeout
        odoo.addons.iap.models.iap.jsonrpc('http://localhost')
        jsonrpc('http://localhost')
        iap.jsonrpc('http://localhost')

        # odoo.addons.iap valid cases
        odoo.addons.iap.models.iap.jsonrpc('http://localhost', timeout=10)
        jsonrpc('http://localhost', timeout=10)
        iap.jsonrpc('http://localhost', timeout=10)

        # FTP  without timeout
        ftplib.FTP('localhost')
        ftplib_r.FTP('localhost')
        FTP('localhost')
        ftp_r('localhost')

        # FTP valid cases
        ftplib.FTP('localhost', timeout=10)
        ftplib_r.FTP('localhost', timeout=10)
        FTP('localhost', timeout=10)
        ftp_r('localhost', timeout=10)


class TestModel3(
    odoo.models.TransientModel):
    # no-wizard-in-model
    pass


class TestModel4(
    odoo.models.TransientModel):
    # Valid no-wizard-in-model
    _inherit = "res.config.settings"


class TestModel5(
    odoo.models.TransientModel):  # pylint: disable=no-wizard-in-models
    # Valid no-wizard-in-model
    _inherit = "my.transient.model"


class NoOdoo(object):
    length = 0


if __name__ == '__main__':
    self = None
    queries = [
        "SELECT id FROM res_partner",
        "SELECT id FROM res_users",
    ]
    for query in queries:
        self.env.cr.execute(query)

class Ccc(object):

    class Ddd(object):
        pass

    class Eee(Ddd):
        pass
