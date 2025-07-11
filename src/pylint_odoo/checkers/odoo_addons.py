"""Enable checkers to visit all nodes different to modules.
You can use:
    visit_annassign
    visit_arg
    visit_arguments
    visit_assert
    visit_assign
    visit_assignattr
    visit_assignname
    visit_asyncfor
    visit_asyncfunctiondef
    visit_asyncwith
    visit_attribute
    visit_augassign
    visit_await
    visit_binop
    visit_boolop
    visit_break
    visit_call
    visit_child
    visit_classdef
    visit_compare
    visit_comprehension
    visit_const
    visit_constant
    visit_continue
    visit_decorators
    visit_delattr
    visit_delete
    visit_delname
    visit_dict
    visit_dictcomp
    visit_dictunpack
    visit_ellipsis
    visit_empty
    visit_emptynode
    visit_evaluatedobject
    visit_excepthandler
    visit_expr
    visit_extslice
    visit_for
    visit_formattedvalue
    visit_frozenset
    visit_functiondef
    visit_generatorexp
    visit_global
    visit_if
    visit_ifexp
    visit_import
    visit_importfrom
    visit_index
    visit_joinedstr
    visit_keyword
    visit_lambda
    visit_list
    visit_listcomp
    visit_match
    visit_matchas
    visit_matchcase
    visit_matchclass
    visit_matchmapping
    visit_matchor
    visit_matchsequence
    visit_matchsingleton
    visit_matchstar
    visit_matchvalue
    visit_module
    visit_name
    visit_nameconstant
    visit_namedexpr
    visit_nonlocal
    visit_num
    visit_pass
    visit_property
    visit_raise
    visit_response
    visit_return
    visit_set
    visit_setcomp
    visit_slice
    visit_starred
    visit_str
    visit_subscript
    visit_super
    visit_transforms
    visit_try
    visit_tryexcept
    visit_tryfinally
    visit_tuple
    visit_unaryop
    visit_uninferable
    visit_unknown
    visit_while
    visit_with
    visit_yield
    visit_yieldfrom
for more info visit pylint doc
"""

import ast
import itertools
import os
import re
import string
import warnings
from collections import Counter, defaultdict
from urllib.parse import urlparse

from astroid import ClassDef, FunctionDef, NodeNG, nodes
from pylint.checkers import BaseChecker, utils
from pylint.lint import PyLinter

from .. import misc
from .odoo_base_checker import OdooBaseChecker

CHECK_DESCRIPTION = (
    "You can review guidelines here: "
    "https://github.com/OCA/odoo-community.org/blob/master/website/"
    "Contribution/CONTRIBUTING.rst"
)

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal
    "C8101": (
        "One of the following authors must be present in manifest: %s",
        "manifest-required-author",
        CHECK_DESCRIPTION,
    ),
    "C8102": ('Missing required key %s"%s" in manifest file', "manifest-required-key", CHECK_DESCRIPTION),
    "C8103": ('Deprecated key "%s" in manifest file', "manifest-deprecated-key", CHECK_DESCRIPTION),
    "C8105": ('License "%s" not allowed in manifest file.', "license-allowed", CHECK_DESCRIPTION),
    "C8106": (
        'Wrong Version Format "%s" in manifest file. Regex to match: "%s"',
        "manifest-version-format",
        CHECK_DESCRIPTION,
    ),
    "C8107": (
        'String parameter on "%s" requires translation. Use %s%s(%s)',
        "translation-required",
        CHECK_DESCRIPTION,
    ),
    "C8108": ('Name of compute method should start with "_compute_"', "method-compute", CHECK_DESCRIPTION),
    "C8109": ('Name of search method should start with "_search_"', "method-search", CHECK_DESCRIPTION),
    "C8110": ('Name of inverse method should start with "_inverse_"', "method-inverse", CHECK_DESCRIPTION),
    "C8111": (
        'Manifest key development_status "%s" not allowed. Use one of: %s.',
        "development-status-allowed",
        CHECK_DESCRIPTION,
    ),
    "C8112": ("Missing ./README.rst file. Template here: %s", "missing-readme", CHECK_DESCRIPTION),
    "C8113": (
        "No wizard class for model directory. See the complete structure "
        "https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#complete-structure",
        "no-wizard-in-models",
        CHECK_DESCRIPTION,
    ),
    "C8114": ('Category "%s" not allowed in manifest file.', "category-allowed", CHECK_DESCRIPTION),
    "C8115": (
        "Missing %s %sfile",
        "missing-odoo-file",
        CHECK_DESCRIPTION,
    ),
    "E8101": (
        "The author key in the manifest file must be a string (with comma separated values)",
        "manifest-author-string",
        CHECK_DESCRIPTION,
    ),
    "E8102": (
        "Use of cr.commit() directly - More info "
        "https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction",  # noqa: B950
        "invalid-commit",
        CHECK_DESCRIPTION,
    ),
    "E8103": (
        "SQL injection risk. Use parameters if you can. - More info "
        "https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection",
        "sql-injection",
        CHECK_DESCRIPTION,
    ),
    "E8104": (
        "The maintainers key in the manifest file must be a list of strings",
        "manifest-maintainers-list",
        CHECK_DESCRIPTION,
    ),
    "E8106": (
        "Use of external request method `%s` without timeout. It could wait for a long time",
        "external-request-timeout",
        CHECK_DESCRIPTION,
    ),
    "E8130": ("Test folder imported in module %s", "test-folder-imported", CHECK_DESCRIPTION),
    "E8135": ("Compute method calling `write`. Use `update` instead.", "no-write-in-compute", CHECK_DESCRIPTION),
    "E8140": (
        "No exceptions should be raised inside unlink() functions",
        "no-raise-unlink",
        "Use @api.ondelete to add any constraints instead",
    ),
    "E8145": (
        "Manifest version (%s) is lower than migration scripts (%s)",
        "manifest-behind-migrations",
        "Update your manifest version, otherwise the migration script won't run",
    ),
    "E8146": (
        "'name_get' is deprecated. Use '_compute_display_name' instead. More info at https://github.com/odoo/odoo/pull/122085.",
        "deprecated-name-get",
        CHECK_DESCRIPTION,
    ),
    "E8147": (
        'Use string method name `"%s"` to preserve inheritability. '
        "More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126",
        "inheritable-method-string",
        CHECK_DESCRIPTION,
    ),
    "E8148": (
        "Use `%s=lambda self: self.%s()` to preserve inheritability. "
        "More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126",
        "inheritable-method-lambda",
        CHECK_DESCRIPTION,
    ),
    "F8101": ('File "%s": "%s" not found.', "resource-not-exist", CHECK_DESCRIPTION),
    "R8101": (
        "`odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` "
        "use `from odoo.exceptions import UserError`",
        "odoo-exception-warning",
        CHECK_DESCRIPTION,
    ),
    "R8180": (
        'Consider merging classes inherited to "%s" from %s.',
        "consider-merging-classes-inherited",
        CHECK_DESCRIPTION,
    ),
    "R8181": (
        'Invalid email "%s"',
        "invalid-email",
        CHECK_DESCRIPTION,
    ),
    "W8103": ('Translation method _("string") in fields is not necessary.', "translation-field", CHECK_DESCRIPTION),
    "W8105": ('attribute "%s" deprecated', "attribute-deprecated", CHECK_DESCRIPTION),
    "W8106": ('Missing `super` call in "%s" method.', "method-required-super", CHECK_DESCRIPTION),
    "W8107": ('Prohibited override of "%s" method.', "prohibited-method-override", CHECK_DESCRIPTION),
    "W8110": ("Missing `return` (`super` is used) in method %s.", "missing-return", CHECK_DESCRIPTION),
    "W8111": (
        'Field parameter "%s" is no longer supported. Use "%s" instead.',
        "renamed-field-parameter",
        CHECK_DESCRIPTION,
    ),
    "W8113": (
        "The attribute string is redundant. String parameter equal to name of variable",
        "attribute-string-redundant",
        CHECK_DESCRIPTION,
    ),
    "W8114": (
        'Website "%s" in manifest key is not a valid URI. %s',
        "website-manifest-key-not-valid-uri",
        CHECK_DESCRIPTION,
    ),
    "W8115": (
        'Translatable term in "%s" contains variables. Use %s instead',
        "translation-contains-variable",
        CHECK_DESCRIPTION,
    ),
    "W8116": ("Print used. Use `logger` instead.", "print-used", CHECK_DESCRIPTION),
    "W8120": (
        "Translation method _(%s) is using positional string printf formatting with "
        'multiple arguments. Use named placeholder `_("%%(placeholder)s")` instead.',
        "translation-positional-used",
        CHECK_DESCRIPTION,
    ),
    "W8121": (
        "Context overridden using dict. Better using kwargs `with_context(**%s)` or `with_context(key=value)`",
        "context-overridden",
        CHECK_DESCRIPTION,
    ),
    "W8125": (
        'The file "%s" is duplicated in lines %s from manifest key "%s"',
        "manifest-data-duplicated",
        CHECK_DESCRIPTION,
    ),
    "W8138": (
        "pass into block except. If you really need to use the pass consider logging that exception",
        "except-pass",
        CHECK_DESCRIPTION,
    ),
    "W8150": (
        'Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.%s"',
        "odoo-addons-relative-import",
        CHECK_DESCRIPTION,
    ),
    "W8155": (
        "Used builtin function `itertools.groupby`. Prefer `odoo.tools.groupby` instead. "
        "More info about https://github.com/odoo/odoo/issues/105376",
        "bad-builtin-groupby",
        CHECK_DESCRIPTION,
    ),
    "W8160": (
        "%s has been deprecated by Odoo. Please look for alternatives.",
        "deprecated-odoo-model-method",
        CHECK_DESCRIPTION,
    ),
    "W8161": (
        "Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844",
        "prefer-env-translation",
        CHECK_DESCRIPTION,
    ),
    "W8162": (
        "Asset %s should be distributed with module's source code. More info at https://httptoolkit.com/blog/public-cdn-risks/",
        "manifest-external-assets",
        CHECK_DESCRIPTION,
    ),
    "W8163": (
        "Using an empty domain `%s([])` without a `limit` will load all records, may impact performance.",
        "no-search-all",
        CHECK_DESCRIPTION,
    ),
}

