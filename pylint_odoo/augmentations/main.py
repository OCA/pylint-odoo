import os

from astroid import nodes
from pylint.checkers.base import BasicChecker, NameChecker
from pylint.checkers.variables import VariablesChecker
from pylint_plugin_utils import suppress_message

from .. import misc


def is_manifest_file(node):
    """Verify if the node file is a manifest file
    :return: Boolean `True` if is manifest file else `False`"""
    filename = os.path.basename(node.root().file)
    is_manifest = filename in misc.MANIFEST_FILES
    return is_manifest


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
    if os.path.basename(os.path.dirname(os.path.dirname(node.root().file))) != "migrations":
        return False

    # pre-migration.py
    # def migrate(cr, version):
    if (
        isinstance(node, nodes.Module)
        and "-" in node.name
        or isinstance(node, nodes.FunctionDef)
        and node.name == "migrate"
    ):
        return True
    return False


def apply_augmentations(linter):
    """Apply suppression rules."""

    # W0104 - pointless-statement
    # manifest file have a valid pointless-statement dict
    suppress_message(linter, BasicChecker.visit_expr, "pointless-statement", is_manifest_file)

    # C0103 - invalid-name and W0613 - unused-argument for migrations/
    suppress_message(linter, NameChecker.visit_module, "invalid-name", is_migration_path)
    suppress_message(linter, NameChecker.visit_functiondef, "invalid-name", is_migration_path)
    suppress_message(linter, VariablesChecker.leave_functiondef, "unused-argument", is_migration_path)
