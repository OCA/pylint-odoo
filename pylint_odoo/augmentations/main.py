
import os

from pylint_plugin_utils import suppress_message
from pylint.checkers.base import BasicChecker
from .. import settings


def is_manifest_file(node):
    """Verify if the node file is a manifest file
    :return: Boolean `True` if is manifest file else `False`"""
    filename = os.path.basename(node.root().file)
    is_manifest = filename in settings.MANIFEST_FILES
    return is_manifest


def apply_augmentations(linter):
    """Apply suppression rules."""

    # W0104 - pointless-statement
    # manifest file have a valid pointless-statement dict
    discard = hasattr(BasicChecker, 'visit_discard') and \
        BasicChecker.visit_discard or BasicChecker.visit_expr
    suppress_message(linter, discard, 'W0104', is_manifest_file)
