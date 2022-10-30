import re
from contextlib import contextmanager
from unittest.mock import patch

from astroid import builder, nodes
from pylint.checkers import logging

from .odoo_base_checker import OdooBaseChecker


@contextmanager
def config_logging_modules(linter, modules):
    original_logging_modules = linter.config.logging_modules
    linter.config.logging_modules = modules
    try:
        yield
    finally:
        linter.config.logging_modules = original_logging_modules


def transform_msgs(msgs):
    """Transform all the 'logging' messages and code to 'translation'
    from:
        - {'W1201': ('logging-*', 'logging ...', ...)}
    to:
        - {'W8301': ('translation-*', 'translation ...', ...)}
    """
    new_msgs = {}
    for msgid, msgattrs in msgs.items():
        msg_short, msg_code, msg_desc = msgattrs[:3]
        if "logging" not in msg_code.lower():  # pragma: no cover
            continue
        msg_short = msg_short.replace("logging", "odoo._")
        msgid = re.sub("12", BASE_CHECKS_ID, msgid, count=1)
        msg_code = msg_code.replace("logging", "translation")
        new_msgs[msgid] = (msg_short, msg_code, msg_desc) + msgattrs[3:]
    return new_msgs


BASE_CHECKS_ID = "83"

ODOO_MSGS = transform_msgs(logging.MSGS)


class CustomLoggingChecker(OdooBaseChecker, logging.LoggingChecker):
    name = "odoolint"
    msgs = ODOO_MSGS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for msg_attrs in self.msgs.values():
            # checks_maxmin_odoo_version = {
            #   check-code: {
            #       "odoo_minversion": tuple(int, int),
            #       "odoo_maxversion": tuple(int, int),
            #   }
            self.checks_maxmin_odoo_version[msg_attrs[1]] = {
                "odoo_minversion": "14.0",
            }

    def add_message(self, msgid, *args, **kwargs):
        """Emit translation-* instead of logging-*
        e.g. translation-not-lazy instead of logging-not-lazy
        """
        msgid = msgid.replace("logging", "translation")
        return super().add_message(msgid, *args, **kwargs)

    def visit_call(self, node):
        if not isinstance(node.func, nodes.Name):
            return
        name = node.func.name
        with config_logging_modules(self.linter, ("odoo",)):
            self._check_log_method(node, name)

    def transform_binop2call(self, node):
        """Transform no detectable node:
           _("lazy not detectable: %s") % es_err.error
        To detectable one:
           _("lazy detectable: %s" % es_err.error)
        """
        new_code = f"{node.left.as_string()[:-1]} {node.op} {node.right.as_string()})"
        new_node = builder.extract_node(new_code)
        node_attrs = ["lineno", "col_offset", "parent", "end_lineno", "end_col_offset", "position", "fromlineno"]
        for node_attr in node_attrs:
            setattr(new_node, node_attr, getattr(node, node_attr, None))
        return new_node

    def visit_binop(self, node):
        if not isinstance(node.left, nodes.Call):
            return
        self.visit_call(self.transform_binop2call(node))

    def _check_log_method(self, *args, **kwargs):
        with patch("pylint.checkers.logging.CHECKED_CONVENIENCE_FUNCTIONS", {"_"}):
            super()._check_log_method(*args, **kwargs)
