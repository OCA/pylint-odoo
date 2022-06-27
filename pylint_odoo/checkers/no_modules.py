"""Enable checkers to visit all nodes different to modules.
You can use:
    visit_arguments
    visit_assattr
    visit_assert
    visit_assign
    visit_assname
    visit_backquote
    visit_binop
    visit_boolop
    visit_break
    visit_call
    visit_classdef
    visit_compare
    visit_continue
    visit_default
    visit_delattr
    visit_delname
    visit_dict
    visit_dictcomp
    visit_excepthandler
    visit_exec
    visit_expr
    visit_extslice
    visit_for
    visit_import
    visit_importfrom
    visit_functiondef
    visit_genexpr
    visit_getattr
    visit_global
    visit_if
    visit_ifexp
    visit_index
    visit_lambda
    visit_listcomp
    visit_name
    visit_pass
    visit_print
    visit_project
    visit_raise
    visit_return
    visit_setcomp
    visit_slice
    visit_subscript
    visit_tryexcept
    visit_tryfinally
    visit_unaryop
    visit_while
    visit_yield
for more info visit pylint doc
"""

import ast
import itertools
import os
import re

import astroid
import rfc3986
from six import string_types
from pylint.checkers import utils
from pylint.interfaces import IAstroidChecker

from .. import settings
from .. import misc
from .modules_odoo import DFTL_MANIFEST_DATA_KEYS

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal

    'R%d01' % settings.BASE_NOMODULE_ID: (
        'Import `Warning` should be renamed as UserError '
        '`from openerp.exceptions import Warning as UserError`',
        'openerp-exception-warning',
        settings.DESC_DFLT
    ),
    'W%d01' % settings.BASE_NOMODULE_ID: (
        'Detected api.one and api.multi decorators together.',
        'api-one-multi-together',
        settings.DESC_DFLT
    ),
    'W%d02' % settings.BASE_NOMODULE_ID: (
        'Missing api.one or api.multi in copy function.',
        'copy-wo-api-one',
        settings.DESC_DFLT
    ),
    'W%d03' % settings.BASE_NOMODULE_ID: (
        'Translation method _("string") in fields is not necessary.',
        'translation-field',
        settings.DESC_DFLT
    ),
    'W%d04' % settings.BASE_NOMODULE_ID: (
        'api.one deprecated',
        'api-one-deprecated',
        settings.DESC_DFLT
    ),
    'W%d05' % settings.BASE_NOMODULE_ID: (
        'attribute "%s" deprecated',
        'attribute-deprecated',
        settings.DESC_DFLT
    ),
    'W%d06' % settings.BASE_NOMODULE_ID: (
        'Missing `super` call in "%s" method.',
        'method-required-super',
        settings.DESC_DFLT
    ),
    'W%d10' % settings.BASE_NOMODULE_ID: (
        'Missing `return` (`super` is used) in method %s.',
        'missing-return',
        settings.DESC_DFLT
    ),
    'E%d01' % settings.BASE_NOMODULE_ID: (
        'The author key in the manifest file must be a string '
        '(with comma separated values)',
        'manifest-author-string',
        settings.DESC_DFLT
    ),
    'E%d02' % settings.BASE_NOMODULE_ID: (
        'Use of cr.commit() directly - More info '
        'https://github.com/OCA/odoo-community.org/blob/master/website/'
        'Contribution/CONTRIBUTING.rst'
        '#never-commit-the-transaction',
        'invalid-commit',
        settings.DESC_DFLT
    ),
    'E%d03' % settings.BASE_NOMODULE_ID: (
        'SQL injection risk. '
        'Use parameters if you can. - More info '
        'https://github.com/OCA/odoo-community.org/blob/master/website/'
        'Contribution/CONTRIBUTING.rst'
        '#no-sql-injection',
        'sql-injection',
        settings.DESC_DFLT
    ),
    'E%d04' % settings.BASE_NOMODULE_ID: (
        'The maintainers key in the manifest file must be a list of strings',
        'manifest-maintainers-list',
        settings.DESC_DFLT
    ),
    'E%d05' % settings.BASE_NOMODULE_ID: (
        'Use of `str.format` method in a translated string. '
        'Use `_("%(varname)s") % {"varname": value}` instead. '
        'Be careful https://lucumr.pocoo.org/2016/12/29/careful-with-str-format',
        'str-format-used',
        settings.DESC_DFLT
    ),
    'E%d06' % settings.BASE_NOMODULE_ID: (
        'Use of external request method `%s` without timeout. '
        'It could wait for a long time',
        'external-request-timeout',
        settings.DESC_DFLT
    ),
    'C%d01' % settings.BASE_NOMODULE_ID: (
        'One of the following authors must be present in manifest: %s',
        'manifest-required-author',
        settings.DESC_DFLT
    ),
    'C%d02' % settings.BASE_NOMODULE_ID: (
        'Missing required key "%s" in manifest file',
        'manifest-required-key',
        settings.DESC_DFLT
    ),
    'C%d03' % settings.BASE_NOMODULE_ID: (
        'Deprecated key "%s" in manifest file',
        'manifest-deprecated-key',
        settings.DESC_DFLT
    ),
    'C%d04' % settings.BASE_NOMODULE_ID: (
        'Use `CamelCase` "%s" in class name "%s". '
        'You can use oca-autopep8 of https://github.com/OCA/maintainer-tools'
        ' to auto fix it.',
        'class-camelcase',
        settings.DESC_DFLT
    ),
    'C%d05' % settings.BASE_NOMODULE_ID: (
        'License "%s" not allowed in manifest file.',
        'license-allowed',
        settings.DESC_DFLT
    ),
    'C%d06' % settings.BASE_NOMODULE_ID: (
        'Wrong Version Format "%s" in manifest file. '
        'Regex to match: "%s"',
        'manifest-version-format',
        settings.DESC_DFLT
    ),
    'C%d07' % settings.BASE_NOMODULE_ID: (
        'String parameter on "%s" requires translation. Use %s_(%s)',
        'translation-required',
        settings.DESC_DFLT
    ),
    'C%d08' % settings.BASE_NOMODULE_ID: (
        'Name of compute method should start with "_compute_"',
        'method-compute',
        settings.DESC_DFLT
    ),
    'C%d09' % settings.BASE_NOMODULE_ID: (
        'Name of search method should start with "_search_"',
        'method-search',
        settings.DESC_DFLT
    ),
    'C%d10' % settings.BASE_NOMODULE_ID: (
        'Name of inverse method should start with "_inverse_"',
        'method-inverse',
        settings.DESC_DFLT
    ),
    'C%d11' % settings.BASE_NOMODULE_ID: (
        'Manifest key development_status "%s" not allowed. '
        'Use one of: %s.',
        'development-status-allowed',
        settings.DESC_DFLT
    ),
    'R%d10' % settings.BASE_NOMODULE_ID: (
        'Method defined with old api version 7',
        'old-api7-method-defined',
        settings.DESC_DFLT
    ),
    'W%d11' % settings.BASE_NOMODULE_ID: (
        'Field parameter "%s" is no longer supported. Use "%s" instead.',
        'renamed-field-parameter',
        settings.DESC_DFLT
    ),
    'W%d12' % settings.BASE_NOMODULE_ID: (
        '"eval" referenced detected.',
        'eval-referenced',
        settings.DESC_DFLT
    ),
    'W%d13' % settings.BASE_NOMODULE_ID: (
        'The attribute string is redundant. '
        'String parameter equal to name of variable',
        'attribute-string-redundant',
        settings.DESC_DFLT
    ),
    'W%d14' % settings.BASE_NOMODULE_ID: (
        'Website "%s" in manifest key is not a valid URI',
        'website-manifest-key-not-valid-uri',
        settings.DESC_DFLT
    ),
    'W%d15' % settings.BASE_NOMODULE_ID: (
        'Translatable term in "%s" contains variables. Use %s instead',
        'translation-contains-variable',
        settings.DESC_DFLT
    ),
    'W%d16' % settings.BASE_NOMODULE_ID: (
        'Print used. Use `logger` instead.',
        'print-used',
        settings.DESC_DFLT
    ),
    'W%d20' % settings.BASE_NOMODULE_ID: (
        'Translation method _(%s) is using positional string printf formatting. '
        'Use named placeholder `_("%%(placeholder)s")` instead.',
        'translation-positional-used',
        settings.DESC_DFLT
    ),
    'W%d21' % settings.BASE_NOMODULE_ID: (
        'Context overridden using dict. '
        'Better using kwargs `with_context(**%s)` or `with_context(key=value)`',
        'context-overridden',
        settings.DESC_DFLT
    ),
    'F%d01' % settings.BASE_NOMODULE_ID: (
        'File "%s": "%s" not found.',
        'resource-not-exist',
        settings.DESC_DFLT
    )
}

