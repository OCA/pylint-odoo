import re
from contextlib import contextmanager
from unittest.mock import patch

import astroid
from pylint.checkers import logging


@contextmanager
def config_logging_modules(linter, modules):
    original_logging_modules = linter.config.logging_modules
    linter.config.logging_modules = modules
    try:
        yield
    finally:
        linter.config.logging_modules = original_logging_modules


BASE_CHECKS_ID = "83"


class CustomLoggingChecker(logging.LoggingChecker):
    name = "odoolint"

    def transform_msgs(self):
        """Transform all the 'logging' messages and code to 'translation'
        from:
            - {'W1201': ('logging-*', 'logging ...', ...)}
        to:
            - {'W8301': ('translation-*', 'translation ...', ...)}
        """
        msgs = {}
        for msgid, msgattrs in self.msgs.items():
            msg_short, msg_code, msg_desc = msgattrs[:3]
            if "logging" not in msg_code.lower():  # pragma: no cover
                continue
            msg_short = msg_short.replace("logging", "odoo._")
            msgid = re.sub("12", BASE_CHECKS_ID, msgid, count=1)
            msg_code = msg_code.replace("logging", "translation")
            msgs[msgid] = (msg_short, msg_code, msg_desc) + msgattrs[3:]
        return msgs

    def add_message(self, msgid, *args, **kwargs):
        """Emit translation-not-lazy instead of logging-not-lazy"""
        msgid = msgid.replace("logging", "translation")
        return super().add_message(msgid, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.msgs = self.transform_msgs()
        super().__init__(*args, **kwargs)

    def visit_call(self, node):
        if not isinstance(node.func, astroid.Name):
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
        new_code = f"{node.left.as_string()[:-1]} % {node.right.as_string()})"
        new_node = astroid.builder.extract_node(new_code)
        node_attrs = ["lineno", "col_offset", "parent", "end_lineno", "end_col_offset", "position", "fromlineno"]
        for node_attr in node_attrs:
            setattr(new_node, node_attr, getattr(node, node_attr, None))
        return new_node

    def visit_binop(self, node):
        if not isinstance(node.left, astroid.Call):
            return
        self.visit_call(self.transform_binop2call(node))

    def _check_log_method(self, *args, **kwargs):
        with patch("pylint.checkers.logging.CHECKED_CONVENIENCE_FUNCTIONS", {"_"}):
            super()._check_log_method(*args, **kwargs)
