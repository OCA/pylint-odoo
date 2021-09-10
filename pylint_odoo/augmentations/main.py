
import os

from astroid import FunctionDef, Module
from pylint.checkers.base import BasicChecker, NameChecker
from pylint.checkers.imports import ImportsChecker
from pylint.checkers.variables import VariablesChecker
from pylint_plugin_utils import suppress_message

from .. import settings


def is_manifest_file(node):
    """Verify if the node file is a manifest file
    :return: Boolean `True` if is manifest file else `False`"""
    filename = os.path.basename(node.root().file)
    is_manifest = filename in settings.MANIFEST_FILES
    return is_manifest


def is_valid_openerp_osv_deprecated(node):
    """Verify if the node is a import deprecated but valid

    E.g. "from openerp.osv import expression" is valid
        but "from openerp.osv import {other} is invalid"
    :returns: True if is a valid import
    """
    submodules = [submodule[0] for submodule in node.names]
    modname = getattr(node, 'modname', [])
    if len(submodules) == 1 and (
            submodules[0] == 'openerp.osv.expression' or
            submodules[0] == 'expression' and 'openerp.osv' in modname
    ) or 'openerp.osv.expression' in modname:
        return True
    return False


def is_migration_path(node):
    """module/x.y.z/migrations/pre-migration.py path has a few false negatives

    Considering that standard method is:
        def migrate(cr, version):

    - invalid-name (C0103) for module and argument name
    e.g. "pre-migration.py" instead of pre_migration.py
    e.g. "cr" for cursor

    - unused-argument (W0613) for argument
    e.g. "version" for version of Odoo

    node: can be module or functiondef
    """

    # get 'migrations' from 'module/migrations/x.y.z/pre-migration.py'
    if os.path.basename(os.path.dirname(os.path.dirname(
            node.root().file))) != 'migrations':
        return False

    # pre-migration.py
    if (isinstance(node, Module) and '-' in node.name or
            # def migrate(cr, version):
            isinstance(node, FunctionDef) and node.name == 'migrate'):
        return True
    return False


def apply_augmentations(linter):
    """Apply suppression rules."""

    # W0104 - pointless-statement
    # manifest file have a valid pointless-statement dict
    discard = hasattr(BasicChecker, 'visit_discard') and \
        BasicChecker.visit_discard or BasicChecker.visit_expr
    suppress_message(linter, discard, 'W0104', is_manifest_file)

    # W0402 - deprecated-module valid openerp.osv.expression
    discard = ImportsChecker.visit_import
    suppress_message(linter, discard, 'W0402', is_valid_openerp_osv_deprecated)
    discard = hasattr(ImportsChecker, 'visit_from') and \
        ImportsChecker.visit_from or ImportsChecker.visit_importfrom
    suppress_message(linter, discard, 'W0402', is_valid_openerp_osv_deprecated)

    # C0103 - invalid-name and W0613 - unused-argument for migrations/
    suppress_message(linter, NameChecker.visit_module, 'C0103', is_migration_path)
    suppress_message(linter, NameChecker.visit_functiondef, 'C0103', is_migration_path)
    suppress_message(linter, VariablesChecker.leave_functiondef, 'W0613',
                     is_migration_path)
