# coding: utf-8

from __future__ import absolute_import
import expression
import expression as expr4
import manifest_lib
import openerp.osv
import openerp.osv.expression

from openerp.osv import expression as expr2
from openerp.osv import osv as osv2
from openerp.osv import osv, expression  # noqa
from openerp.osv import osv, expression as expr3  # noqa
from openerp.osv.expression import is_operator  # noqa


def dummy():
    return (expression, osv, osv2, expr2, openerp.osv.expression, openerp.osv,
            expr4, expr3, absolute_import, manifest_lib)
