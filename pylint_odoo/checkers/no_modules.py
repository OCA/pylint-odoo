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
import os
import re
import types

import astroid
from pylint.checkers import BaseChecker, utils
from pylint.interfaces import IAstroidChecker

from .. import settings
from .. import misc

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
    'E%d01' % settings.BASE_NOMODULE_ID: (
        'The author key in the manifest file must be a string '
        '(with comma separated values)',
        'manifest-author-string',
        settings.DESC_DFLT
    ),
    'E%d02' % settings.BASE_NOMODULE_ID: (
        'Use of cr.commit() directly - More info '
        'https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md'
        '#never-commit-the-transaction',
        'invalid-commit',
        settings.DESC_DFLT
    ),
    'E%d03' % settings.BASE_NOMODULE_ID: (
        'Use of "%" operator in execute database method. '
        'Better use parameters instead. - More info '
        'https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md'
        '#no-sql-injection',
        'sql-injection',
        settings.DESC_DFLT
    ),
    'C%d01' % settings.BASE_NOMODULE_ID: (
        'Missing author required "%s" in manifest file',
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
        'String parameter of raise "%s" requires translation. Use _(%s)',
        'translation-required',
        settings.DESC_DFLT
    ),
    'C%d08' % settings.BASE_NOMODULE_ID: (
        'Name of compute method should starts with "_compute_"',
        'method-compute',
        settings.DESC_DFLT
    ),
    'C%d09' % settings.BASE_NOMODULE_ID: (
        'Name of search method should starts with "_search_"',
        'method-search',
        settings.DESC_DFLT
    ),
    'C%d10' % settings.BASE_NOMODULE_ID: (
        'Name of inverse method should starts with "_inverse_"',
        'method-inverse',
        settings.DESC_DFLT
    ),
    'R%d10' % settings.BASE_NOMODULE_ID: (
        'Method defined with old api version 7',
        'old-api7-method-defined',
        settings.DESC_DFLT
    ),
}

DFTL_MANIFEST_REQUIRED_KEYS = ['license']
DFTL_MANIFEST_REQUIRED_AUTHOR = 'Odoo Community Association (OCA)'
DFTL_MANIFEST_DEPRECATED_KEYS = ['description']
DFTL_LICENSE_ALLOWED = [
    'AGPL-3', 'GPL-2', 'GPL-2 or any later version',
    'GPL-3', 'GPL-3 or any later version', 'LGPL-3',
    'Other OSI approved licence', 'Other proprietary',
]
DFTL_ATTRIBUTE_DEPRECATED = [
    '_columns', '_defaults',
]
DFTL_METHOD_REQUIRED_SUPER = [
    'create', 'write', 'read', 'unlink', 'copy',
    'setUp', 'tearDown', 'default_get',
]
DFTL_MANIFEST_VERSION_FORMAT = r"(\d+.\d+.\d+.\d+.\d+)"
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


class NoModuleChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = settings.CFG_SECTION
    msgs = ODOO_MSGS
    options = (
        ('manifest_required_author', {
            'type': 'string',
            'metavar': '<string>',
            'default': DFTL_MANIFEST_REQUIRED_AUTHOR,
            'help': 'Name of author required in manifest file.'
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
        ('attribute_deprecated', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFTL_ATTRIBUTE_DEPRECATED,
            'help': 'List of attributes deprecated, ' +
                    'separated by a comma.'
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
            'default': DFTL_MANIFEST_VERSION_FORMAT,
            'help': 'Regex to check version format in manifest file'
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
    )

    @utils.check_messages('translation-field', 'invalid-commit',
                          'method-compute', 'method-search', 'method-inverse',
                          'sql-injection',
                          )
    def visit_call(self, node):
        if node.as_string().lower().startswith('fields.'):
            args = misc.join_node_args_kwargs(node)
            for argument in args:
                argument_aux = argument
                if isinstance(argument, astroid.Keyword):
                    argument_aux = argument.value
                    if argument.arg in ['compute', 'search', 'inverse'] and \
                            isinstance(argument.value, astroid.Const) and \
                            not argument.value.value.startswith(
                                '_' + argument.arg + '_'):
                        self.add_message('method-' + argument.arg,
                                         node=argument_aux)
                if isinstance(argument_aux, astroid.CallFunc) and \
                        isinstance(argument_aux.func, astroid.Name) and \
                        argument_aux.func.name == '_':
                    self.add_message('translation-field', node=argument_aux)
        # Check cr.commit()
        if isinstance(node, astroid.CallFunc) and \
                isinstance(node.func, astroid.Getattr) and \
                node.func.attrname == 'commit' and \
                self.get_cursor_name(node.func) in self.config.cursor_expr:
            self.add_message('invalid-commit', node=node)
        # SQL Injection
        if isinstance(node, astroid.CallFunc) and node.args and \
                isinstance(node.func, astroid.Getattr) and \
                node.func.attrname == 'execute' and \
                self.get_cursor_name(node.func) in self.config.cursor_expr:
            first_arg = node.args[0]
            is_bin_op = isinstance(first_arg, astroid.BinOp) and \
                first_arg.op == '%'
            is_format = isinstance(first_arg, astroid.CallFunc) and \
                self.get_func_name(first_arg.func) == 'format'
            if is_bin_op or is_format:
                self.add_message('sql-injection', node=node)

    @utils.check_messages('manifest-required-author', 'manifest-required-key',
                          'manifest-deprecated-key')
    def visit_dict(self, node):
        if not os.path.basename(self.linter.current_file) in \
                settings.MANIFEST_FILES \
                or not isinstance(node.parent, astroid.Discard):
            return
        manifest_dict = ast.literal_eval(node.as_string())

        # Check author is a string
        author = manifest_dict.get('author', '')
        if not isinstance(author, types.StringTypes):
            self.add_message('manifest-author-string', node=node)
        else:
            # Check author required
            authors = map(lambda author: author.strip(), author.split(','))
            required_author = self.config.manifest_required_author
            if required_author not in authors:
                self.add_message('manifest-required-author', node=node,
                                 args=(required_author,))

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
                                   self.config.manifest_version_format,))

    @utils.check_messages('api-one-multi-together',
                          'copy-wo-api-one', 'api-one-deprecated',
                          'method-required-super', 'old-api7-method-defined',
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
                for call_func in node.nodes_of_class((astroid.CallFunc,))
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

    @utils.check_messages('openerp-exception-warning')
    def visit_importfrom(self, node):
        if node.modname == 'openerp.exceptions':
            for (import_name, import_as_name) in node.names:
                if import_name == 'Warning' and import_as_name != 'UserError':
                    self.add_message('openerp-exception-warning', node=node)

    @utils.check_messages('class-camelcase')
    def visit_classdef(self, node):
        camelized = self.camelize(node.name)
        if camelized != node.name:
            self.add_message('class-camelcase', node=node,
                             args=(camelized, node.name))

    @utils.check_messages('attribute-deprecated')
    def visit_assign(self, node):
        node_left = node.targets[0]
        if isinstance(node_left, astroid.node_classes.AssName):
            if node_left.name in self.config.attribute_deprecated:
                self.add_message('attribute-deprecated',
                                 node=node_left, args=(node_left.name,))

    def camelize(self, string):
        return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)

    def formatversion(self, string):
        return re.match(self.config.manifest_version_format, string)

    def get_decorators_names(self, decorators):
        nodes = []
        if decorators:
            nodes = decorators.nodes
        return [getattr(decorator, 'attrname', '')
                for decorator in nodes if decorator is not None]

    def get_func_name(self, node):
        func_name = isinstance(node, astroid.Name) and node.name or \
            isinstance(node, astroid.Getattr) and node.attrname or ''
        return func_name

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
        if not isinstance(expr, astroid.CallFunc):
            # ignore raise without a call
            return
        if not expr.args:
            return
        func_name = self.get_func_name(expr.func)

        argument = expr.args[0]
        if isinstance(argument, astroid.CallFunc) and \
                'format' == self.get_func_name(argument.func):
            argument = argument.func.expr
        elif isinstance(argument, astroid.BinOp):
            argument = argument.left

        if isinstance(argument, astroid.Const) and \
                argument.name == 'str' and \
                func_name in self.config.odoo_exceptions:
            self.add_message(
                'translation-required', node=node,
                args=(func_name, argument.as_string()))

    def get_cursor_name(self, node):
        expr_list = []
        node_expr = node.expr
        while isinstance(node_expr, astroid.Getattr):
            expr_list.insert(0, node_expr.attrname)
            node_expr = node_expr.expr
        if isinstance(node_expr, astroid.Name):
            expr_list.insert(0, node_expr.name)
        cursor_name = '.'.join(expr_list)
        return cursor_name
