# coding: utf-8
import expression
import expression as expr4
import openerp.osv
import openerp.osv.expression

from openerp.osv import expression as expr2
from openerp.osv import osv as osv2
from openerp.osv import osv, expression  # noqa
from openerp.osv import osv, expression as expr3  # noqa


def dummy():
    return (expression, osv, osv2, expr2, openerp.osv.expression, openerp.osv,
            expr4, expr3)
