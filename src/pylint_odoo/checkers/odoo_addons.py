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
import os
import re
from collections import defaultdict

from astroid import nodes
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
    "C8106": (
        'Wrong Version Format "%s" in manifest file. Regex to match: "%s"',
        "manifest-version-format",
        CHECK_DESCRIPTION,
    ),
    "C8114": ('Category "%s" not allowed in manifest file.', "category-allowed", CHECK_DESCRIPTION),
    "C8115": (
        "Missing %s file",
        "missing-odoo-file",
        CHECK_DESCRIPTION,
    ),
    "C8117": (
        'Category "%s" not allowed in manifest file for modules with price.',
        "category-allowed-app",
        CHECK_DESCRIPTION,
    ),
    "C8118": (
        "Missing %s file for modules with price",
        "missing-odoo-file-app",
        CHECK_DESCRIPTION,
    ),
    "C8119": (
        'Missing required key "%s" in manifest file for modules with price.',
        "manifest-required-key-app",
        CHECK_DESCRIPTION,
    ),
    "E8145": (
        "Manifest version (%s) is lower than migration scripts (%s)",
        "manifest-behind-migrations",
        "Update your manifest version, otherwise the migration script won't run",
    ),
    "R8180": (
        'Consider merging classes inherited to "%s" from %s.',
        "consider-merging-classes-inherited",
        CHECK_DESCRIPTION,
    ),
    "W8107": ('Prohibited override of "%s" method.', "prohibited-method-override", CHECK_DESCRIPTION),
}

DFTL_MANIFEST_REQUIRED_KEYS = ["license"]
DFTL_MANIFEST_REQUIRED_KEYS_APP = ["currency", "images", "license", "support"]
DFTL_ODOO_REQUIRED_FILES = []
DFTL_ODOO_REQUIRED_FILES_APP = [os.path.join("static", "description", "index.html")]
DFTL_CATEGORY_ALLOWED = []
DFTL_CATEGORY_ALLOWED_APP = [
    # Based on https://apps.odoo.com/apps
    "Accounting",
    "Discuss",
    "Document Management",
    "eCommerce",
    "Extra Tools",
    "Human Resources",
    "Industries",
    "Localization",
    "Manufacturing",
    "Marketing",
    "Point of Sale",
    "Productivity",
    "Project",
    "Purchases",
    "Sales",
    "Tutorial",
    "Warehouse",
    "Website",
]
DFTL_PROHIBITED_OVERRIDE_METHODS = []


