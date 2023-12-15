from odoo import SUPERUSER_ID, api
from odoo.addons.test_module import random_stuff


def method(cr, unused):
    # invalid-name cr and unused-argument unused
    return cr


def migrate(cr, version):
    # suppressed invalid-name cr and unused-argument version
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.ref('xmlid').unlink()
