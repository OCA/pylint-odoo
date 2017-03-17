
import os

from pylint_plugin_utils import suppress_message
from pylint.checkers.base import BasicChecker
from pylint.checkers.imports import ImportsChecker
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