class OdooAddons(OdooBaseChecker, BaseChecker):
    name = "odoolint"
    msgs = ODOO_MSGS
    options = (
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
            "prohibited-method-override",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_PROHIBITED_OVERRIDE_METHODS,
                "help": "List of methods that have been marked as prohibited to override.",
            },
        ),
        (
            "odoo-required-files",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_ODOO_REQUIRED_FILES,
                "help": (
                    "List of mandatory relative paths (comma-separated) expected inside Odoo module. "
                    "Example: static/description/index.html"
                ),
            },
        ),
        (
            "odoo-required-files-app",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_ODOO_REQUIRED_FILES_APP,
                "help": (
                    "List of mandatory relative paths (comma-separated) expected inside Odoo module for modules with price. "
                    "Example: static/description/index.html"
                ),
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
            "category-allowed",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_CATEGORY_ALLOWED,
                "help": "List of categories allowed in manifest file, separated by a comma.",
            },
        ),
        (
            "category-allowed-app",
            {
                "type": "csv",
                "metavar": "<comma separated values>",
                "default": DFTL_CATEGORY_ALLOWED_APP,
                "help": "List of categories allowed in manifest file for apps, separated by a comma.",
            },
        ),
    )

    def __init__(self, linter: PyLinter):
        super().__init__(linter)
        self._odoo_inherit_items = defaultdict(set)

    def close(self):
        """Final process get all cached values and add messages"""
        if self.linter.config.jobs > 1 and not self.linter.config.from_stdin:
            # In parallel mode (--jobs) close() is called once per file inside each
            # worker so the aggregated values are incomplete here. The messages are
            # added by reduce_map_data in the main process instead
            return
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

    def get_map_data(self):
        """Serialize the inherit items collected for the current file in a worker
        to be merged in the main process when running in parallel mode (--jobs)"""
        data = []
        for (manifest_path, odoo_class_inherit), inh_nodes in self._odoo_inherit_items.items():
            for inh_node in inh_nodes:
                # Skip _inherit='other.model' _name='model.name' because is valid
                if getattr(inh_node.parent, "odoo_attribute_name", None):
                    continue
                data.append(
                    (
                        manifest_path,
                        odoo_class_inherit,
                        inh_node.root().name,
                        inh_node.root().file,
                        inh_node.lineno,
                        inh_node.col_offset,
                    )
                )
        self._odoo_inherit_items = defaultdict(set)
        return data or None

    def reduce_map_data(self, linter, data):
        """Merge the inherit items of all the workers and add the messages
        skipped by close() in parallel mode (--jobs)"""
        inherit_items = defaultdict(set)
        for records in data:
            for manifest_path, odoo_class_inherit, modname, node_path, lineno, col_offset in records:
                inherit_items[(manifest_path, odoo_class_inherit)].add((node_path, lineno, col_offset, modname))
        for (_manifest_path, odoo_class_inherit), records in inherit_items.items():
            if len(records) <= 1:
                continue
            # deterministic order of the output
            records = sorted(records)
            first_path, first_lineno, first_col_offset, first_modname = records.pop()
            path_records = [
                "%s:%d:%d" % (os.path.relpath(node_path, os.getcwd()), lineno, col_offset)
                for node_path, lineno, col_offset, _modname in records
            ]
            linter.set_current_module(first_modname, first_path)
            self.add_message(
                "consider-merging-classes-inherited",
                line=first_lineno,
                col_offset=first_col_offset,
                args=(odoo_class_inherit, ", ".join(path_records)),
            )

    @utils.only_required_for_messages(
        "category-allowed-app",
        "category-allowed",
        "manifest-behind-migrations",
        "manifest-required-key-app",
        "manifest-version-format",
        "missing-odoo-file-app",
        "missing-odoo-file",
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

        # Check category allowed
        category_str = manifest_dict.get("category")
        if (
            category_str
            and self.linter.config.category_allowed
            and category_str not in self.linter.config.category_allowed
            and "price" not in manifest_dict
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

        dirname = os.path.dirname(self.linter.current_file)
        if "price" in manifest_dict:
            # manifest has "price" so it is an App
            app_required_keys = set(self.linter.config.manifest_required_keys_app) - set(
                self.linter.config.manifest_required_keys
            )
            for app_required_key in app_required_keys:
                if app_required_key not in manifest_dict:
                    self.add_message(
                        "manifest-required-key-app",
                        node=node,
                        args=(app_required_key,),
                    )

            for subpath in self.linter.config.odoo_required_files:
                required_path = os.path.join(dirname, subpath)
                if not os.path.isfile(required_path):
                    required_relative_path = os.path.join(os.path.basename(dirname), subpath)
                    self.add_message(
                        "missing-odoo-file",
                        node=node,
                        args=(required_relative_path,),
                    )

            for subpath in self.linter.config.odoo_required_files_app:
                required_path = os.path.join(dirname, subpath)
                if not os.path.isfile(required_path):
                    required_relative_path = os.path.join(os.path.basename(dirname), subpath)
                    self.add_message(
                        "missing-odoo-file-app",
                        node=node,
                        args=(required_relative_path,),
                    )

            # Check category allowed for apps
            if (
                category_str
                and self.linter.config.category_allowed_app
                and category_str not in self.linter.config.category_allowed_app
            ):
                self.add_message(
                    "category-allowed-app",
                    node=manifest_keys_nodes.get("category") or node,
                    args=(category_str,),
                )

    @utils.only_required_for_messages(
        "prohibited-method-override",
    )
    def visit_functiondef(self, node):
        if not node.is_method():
            return

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

    @utils.only_required_for_messages("consider-merging-classes-inherited")
    def visit_assign(self, node):
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

    def formatversion(self, version_string):
        valid_odoo_versions = self.linter.config.valid_odoo_versions
        valid_odoo_versions = "|".join(map(re.escape, valid_odoo_versions))
        manifest_version_format = self.linter.config.manifest_version_format
        manifest_version_format_parsed = manifest_version_format.format(valid_odoo_versions=valid_odoo_versions)
        return re.match(manifest_version_format_parsed, version_string), manifest_version_format_parsed
