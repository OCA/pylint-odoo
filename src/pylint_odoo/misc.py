import ast
import os
import re
import string

from pylint.checkers import BaseChecker, BaseTokenChecker
from pylint.interfaces import UNDEFINED
from pylint.interfaces import IAstroidChecker, ITokenChecker


from . import settings


DFTL_VALID_ODOO_VERSIONS = [
    '4.2', '5.0', '6.0', '6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0',
    '13.0', '14.0', '15.0', '16.0',
]
DFTL_MANIFEST_VERSION_FORMAT = r"({valid_odoo_versions})\.\d+\.\d+\.\d+$"

# Regex used from https://github.com/translate/translate/blob/9de0d72437/translate/filters/checks.py#L50-L62  # noqa
PRINTF_PATTERN = re.compile(r'''
        %(                          # initial %
        (?P<boost_ord>\d+)%         # boost::format style variable order, like %1%
        |
              (?:(?P<ord>\d+)\$|    # variable order, like %1$s
              \((?P<key>\w+)\))?    # Python style variables, like %(var)s
        (?P<fullvar>
            [+#-]*                  # flags
            (?:\d+)?                # width
            (?:\.\d+)?              # precision
            (hh\|h\|l\|ll)?         # length formatting
            (?P<type>[\w@]))        # type (%s, %d, etc.)
        )''', re.VERBOSE)


class StringParseError(TypeError):
    pass


def get_plugin_msgs(pylint_run_res):
    """Get all message of this pylint plugin.
    :param pylint_run_res: Object returned by pylint.run method.
    :return: List of strings with message name.
    """
    msgs_store = pylint_run_res.linter.msgs_store

    def get_messages():
        return pylint_run_res.linter.msgs_store._messages_definitions

    messages = get_messages()

    all_plugin_msgs = []
    for key in messages:
        message = messages[key]
        checker_name =  message.msgid
        if checker_name == settings.CFG_SECTION:
            all_plugin_msgs.append(key)
    return all_plugin_msgs


def join_node_args_kwargs(node):
    """Method to join args and keywords
    :param node: node to get args and keywords
    :return: List of args
    """
    args = (getattr(node, 'args', None) or []) + \
        (getattr(node, 'keywords', None) or [])
    return args


class PylintOdooChecker(BaseChecker):

    # Auto call to `process_tokens` method
    __implements__ = IAstroidChecker

    odoo_node = None
    odoo_module_name = None
    manifest_file = None
    manifest_dict = {}

    def formatversion(self, string):
        valid_odoo_versions = self.linter._all_options[
            'valid_odoo_versions'].config.valid_odoo_versions
        valid_odoo_versions = '|'.join(
            map(re.escape, valid_odoo_versions))
        manifest_version_format = self.linter._all_options[
            'manifest_version_format'].config.manifest_version_format
        self.config.manifest_version_format_parsed = (
            manifest_version_format.format(valid_odoo_versions=valid_odoo_versions))
        return re.match(self.config.manifest_version_format_parsed, string)

    def get_manifest_file(self, node):
        """Get manifest file path
        :param node_file: String with full path of a python module file.
        :return: Full path of manifest file if exists else return None"""
        if not node.file or not os.path.isfile(node.file):
            return

        # Get 'module' part from node.name 'module.models.file'
        module_path = node.file
        node_name = node.name
        if "odoo.addons." in node_name:
            # we are into a namespace package...
            node_name = node_name.split("odoo.addons.")[1]
        if os.path.basename(node.file) == '__init__.py':
            node_name += '.__init__'
        for _ in range(node_name.count('.')):
            module_path = os.path.dirname(module_path)

        for manifest_basename in settings.MANIFEST_FILES:
            manifest_file = os.path.join(module_path, manifest_basename)
            if os.path.isfile(manifest_file):
                return manifest_file

    def wrapper_visit_module(self, node):
        """Call methods named with name-key from self.msgs
        Method should be named with next standard:
            def _check_{NAME_KEY}(self, module_path)
        by example: def _check_missing_icon(self, module_path)
                    to check missing-icon message name key
            And should return True if all fine else False.
        if a False is returned then add message of name-key.
        Assign object variables to use in methods.
        :param node: A astroid.scoped_nodes.Module
        :return: None
        """
        manifest_file = self.get_manifest_file(node)
        if manifest_file:
            self.manifest_file = manifest_file
            self.odoo_node = node
            self.odoo_module_name = os.path.basename(
                os.path.dirname(manifest_file))
            self.odoo_module_name_with_ns = "odoo.addons.{}".format(
                self.odoo_module_name
            )
            with open(self.manifest_file) as f_manifest:
                self.manifest_dict = ast.literal_eval(f_manifest.read())
        elif self.odoo_node and os.path.commonprefix(
                [os.path.dirname(self.odoo_node.file),
                 os.path.dirname(node.file)]) != os.path.dirname(
                self.odoo_node.file):
            # It's not a sub-module python of a odoo module and
            #  it's not a odoo module
            self.odoo_node = None
            self.odoo_module_name = None
            self.manifest_dict = {}
            self.manifest_file = None
        self.is_main_odoo_module = False
        if self.manifest_file and os.path.basename(node.file) == '__init__.py' and (
                node.name.count('.') == 0 or
                node.name.endswith(self.odoo_module_name_with_ns)
        ):
            self.is_main_odoo_module = True
        self.node = node
        self.module_path = os.path.dirname(node.file)
        self.module = os.path.basename(self.module_path)
        for msg_code, msg_params in sorted(self.msgs.items()):
            name_key = msg_params[1]
            self.msg_code = msg_code
            self.msg_name_key = name_key
            self.msg_args = None
            if not self.linter.is_message_enabled(msg_code):
                continue
            check_method = getattr(
                self, '_check_' + name_key.replace('-', '_'),
                None)
            is_odoo_check = self.is_main_odoo_module and \
                msg_code[1:3] == str(settings.BASE_OMODULE_ID)
            is_py_check = msg_code[1:3] == str(settings.BASE_PYMODULE_ID)

    def visit_module(self, node):
        self.wrapper_visit_module(node)

    def add_message(self, msg_id, line=None, node=None, args=None,
                    confidence=UNDEFINED):
        version = (self.manifest_dict.get('version') or ''
                   if isinstance(self.manifest_dict, dict) else '')
        match = self.formatversion(version)
        short_version = match.group(1) if match else ''
        if not short_version:
            valid_odoo_versions = self.linter._all_options[
                'valid_odoo_versions'].config.valid_odoo_versions
            short_version = (valid_odoo_versions[0] if
                             len(valid_odoo_versions) == 1 else '')
        return super(PylintOdooChecker, self).add_message(
            msg_id, line, node, args, confidence)