DFTL_MANIFEST_REQUIRED_KEYS = ['license']
DFTL_MANIFEST_REQUIRED_AUTHORS = ['Odoo Community Association (OCA)']
DFTL_MANIFEST_DEPRECATED_KEYS = ['description']
DFTL_LICENSE_ALLOWED = [
    'AGPL-3', 'GPL-2', 'GPL-2 or any later version',
    'GPL-3', 'GPL-3 or any later version', 'LGPL-3',
    'Other OSI approved licence', 'Other proprietary',
    'OEEL-1',
]
DFTL_DEVELOPMENT_STATUS_ALLOWED = [
    'Alpha', 'Beta', 'Production/Stable', 'Mature',
]
DFTL_ATTRIBUTE_DEPRECATED = [
    '_columns', '_defaults', 'length',
]
DFTL_METHOD_REQUIRED_SUPER = [
    'create', 'write', 'read', 'unlink', 'copy',
    'setUp', 'setUpClass', 'tearDown', 'tearDownClass', 'default_get',
]
DFTL_CURSOR_EXPR = [
    'self.env.cr', 'self._cr',  # new api
    'self.cr',  # controllers and test
    'cr',  # old api
]
DFTL_ODOO_EXCEPTIONS = [
    # Extracted from openerp/exceptions.py of 8.0 and master
    'AccessDenied', 'AccessError', 'DeferredException', 'except_orm',
    'MissingError', 'QWebException', 'RedirectWarning', 'UserError',
    'ValidationError', 'Warning',
]
DFTL_NO_MISSING_RETURN = [
    '__init__', 'setUp', 'setUpClass', 'tearDown', 'tearDownClass', '_register_hook',
]
FIELDS_METHOD = {
    'Many2many': 4,
    'One2many': 2,
    'Many2one': 1,
    'Reference': 1,
    'Selection': 1,
}
DFTL_DEPRECATED_FIELD_PARAMETERS = [
    # From odoo/odoo 10.0: odoo/odoo/fields.py:29
    'digits_compute:digits', 'select:index'
]
DFTL_EXTERNAL_REQUEST_TIMEOUT_METHODS = [
    "http.client.HTTPConnection",
    "http.client.HTTPSConnection",
    "odoo.addons.iap.models.iap.jsonrpc",
    "requests.delete",
    "requests.get",
    "requests.head",
    "requests.options",
    "requests.patch",
    "requests.post",
    "requests.put",
    "requests.request",
    "serial.Serial",
    "smtplib.SMTP",
    "suds.client.Client",
    "urllib.request.urlopen",
]


