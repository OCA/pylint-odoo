import re
from typing import Union

from astroid import Import, ImportFrom, Module
from astroid.modutils import modpath_from_file
from pylint.checkers.utils import only_required_for_messages
from pylint.lint import PyLinter

from .odoo_base_checker import OdooBaseChecker

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal
    "E8401": (
        "This python module is not imported and has no effect",
        "unused-module",
        "",
    ),
}

EXCLUDED = re.compile(
    "__manifest__.py$|__openerp__.py$|__init__.py$|tests/|migrations/|docs/|tests\\\\|migrations\\\\|docs\\\\"
)


class ImportChecker(OdooBaseChecker):
    msgs = ODOO_MSGS
    name = "odoolint"

    def __init__(self, linter: PyLinter):
        self.imports = set()
        self.modules = set()

        super().__init__(linter)

    @staticmethod
    def get_module_from_node(node, max_attempts: int = 15) -> Union[None, Module]:
        """Obtain the module which contains the given node.

        :param node: Node that belongs to the module which wil be obtained.
        :param int max_attempts: Number of attempts that will be made to obtain the module. Nodes that are
            nested deeper than max_attempts won't be found.

        :returns: Module if found, otherwise None.
        """
        for _attempt in range(max_attempts):
            if not getattr(node, "parent", False):
                return None

            if isinstance(node.parent, Module):
                return node.parent

            node = node.parent

        return None

    def store_imported_modules(self, node):
        """Store all modules that are imported by 'from x import y' and 'import x,y,z' statements.

        Relative paths are taken into account for ImportFrom nodes. For example, the following statements
        would import the following modules (consider the file which contains these statements is module.models.partner):

        ``from ..wizard import cap, hello  # module.wizard, module.wizard.cap, module.wizard.hello``

        ``from ..utils.legacy import db   # module.utils.legacy, module.utils.legacy.db``

        ``from . import sale_order   # module.models.sale_order``

        ``import foo  # module.models.foo``
        """
        module = ImportChecker.get_module_from_node(node)
        if not module or "tests" in module.name:
            return

        if isinstance(node, ImportFrom):
            level = node.level or 0
        elif isinstance(node, Import):
            level = 1
        else:
            return

        module_name = ".".join(modpath_from_file(module.file))
        if level > module_name.count("."):
            return

        slice_index = 0
        current_level = 0
        for char in reversed(module_name):
            if current_level >= level:
                break
            if char == ".":
                current_level += 1

            slice_index += 1

        root_module = module_name[:-slice_index] if slice_index else module_name

        modname_separator = ""
        modname = getattr(node, "modname", "")
        if getattr(node, "modname", False):
            self.imports.add(f"{root_module}.{modname}")
            modname_separator = "."

        for name in node.names:
            self.imports.add(f"{root_module}{modname_separator}{modname}.{name[0]}")

    @only_required_for_messages("unused-module")
    def visit_module(self, node):
        if EXCLUDED.search(node.file):
            return

        self.modules.add(node)

    @only_required_for_messages("unused-module")
    def visit_importfrom(self, node):
        self.store_imported_modules(node)

    @only_required_for_messages("unused-module")
    def visit_import(self, node):
        self.store_imported_modules(node)

    @only_required_for_messages("unused-module")
    def close(self):
        for module in self.modules:
            if module.name not in self.imports:
                self.add_message("unused-module", node=module)
