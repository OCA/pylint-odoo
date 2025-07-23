import re
from contextlib import contextmanager
from typing import Literal
from unittest.mock import patch

from astroid import builder, exceptions as astroid_exceptions, nodes
from pylint.checkers import logging

from .. import misc
from .odoo_addons import OdooAddons
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
        name = OdooAddons.get_func_name(node.func)
        if name == "format" and (new_node := self.transform_formatcall2tlcall(node)):
            node = new_node
            name = OdooAddons.get_func_name(node.func)
        if name not in misc.TRANSLATION_METHODS:
            return
        with config_logging_modules(self.linter, ("odoo",)):
            self._check_log_method(node, name)

    def transform_formatcall2tlcall(self, node):
        """Transform no detectable node:
           _("lazy not detectable: {}").format("var")
        To detectable one:
           _("lazy detectable: {}".format("vat"))
        """
        if not (
            isinstance(node, nodes.Call) and isinstance(node.func, nodes.Attribute) and node.func.attrname == "format"
        ):
            return

        format_expr = node.func.expr.as_string()

        args_str = ", ".join(arg.as_string() for arg in node.args)
        kwargs_str = ", ".join(f"{kw.arg}={kw.value.as_string()}" for kw in node.keywords)
        all_args = ", ".join(item for item in [args_str, kwargs_str] if item)
        new_code = f"{format_expr[:-1]}.format({all_args}))"
        try:
            new_node = builder.extract_node(new_code)
        except astroid_exceptions.AstroidSyntaxError:
            return
        # node = self.env._('{param1}').format(param1='hello')
        # new_node = self.env._('{param1}'.format(param1='hello'))
        # new_node.args[0] = '{param1}'.format(param1='hello')
        if not new_node.args:
            return
        node_attrs = ["lineno", "col_offset", "parent", "end_lineno", "end_col_offset", "position", "fromlineno"]
        for node_attr in node_attrs:
            setattr(new_node, node_attr, getattr(node, node_attr, None))
            # Help to preserve the lineno of the first arg used from pylint/checkers/logging.py::_check_log_method
            setattr(new_node.args[0], node_attr, getattr(node, node_attr, None))
        return new_node

    def transform_binop2call(self, node):
        """Transform no detectable node:
           _("lazy not detectable: %s") % es_err.error
        To detectable one:
           _("lazy detectable: %s" % es_err.error)
        """
        new_code = f"{node.left.as_string()[:-1]} {node.op} {node.right.as_string()})"
        try:
            new_node = builder.extract_node(new_code)
        except astroid_exceptions.AstroidSyntaxError:
            return
        node_attrs = ["lineno", "col_offset", "parent", "end_lineno", "end_col_offset", "position", "fromlineno"]
        for node_attr in node_attrs:
            setattr(new_node, node_attr, getattr(node, node_attr, None))
        return new_node

    def visit_binop(self, node):
        if not isinstance(node.left, nodes.Call) or node.op != "%" or OdooAddons.get_func_name(node.left.func) != "_":
            return
        new_node = self.transform_binop2call(node)
        if new_node:
            self.visit_call(new_node)

    def _check_log_method(self, *args, **kwargs):
        with patch("pylint.checkers.logging.CHECKED_CONVENIENCE_FUNCTIONS", {"_"}):
            super()._check_log_method(*args, **kwargs)

    def _check_format_string(self, node: nodes.Call, format_arg: Literal[0, 1]) -> None:
        num_args = logging._count_supplied_tokens(node.args[format_arg + 1 :])
        # Custom revert for https://github.com/pylint-dev/pylint/commit/c23674554a7fac2fbb390cb67
        # since translation returns a string so it is a valid case for translation but not for logging
        if not num_args:
            # If no args were supplied the string is not interpolated and can contain
            # formatting characters - it's used verbatim. Don't check any further.
            return
        return super()._check_format_string(node=node, format_arg=format_arg)