DFTL_MANIFEST_REQUIRED_KEYS = ["license"]
DFTL_MANIFEST_REQUIRED_KEYS_APP = ["currency", "images", "license", "support"]
DFTL_ODOO_REQUIRED_FILES_APP = [os.path.join("static", "description", "index.html")]
DFTL_MANIFEST_REQUIRED_AUTHORS = ["Odoo Community Association (OCA)"]
DFTL_MANIFEST_DEPRECATED_KEYS = ["description"]
DFTL_LICENSE_ALLOWED = [
    "AGPL-3",
    "GPL-2 or any later version",
    "GPL-2",
    "GPL-3 or any later version",
    "GPL-3",
    "LGPL-3",
    "OEEL-1",
    "Other OSI approved licence",
    "Other proprietary",
]
DFTL_DEVELOPMENT_STATUS_ALLOWED = [
    "Alpha",
    "Beta",
    "Mature",
    "Production/Stable",
]
DFTL_ATTRIBUTE_DEPRECATED = [
    "_columns",
    "_defaults",
    "length",
]
DFTL_CATEGORY_ALLOWED = []
DFTL_METHOD_REQUIRED_SUPER = [
    "copy",
    "create",
    "default_get",
    "read",
    "setUp",
    "setUpClass",
    "tearDown",
    "tearDownClass",
    "unlink",
    "write",
]
DFTL_PROHIBITED_OVERRIDE_METHODS = []
DFTL_CURSOR_EXPR = [
    "cr",  # old api
    "self._cr",  # new api
    "self.cr",  # controllers and test
    "self.env.cr",
]
DFTL_ODOO_EXCEPTIONS = [
    # Extracted from odoo/exceptions.py of 16.0 and master
    "AccessDenied",
    "AccessError",
    "CacheMiss",
    "except_orm",
    "MissingError",
    "RedirectWarning",
    "UserError",
    "ValidationError",
    "Warning",
]
DFTL_NO_MISSING_RETURN = [
    "__init__",
    "_register_hook",
    "setUp",
    "setUpClass",
    "tearDown",
    "tearDownClass",
]
FIELDS_METHOD = {
    "Many2many": 4,
    "One2many": 2,
    "Many2one": 1,
    "Reference": 1,
    "Selection": 1,
}
DFTL_DEPRECATED_FIELD_PARAMETERS = [
    # From odoo/odoo 10.0: odoo/odoo/fields.py:29
    "digits_compute:digits",
    "select:index",
]
DFTL_EXTERNAL_REQUEST_TIMEOUT_METHODS = [
    "ftplib.FTP",
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
DFTL_DEPRECATED_ODOO_MODEL_METHODS = {"16.0": {"fields_view_get"}}

# Regex used from https://github.com/translate/translate/blob/9de0d72437/translate/filters/checks.py#L50-L62  # noqa
PRINTF_PATTERN = re.compile(
    r"""
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
        )""",
    re.VERBOSE,
)


class OdooAddons(OdooBaseChecker, BaseChecker):
    _from_imports = None
    name = "odoolint"
    msgs = ODOO_MSGS
    options = (
        (
            "attribute-deprecated",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_ATTRIBUTE_DEPRECATED,
                "help": "List of attributes deprecated, separated by a comma.",
            },
        ),
        (
            "cursor-expr",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_CURSOR_EXPR,
                "help": "List of cursor expr separated by a comma.",
            },
        ),
        (
            "deprecated-field-parameters",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_DEPRECATED_FIELD_PARAMETERS,
                "help": "List of deprecated field parameters, separated by a "
                "comma. If the param was renamed, separate the old and "
                "new name with a colon. If the param was removed, keep "
                "the right side of the colon empty. "
                '"deprecated_param:" means that "deprecated_param" was '
                "deprecated and it doesn't have a new alternative. "
                '"deprecated_param:new_param" means that it was '
                'deprecated and renamed as "new_param".',
            },
        ),
        (
            "development-status-allowed",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_DEVELOPMENT_STATUS_ALLOWED,
                "help": "List of development status allowed in manifest file, separated by a comma.",
            },
        ),
        (
            "external-request-timeout-methods",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_EXTERNAL_REQUEST_TIMEOUT_METHODS,
                "help": "List of library.method that must have a timeout "
                "parameter defined, separated by a comma. "
                'e.g. "requests.get,requests.post"',
            },
        ),
        (
            "license-allowed",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_LICENSE_ALLOWED,
                "help": "List of license allowed in manifest file, separated by a comma.",
            },
        ),
        (
            "manifest-deprecated-keys",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_MANIFEST_DEPRECATED_KEYS,
                "help": "List of keys deprecated in manifest file, separated by a comma.",
            },
        ),
        (
            "manifest-required-authors",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_MANIFEST_REQUIRED_AUTHORS,
                "help": "Author names, at least one is required in manifest file.",
            },
        ),
        (
            "manifest-required-keys",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_MANIFEST_REQUIRED_KEYS,
                "help": "List of keys required in manifest file, separated by a comma.",
            },
        ),
        (
            "manifest-required-keys-app",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_MANIFEST_REQUIRED_KEYS_APP,
                "help": "List of keys required in manifest file for apps, separated by a comma.",
            },
        ),
        (
            "manifest-version-format",
            {
                "type": "string",
                "metavar": "<string>",
                "default": misc.DFTL_MANIFEST_VERSION_FORMAT,
                "help": "Regex to check version format in manifest file. "
                'Use "{valid_odoo_versions}" to check the parameter of '
                '"valid_odoo_versions"',
            },
        ),
        (
            "method-required-super",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_METHOD_REQUIRED_SUPER,
                "help": "List of methods where call to `super` is required.separated by a comma.",
            },
        ),
        (
            "prohibited-method-override",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_PROHIBITED_OVERRIDE_METHODS,
                "help": "List of methods that have been marked as prohibited to override.",
            },
        ),
        (
            "no-missing-return",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_NO_MISSING_RETURN,
                "help": "List of valid missing return method names, " "separated by a comma.",
            },
        ),
        (
            "odoo-exceptions",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_ODOO_EXCEPTIONS,
                "help": "List of odoo exceptions separated by a comma.",
            },
        ),
        (
            "odoo-required-files",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_ODOO_REQUIRED_FILES_APP,
                "help": (
                    "List of mandatory relative paths (comma-separated) expected inside Odoo module. "
                    "Example: static/description/index.html"
                ),
            },
        ),
        (
            "readme-template-url",
            {
                "type": "string",
                "metavar": "<string>",
                "default": misc.DFTL_README_TMPL_URL,
                "help": "URL of README.rst template file",
            },
        ),
        (
            "valid-odoo-versions",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": misc.DFTL_VALID_ODOO_VERSIONS,
                "help": "List of valid odoo versions separated by a comma.",
            },
        ),
        (
            "deprecated-odoo-model-methods",
            {
                "type": "string",
                "metavar": "python_expression",
                "default": "",
                "help": "Dictionary consisting of versions (keys) and methods that have been marked as deprecated.",
            },
        ),
        (
            "category-allowed",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_CATEGORY_ALLOWED,
                "help": "List of categories allowed in manifest file, separated by a comma.",
            },
        ),
    )

    checks_maxmin_odoo_version = {
        # For v14.0 use custom_logging.py checks e.g. "translation-not-lazy"
        "translation-contains-variable": {
            "odoo_maxversion": "13.0",
        },
        "no-raise-unlink": {"odoo_minversion": "15.0"},
        "prefer-env-translation": {"odoo_minversion": "18.0"},
        "deprecated-name-get": {"odoo_minversion": "17.0"},
    }

    def __init__(self, linter: PyLinter):
        super().__init__(linter)
        self._deprecated_odoo_methods = set()
        self.deprecated_field_parameters = {}
        self._odoo_inherit_items = defaultdict(set)

    def close(self):
        """Final process get all cached values and add messages"""
        for (_manifest_path, odoo_class_inherit), inh_nodes in self._odoo_inherit_items.items():
            # Skip _inherit='other.model' _name='model.name' because is valid
            inh_nodes = {
                inh_node for inh_node in inh_nodes if not getattr(inh_node.parent, "odoo_attribute_name", None)
            }
            if len(inh_nodes) <= 1:
                continue
            path_nodes = []
            # deterministic order of the output
            inh_nodes = sorted(inh_nodes, key=lambda node: (node.root().file, node.lineno))
            first_node = inh_nodes.pop()
            for node in inh_nodes:
                relpath = os.path.relpath(node.root().file, os.getcwd())
                path_nodes.append("%s:%d:%d" % (relpath, node.lineno, node.col_offset))
            self.add_message(
                "consider-merging-classes-inherited", node=first_node, args=(odoo_class_inherit, ", ".join(path_nodes))
            )
        self._odoo_inherit_items = defaultdict(set)

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

    def _get_max_valid_odoo_versions(self):
        odoo_versions = [misc.version_parse(odoo_version) for odoo_version in self.linter.config.valid_odoo_versions]
        if () in odoo_versions:
            # Empty value means odoo_version value could not be adapted
            return
        max_valid_version = max(odoo_versions)
        return max_valid_version

    def open(self):
        super().open()
        self.deprecated_field_parameters = self.colon_list_to_dict(self.linter.config.deprecated_field_parameters)

        if self.linter.config.deprecated_odoo_model_methods:
            deprecated_model_methods = ast.literal_eval(self.linter.config.deprecated_odoo_model_methods)
        else:
            deprecated_model_methods = DFTL_DEPRECATED_ODOO_MODEL_METHODS

        max_valid_version = self._get_max_valid_odoo_versions()
        if max_valid_version is None:
            warnings.warn(
                f"Invalid manifest versions format {self.linter.config.valid_odoo_versions}. "
                "It was not possible to supress checks based on particular odoo version",
                UserWarning,
                stacklevel=2,
            )
            return
        for version, checks in deprecated_model_methods.items():
            if misc.version_parse(version) <= max_valid_version:
                self._deprecated_odoo_methods.update(checks)

    def colon_list_to_dict(self, colon_list):
        """Converts a colon list to a dictionary.

        :param colon_list: A list of strings representing keys and values,
            separated with a colon. If a key doesn't have a value, keep the
            right side of the colon empty.
        :type colon_list: list
        :returns: A dictionary with the values assigned to corresponding keys.
        :rtype: dict

        :Example:

        self.colon_list_to_dict(['colon:list', 'empty_key:'])
        {'colon': 'list', 'empty_key': ''}
        """
        return dict(item.split(":") for item in colon_list)

    def _sqli_allowable(self, node):
        # sql.SQL or sql.Identifier is OK
        if self._is_psycopg2_sql(node):
            return True
        if isinstance(node, nodes.FormattedValue):
            if hasattr(node, "value"):
                return self._sqli_allowable(node.value)
            if hasattr(node, "values"):
                return all(self._sqli_allowable(v) for v in node.values)
        if isinstance(node, nodes.Call):
            node = node.func
        # self._thing is OK (mostly self._table), self._thing() also because
        # it's a common pattern of reports (self._select, self._group_by, ...)
        return (
            isinstance(node, nodes.Attribute)
            and isinstance(node.expr, nodes.Name)
            and node.attrname.startswith("_")
            # cr.execute('SELECT * FROM %s' % 'table') is OK
            # since that is a constant and constant can not be injected
            or isinstance(node, nodes.Const)
        )

    def _is_psycopg2_sql(self, node):
        if isinstance(node, nodes.Name):
            for assignation_node in self._get_assignation_nodes(node):
                if self._is_psycopg2_sql(assignation_node):
                    return True
        if not isinstance(node, nodes.Call) or not isinstance(node.func, (nodes.Attribute, nodes.Name)):
            return False
        imported_name = node.func.as_string().split(".")[0]
        imported_node = node.root().locals.get(imported_name)
        # "from psycopg2 import *" not considered since that it is hard
        # and there is another check detecting these kind of imports
        if not imported_node:
            return None
        imported_node = imported_node[0]
        if isinstance(imported_node, nodes.ImportFrom):
            package_names = imported_node.modname.split(".")[:1]
        elif isinstance(imported_node, nodes.Import):
            package_names = [name[0].split(".")[0] for name in imported_node.names]
        else:
            return False
        if "psycopg2" in package_names:
            return True

    def _check_node_for_sqli_risk(self, node):
        if isinstance(node, nodes.BinOp) and node.op in ("%", "+"):
            if isinstance(node.right, nodes.Tuple):
                # execute("..." % (self._table, thing))
                if not all(map(self._sqli_allowable, node.right.elts)):
                    return True
            elif isinstance(node.right, nodes.Dict):
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
            if not self._sqli_allowable(node.left) and self._check_node_for_sqli_risk(node.left):
                return True

        # check execute("...".format(self._table, table=self._table))
        # ignore sql.SQL().format
        if isinstance(node, nodes.Call) and isinstance(node.func, nodes.Attribute) and node.func.attrname == "format":
            if not all(map(self._sqli_allowable, node.args or [])):
                return True

            if not all(self._sqli_allowable(keyword.value) for keyword in (node.keywords or [])):
                return True

        # Check fstrings (PEP 498). Only Python >= 3.6
        if isinstance(node, nodes.JoinedStr):
            if hasattr(node, "value"):
                return self._sqli_allowable(node.value)
            if hasattr(node, "values"):
                return not all(self._sqli_allowable(v) for v in node.values)

        return False

    def _check_sql_injection_risky(self, node):
        # Inspired from OCA/pylint-odoo project
        # Thanks @moylop260 (Moises Lopez) & @nilshamerlinck (Nils Hamerlinck)
        current_file_bname = os.path.basename(self.linter.current_file)
        if not (
            # .execute() or .executemany()
            isinstance(node, nodes.Call)
            and node.args
            and isinstance(node.func, nodes.Attribute)
            and node.func.attrname in ("execute", "executemany")
            and
            # cursor expr (see above)
            self.get_cursor_name(node.func) in DFTL_CURSOR_EXPR
            and
            # cr.execute("select * from %s" % foo, [bar]) -> probably a good reason
            # for string formatting
            len(node.args) <= 1
            and
            # ignore in test files, probably not accessible
            not current_file_bname.startswith("test_")
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
        if isinstance(node, (nodes.Name, nodes.Subscript)):
            # 1) look for parent method / controller
            current = node
            while current and not isinstance(current.parent, nodes.FunctionDef):
                current = current.parent
            if current:
                parent = current.parent
                # 2) check how was the variable built
                for assign_node in parent.nodes_of_class(nodes.Assign):
                    if assign_node.targets[0].as_string() == node.as_string():
                        yield assign_node.value

    def _get_str_value(self, node):
        """Check if the node is str (constant) and get value or f-string get values"""
        if isinstance(node, nodes.Const) and node.name == "str":
            return node.value
        if isinstance(node, nodes.JoinedStr):
            value = ""
            for val in node.values:
                if isinstance(val, nodes.Const):
                    value += val.value
                else:
                    value += "{}"
            return value

    @utils.only_required_for_messages(
        "attribute-string-redundant",
        "bad-builtin-groupby",
        "context-overridden",
        "external-request-timeout",
        "inheritable-method-lambda",
        "inheritable-method-string",
        "invalid-commit",
        "method-compute",
        "method-inverse",
        "method-search",
        "no-search-all",
        "no-write-in-compute",
        "prefer-env-translation",
        "print-used",
        "renamed-field-parameter",
        "sql-injection",
        "translation-contains-variable",
        "translation-field",
        "translation-positional-used",
        "translation-required",
    )
    def visit_call(self, node):
        if (
            self.linter.is_message_enabled("print-used", node.lineno)
            and isinstance(node.func, nodes.Name)
            and node.func.name == "print"
        ):
            infer_node = utils.safe_infer(node.func)
            if utils.is_builtin_object(infer_node) and infer_node.name == "print":
                self.add_message("print-used", node=node)
        if (
            "fields" == self.get_func_lib(node.func)
            and isinstance(node.parent, nodes.Assign)
            and isinstance(node.parent.parent, nodes.ClassDef)
        ):
            args = self.join_node_args_kwargs(node)
            index = 0
            field_name = ""
            if (
                isinstance(node.parent, nodes.Assign)
                and node.parent.targets
                and isinstance(node.parent.targets[0], nodes.AssignName)
            ):
                field_name = node.parent.targets[0].name.replace("_", " ")
            is_related = bool([1 for kw in node.keywords or [] if kw.arg == "related"])
            for argument in args:
                argument_aux = argument
                # Check this 'name = fields.Char("name")'
                if (
                    not is_related
                    and self._get_str_value(argument) == field_name.title()
                    and index == FIELDS_METHOD.get(argument.parent.func.attrname, 0)
                ):
                    self.add_message("attribute-string-redundant", node=node)
                if isinstance(argument, nodes.Keyword):
                    argument_aux = argument.value
                    deprecated = self.deprecated_field_parameters
                    value = self._get_str_value(argument_aux)
                    if (
                        argument.arg in ["compute", "search", "inverse"]
                        and value is not None
                        and not value.startswith("_" + argument.arg + "_")
                    ):
                        self.add_message("method-" + argument.arg, node=argument_aux)
                    # Check if the param string is equal to the name
                    #   of variable
                    elif (
                        not is_related
                        and argument.arg == "string"
                        and self._get_str_value(argument_aux) == field_name.title()
                    ):
                        self.add_message("attribute-string-redundant", node=node)
                    elif argument.arg in deprecated:
                        self.add_message(
                            "renamed-field-parameter", node=node, args=(argument.arg, deprecated[argument.arg])
                        )
                    # no write in compute method
                    if (
                        self.linter.is_message_enabled("no-write-in-compute", argument.lineno)
                        and argument.arg == "compute"
                        and isinstance(argument.value, (nodes.Const, nodes.Name))
                    ):
                        method_name = (
                            argument.value.value
                            if isinstance(argument.value, nodes.Const)
                            else argument.value.name
                            if isinstance(argument.value, nodes.Name)
                            else None
                        )
                        if method_name and self.class_odoo_models:
                            self.odoo_computes.add(method_name)
                    if (
                        self.linter.is_message_enabled("inheritable-method-string", node.lineno)
                        and argument.arg in ["compute", "search", "inverse"]
                        and isinstance(argument.value, nodes.Name)
                    ):
                        # Check if the value is a method of the class
                        infered = utils.safe_infer(argument.value)
                        if isinstance(infered, nodes.FunctionDef) and infered.is_method():
                            self.add_message(
                                "inheritable-method-string", node=argument.value, args=(argument.value.name,)
                            )
                    if (
                        self.linter.is_message_enabled("inheritable-method-lambda", node.lineno)
                        and argument.arg in ["default", "domain"]
                        and isinstance(argument.value, nodes.Name)
                    ):
                        # Check if the value is a method of the class
                        infered = utils.safe_infer(argument.value)
                        if isinstance(infered, nodes.FunctionDef) and infered.is_method():
                            self.add_message(
                                "inheritable-method-lambda",
                                node=argument.value,
                                args=(
                                    argument.arg,
                                    argument.value.name,
                                ),
                            )

                if (
                    isinstance(argument_aux, nodes.Call)
                    and self.get_func_name(argument_aux.func) in misc.TRANSLATION_METHODS
                ):
                    self.add_message("translation-field", node=argument_aux)
                index += 1
        # Check cr.commit()
        if (
            isinstance(node, nodes.Call)
            and isinstance(node.func, nodes.Attribute)
            and node.func.attrname == "commit"
            and self.get_cursor_name(node.func) in self.linter.config.cursor_expr
        ):
            self.add_message("invalid-commit", node=node)

        if (
            isinstance(node, nodes.Call)
            and isinstance(node.func, nodes.Attribute)
            and node.func.attrname == "with_context"
            and not node.keywords
            and node.args
        ):
            # with_context(**ctx) is considered a keywords
            # So, if only one args is received it is overridden
            self.add_message("context-overridden", node=node, args=(node.args[0].as_string(),))

        # Call the message_post()
        base_dirname = os.path.basename(os.path.normpath(os.path.dirname(self.linter.current_file)))
        if (
            base_dirname != "tests"
            and isinstance(node, nodes.Call)
            and isinstance(node.func, nodes.Attribute)
            and node.func.attrname == "message_post"
        ):
            for arg in itertools.chain(node.args, node.keywords or []):
                if isinstance(arg, nodes.Keyword):
                    keyword = arg.arg
                    value = arg.value
                else:
                    keyword = ""
                    value = arg
                if keyword and keyword not in ("subject", "body"):
                    continue
                as_string = ""
                # case: message_post(body='String')
                if isinstance(value, (nodes.Const, nodes.JoinedStr)):
                    as_string = value.as_string()
                # case: message_post(body='String %s' % (...))
                elif (
                    isinstance(value, nodes.BinOp)
                    and value.op == "%"
                    and isinstance(value.left, (nodes.Const, nodes.JoinedStr))
                    # The right part is translatable only if it's a
                    # function or a list of functions
                    and not (
                        isinstance(value.right, (nodes.Call, nodes.Tuple, nodes.List))
                        and all(isinstance(child, nodes.Call) for child in getattr(value.right, "elts", []))
                    )
                ):
                    as_string = value.left.as_string()
                # case: message_post(body='String {...}'.format(...))
                elif (
                    isinstance(value, nodes.Call)
                    and isinstance(value.func, nodes.Attribute)
                    and isinstance(value.func.expr, (nodes.Const, nodes.JoinedStr))
                    and value.func.attrname == "format"
                ):
                    as_string = value.func.expr.as_string()
                if as_string:
                    keyword = keyword and "%s=" % keyword
                    tl_method = "_"
                    max_valid_odoo_version = self._get_max_valid_odoo_versions()
                    if max_valid_odoo_version is None or max_valid_odoo_version >= (8, 0):
                        tl_method = "self.env._"
                    self.add_message(
                        "translation-required", node=node, args=("message_post", keyword, tl_method, as_string)
                    )

        # Call _(...) with variables into the term to be translated
        if self.get_func_name(node.func) in misc.TRANSLATION_METHODS and node.args:
            # "_" -> isinstance(node.func, nodes.Name)
            # "self.env._" -> isinstance(node.func, nodes.Attribute)
            if isinstance(node.func, nodes.Name) and node.func.as_string() in misc.TRANSLATION_METHODS:
                self.add_message("prefer-env-translation", node=node)

            wrong = ""
            right = ""
            arg = node.args[0]
            # case: _('...' % (variables))
            if isinstance(arg, nodes.BinOp) and arg.op == "%":
                wrong = "%s %% %s" % (arg.left.as_string(), arg.right.as_string())
                right = "_(%s) %% %s" % (arg.left.as_string(), arg.right.as_string())
            # Case: _('...'.format(variables))
            elif (
                isinstance(arg, nodes.Call)
                and isinstance(arg.func, nodes.Attribute)
                and isinstance(arg.func.expr, nodes.Const)
                and arg.func.attrname == "format"
            ):
                wrong = arg.as_string()
                params_as_string = ", ".join([x.as_string() for x in itertools.chain(arg.args, arg.keywords or [])])
                right = "_(%s).format(%s)" % (arg.func.expr.as_string(), params_as_string)
            if wrong and right:
                self.add_message("translation-contains-variable", node=node, args=(wrong, right))

            # translation-positional-used: Check "string to translate"
            # to check "%s %s..." used where the position can't be changed
            str2translate = arg.as_string()
            printf_args = self._get_printf_str_args_kwargs(str2translate)
            format_args = self._get_format_str_args_kwargs(str2translate)[0]
            if isinstance(printf_args, tuple) and len(printf_args) >= 2 or len(format_args) >= 2:
                # Return tuple for %s and dict for %(varname)s
                # Check just the following cases "%s %s..."
                self.add_message("translation-positional-used", node=node, args=(str2translate,))

        # SQL Injection
        if self._check_sql_injection_risky(node):
            self.add_message("sql-injection", node=node)

        # external-request-timeout
        lib_alias = self.get_func_lib(node.func)
        # Use dict "self._from_imports" to know the source library of the method
        lib_original = self._from_imports.get(lib_alias) or lib_alias
        func_name = self.get_func_name(node.func)
        lib_original_func_name = (
            # If it using "requests.request()"
            "%s.%s" % (lib_original, func_name)
            if lib_original
            # If it using "from requests import request;request()"
            else self._from_imports.get(func_name)
        )
        if lib_original_func_name in self.linter.config.external_request_timeout_methods:
            for argument in self.join_node_args_kwargs(node):
                if not isinstance(argument, nodes.Keyword):
                    continue
                if argument.arg == "timeout":
                    break
            else:
                self.add_message("external-request-timeout", node=node, args=(lib_original_func_name,))
        if self.linter.is_message_enabled("bad-builtin-groupby", node.lineno) and node.func.as_string().endswith(
            "groupby"
        ):
            if node.func.as_string() == "itertools.groupby":
                self.add_message("bad-builtin-groupby", node=node)
            elif not node.func.as_string().endswith("tools.groupby"):
                # infer node is heavy so discarding cases early to improve perf
                infer_node = utils.safe_infer(node.func)
                if infer_node and infer_node.qname() == "itertools.groupby":
                    self.add_message("bad-builtin-groupby", node=node)
        if (
            self.linter.is_message_enabled("no-search-all", node.lineno)
            # only odoo valid structure class -> def -> search()
            and isinstance(node.scope(), nodes.FunctionDef)
            and isinstance(node.scope().parent, nodes.ClassDef)
            and self.get_odoo_models_class(node.scope().parent)
            and self.get_func_name(node.func) in ("search", "search_read")
            and (node.args or node.keywords)
        ):
            if node.args:
                domain = node.args[0]
            else:
                domain = next((kw.value for kw in node.keywords if kw.arg == "domain"), None)
            if domain:
                empty_domain = False
                if isinstance(domain, nodes.List) and not domain.elts:
                    # search([])
                    # search(domain=[])
                    empty_domain = True
                elif isinstance(domain, nodes.Name):
                    # domain=[]; search(domain)
                    # domain=[]; search(domain=domain)

                    domain_assignation = utils.safe_infer(domain)
                    if (
                        domain_assignation is not None
                        and isinstance(domain_assignation, nodes.List)
                        # empty list. Infer consider domain += ... with values not needed look for nodes.AugAssign
                        and not domain_assignation.elts
                        # assigned the domain in the same method than search call
                        and domain_assignation.scope() == node.scope()
                    ):
                        empty_domain = True
                        for subnode in node.scope().nodes_of_class(nodes.Call):
                            if (
                                # only get nodes between assignation domain=... to use in search(domain)
                                # not consider DOMAIN_EMPTY global variables in order to avoid
                                # looking for in the whole code since it could be slow and complex
                                # to detect an "append"
                                domain_assignation.lineno <= subnode.lineno <= node.lineno
                                and self.get_func_lib(subnode.func) == domain.name
                                and self.get_func_name(subnode.func) in ("append", "extend", "insert")
                            ):
                                # Consider domain.append(), domain.extend(), domain.insert()
                                empty_domain = False
                                break
                limit_or_count = (
                    any(kw.arg in ("limit", "count") for kw in node.keywords)
                    or len(node.args) >= 3
                    or (self.get_func_name(node.func) == "search" and len(node.args) >= 5)
                )
                if empty_domain and not limit_or_count:
                    self.add_message("no-search-all", node=node, args=(self.get_func_name(node.func),))

    @utils.only_required_for_messages(
        "category-allowed",
        "development-status-allowed",
        "invalid-email",
        "license-allowed",
        "manifest-author-string",
        "manifest-behind-migrations",
        "manifest-data-duplicated",
        "manifest-deprecated-key",
        "manifest-external-assets",
        "manifest-maintainers-list",
        "manifest-required-author",
        "manifest-required-key",
        "manifest-version-format",
        "missing-odoo-file",
        "missing-readme",
        "resource-not-exist",
        "website-manifest-key-not-valid-uri",
    )
    def visit_dict(self, node):
        if not os.path.basename(self.linter.current_file) in misc.MANIFEST_FILES or not isinstance(
            node.parent, nodes.Expr
        ):
            return
        try:
            manifest_dict = ast.literal_eval(node.as_string())
        except ValueError:
            # There is code that the node is formed but literal_eval raises error
            # e.g. {"key": "" or ""}
            return
        manifest_keys_nodes = {
            key_node.value: key_node for key_node, _value in node.items if isinstance(key_node, nodes.Const)
        }

        # Check author is a string
        author = manifest_dict.get("author", "")
        if not isinstance(author, str):
            self.add_message("manifest-author-string", node=manifest_keys_nodes.get("author") or node)
        else:
            # Check author required
            authors = {auth.strip() for auth in author.split(",")}

            required_authors = set(self.linter.config.manifest_required_authors)
            if not authors & required_authors:
                # None of the required authors is present in the manifest
                # Authors will be printed as 'author1', 'author2', ...
                authors_str = ", ".join(["'%s'" % auth for auth in required_authors])
                self.add_message(
                    "manifest-required-author", node=manifest_keys_nodes.get("author") or node, args=(authors_str,)
                )

        # Check keys required
        required_keys = self.linter.config.manifest_required_keys
        for required_key in required_keys:
            if required_key not in manifest_dict:
                self.add_message(
                    "manifest-required-key",
                    node=node,
                    args=(
                        "",
                        required_key,
                    ),
                )

        # Check keys deprecated
        deprecated_keys = self.linter.config.manifest_deprecated_keys
        for deprecated_key in deprecated_keys:
            if deprecated_key in manifest_dict:
                self.add_message(
                    "manifest-deprecated-key",
                    node=manifest_keys_nodes.get(deprecated_key) or node,
                    args=(deprecated_key,),
                )

        # Check license allowed
        license_str = manifest_dict.get("license", None)
        if license_str and license_str not in self.linter.config.license_allowed:
            self.add_message("license-allowed", node=manifest_keys_nodes.get("license") or node, args=(license_str,))

        # Check category allowed
        category_str = manifest_dict.get("category")
        if (
            category_str
            and self.linter.config.category_allowed
            and category_str not in self.linter.config.category_allowed
        ):
            self.add_message(
                "category-allowed", node=manifest_keys_nodes.get("category") or node, args=(category_str,)
            )

        # Check version format
        version_format = manifest_dict.get("version", "")

        # Check version format
        formatrgx, manifest_version_format_parsed = self.formatversion(version_format)
        if version_format and not formatrgx:
            self.add_message(
                "manifest-version-format",
                node=manifest_keys_nodes.get("version") or node,
                args=(version_format, manifest_version_format_parsed),
            )

        # Check manifest-behind-migrations
        migrations_path = os.path.join(os.path.dirname(self.linter.current_file), "migrations")
        if self.linter.is_message_enabled("manifest-behind-migrations") and os.path.isdir(migrations_path):
            for migration_path in sorted(os.listdir(migrations_path), reverse=True):
                if not os.path.isdir(os.path.join(migrations_path, migration_path)):
                    continue
                try:
                    migration_path_v = misc.version2tuple(migration_path)
                    version_format_v = misc.version2tuple(version_format)
                    if migration_path_v > version_format_v:
                        self.add_message(
                            "manifest-behind-migrations", node=node, args=(version_format, migration_path)
                        )
                        break
                except misc.InvalidVersion:
                    continue

        # Check if resource exist
        # Check manifest-data-duplicated
        dirname = os.path.dirname(self.linter.current_file)
        for key in set(misc.MANIFEST_DATA_KEYS) & set(manifest_dict.keys()):
            list_node = node.getitem(manifest_keys_nodes.get(key))
            fname_str_nodes = defaultdict(list)
            for str_node in getattr(list_node, "elts", []):
                fname_str_nodes[str_node.value].append(str_node)
            for resource, coincidences in Counter(manifest_dict.get(key) or []).items():
                fname_str_node = (
                    fname_str_nodes.get(resource)[0] if len(fname_str_nodes.get(resource) or []) >= 1 else node
                )
                if coincidences >= 2:
                    lines_str = ", ".join(
                        f"{fname_str_node.lineno}" for fname_str_node in (fname_str_nodes.get(resource) or [])[1:]
                    )
                    self.add_message(
                        "manifest-data-duplicated",
                        node=fname_str_node,
                        args=(resource, lines_str, key),
                    )
                if os.path.isfile(os.path.join(dirname, resource)):
                    continue
                self.add_message("resource-not-exist", node=fname_str_node, args=(key, resource))
                # Check missing readme

        if not any(os.path.isfile(os.path.join(dirname, readme)) for readme in misc.README_FILES):
            self.add_message("missing-readme", args=(self.linter.config.readme_template_url,), node=node)

        # Check if the website is valid URI
        website = manifest_dict.get("website") or ""
        msg = ""
        url_is_valid = False
        try:
            url_is_valid = misc.validate_url(website)
        except misc.InvalidURL as url_exc:
            msg = str(url_exc)
        if website and not url_is_valid:
            self.add_message(
                "website-manifest-key-not-valid-uri",
                node=manifest_keys_nodes.get("website") or node,
                args=(website, msg),
            )

        # Check if the email is valid
        if (email_support := manifest_dict.get("support")) and not misc.validate_email(email_support):
            self.add_message("invalid-email", node=manifest_keys_nodes.get("support") or node, args=(email_support,))

        # Check valid development_status values
        dev_status = manifest_dict.get("development_status")
        if dev_status and dev_status not in self.linter.config.development_status_allowed:
            valid_status = ", ".join(self.linter.config.development_status_allowed)
            self.add_message(
                "development-status-allowed",
                node=manifest_keys_nodes.get("development_status") or node,
                args=(dev_status, valid_status),
            )

        # Check maintainers key is a list of strings
        maintainers = manifest_dict.get("maintainers")
        if maintainers and (
            not isinstance(maintainers, list) or any(not isinstance(item, str) for item in maintainers)
        ):
            self.add_message("manifest-maintainers-list", node=manifest_keys_nodes.get("maintainers") or node)

        # Check there are no external assets
        if self.linter.is_message_enabled("manifest-external-assets"):
            assets_node = None
            for item in node.items:
                if item[0].value == "assets":
                    assets_node = item[1]

            # it is important to use the actual astroid.node instead of manifest_dict, otherwise the
            # errors are not attributed to the proper node.
            if assets_node:
                self._check_manifest_external_assets(assets_node)

        if "price" in manifest_dict:
            # manifest has "price" so it is an App
            app_required_keys = set(self.linter.config.manifest_required_keys_app) - set(
                self.linter.config.manifest_required_keys
            )
            for app_required_key in app_required_keys:
                self.add_message(
                    "manifest-required-key",
                    node=node,
                    args=(
                        "app ",
                        app_required_key,
                    ),
                )

            for subpath in self.linter.config.odoo_required_files:
                required_path = os.path.join(dirname, subpath)
                if not os.path.isfile(required_path):
                    required_relative_path = os.path.join(os.path.basename(dirname), subpath)
                    self.add_message(
                        "missing-odoo-file",
                        node=node,
                        args=(
                            required_relative_path,
                            "app ",
                        ),
                    )

    def _check_manifest_external_assets(self, node):
        def is_external_url(url):
            return urlparse(url).scheme

        for _, item in node.items:
            for element in item.elts:
                if (value := self._get_str_value(element)) is not None:
                    if is_external_url(value):
                        self.add_message("manifest-external-assets", node=element, args=(value,))
                elif isinstance(element, (nodes.Tuple, nodes.List)):
                    for entry in element.elts:
                        if isinstance(entry, nodes.Const) and is_external_url(entry.value):
                            self.add_message("manifest-external-assets", node=element, args=(entry.value,))

    def check_deprecated_odoo_method(self, node: NodeNG) -> bool:
        """Verify the given method is not marked as deprecated under the set Odoo versions.
        :param node: Function definition to be checked
        :return: True if the method is deprecated, false otherwise.
        """
        try:
            if not self.get_odoo_models_class(node.parent):
                return False
        except AttributeError:
            return False

        return node.name in self._deprecated_odoo_methods

    @utils.only_required_for_messages(
        "deprecated-name-get",
        "deprecated-odoo-model-method",
        "method-required-super",
        "missing-return",
        "prohibited-method-override",
    )
    def visit_functiondef(self, node):
        """Check that `api.one` and `api.multi` decorators not exists together
        Check that method `copy` exists `api.one` decorator
        Check deprecated `api.one`.
        """
        if not node.is_method():
            return

        if self.is_odoo_message_enabled("deprecated-odoo-model-method") and self.check_deprecated_odoo_method(node):
            self.add_message("deprecated-odoo-model-method", node=node, args=(node.name,))
        if self.is_odoo_message_enabled("deprecated-name-get") and node.name == "name_get":
            self.add_message("deprecated-name-get", node=node)
        if node.name in self.linter.config.method_required_super:
            calls = [
                call_func.func.name
                for call_func in node.nodes_of_class((nodes.Call,))
                if isinstance(call_func.func, nodes.Name)
            ]
            if "super" not in calls:
                self.add_message("method-required-super", node=node, args=(node.name,))

        there_is_super = False
        for stmt in node.nodes_of_class(nodes.Call):
            func = stmt.func
            if isinstance(func, nodes.Name) and func.name == "super":
                there_is_super = True
                break

        # Verify if super attributes are prohibited methods to override
        if there_is_super and self.linter.config.prohibited_method_override or DFTL_PROHIBITED_OVERRIDE_METHODS:
            for attr in node.nodes_of_class(nodes.Attribute):
                if attr.attrname != node.name or not hasattr(attr.expr, "func"):
                    continue
                func_name = self.get_func_name(attr.expr.func)
                if func_name == "super" and (
                    attr.attrname in self.linter.config.prohibited_method_override
                    or attr.attrname in DFTL_PROHIBITED_OVERRIDE_METHODS
                ):
                    self.add_message("prohibited-method-override", node=node, args=(attr.attrname,))

        there_is_return = any(node.nodes_of_class(nodes.Return, skip_klass=(nodes.FunctionDef, nodes.ClassDef)))
        if (
            there_is_super
            and not there_is_return
            and not node.is_generator()
            and node.name not in self.linter.config.no_missing_return
        ):
            self.add_message("missing-return", node=node, args=(node.name,))

    @utils.only_required_for_messages(
        "external-request-timeout", "odoo-addons-relative-import", "test-folder-imported"
    )
    def visit_import(self, node):
        self._from_imports.update({alias or name: "%s" % name for name, alias in node.names})
        self.check_odoo_relative_import(node)
        self.check_folder_test_imported(node)

    @utils.only_required_for_messages(
        "external-request-timeout", "odoo-addons-relative-import", "odoo-exception-warning", "test-folder-imported"
    )
    def visit_importfrom(self, node):
        if node.modname == "odoo.exceptions":
            for import_name, _import_as_name in node.names:
                if import_name == "Warning":
                    self.add_message("odoo-exception-warning", node=node)
        self._from_imports.update({alias or name: "%s.%s" % (node.modname, name) for name, alias in node.names})
        self.check_odoo_relative_import(node)
        self.check_folder_test_imported(node)

    @utils.only_required_for_messages(
        "attribute-deprecated", "consider-merging-classes-inherited", "no-wizard-in-models"
    )
    def visit_assign(self, node):
        node_left = node.targets[0]
        if (
            self.linter.is_message_enabled("attribute-deprecated", node.lineno)
            and isinstance(node.parent, nodes.ClassDef)
            and isinstance(node_left, nodes.AssignName)
            and [1 for m in node.parent.basenames if "Model" in m]
        ):
            if node_left.name in self.linter.config.attribute_deprecated:
                self.add_message("attribute-deprecated", node=node_left, args=(node_left.name,))
        if self.linter.is_message_enabled(
            "consider-merging-classes-inherited", node.lineno
        ) or self.linter.is_message_enabled("no-wizard-in-models"):
            node_left = node.targets[0]
            if (
                not isinstance(node_left, nodes.node_classes.AssignName)
                or node_left.name not in ("_inherit", "_name")
                or not isinstance(node.value, nodes.node_classes.Const)
                or not isinstance(node.parent, nodes.ClassDef)
            ):
                return
            if node_left.name == "_name":
                node.parent.odoo_attribute_name = node.value.value
                return
            odoo_class_name = getattr(node.parent, "odoo_attribute_name", None)
            odoo_class_inherit = node.value.value
            # Used in no-wizard-in-models check
            node.parent.odoo_attribute_inherit = odoo_class_inherit
            if (
                not self.linter.is_message_enabled("consider-merging-classes-inherited", node.lineno)
                or odoo_class_name
                and odoo_class_name != odoo_class_inherit
            ):
                # Skip _name='model.name' _inherit='other.model' because is valid
                # Skip pylint magic disable comment for consider-merging-classes-inherited
                return
            node_dirpath = os.path.dirname(node.root().file)
            manifest_path = misc.walk_up(node_dirpath, tuple(misc.MANIFEST_FILES), misc.top_path(node_dirpath))
            if manifest_path:
                self._odoo_inherit_items[(manifest_path, odoo_class_inherit)].add(node)

    @staticmethod
    def get_func_name(node):
        func_name = (
            isinstance(node, nodes.Name) and node.name or isinstance(node, nodes.Attribute) and node.attrname or ""
        )
        return func_name

    def get_func_lib(self, node):
        if isinstance(node, nodes.Attribute) and isinstance(node.expr, nodes.Name):
            return node.expr.name
        return ""

    @staticmethod
    def _is_unlink(node: FunctionDef) -> bool:
        parent = getattr(node, "parent", False)
        return (
            isinstance(parent, ClassDef)
            and ("_name" in parent.locals or "_inherit" in parent.locals)
            and node.name == "unlink"
        )

    @staticmethod
    def get_enclosing_function(node: NodeNG, depth=10):
        parent = getattr(node, "parent", False)
        for _i in range(depth):
            if not parent or isinstance(parent, FunctionDef):
                break
            parent = parent.parent

        return parent

    def check_translation_required(self, node):
        """Search methods with an untranslated string parameter.
        Wrong:  ``raise UserError('My String')``
        Correct: ``raise UserError(_('My String'))``
        """
        # TODO: Consider the case where a string variable is used
        # my_string = 'My String'  # wrong
        # raise UserError(my_string)  # Detect variable string here
        if node.exc is None:
            # ignore empty raise
            return
        expr = node.exc
        if not isinstance(expr, nodes.Call):
            # ignore raise without a call
            return
        if not expr.args:
            return
        func_name = self.get_func_name(expr.func)

        argument = expr.args[0]
        if isinstance(argument, nodes.Call) and "format" == self.get_func_name(argument.func):
            argument = argument.func.expr
        elif isinstance(argument, nodes.BinOp):
            argument = argument.left
        if self._get_str_value(argument) is not None and func_name in self.linter.config.odoo_exceptions:
            tl_method = "_"
            max_valid_odoo_version = self._get_max_valid_odoo_versions()
            if max_valid_odoo_version is None or max_valid_odoo_version >= (8, 0):
                tl_method = "self.env._"
            self.add_message("translation-required", node=node, args=(func_name, "", tl_method, argument.as_string()))

    @utils.only_required_for_messages("translation-required", "no-raise-unlink")
    def visit_raise(self, node):
        if self.linter.is_message_enabled("no-raise-unlink"):
            function = self.get_enclosing_function(node)
            if self._is_unlink(function):
                self.add_message("no-raise-unlink", node=node)

        if self.linter.is_message_enabled("translation-required"):
            self.check_translation_required(node)

    def get_cursor_name(self, node):
        expr_list = []
        node_expr = node.expr
        while isinstance(node_expr, nodes.Attribute):
            expr_list.insert(0, node_expr.attrname)
            node_expr = node_expr.expr
        if isinstance(node_expr, nodes.Name):
            expr_list.insert(0, node_expr.name)
        cursor_name = ".".join(expr_list)
        return cursor_name

    def formatversion(self, version_string):
        valid_odoo_versions = self.linter.config.valid_odoo_versions
        valid_odoo_versions = "|".join(map(re.escape, valid_odoo_versions))
        manifest_version_format = self.linter.config.manifest_version_format
        manifest_version_format_parsed = manifest_version_format.format(valid_odoo_versions=valid_odoo_versions)
        return re.match(manifest_version_format_parsed, version_string), manifest_version_format_parsed

    def join_node_args_kwargs(self, node):
        """Method to join args and keywords
        :param node: node to get args and keywords
        :return: List of args
        """
        args = (getattr(node, "args", None) or []) + (getattr(node, "keywords", None) or [])
        return args

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
                placeholders.extend(name for _, name, _, _ in string.Formatter().parse(line) if name is not None)
            except ValueError:
                continue
            for placeholder in placeholders:
                if not placeholder:
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
            format_str_args = range(len(format_str_args)) if not max(format_str_args) else range(max(format_str_args))
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
        printf_str = re.sub("%%", "", printf_str)
        for line in printf_str.splitlines():
            for match in PRINTF_PATTERN.finditer(line):
                match_items = match.groupdict()
                var = "" if match_items["type"] == "s" else 0
                if match_items["key"] is None:
                    args.append(var)
                else:
                    kwargs[match_items["key"]] = var
        return tuple(args) or kwargs

    @utils.only_required_for_messages("except-pass")
    def visit_try(self, node):
        """Visit block try except"""
        for handler in node.handlers:
            if not handler.name and len(handler.body) == 1 and isinstance(handler.body[0], nodes.node_classes.Pass):
                self.add_message("except-pass", node=handler)

    def _get_odoo_module_imported(self, node, manifest_path):
        if hasattr(node.parent, "file"):
            relpath = os.path.relpath(node.parent.file, os.path.dirname(manifest_path))
            if os.path.dirname(relpath) == "tests":
                # import errors rules don't apply to the test files
                # since these files are loaded only when running tests
                # and in such a case your
                # module and their external dependencies are installed.
                return []
        odoo_module = []
        if isinstance(node, nodes.ImportFrom) and "odoo.addons" in node.modname:
            packages = node.modname.split(".")
            if len(packages) >= 3:
                # from odoo.addons.odoo_module import models
                odoo_module.append(packages[2])
            else:
                # from odoo.addons import odoo_module
                odoo_module.append(node.names[0][0])
        elif isinstance(node, nodes.Import):
            for name, _ in node.names:
                if "odoo.addons" not in name and "odoo.addons" not in name:
                    continue
                packages = name.split(".")
                if len(packages) >= 3:
                    # import odoo.addons.odoo_module
                    odoo_module.append(packages[2])
        return odoo_module

    def check_odoo_relative_import(self, node):
        node_dirpath = os.path.dirname(node.root().file)
        if os.path.basename(os.path.dirname(node_dirpath)) == "migrations":
            return

        manifest_path = misc.walk_up(node_dirpath, tuple(misc.MANIFEST_FILES), misc.top_path(node_dirpath))
        if not manifest_path:
            return
        odoo_module_name = os.path.basename(os.path.dirname(manifest_path))
        if odoo_module_name in self._get_odoo_module_imported(node, manifest_path):
            self.add_message("odoo-addons-relative-import", node=node, args=(odoo_module_name,))

    def check_folder_test_imported(self, node):
        if hasattr(node.parent, "file") and os.path.basename(node.parent.file) == "__init__.py":
            package_names = []
            if isinstance(node, nodes.ImportFrom):
                if node.modname:
                    # from .tests import test_file
                    package_names = node.modname.split(".")[:1]
                else:
                    # from . import tests
                    package_names = [name for name, alias in node.names]
            elif isinstance(node, nodes.Import):
                package_names = [name[0].split(".")[0] for name in node.names]
            if "tests" in package_names:
                self.add_message("test-folder-imported", node=node, args=(node.parent.name,))

    def check_no_write_compute(self, node, method_name):
        for node_function_def in node.nodes_of_class(nodes.FunctionDef):
            if node_function_def.name != method_name:
                continue
            for node_compute_call in node_function_def.nodes_of_class(nodes.Call):
                if (
                    not self.linter.is_message_enabled("no-write-in-compute", node_compute_call.lineno)
                    or self.get_func_name(node_compute_call.func) != "write"
                ):
                    continue
                if self.get_func_lib(node_compute_call.func) == "self":
                    # self.write(...)
                    self.add_message("no-write-in-compute", node=node_compute_call)
                    continue
                _root_assignation_node, root_assignation_name = self._get_root_method_assignation(node_compute_call)
                # TODO: Support "browse(2) | browse(1)"
                if root_assignation_name in [
                    # All methods returning browseables
                    "self.browse",
                    "self.copy",
                    "self.env",
                    "self.filtered",
                    "self.filtered_domain",
                    "self.mapped",
                    "self.search",
                    "self.sorted",
                    "self",
                ] or root_assignation_name.startswith("self.with_"):
                    self.add_message("no-write-in-compute", node=node_compute_call)

    def _get_root_method_assignation(self, node, libname=None):
        new_node = node
        new_libname = libname
        if isinstance(node, nodes.Call):
            new_node = node.func
        elif isinstance(node, nodes.Subscript):
            new_node = node.value
        elif isinstance(node, nodes.AssignName):
            new_node = node.parent
        elif isinstance(node, nodes.Assign):
            new_node = node.value
        elif isinstance(node, nodes.For):
            new_node = node.iter
            new_libname = node.iter.as_string()
        elif isinstance(node, nodes.Attribute):
            new_node = node.expr
            new_libname = node.as_string()
        elif isinstance(node, nodes.Name):
            if node.name == "self":
                return node, libname
            new_node = node.lookup(node.name)[1][-1]
        if new_node == node:
            return new_node, new_libname
        return self._get_root_method_assignation(new_node, new_libname)

    def get_odoo_models_class(self, node):
        for class_base in node.bases:
            attr = class_base
            while True:
                if isinstance(attr, nodes.Attribute):
                    attr = attr.expr
                    continue
                break
            if not isinstance(attr, nodes.Name):
                continue
            imported_class = node.lookup(attr.name)[1]
            if not imported_class:
                continue
            imported_class = imported_class[-1]
            package_names = []
            if isinstance(imported_class, nodes.ImportFrom):
                package_names = imported_class.modname.split(".")[:1]
            elif isinstance(imported_class, nodes.Import):
                package_names = [name[0].split(".")[0] for name in imported_class.names]
            if "odoo" in package_names:
                class_base_name = class_base.as_string().split(".")[-1]
                if class_base_name in ["Model", "AbstractModel", "TransientModel"]:
                    return (class_base_name, class_base)

    @utils.only_required_for_messages(
        "no-wizard-in-models",
        "no-write-in-compute",
    )
    def visit_classdef(self, node):
        self.class_odoo_models = self.get_odoo_models_class(node)
        self.odoo_computes = set()

    @utils.only_required_for_messages(
        "no-wizard-in-models",
        "no-write-in-compute",
    )
    def leave_classdef(self, node):
        if self.class_odoo_models:
            for odoo_compute in self.odoo_computes:
                self.check_no_write_compute(node, odoo_compute)
            if (
                self.linter.is_message_enabled("no-wizard-in-models", self.class_odoo_models[1].lineno)
                and self.class_odoo_models[0] == "TransientModel"
                and os.path.basename(os.path.dirname(node.root().file)).startswith("model")
                and not getattr(node, "odoo_attribute_inherit", "").startswith("res.config")
            ):
                self.add_message("no-wizard-in-models", node=self.class_odoo_models[1])
        self.odoo_computes = set()
        self.class_odoo_models = False