class PylintOdooTokenChecker(BaseTokenChecker, PylintOdooChecker):

    # Auto call to `process_tokens` method
    __implements__ = (ITokenChecker, IAstroidChecker)


# TODO: Change all methods here

class WrapperModuleChecker(PylintOdooChecker):

    node = None
    module_path = None
    msg_args = None
    msg_code = None
    msg_name_key = None
    module = None
    is_main_odoo_module = None

    def open(self):
        self.odoo_node = None

    @staticmethod
    def _get_format_str_args_kwargs(format_str):
        """Get dummy args and kwargs of a format string
        e.g. format_str = '{} {} {variable}'
            dummy args = (0, 0)
            kwargs = {'variable': 0}
        return args, kwargs
        Motivation to use format_str.format(*args, **kwargs)
        and validate if it was parsed correctly
        """
        format_str_args = []
        format_str_kwargs = {}
        placeholders = []
        for line in format_str.splitlines():
            try:
                placeholders.extend(
                    name for _, name, _, _ in string.Formatter().parse(line)
                    if name is not None)
            except ValueError:
                continue
            for placeholder in placeholders:
                if placeholder == "":
                    # unnumbered "{} {}"
                    # append 0 to use max(0, 0, ...) == 0
                    # and identify that all args are unnumbered vs numbered
                    format_str_args.append(0)
                elif placeholder.isdigit():
                    # numbered "{0} {1} {2} {0}"
                    # append +1 to use max(1, 2) and know the quantity of args
                    # and identify that the args are numbered
                    format_str_args.append(int(placeholder) + 1)
                else:
                    # named "{var0} {var1} {var2} {var0}"
                    format_str_kwargs[placeholder] = 0
        if format_str_args:
            format_str_args = (range(len(format_str_args)) if max(format_str_args) == 0
                               else range(max(format_str_args)))
        return format_str_args, format_str_kwargs

    @staticmethod
    def _get_printf_str_args_kwargs(printf_str):
        """Get dummy args and kwargs of a printf string
        e.g. printf_str = '%s %d'
            dummy args = ('', 0)
        e.g. printf_str = '%(var1)s %(var2)d'
            dummy kwargs = {'var1': '', 'var2': 0}
        return args or kwargs
        Motivation to use printf_str % (args or kwargs)
        and validate if it was parsed correctly
        """
        args = []
        kwargs = {}

        # Remove all escaped %%
        printf_str = re.sub('%%', '', printf_str)
        for line in printf_str.splitlines():
            for match in PRINTF_PATTERN.finditer(line):
                match_items = match.groupdict()
                var = '' if match_items['type'] == 's' else 0
                if match_items['key'] is None:
                    args.append(var)
                else:
                    kwargs[match_items['key']] = var
        return tuple(args) or kwargs