class NoModuleChecker(misc.PylintOdooChecker):

    __implements__ = IAstroidChecker

    name = settings.CFG_SECTION
    msgs = ODOO_MSGS
    options = (
        ('manifest_required_authors', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_MANIFEST_REQUIRED_AUTHORS,
            'help': 'Author names, at least one is required in manifest file.'
        }),
        ('manifest_required_author', {
            'type': 'string',
            'metavar': '<string>',
            'default': '',
            'help': ('Name of author required in manifest file. '
                     'This parameter is deprecated use '
                     '"manifest_required_authors" instead.')
        }),
        ('manifest_required_keys', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_MANIFEST_REQUIRED_KEYS,
            'help': 'List of keys required in manifest file, ' +
                    'separated by a comma.'
        }),
        ('manifest_deprecated_keys', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_MANIFEST_DEPRECATED_KEYS,
            'help': 'List of keys deprecated in manifest file, ' +
                    'separated by a comma.'
        }),
        ('license_allowed', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_LICENSE_ALLOWED,
            'help': 'List of license allowed in manifest file, ' +
                    'separated by a comma.'
        }),
        ('development_status_allowed', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_DEVELOPMENT_STATUS_ALLOWED,
            'help': 'List of development status allowed in manifest file, ' +
                    'separated by a comma.'
        }),
        ('attribute_deprecated', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_ATTRIBUTE_DEPRECATED,
            'help': 'List of attributes deprecated, ' +
                    'separated by a comma.'
        }),
        ('deprecated_field_parameters', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_DEPRECATED_FIELD_PARAMETERS,
            'help': 'List of deprecated field parameters, separated by a '
                    'comma. If the param was renamed, separate the old and '
                    'new name with a colon. If the param was removed, keep '
                    'the right side of the colon empty. '
                    '"deprecated_param:" means that "deprecated_param" was '
                    'deprecated and it doesn\'t have a new alternative. '
                    '"deprecated_param:new_param" means that it was '
                    'deprecated and renamed as "new_param". '
        }),
        ('method_required_super', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_METHOD_REQUIRED_SUPER,
            'help': 'List of methods where call to `super` is required.' +
                    'separated by a comma.'
        }),
        ('manifest_version_format', {
            'type': 'string',
            'metavar': '<string>',
            'default': misc.DFTL_MANIFEST_VERSION_FORMAT,
            'help': 'Regex to check version format in manifest file. '
            'Use "{valid_odoo_versions}" to check the parameter of '
            '"valid_odoo_versions"'
        }),
        ('cursor_expr', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_CURSOR_EXPR,
            'help': 'List of cursor expr separated by a comma.'
        }),
        ('odoo_exceptions', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_ODOO_EXCEPTIONS,
            'help': 'List of odoo exceptions separated by a comma.'
        }),
        ('valid_odoo_versions', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': misc.DFTL_VALID_ODOO_VERSIONS,
            'help': 'List of valid odoo versions separated by a comma.'
        }),
        ('no_missing_return', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_NO_MISSING_RETURN,
            'help': 'List of valid missing return method names, '
            'separated by a comma.'
        }),
        ('external_request_timeout_methods', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_EXTERNAL_REQUEST_TIMEOUT_METHODS,
            'help': 'List of library.method that must have a timeout '
                    'parameter defined, separated by a comma. '
                    'e.g. "requests.get,requests.post"'
        }),
    )

    def visit_module(self, node):
        """Initizalize the cache to save the original library name
        of all imported node
        It is filled from "visit_importfrom" and "visit_import"
        and it is used in "visit_call"
        All these methods are these "visit_*" methods are called from pylint API
        """
        self._from_imports = {}

    def leave_module(self, node):
        """Clear variables"""
        self._from_imports = {}

    def open(self):
        super(NoModuleChecker, self).open()
        self.config.deprecated_field_parameters = \
            self.colon_list_to_dict(self.config.deprecated_field_parameters)

    def colon_list_to_dict(self, colon_list):
        """Converts a colon list to a dictionary.

        :param colon_list: A list of strings representing keys and values,
            separated with a colon. If a key doesn't have a value, keep the
            right side of the colon empty.
        :type colon_list: list
        :returns: A dictionary with the values assigned to corresponding keys.
        :rtype: dict

        :Example:

        >>> self.colon_list_to_dict(['colon:list', 'empty_key:'])
        {'colon': 'list', 'empty_key': ''}
        """
        return dict(item.split(":") for item in colon_list)

    def _sqli_allowable(self, node):
        # sql.SQL or sql.Identifier is OK
        if self._is_psycopg2_sql(node):
            return True
        if isinstance(node, astroid.FormattedValue):
            if hasattr(node, 'value'):
                return self._sqli_allowable(node.value)
            if hasattr(node, 'values'):
                return all(self._sqli_allowable(v) for v in node.values)
        if isinstance(node, astroid.Call):
            node = node.func
        # self._thing is OK (mostly self._table), self._thing() also because
        # it's a common pattern of reports (self._select, self._group_by, ...)
        return (isinstance(node, astroid.Attribute)
                and isinstance(node.expr, astroid.Name)
                and node.attrname.startswith('_')
                # cr.execute('SELECT * FROM %s' % 'table') is OK
                # since that is a constant and constant can not be injected
                or isinstance(node, astroid.Const))

    def _is_psycopg2_sql(self, node):
        if isinstance(node, astroid.Name):
            for assignation_node in self._get_assignation_nodes(node):
                if self._is_psycopg2_sql(assignation_node):
                    return True
        if (not isinstance(node, astroid.Call) or
                not isinstance(node.func, (astroid.Attribute, astroid.Name))):
            return False
        imported_name = node.func.as_string().split('.')[0]
        imported_node = node.root().locals.get(imported_name)
        # "from psycopg2 import *" not considered since that it is hard
        # and there is another check detecting these kind of imports
        if not imported_node:
            return None
        imported_node = imported_node[0]
        if isinstance(imported_node, astroid.ImportFrom):
            package_names = imported_node.modname.split('.')[:1]
        elif isinstance(imported_node, astroid.Import):
            package_names = [name[0].split('.')[0] for name in imported_node.names]
        else:
            return False
        if 'psycopg2' in package_names:
            return True

    def _check_node_for_sqli_risk(self, node):
        if isinstance(node, astroid.BinOp) and node.op in ('%', '+'):
            if isinstance(node.right, astroid.Tuple):
                # execute("..." % (self._table, thing))
                if not all(map(self._sqli_allowable, node.right.elts)):
                    return True
            elif isinstance(node.right, astroid.Dict):
                # execute("..." % {'table': self._table}
                if not all(self._sqli_allowable(v) for _, v in node.right.items):
                    return True
            elif not self._sqli_allowable(node.right):
                # execute("..." % self._table)
                return True

            # Consider cr.execute('SELECT ' + operator + ' FROM table' + 'WHERE')"
            # node.repr_tree()
            # BinOp(
            #    op='+',
            #    left=BinOp(
            #       op='+',
            #       left=BinOp(
            #          op='+',
            #          left=Const(value='SELECT '),
            #          right=Name(name='operator')),
            #       right=Const(value=' FROM table')),
            #    right=Const(value='WHERE'))
            if (not self._sqli_allowable(node.left) and
                    self._check_node_for_sqli_risk(node.left)):
                return True

        # check execute("...".format(self._table, table=self._table))
        # ignore sql.SQL().format
        if isinstance(node, astroid.Call) \
                and isinstance(node.func, astroid.Attribute) \
                and node.func.attrname == 'format':

            if not all(map(self._sqli_allowable, node.args or [])):
                return True

            if not all(
                self._sqli_allowable(keyword.value)
                for keyword in (node.keywords or [])
            ):
                return True

        # Check fstrings (PEP 498). Only Python >= 3.6
        if isinstance(node, astroid.JoinedStr):
            if hasattr(node, 'value'):
                return self._sqli_allowable(node.value)
            elif hasattr(node, 'values'):
                return not all(self._sqli_allowable(v) for v in node.values)

        return False

    def _check_sql_injection_risky(self, node):
        # Inspired from OCA/pylint-odoo project
        # Thanks @moylop260 (Moises Lopez) & @nilshamerlinck (Nils Hamerlinck)
        current_file_bname = os.path.basename(self.linter.current_file)
        if not (
            # .execute() or .executemany()
            isinstance(node, astroid.Call) and node.args and
            isinstance(node.func, astroid.Attribute) and
            node.func.attrname in ('execute', 'executemany') and
            # cursor expr (see above)
            self.get_cursor_name(node.func) in DFTL_CURSOR_EXPR and
            # cr.execute("select * from %s" % foo, [bar]) -> probably a good reason
            # for string formatting
            len(node.args) <= 1 and
            # ignore in test files, probably not accessible
            not current_file_bname.startswith('test_')
        ):
            return False
        first_arg = node.args[0]
        is_concatenation = self._check_node_for_sqli_risk(first_arg)
        # if first parameter is a variable, check how it was built instead
        if not is_concatenation:
            for node_assignation in self._get_assignation_nodes(first_arg):
                is_concatenation = self._check_node_for_sqli_risk(node_assignation)
                if is_concatenation:
                    break
        return is_concatenation

    def _get_assignation_nodes(self, node):
        if isinstance(node, (astroid.Name, astroid.Subscript)):
            # 1) look for parent method / controller
            current = node
            while (current and not isinstance(current.parent, astroid.FunctionDef)):
                current = current.parent
            if current:
                parent = current.parent
                # 2) check how was the variable built
                for assign_node in parent.nodes_of_class(astroid.Assign):
                    if assign_node.targets[0].as_string() == node.as_string():
                        yield assign_node.value

    @utils.check_messages("print-used")
    def visit_print(self, node):
        self.add_message("print-used", node=node)

    @utils.check_messages('translation-field', 'invalid-commit',
                          'method-compute', 'method-search', 'method-inverse',
                          'sql-injection',
                          'attribute-string-redundant',
                          'renamed-field-parameter',
                          'translation-required',
                          'translation-contains-variable',
                          'print-used', 'translation-positional-used',
                          'str-format-used', 'context-overridden',
                          'external-request-timeout',
                          )
    def visit_call(self, node):
        infer_node = utils.safe_infer(node.func)
        if utils.is_builtin_object(infer_node) and infer_node.name == 'print':
            self.add_message('print-used', node=node)
        if ('fields' == self.get_func_lib(node.func) and
                isinstance(node.parent, astroid.Assign) and
                isinstance(node.parent.parent, astroid.ClassDef)):
            args = misc.join_node_args_kwargs(node)
            index = 0
            field_name = ''
            if (isinstance(node.parent, astroid.Assign) and
                    node.parent.targets and
                    isinstance(node.parent.targets[0], astroid.AssignName)):
                field_name = (node.parent.targets[0].name
                              .replace('_', ' '))
            is_related = bool([1 for kw in node.keywords or [] if kw.arg == 'related'])
            for argument in args:
                argument_aux = argument
                # Check this 'name = fields.Char("name")'
                if (not is_related and isinstance(argument, astroid.Const) and
                    (index ==
                     FIELDS_METHOD.get(argument.parent.func.attrname, 0)) and
                    (argument.value in
                     [field_name.capitalize(), field_name.title()])):
                    self.add_message('attribute-string-redundant', node=node)
                if isinstance(argument, astroid.Keyword):
                    argument_aux = argument.value
                    deprecated = self.config.deprecated_field_parameters
                    if argument.arg in ['compute', 'search', 'inverse'] and \
                            isinstance(argument_aux, astroid.Const) and \
                            isinstance(argument_aux.value, string_types) and \
                            not argument_aux.value.startswith(
                                '_' + argument.arg + '_'):
                        self.add_message('method-' + argument.arg,
                                         node=argument_aux)
                    # Check if the param string is equal to the name
                    #   of variable
                    elif not is_related and argument.arg == 'string' and \
                        (isinstance(argument_aux, astroid.Const) and
                         argument_aux.value in
                         [field_name.capitalize(), field_name.title()]):
                        self.add_message(
                            'attribute-string-redundant', node=node)
                    elif (argument.arg in deprecated):
                        self.add_message(
                            'renamed-field-parameter', node=node,
                            args=(argument.arg, deprecated[argument.arg])
                        )
                if isinstance(argument_aux, astroid.Call) and \
                        isinstance(argument_aux.func, astroid.Name) and \
                        argument_aux.func.name == '_':
                    self.add_message('translation-field', node=argument_aux)
                index += 1
        # Check cr.commit()
        if isinstance(node, astroid.Call) and \
                isinstance(node.func, astroid.Attribute) and \
                node.func.attrname == 'commit' and \
                self.get_cursor_name(node.func) in self.config.cursor_expr:
            self.add_message('invalid-commit', node=node)

        if (isinstance(node, astroid.Call) and
                isinstance(node.func, astroid.Attribute) and
                node.func.attrname == 'with_context' and
                not node.keywords and node.args):
            # with_context(**ctx) is considered a keywords
            # So, if only one args is received it is overridden
            self.add_message('context-overridden', node=node,
                             args=(node.args[0].as_string(),))

        # Call the message_post()
        base_dirname = os.path.basename(os.path.normpath(
            os.path.dirname(self.linter.current_file)))
        if (base_dirname != 'tests' and isinstance(node, astroid.Call) and
                isinstance(node.func, astroid.Attribute) and
                node.func.attrname == 'message_post'):
            for arg in itertools.chain(node.args, node.keywords or []):
                if isinstance(arg, astroid.Keyword):
                    keyword = arg.arg
                    value = arg.value
                else:
                    keyword = ''
                    value = arg
                if keyword and keyword not in ('subject', 'body'):
                    continue
                as_string = ''
                # case: message_post(body='String')
                if isinstance(value, astroid.Const):
                    as_string = value.as_string()
                # case: message_post(body='String %s' % (...))
                elif (isinstance(value, astroid.BinOp)
                        and value.op == '%'
                        and isinstance(value.left, astroid.Const)
                        # The right part is translatable only if it's a
                        # function or a list of functions
                        and not (
                            isinstance(value.right, (
                                astroid.Call, astroid.Tuple, astroid.List))
                            and all([
                                isinstance(child, astroid.Call)
                                for child in getattr(value.right, 'elts', [])
                            ]))):
                    as_string = value.left.as_string()
                # case: message_post(body='String {...}'.format(...))
                elif (isinstance(value, astroid.Call)
                        and isinstance(value.func, astroid.Attribute)
                        and isinstance(value.func.expr, astroid.Const)
                        and value.func.attrname == 'format'):
                    as_string = value.func.expr.as_string()
                if as_string:
                    keyword = keyword and '%s=' % keyword
                    self.add_message(
                        'translation-required', node=node,
                        args=('message_post', keyword, as_string))

        # Call _(...) with variables into the term to be translated
        if (isinstance(node.func, astroid.Name)
                and node.func.name == '_'
                and node.args):
            wrong = ''
            right = ''
            arg = node.args[0]
            # case: _('...' % (variables))
            if isinstance(arg, astroid.BinOp) and arg.op == '%':
                wrong = '%s %% %s' % (
                    arg.left.as_string(), arg.right.as_string())
                right = '_(%s) %% %s' % (
                    arg.left.as_string(), arg.right.as_string())
            # Case: _('...'.format(variables))
            elif (isinstance(arg, astroid.Call)
                    and isinstance(arg.func, astroid.Attribute)
                    and isinstance(arg.func.expr, astroid.Const)
                    and arg.func.attrname == 'format'):
                self.add_message('str-format-used', node=node)
                wrong = arg.as_string()
                params_as_string = ', '.join([
                    x.as_string()
                    for x in itertools.chain(arg.args, arg.keywords or [])])
                right = '_(%s).format(%s)' % (
                    arg.func.expr.as_string(), params_as_string)
            if wrong and right:
                self.add_message(
                    'translation-contains-variable', node=node,
                    args=(wrong, right))

            # translation-positional-used: Check "string to translate"
            # to check "%s %s..." used where the position can't be changed
            str2translate = arg.as_string()
            printf_args = (
                misc.WrapperModuleChecker.
                _get_printf_str_args_kwargs(str2translate))
            if isinstance(printf_args, tuple) and len(printf_args) >= 2:
                # Return tuple for %s and dict for %(varname)s
                # Check just the following cases "%s %s..."
                self.add_message('translation-positional-used',
                                 node=node, args=(str2translate,))

        # SQL Injection
        if self._check_sql_injection_risky(node):
            self.add_message('sql-injection', node=node)

        # external-request-timeout
        lib_alias = self.get_func_lib(node.func)
        # Use dict "self._from_imports" to know the source library of the method
        lib_original = self._from_imports.get(lib_alias) or lib_alias
        func_name = self.get_func_name(node.func)
        lib_original_func_name = (
            # If it using "requests.request()"
            "%s.%s" % (lib_original, func_name) if lib_original
            # If it using "from requests import request;request()"
            else self._from_imports.get(func_name))
        if lib_original_func_name in self.config.external_request_timeout_methods:
            for argument in misc.join_node_args_kwargs(node):
                if not isinstance(argument, astroid.Keyword):
                    continue
                if argument.arg == 'timeout':
                    break
            else:
                self.add_message(
                    'external-request-timeout', node=node,
                    args=(lib_original_func_name,))

    @utils.check_messages(
        'license-allowed', 'manifest-author-string', 'manifest-deprecated-key',
        'manifest-required-author', 'manifest-required-key',
        'manifest-version-format', 'resource-not-exist',
        'website-manifest-key-not-valid-uri', 'development-status-allowed',
        'manifest-maintainers-list')
    def visit_dict(self, node):
        if not os.path.basename(self.linter.current_file) in \
                settings.MANIFEST_FILES \
                or not isinstance(node.parent, astroid.Expr):
            return
        manifest_dict = ast.literal_eval(node.as_string())

        # Check author is a string
        author = manifest_dict.get('author', '')
        if not isinstance(author, string_types):
            self.add_message('manifest-author-string', node=node)
        else:
            # Check author required
            authors = set([auth.strip() for auth in author.split(',')])

            if self.config.manifest_required_author:
                # Support compatibility for deprecated attribute
                required_authors = set((self.config.manifest_required_author,))
            else:
                required_authors = set(self.config.manifest_required_authors)
            if not (authors & required_authors):
                # None of the required authors is present in the manifest
                # Authors will be printed as 'author1', 'author2', ...
                authors_str = ", ".join([
                    "'%s'" % auth for auth in required_authors
                ])
                self.add_message('manifest-required-author', node=node,
                                 args=(authors_str,))

        # Check keys required
        required_keys = self.config.manifest_required_keys
        for required_key in required_keys:
            if required_key not in manifest_dict:
                self.add_message('manifest-required-key', node=node,
                                 args=(required_key,))

        # Check keys deprecated
        deprecated_keys = self.config.manifest_deprecated_keys
        for deprecated_key in deprecated_keys:
            if deprecated_key in manifest_dict:
                self.add_message('manifest-deprecated-key', node=node,
                                 args=(deprecated_key,))

        # Check license allowed
        license = manifest_dict.get('license', None)
        if license and license not in self.config.license_allowed:
            self.add_message('license-allowed',
                             node=node, args=(license,))

        # Check version format
        version_format = manifest_dict.get('version', '')
        formatrgx = self.formatversion(version_format)
        if version_format and not formatrgx:
            self.add_message('manifest-version-format', node=node,
                             args=(version_format,
                                   self.config.manifest_version_format_parsed))

        # Check if resource exist
        dirname = os.path.dirname(self.linter.current_file)
        for key in DFTL_MANIFEST_DATA_KEYS:
            for resource in (manifest_dict.get(key) or []):
                if os.path.isfile(os.path.join(dirname, resource)):
                    continue
                self.add_message('resource-not-exist', node=node,
                                 args=(key, resource))

        # Check if the website is valid URI
        website = manifest_dict.get('website', '')
        uri = rfc3986.uri_reference(website)
        if ((website and ',' not in website) and
                (not uri.is_valid(require_scheme=True,
                                  require_authority=True) or
                 uri.scheme not in {"http", "https"})):
            self.add_message('website-manifest-key-not-valid-uri',
                             node=node, args=(website))

        # Check valid development_status values
        dev_status = manifest_dict.get('development_status')
        if (dev_status and
                dev_status not in self.config.development_status_allowed):
            valid_status = ", ".join(self.config.development_status_allowed)
            self.add_message('development-status-allowed',
                             node=node, args=(dev_status, valid_status))

        # Check maintainers key is a list of strings
        maintainers = manifest_dict.get('maintainers')
        if(maintainers and (not isinstance(maintainers, list)
                            or any(not isinstance(item, str) for item in maintainers))):
            self.add_message('manifest-maintainers-list',
                             node=node)

    @utils.check_messages('api-one-multi-together',
                          'copy-wo-api-one', 'api-one-deprecated',
                          'method-required-super', 'old-api7-method-defined',
                          'missing-return',
                          )
    def visit_functiondef(self, node):
        """Check that `api.one` and `api.multi` decorators not exists together
        Check that method `copy` exists `api.one` decorator
        Check deprecated `api.one`.
        """
        if not node.is_method():
            return

        decor_names = self.get_decorators_names(node.decorators)
        decor_lastnames = [
            decor.split('.')[-1]
            for decor in decor_names]
        if self.linter.is_message_enabled('api-one-multi-together'):
            if 'one' in decor_lastnames \
                    and 'multi' in decor_lastnames:
                self.add_message('api-one-multi-together', node=node)

        if self.linter.is_message_enabled('copy-wo-api-one'):
            if 'copy' == node.name and ('one' not in decor_lastnames and
                                        'multi' not in decor_lastnames):
                self.add_message('copy-wo-api-one', node=node)

        if self.linter.is_message_enabled('api-one-deprecated'):
            if 'one' in decor_lastnames:
                self.add_message('api-one-deprecated', node=node)

        if node.name in self.config.method_required_super:
            calls = [
                call_func.func.name
                for call_func in node.nodes_of_class((astroid.Call,))
                if isinstance(call_func.func, astroid.Name)]
            if 'super' not in calls:
                self.add_message('method-required-super', node=node,
                                 args=(node.name))

        if self.linter.is_message_enabled('old-api7-method-defined'):
            first_args = [arg.name for arg in node.args.args][:3]
            if len(first_args) == 3 and first_args[0] == 'self' and \
               first_args[1] in ['cr', 'cursor'] and \
               first_args[2] in ['uid', 'user', 'user_id']:
                self.add_message('old-api7-method-defined', node=node)

        there_is_super = False
        for stmt in node.nodes_of_class(astroid.Call):
            func = stmt.func
            if isinstance(func, astroid.Name) and func.name == 'super':
                there_is_super = True
                break
        there_is_return = False
        for stmt in node.nodes_of_class(astroid.Return,
                                        skip_klass=(astroid.FunctionDef,
                                                    astroid.ClassDef)):
            there_is_return = True
            break
        if there_is_super and not there_is_return and \
                not node.is_generator() and \
                node.name not in self.config.no_missing_return:
            self.add_message('missing-return', node=node, args=(node.name))

    @utils.check_messages('external-request-timeout')
    def visit_import(self, node):
        self._from_imports.update({
            alias or name: "%s" % name
            for name, alias in node.names
        })

    @utils.check_messages('openerp-exception-warning', 'external-request-timeout')
    def visit_importfrom(self, node):
        if node.modname == 'openerp.exceptions':
            for (import_name, import_as_name) in node.names:
                if import_name == 'Warning' and import_as_name != 'UserError':
                    self.add_message('openerp-exception-warning', node=node)
        self._from_imports.update({
            alias or name: "%s.%s" % (node.modname, name)
            for name, alias in node.names})

    @utils.check_messages('class-camelcase')
    def visit_classdef(self, node):
        camelized = self.camelize(node.name)
        if camelized != node.name:
            self.add_message('class-camelcase', node=node,
                             args=(camelized, node.name))

    @utils.check_messages('attribute-deprecated')
    def visit_assign(self, node):
        node_left = node.targets[0]
        if (isinstance(node.parent, astroid.ClassDef) and
                isinstance(node_left, astroid.AssignName) and
                [1 for m in node.parent.basenames if 'Model' in m]):
            if node_left.name in self.config.attribute_deprecated:
                self.add_message('attribute-deprecated',
                                 node=node_left, args=(node_left.name,))

    @utils.check_messages('eval-referenced')
    def visit_name(self, node):
        """Detect when a "bad" built-in is referenced."""
        node_infer = utils.safe_infer(node)
        if not utils.is_builtin_object(node_infer):
            # Skip not builtin objects
            return
        if node_infer.name == 'eval':
            self.add_message('eval-referenced', node=node)

    def camelize(self, string):
        return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)

    def get_decorators_names(self, decorators):
        nodes = []
        if decorators:
            nodes = decorators.nodes
        return [getattr(decorator, 'attrname', '')
                for decorator in nodes if decorator is not None]

    def get_func_name(self, node):
        func_name = isinstance(node, astroid.Name) and node.name or \
            isinstance(node, astroid.Attribute) and node.attrname or ''
        return func_name

    def get_func_lib(self, node):
        if isinstance(node, astroid.Attribute) and \
                isinstance(node.expr, astroid.Name):
            return node.expr.name
        return ""

    @utils.check_messages('translation-required')
    def visit_raise(self, node):
        """Visit raise and search methods with a string parameter
        without a method.
        Example wrong: raise UserError('My String')
        Example done: raise UserError(_('My String'))
        TODO: Consider the case where is used a variable with string value
              my_string = 'My String'  # wrong
              raise UserError(my_string)  # Detect variable string here
        """
        if node.exc is None:
            # ignore empty raise
            return
        expr = node.exc
        if not isinstance(expr, astroid.Call):
            # ignore raise without a call
            return
        if not expr.args:
            return
        func_name = self.get_func_name(expr.func)

        argument = expr.args[0]
        if isinstance(argument, astroid.Call) and \
                'format' == self.get_func_name(argument.func):
            argument = argument.func.expr
        elif isinstance(argument, astroid.BinOp):
            argument = argument.left

        if isinstance(argument, astroid.Const) and \
                argument.name == 'str' and \
                func_name in self.config.odoo_exceptions:
            self.add_message(
                'translation-required', node=node,
                args=(func_name, '', argument.as_string()))

    def get_cursor_name(self, node):
        expr_list = []
        node_expr = node.expr
        while isinstance(node_expr, astroid.Attribute):
            expr_list.insert(0, node_expr.attrname)
            node_expr = node_expr.expr
        if isinstance(node_expr, astroid.Name):
            expr_list.insert(0, node_expr.name)
        cursor_name = '.'.join(expr_list)
        return cursor_name
