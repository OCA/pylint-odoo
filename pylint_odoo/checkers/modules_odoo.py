"""Visit module to add odoo checks
"""

import os
import re

import astroid
import polib
from collections import defaultdict
from lxml import etree
from pylint.checkers import utils

from .. import misc, settings

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal

    # Visit odoo module with settings.BASE_OMODULE_ID
    'C%d02' % settings.BASE_OMODULE_ID: (
        'Missing ./README.rst file. Template here: %s',
        'missing-readme',
        settings.DESC_DFLT
    ),
    'E%d01' % settings.BASE_OMODULE_ID: (
        '%s %s',
        'rst-syntax-error',
        settings.DESC_DFLT
    ),
    'E%d02' % settings.BASE_OMODULE_ID: (
        '%s error: %s',
        'xml-syntax-error',
        settings.DESC_DFLT
    ),
    'E%d03' % settings.BASE_OMODULE_ID: (
        'Test folder imported in module %s',
        'test-folder-imported',
        settings.DESC_DFLT
    ),
    'W%d01' % settings.BASE_OMODULE_ID: (
        '%s Dangerous filter without explicit `user_id` in xml_id %s',
        'dangerous-filter-wo-user',
        settings.DESC_DFLT
    ),
    'W%d02' % settings.BASE_OMODULE_ID: (
        '%s Duplicate xml record id "%s" in %s',
        'duplicate-xml-record-id',
        settings.DESC_DFLT
    ),
    'W%d03' % settings.BASE_OMODULE_ID: (
        '%s',
        'javascript-lint',
        settings.DESC_DFLT
    ),
    'W%d04' % settings.BASE_OMODULE_ID: (
        '%s Deprecated <openerp> xml node',
        'deprecated-openerp-xml-node',
        settings.DESC_DFLT
    ),
    'W%d05' % settings.BASE_OMODULE_ID: (
        '%s record res.users without '
        'context="{\'no_reset_password\': True}"',
        'create-user-wo-reset-password',
        settings.DESC_DFLT
    ),
    'W%d06' % settings.BASE_OMODULE_ID: (
        '%s Duplicate id "%s"',
        'duplicate-id-csv',
        settings.DESC_DFLT
    ),
    'W%d07' % settings.BASE_OMODULE_ID: (
        '%s Duplicate xml field "%s" in lines %s',
        'duplicate-xml-fields',
        settings.DESC_DFLT
    ),
    'W%d08' % settings.BASE_OMODULE_ID: (
        '%s Missing newline',
        'missing-newline-extrafiles',
        settings.DESC_DFLT
    ),
    'W%d09' % settings.BASE_OMODULE_ID: (
        '%s Redundant name module reference in xml_ids "%s".',
        'redundant-modulename-xml',
        settings.DESC_DFLT
    ),
    'W%d10' % settings.BASE_OMODULE_ID: (
        '%s Use wrong tabs indentation instead of four spaces',
        'wrong-tabs-instead-of-spaces',
        settings.DESC_DFLT
    ),
    'R%d80' % settings.BASE_OMODULE_ID: (
        'Consider merging classes inherited to "%s" from %s.',
        'consider-merging-classes-inherited',
        settings.DESC_DFLT
    ),
    'W%d50' % settings.BASE_OMODULE_ID: (
        'Same Odoo module absolute import. You should use '
        'relative import with "." '
        'instead of "openerp.addons.%s"',
        'odoo-addons-relative-import',
        settings.DESC_DFLT
    ),
    'W%d40' % settings.BASE_OMODULE_ID: (
        '%s Dangerous use of "replace" from view '
        'with priority %s < %s',
        'dangerous-view-replace-wo-priority',
        settings.DESC_DFLT
    ),
    'W%d41' % settings.BASE_OMODULE_ID: (
        '%s Dangerous use of "replace" from view '
        'with priority %s < %s',
        'dangerous-qweb-replace-wo-priority',
        settings.DESC_DFLT
    ),
    'W%d30' % settings.BASE_OMODULE_ID: (
        '%s not used from manifest',
        'file-not-used',
        settings.DESC_DFLT
    ),
    'W%d35' % settings.BASE_OMODULE_ID: (
        'External dependency "%s" without ImportError. More info: '
        'https://github.com/OCA/odoo-community.org/blob/master/website/'
        'Contribution/CONTRIBUTING.rst'
        '#external-dependencies',
        'missing-import-error',
        settings.DESC_DFLT
    ),
    'W%d36' % settings.BASE_OMODULE_ID: (
        'Missing external dependency "%s" from manifest. More info: '
        'https://github.com/OCA/odoo-community.org/blob/master/website/'
        'Contribution/CONTRIBUTING.rst'
        '#external-dependencies',
        'missing-manifest-dependency',
        settings.DESC_DFLT
    ),
    'W%d38' % settings.BASE_OMODULE_ID: (
        'pass into block except. '
        'If you really need to use the pass consider logging that exception',
        'except-pass',
        settings.DESC_DFLT
    ),
    'W%d37' % settings.BASE_OMODULE_ID: (
        '%s The xml attribute is missing the translation="off" tag %s',
        'xml-attribute-translatable',
        settings.DESC_DFLT
    ),
    'W%d42' % settings.BASE_OMODULE_ID: (
        '%s Deprecated <tree> xml attribute "%s"',
        'xml-deprecated-tree-attribute',
        settings.DESC_DFLT
    ),
    'W%d43' % settings.BASE_OMODULE_ID: (
        '%s Deprecated QWeb directive "%s". Use "t-options" instead',
        'xml-deprecated-qweb-directive',
        settings.DESC_DFLT
    ),
    'W%d39' % settings.BASE_OMODULE_ID: (
        '%s Use <odoo> instead of <odoo><data> or use <odoo noupdate="1">'
        'instead of <odoo><data noupdate="1">',
        'deprecated-data-xml-node',
        settings.DESC_DFLT
    ),
    'W%d44' % settings.BASE_OMODULE_ID: (
        '%s The resource in in src/href contains a not valid chararter',
        'character-not-valid-in-resource-link',
        settings.DESC_DFLT
    ),
    'W%d47' % settings.BASE_OMODULE_ID: (
        '%s Duplicate PO message definition "%s" in lines %s',
        'duplicate-po-message-definition',
        settings.DESC_DFLT
    ),
    'E%d12' % settings.BASE_OMODULE_ID: (
        '%s %s',
        'po-syntax-error',
        settings.DESC_DFLT
    ),
    'W%d68' % settings.BASE_OMODULE_ID: (
        '%s %s',
        'po-msgstr-variables',
        settings.DESC_DFLT
    ),
}


DFTL_README_TMPL_URL = 'https://github.com/OCA/maintainer-tools' + \
    '/blob/master/template/module/README.rst'
DFTL_README_FILES = ['README.rst', 'README.md', 'README.txt']
DFTL_MIN_PRIORITY = 99
# Files supported from manifest to convert
# Extracted from openerp/tools/convert.py:def convert_file
DFLT_EXTFILES_CONVERT = ['csv', 'sql', 'xml', 'yml']
DFLT_EXTFILES_TO_LINT = DFLT_EXTFILES_CONVERT + [
    'po', 'js', 'mako', 'rst', 'md', 'markdown']
DFLT_IMPORT_NAME_WHITELIST = [
    # self-odoo
    'odoo', 'openerp',
    # Known external packages of odoo
    'PIL', 'PyPDF2', 'anybox.testing.openerp', 'argparse', 'babel', 'chardet',
    'dateutil', 'decorator', 'docutils', 'faces', 'feedparser',
    'gdata', 'gevent', 'greenlet', 'jcconv', 'jinja2',
    'ldap', 'lxml', 'mako', 'markupsafe', 'mock', 'odf',
    'ofxparse', 'openid', 'passlib', 'pkg_resources',
    'psutil', 'psycogreen', 'psycopg2', 'pyPdf', 'pychart',
    'pydot', 'pyparsing', 'pytz', 'qrcode', 'reportlab',
    'requests', 'serial', 'simplejson', 'six', 'suds',
    'unittest2', 'urllib3', 'usb', 'vatnumber', 'vobject', 'werkzeug',
    'wsgiref', 'xlsxwriter', 'xlwt', 'yaml',
    # OpenUpgrade migration
    'openupgradelib'
]
DFTL_JSLINTRC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'examples', '.jslintrc'
)
DFLT_DEPRECATED_TREE_ATTRS = ['colors', 'fonts', 'string']
DFTL_MANIFEST_DATA_KEYS = ['data', 'demo', 'demo_xml', 'init_xml', 'test',
                           'update_xml']


class ModuleChecker(misc.WrapperModuleChecker):
    name = settings.CFG_SECTION
    msgs = ODOO_MSGS
    options = (
        ('readme_template_url', {
            'type': 'string',
            'metavar': '<string>',
            'default': DFTL_README_TMPL_URL,
            'help': 'URL of README.rst template file',
        }),
        ('extfiles_to_lint', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_EXTFILES_TO_LINT,
            'help': 'List of extension files to check separated by a comma.'
        }),
        ('min-priority', {
            'type': 'int',
            'metavar': '<int>',
            'default': DFTL_MIN_PRIORITY,
            'help': 'Minimum priority number of a view with replace of fields.'
        }),
        ('extfiles_convert', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_EXTFILES_CONVERT,
            'help': 'List of extension files supported to convert '
                    'from manifest separated by a comma.'
        }),
        ('import_name_whitelist', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_IMPORT_NAME_WHITELIST,
            'help': 'List of known import dependencies of odoo,'
            ' separated by a comma.'
        }),
        ('jslintrc', {
            'type': 'string',
            'metavar': '<path to file>',
            'default': os.environ.get('PYLINT_ODOO_JSLINTRC') or DFTL_JSLINTRC,
            'help': ('A path to a file that contains a configuration file of '
                     'javascript lint. You can use the environment variable '
                     '"PYLINT_ODOO_JSLINTRC" too. Default: %s' % DFTL_JSLINTRC)
        }),
        ('deprecated_tree_attributes', {
            'type': 'multiple_choice',
            'metavar': '<attributes>',
            'default': DFLT_DEPRECATED_TREE_ATTRS,
            'choices': DFLT_DEPRECATED_TREE_ATTRS,
            'help': 'List of deprecated list view attributes,'
            ' separated by a comma. Valid values: %s' % ', '.join(
                DFLT_DEPRECATED_TREE_ATTRS)
        }),
    )

    odoo_check_versions = {
        'missing-import-error': {
            'max_odoo_version': '11.0',
        },
    }

    class_inherit_names = []

    @utils.check_messages('consider-merging-classes-inherited')
    def visit_assign(self, node):
        if not self.odoo_node:
            return
        if not self.linter.is_message_enabled(
                'consider-merging-classes-inherited', node.lineno):
            return
        node_left = node.targets[0]
        if not isinstance(node_left, astroid.node_classes.AssignName) or \
                node_left.name not in ('_inherit', '_name') or \
                not isinstance(node.value, astroid.node_classes.Const) or \
                not isinstance(node.parent, astroid.ClassDef):
            return
        if node_left.name == '_name':
            node.parent.odoo_attribute_name = node.value.value
            return
        _name = getattr(node.parent, 'odoo_attribute_name', None)
        _inherit = node.value.value
        if _name and _name != _inherit:
            # Skip _name='model.name' _inherit='other.model' because is valid
            return
        key = (self.odoo_node, _inherit)
        node.file = self.linter.current_file
        self.inh_dup.setdefault(key, []).append(node)

    def _build_whitelist_module_patterns(self):
        known_patterns = []
        for known_pattern in self.config.import_name_whitelist:
            pattern = known_pattern.replace('*', '.*').replace('?', '.?')
            known_patterns.append(re.compile('^' + pattern + '$'))
        return known_patterns

    def open(self):
        """Define variables to use cache"""
        self.inh_dup = {}
        patterns = self._build_whitelist_module_patterns()
        self._whitelist_module_patterns = patterns
        super(ModuleChecker, self).open()

    def close(self):
        """Final process get all cached values and add messages"""
        for (odoo_node, class_dup_name), nodes in self.inh_dup.items():
            if len(nodes) == 1:
                continue
            path_nodes = []
            for node in nodes[1:]:
                relpath = os.path.relpath(node.file,
                                          os.path.dirname(odoo_node.file))
                path_nodes.append("%s:%d" % (relpath, node.lineno))
            self.add_message('consider-merging-classes-inherited',
                             node=nodes[0],
                             args=(class_dup_name, ', '.join(path_nodes)))

    def _get_odoo_module_imported(self, node):
        odoo_module = []
        if self.manifest_file and hasattr(node.parent, 'file'):
            relpath = os.path.relpath(
                node.parent.file, os.path.dirname(self.manifest_file))
            if os.path.dirname(relpath) == 'tests':
                # import errors rules don't apply to the test files
                # since these files are loaded only when running tests
                # and in such a case your
                # module and their external dependencies are installed.
                return odoo_module
        if isinstance(node, astroid.ImportFrom) and \
                ('openerp.addons' in node.modname or
                 'odoo.addons' in node.modname):
            packages = node.modname.split('.')
            if len(packages) >= 3:
                # from openerp.addons.odoo_module import models
                odoo_module.append(packages[2])
            else:
                # from openerp.addons import odoo_module
                odoo_module.append(node.names[0][0])
        elif isinstance(node, astroid.Import):
            for name, _ in node.names:
                if 'openerp.addons' not in name and 'odoo.addons' not in name:
                    continue
                packages = name.split('.')
                if len(packages) >= 3:
                    # import openerp.addons.odoo_module
                    odoo_module.append(packages[2])
        return odoo_module

    def check_odoo_relative_import(self, node):
        if self.odoo_module_name in self._get_odoo_module_imported(node):
            self.add_message('odoo-addons-relative-import', node=node,
                             args=(self.odoo_module_name))

    def check_folder_test_imported(self, node):
        if (hasattr(node.parent, 'file')
                and os.path.basename(node.parent.file) == '__init__.py'):
            package_names = []
            if isinstance(node, astroid.ImportFrom):
                package_names = node.modname.split('.')[:1]
            elif isinstance(node, astroid.Import):
                package_names = [name[0].split('.')[0] for name in node.names]
            if "tests" in package_names:
                self.add_message('test-folder-imported', node=node,
                                 args=(node.parent.name,))

    @staticmethod
    def _is_absolute_import(node, name):
        modnode = node.root()
        importedmodnode = ModuleChecker._get_imported_module(node, name)
        if importedmodnode and importedmodnode.file and \
                modnode is not importedmodnode and \
                importedmodnode.name != name:
            return True
        return False

    @staticmethod
    def _get_imported_module(importnode, modname):
        try:
            return importnode.do_import_module(modname)
        except:
            pass

    def _is_module_name_in_whitelist(self, module_name):
        # Try to find most specific placement instruction match (if any)
        # (from isort place_module() method)
        parts = module_name.split('.')
        module_names_to_check = [
            '.'.join(parts[:first_k])
            for first_k in range(len(parts), 0, -1)
        ]
        # Check if one of the module name is part of the whitelist.
        # For an module name such as 'anybox.testing.openerp', the
        # modules names to check will be:
        # ['anybox.testing.openerp', 'anybox.testing', 'anybox']
        # Only one of them has to be in the whitelist to be accepted.
        for module_name_to_check in module_names_to_check:
            for pattern in self._whitelist_module_patterns:
                if pattern.match(module_name_to_check):
                    return True
        return False

    def _check_imported_packages(self, node, module_name):
        """Check if the import node is a external dependency to validate it"""
        if not module_name:
            # skip local packages because is not a external dependency.
            return
        if not self.manifest_dict:
            # skip if is not a module of odoo
            return
        if not isinstance(node.parent, astroid.Module):
            # skip nested import sentences
            return
        if self._is_absolute_import(node, module_name):
            # skip absolute imports
            return
        if self._is_module_name_in_whitelist(module_name):
            # ignore whitelisted modules
            return
        isort_driver = misc.IsortDriver()
        import_category = isort_driver.place_module(module_name)
        if import_category not in ('FIRSTPARTY', 'THIRDPARTY'):
            # skip if is not a external library or is a white list library
            return
        relpath = os.path.relpath(
            node.parent.file, os.path.dirname(self.manifest_file))
        if os.path.dirname(relpath) == 'tests':
            # import errors rules don't apply to the test files
            # since these files are loaded only when running tests
            # and in such a case your
            # module and their external dependencies are installed.
            return
        self.add_message('missing-import-error', node=node,
                         args=(module_name,))

        ext_deps = self.manifest_dict.get('external_dependencies') or {}
        py_ext_deps = ext_deps.get('python') or []
        if isinstance(node, astroid.ImportFrom) and (node.level or 0) >= 1:
            return
        if module_name not in py_ext_deps and \
                module_name.split('.')[0] not in py_ext_deps and \
                not any(dep in module_name for dep in py_ext_deps):
            self.add_message('missing-manifest-dependency', node=node,
                             args=(module_name,))

    @utils.check_messages('odoo-addons-relative-import',
                          'missing-import-error',
                          'missing-manifest-dependency',
                          'test-folder-imported')
    def visit_importfrom(self, node):
        self.check_odoo_relative_import(node)
        self.check_folder_test_imported(node)
        if isinstance(node.scope(), astroid.Module):
            package = node.modname
            self._check_imported_packages(node, package)

    @utils.check_messages('odoo-addons-relative-import',
                          'missing-import-error',
                          'missing-manifest-dependency',
                          'test-folder-imported')
    def visit_import(self, node):
        self.check_odoo_relative_import(node)
        self.check_folder_test_imported(node)
        for name, _ in node.names:
            if isinstance(node.scope(), astroid.Module):
                self._check_imported_packages(node, name)

    @utils.check_messages('except-pass')
    def visit_tryexcept(self, node):
        """Visit block try except"""
        for handler in node.handlers:
            if (not handler.name and
                    len(handler.body) == 1 and
                    isinstance(handler.body[0], astroid.node_classes.Pass)):
                self.add_message('except-pass', node=handler)

    def _get_po_line_number(self, po_entry):
        """Get line number of a PO entry similar to 'msgfmt' output
        entry.linenum returns line number of the definition of the entry
        'msgfmt' returns line number of the 'msgid'
        This method also gets line number of the 'msgid'
        """
        linenum = po_entry.linenum
        for line in str(po_entry).split('\n'):
            if not line.startswith('#'):
                break
            linenum += 1
        return linenum

    def _check_po_syntax_error(self):
        """Check syntax error in PO files"""
        self.msg_args = []
        for po_file in self.filter_files_ext('po') + self.filter_files_ext('pot'):
            try:
                po = polib.pofile(os.path.join(self.module_path, po_file))
            except (IOError, OSError) as oe:
                fname = os.path.join(self.module_path, po_file)
                msg = str(oe).replace(fname + ' ', '').strip()
                self.msg_args.append((po_file, msg))
                continue
            for entry in po:
                if entry.obsolete:
                    continue
                # Regex from https://github.com/odoo/odoo/blob/fa4f36bb631e82/odoo/tools/translate.py#L616  # noqa
                match = re.match(r"(module[s]?): (\w+)", entry.comment)
                if match:
                    continue
                linenum = self._get_po_line_number(entry)
                po_fname_linenum = "%s:%d" % (po_file, linenum)
                self.msg_args.append((
                    po_fname_linenum, "Translation entry requires comment "
                    "'#. module: MODULE'"))

    def _check_duplicate_po_message_definition(self):
        """Check duplicate message definition (message-id)
        in all entries of PO files

        We are not using `check_for_duplicates` parameter of polib.pofile method
            e.g. polib.pofile(..., check_for_duplicates=True)
        Because the output is:
            raise ValueError('Entry "%s" already exists' % entry.msgid)
        It doesn't show the number of lines duplicated
        It shows the entire string of the message_id without truncating it
            or replacing newlines
        """
        self.msg_args = []
        for po_file in self.filter_files_ext('po') + self.filter_files_ext('pot'):
            try:
                po = polib.pofile(os.path.join(self.module_path, po_file))
            except (IOError, OSError):
                # If there is a syntax error, it will be covered in another check
                continue
            duplicated = defaultdict(list)
            for entry in po:
                if entry.obsolete:
                    continue
                # Using `set` in order to fix false red
                # if the same entry has duplicated occurrences
                for occurrence in set(entry.occurrences):
                    duplicated[(hash(entry.msgid), hash(occurrence))].append(entry)
            for entries in duplicated.values():
                if len(entries) < 2:
                    continue
                linenum = self._get_po_line_number(entries[0])
                po_fname_linenum = "%s:%d" % (po_file, linenum)
                duplicated = ', '.join(str(self._get_po_line_number(x))
                                       for x in entries[1:])
                msg_id_short = re.sub(r"[\n\t]*", "", entries[0].msgid[:40]).strip()
                if len(entries[0].msgid) > 40:
                    msg_id_short = "%s..." % msg_id_short
                self.msg_args.append((po_fname_linenum, msg_id_short, duplicated))

    def _check_po_msgstr_variables(self):
        """Check if 'msgid' is using 'str' variables like '%s'
        So translation 'msgstr' must be the same number of variables too"""
        self.msg_args = []
        for po_file in self.filter_files_ext('po'):
            try:
                po = polib.pofile(os.path.join(self.module_path, po_file))
            except (IOError, OSError):
                # If there is a syntax error, it will be covered in another check
                continue
            for entry in po:
                if entry.obsolete:
                    continue
                if not entry.msgstr or 'python-format' not in entry.flags:
                    # skip untranslated entry
                    # skip if it is not a python format
                    # because "%s"%var won't be parsed
                    continue
                linenum = self._get_po_line_number(entry)
                po_fname_linenum = "%s:%d" % (po_file, linenum)
                try:
                    self.parse_printf(entry.msgid, entry.msgstr)
                except misc.StringParseError as str_parse_exc:
                    self.msg_args.append((
                        po_fname_linenum, "Translation string couldn't be parsed "
                        "correctly using string%%variables %s" % str_parse_exc))
                    continue
                try:
                    self.parse_format(entry.msgid, entry.msgstr)
                except misc.StringParseError as str_parse_exc:
                    self.msg_args.append((
                        po_fname_linenum, "Translation string couldn't be parsed "
                        "correctly using string.format() %s" % str_parse_exc))

    def _check_rst_syntax_error(self):
        """Check if rst file there is syntax error
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        rst_files = self.filter_files_ext('rst')
        self.msg_args = []
        for rst_file in rst_files:
            errors = self.check_rst_syntax(
                os.path.join(self.module_path, rst_file))
            for error in errors:
                msg = error.full_message
                res = re.search(
                    r'No directive entry for "([\w|\-]+)"|'
                    r'Unknown directive type "([\w|\-]+)"|'
                    r'No role entry for "([\w|\-]+)"|'
                    r'Unknown interpreted text role "([\w|\-]+)"', msg)
                # TODO: Add support for sphinx directives after fix
                # https://github.com/twolfson/restructuredtext-lint/issues/29
                if res:
                    # Skip directive errors
                    continue
                self.msg_args.append((
                    "%s:%d" % (rst_file, error.line or 0),
                    msg.strip('\n').replace('\n', '|')))
        if self.msg_args:
            return False
        return True

    def _check_missing_readme(self):
        """Check if exists ./README.{rst,md,txt} file
        :return: If exists return True else False
        """
        self.msg_args = (self.config.readme_template_url,)
        for readme in DFTL_README_FILES:
            if os.path.isfile(os.path.join(self.module_path, readme)):
                return True
        return False

    def _check_xml_syntax_error(self):
        """Check if xml file there is syntax error
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=True):
            try:
                self.parse_xml(os.path.join(self.module_path, xml_file),
                               raise_if_error=True)
            except etree.XMLSyntaxError as xmlsyntax_error:
                self.msg_args.append((
                    xml_file, str(xmlsyntax_error).strip('\n').replace('\n', '|')))
        if self.msg_args:
            return False
        return True

    def _get_duplicate_xml_record_id(self, records):
        """Get duplicated records based on attribute id
        :param records list: List of lxml.etree.Element "<record"
        :return: Duplicated items.
            e.g. {record.id: [record_node1, record_node2]}
        :rtype: dict
        """
        all_records = {}
        for record in records:
            record_id = "%s/%s_noupdate_%s" % (
                record.attrib.get('section', ''),
                record.attrib.get('id', ''),
                record.getparent().attrib.get('noupdate', '0'),
            )
            all_records.setdefault(record_id, []).append(record)
        # Remove all keys which not duplicated
        records = {}
        for key, items in all_records.items():
            if not len(items) < 2:
                records[key] = items
        return records

    def _check_duplicate_xml_record_id(self):
        """Check duplicated XML-IDs inside of the files of
        each manifest-section treated them separately
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        xml_records = []
        for fname, section in self._get_manifest_referenced_files().items():
            if os.path.splitext(fname)[1].lower() != '.xml':
                continue
            fname = os.path.join(self.module_path, fname)
            for xml_record in self.get_xml_records(fname):
                xml_record.attrib['section'] = section
                xml_records.append(xml_record)
        for name, fobjs in \
                self._get_duplicate_xml_record_id(xml_records).items():
            self.msg_args.append((
                "%s:%d" % (os.path.relpath(fobjs[0].base, self.module_path),
                           fobjs[0].sourceline),
                name,
                ', '.join([os.path.relpath(fobj.base, self.module_path) +
                           ':' + str(fobj.sourceline)
                           for fobj in fobjs[1:]]),
            ))
        if self.msg_args:
            return False
        return True

    def _check_duplicate_id_csv(self):
        """Check duplicate xml id in ir.model.access.csv files of a odoo module.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        all_csv_ids = []
        self.msg_args = []
        for csv_file_rel in self.filter_files_ext('csv', relpath=True):
            csv_file = os.path.join(self.module_path, csv_file_rel)
            if os.path.basename(csv_file) == 'ir.model.access.csv':
                all_csv_ids.extend(self.get_field_csv(csv_file))
        duplicated_ids_csv = self.get_duplicated_items(all_csv_ids)
        for duplicated_id_csv in duplicated_ids_csv:
            self.msg_args.append((csv_file_rel, duplicated_id_csv))
        if duplicated_ids_csv:
            return False
        return True

    def _check_redundant_modulename_xml(self):
        """Check redundant module name in xml file.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for xml_file_rel in self.filter_files_ext('xml', relpath=True):
            xml_file = os.path.join(self.module_path, xml_file_rel)
            for xml_id, lineno in self.get_xml_redundant_module_name(
                    xml_file, self.module):
                self.msg_args.append(
                    ("%s:%d" % (xml_file_rel, lineno), xml_id))
        if self.msg_args:
            return False
        return True

    def _check_character_not_valid_in_resource_link(self):
        """The resource in in src/href contains a not valid chararter"""
        self.msg_args = []
        for xml_file in self.filter_files_ext('xml'):
            doc = self.parse_xml(os.path.join(self.module_path, xml_file))
            for name, attr in (('link', 'href'), ('script', 'src')):
                nodes = doc.xpath('.//%s[@%s]' % (name, attr))
                for node in nodes:
                    resource = node.get(attr, '')
                    ext = os.path.splitext(os.path.basename(resource))[1]
                    if (resource.startswith('/') and not
                            re.search('^[.][a-zA-Z]+$', ext)):
                        self.msg_args.append(("%s:%s" % (xml_file,
                                                         node.sourceline)))
        if self.msg_args:
            return False
        return True

    def _get_duplicate_xml_fields(self, fields):
        """Get duplicated xml fields based on attribute name
        :param fields list: List of lxml.etree.Element "<field"
        :return: Duplicated items.
            e.g. {field.name: [field_node1, field_node2]}
        :rtype: dict
        """
        all_fields = {}
        for field in fields:
            field_xml = field.attrib.get('name')
            if not field_xml:
                continue
            all_fields.setdefault(
                (field_xml, field.attrib.get('context'),
                 field.attrib.get('filter_domain'),
                 field.getparent()), []).append(field)
        # Remove all keys which not duplicated by excluding them from the
        return dict(((name, context, filter_domain, parent_node), nodes) for
                    (name, context, filter_domain, parent_node), nodes in
                    all_fields.items() if len(nodes) >= 2)

    def _check_duplicate_xml_fields(self):
        """Check duplicate field in all record of xml files of a odoo module.
        Important note: this check does not work with inherited views.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=True):
            for record in self.get_xml_records(
                    os.path.join(self.module_path, xml_file)):
                if record.xpath('field[@name="inherit_id"]'):
                    continue
                for xpath in ['field', 'field/*/field',
                              'field/*/field/tree/field',
                              'field/*/field/form/field']:
                    for name, fobjs in self._get_duplicate_xml_fields(
                            record.xpath(xpath)).items():
                        self.msg_args.append((
                            "%s:%d" % (xml_file, fobjs[0].sourceline), name[0],
                            ', '.join([str(fobj.sourceline)
                                       for fobj in fobjs[1:]]),
                        ))
        if self.msg_args:
            return False
        return True

    def _check_dangerous_filter_wo_user(self):
        """Check dangerous filter without a user assigned.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        xml_files = self.filter_files_ext('xml')
        for xml_file in xml_files:
            ir_filter_records = self.get_xml_records(
                os.path.join(self.module_path, xml_file), model='ir.filters')
            for ir_filter_record in ir_filter_records:
                ir_filter_fields = ir_filter_record.xpath(
                    "field[@name='name' or @name='user_id']")
                # if exists field="name" then is a new record
                # then should be field="user_id" too
                if ir_filter_fields and len(ir_filter_fields) == 1:
                    # TODO: Add a list of msg_args before of return
                    # TODO: Add source lineno in all xml checks
                    self.msg_args = (
                        "%s:%d" % (xml_file, ir_filter_record.sourceline),
                        ir_filter_record.get('id'),)
                    return False
        return True

    @staticmethod
    def _get_priority(view):
        try:
            priority_node = view.xpath("field[@name='priority'][1]")[0]
            return int(priority_node.get('eval', priority_node.text) or 0)
        except (IndexError, ValueError):
            # IndexError: If the field is not found
            # ValueError: If the value found is not valid integer
            pass
        return 0

    @staticmethod
    def _is_replaced_field(view):
        try:
            arch = view.xpath("field[@name='arch' and @type='xml'][1]")[0]
        except IndexError:
            return None
        replaces = \
            arch.xpath(".//field[@name='name' and @position='replace'][1]") + \
            arch.xpath(".//*[@position='replace'][1]")
        return bool(replaces)

    def _check_dangerous_view_replace_wo_priority(self):
        """Check dangerous view defined with low priority
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        xml_files = self.filter_files_ext('xml')
        for xml_file in xml_files:
            views = self.get_xml_records(
                os.path.join(self.module_path, xml_file), model='ir.ui.view')
            for view in views:
                priority = self._get_priority(view)
                is_replaced_field = self._is_replaced_field(view)
                if is_replaced_field and priority < self.config.min_priority:
                    self.msg_args.append((
                        "%s:%s" % (xml_file, view.sourceline), priority,
                        self.config.min_priority))
        if self.msg_args:
            return False
        return True

    def _check_dangerous_qweb_replace_wo_priority(self):
        """Check dangerous qweb view defined with low priority
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        xml_files = self.filter_files_ext('xml')
        for xml_file in self._skip_files_ext('.xml', xml_files):
            xml_file_path = os.path.join(self.module_path, xml_file)

            # view template
            xml_doc = self.parse_xml(xml_file_path)
            for template in xml_doc.xpath("/odoo//template|/openerp//template"):
                try:
                    priority = int(template.get('priority'))
                except (ValueError, TypeError):
                    priority = 0
                for child in template.iterchildren():
                    if (child.get('position') == 'replace' and
                            priority < self.config.min_priority):
                        self.msg_args.append((
                            "%s:%s" % (xml_file, template.sourceline), priority,
                            self.config.min_priority))
                        break
        if self.msg_args:
            return False
        return True

    def _check_create_user_wo_reset_password(self):
        """Check xml records of user without the context
        'context="{'no_reset_password': True}"'
        This context avoid send email and mail log warning
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        xml_files = self.filter_files_ext('xml')
        for xml_file in xml_files:
            user_records = self.get_xml_records(
                os.path.join(self.module_path, xml_file), model='res.users')
            # if exists field="name" then is a new record
            # then should be context
            self.msg_args.extend([
                ("%s:%s" % (xml_file, user_record.sourceline))
                for user_record in user_records
                if user_record.xpath("field[@name='name']") and
                'no_reset_password' not in (user_record.get('context') or '')])
        if self.msg_args:
            return False
        return True

    def _check_javascript_lint(self):
        """Check javascript lint
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for js_file_rel in self.filter_files_ext('js', relpath=True):
            js_file = os.path.join(self.module_path, js_file_rel)
            errors = self.check_js_lint(js_file, self.config.jslintrc)
            for error in errors:
                self.msg_args.append((js_file_rel + error,))
        if self.msg_args:
            return False
        return True

    def _check_deprecated_data_xml_node(self):
        """Check deprecated <data> xml node inside <odoo> xml node
        :return: False if found <data> xml node inside <odoo> xml node"""
        xml_files = self.filter_files_ext('xml')
        self.msg_args = []
        for xml_file in xml_files:
            doc = self.parse_xml(os.path.join(self.module_path, xml_file))
            odoo_nodes = doc.xpath("/odoo")
            children, data_node = ((odoo_nodes[0].getchildren(),
                                    odoo_nodes[0].findall('data'))
                                   if odoo_nodes else ([], []))
            if len(children) == 1 and len(data_node) == 1:
                lineno = odoo_nodes[0].sourceline
                self.msg_args.append(("%s:%s" % (xml_file, lineno)))
        if self.msg_args:
            return False
        return True

    def _check_deprecated_openerp_xml_node(self):
        """Check deprecated <openerp> xml node
        :return: False if exists <openerp> node and
                 add list of xml files in self.msg_args
        """
        xml_files = self.filter_files_ext('xml')
        self.msg_args = []
        for xml_file in xml_files:
            doc = self.parse_xml(os.path.join(self.module_path, xml_file))
            openerp_nodes = doc.xpath("/openerp")
            if openerp_nodes:
                lineno = openerp_nodes[0].sourceline
                self.msg_args.append(("%s:%s" % (xml_file, lineno)))
        if self.msg_args:
            return False
        return True

    def _check_wrong_tabs_instead_of_spaces(self):
        """Check wrong tabs character instead of four spaces.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for type_file in self.config.extfiles_to_lint:
            for ext_file_rel in self.filter_files_ext(type_file, relpath=True):
                ext_file = os.path.join(self.module_path, ext_file_rel)
                countline = 0
                with open(ext_file, 'rb') as fp:
                    for line in fp:
                        countline += 1
                        line_space_trip = line.lstrip(b' ')
                        if line_space_trip != line_space_trip.lstrip(b'\t'):
                            self.msg_args.append(
                                ("%s:%d" % (ext_file_rel, countline)))
        if self.msg_args:
            return False
        return True

    def _check_missing_newline_extrafiles(self):
        """Check missing newline in other ext files (.xml, .csv, .po)
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for type_file in self.config.extfiles_to_lint:
            for ext_file_rel in self.filter_files_ext(type_file, relpath=True):
                ext_file = os.path.join(self.module_path, ext_file_rel)
                last_line = ''
                # NOTE: SEEK_END just is supported with 'rb' mode for py3
                with open(ext_file, 'rb') as fp:
                    if os.stat(ext_file).st_size > 1:
                        fp.seek(-2, os.SEEK_END)
                        last_line = fp.readline()
                        if not (last_line.endswith(b'\n') or
                                last_line.endswith(b'\r')):
                            self.msg_args.append((ext_file_rel,))
        if self.msg_args:
            return False
        return True

    def _get_manifest_referenced_files(self):
        referenced_files = {}
        for data_type in DFTL_MANIFEST_DATA_KEYS:
            for fname in self.manifest_dict.get(data_type) or []:
                referenced_files[os.path.normpath(fname)] = data_type
        return referenced_files

    def _get_xml_referenced_files(self):
        referenced_files = {}
        for data_type in DFTL_MANIFEST_DATA_KEYS:
            for fname in self.manifest_dict.get(data_type) or []:
                if not fname.endswith('.xml'):
                    continue
                referenced_files.update(
                    self._get_xml_referenced_files_report(
                        os.path.normpath(fname), data_type)
                )
        return referenced_files

    def _get_xml_referenced_files_report(self, fname, data_type):
        return {
            # those files are relative to the addon path
            os.path.join(
                *os.path.normpath(record.attrib[attribute]).split(os.sep)[1:]
            ): data_type
            for attribute in ['xml', 'xsl']
            for record in self.parse_xml(
                os.path.join(self.module_path, fname)
            )
            .xpath('//report[@%s]' % attribute)
        }

    def _get_module_files(self):
        module_files = []
        for type_file in self.config.extfiles_convert:
            for ext_file_rel in self.filter_files_ext(type_file, relpath=True):
                module_files.append(ext_file_rel)
        return module_files

    def _check_file_not_used(self):
        """Check if a file is not used from manifest"""
        module_files = set(self._get_module_files())
        referenced_files = set(self._get_manifest_referenced_files()).union(
            set(self._get_xml_referenced_files())
        )
        excluded_dirs = ['static', 'test', 'tests', 'migrations']
        no_referenced_files = [
            f for f in (module_files - referenced_files)
            if f.split(os.path.sep)[0] not in excluded_dirs
        ]
        self.msg_args = no_referenced_files
        return not no_referenced_files

    def _check_xml_attribute_translatable(self):
        """The xml attribute is missing the translation="off" tag
            Example  <attribute name="groups">sale.group</attribute>
        """
        if (self.linter._all_options['valid_odoo_versions'].config
                .valid_odoo_versions != ['8.0']):
            return True
        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=True):
            for record in self.get_xml_records(
                    os.path.join(self.module_path, xml_file), None,
                    '//attribute[not(@name="string") and not(@translation)]'):
                self.msg_args.append(
                    ("%s:%d" % (xml_file, record.sourceline), 'xml_id'))
        if self.msg_args:
            return False
        return True

    def _check_xml_deprecated_tree_attribute(self):
        """The tree-view declaration is using a deprecated attribute.
            Example <tree string="Partners"></tree>
        """
        checks = [
            {
                'attr': 'colors',
                'skip_versions': {'4.2', '5.0', '6.0', '6.1', '7.0', '8.0'},
                'xpath': './/tree[@colors]',
            },
            {
                'attr': 'fonts',
                'skip_versions': {'4.2', '5.0', '6.0', '6.1', '7.0', '8.0'},
                'xpath': './/tree[@fonts]',
            },
            {
                'attr': 'string',
                'skip_versions': {'4.2', '5.0', '6.0', '6.1', '7.0'},
                'xpath': './/tree[@string]',
            },
        ]
        valid_versions = set(
            self.linter._all_options['valid_odoo_versions'].config
            .valid_odoo_versions)

        applicable_checks = [check for check in checks if (
            check['attr'] in self.config.deprecated_tree_attributes and
            bool(valid_versions - check['skip_versions']))]

        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=True):
            for record in self.get_xml_records(
                    os.path.join(self.module_path, xml_file),
                    model='ir.ui.view'):

                for check in applicable_checks:
                    if record.xpath(check['xpath']):
                        self.msg_args.append((
                            '%s:%d' % (xml_file, record.sourceline),
                            check['attr']))
        if self.msg_args:
            return False
        return True

    def _check_xml_deprecated_qweb_directive(self):
        """Check for use of deprecated QWeb directives t-*-options.
        :return: False if deprecated directives are found, in which case
                 self.msg_args will contain the error messages.
        """
        valid_versions = set(self.linter._all_options[
            'valid_odoo_versions'].config.valid_odoo_versions)
        if not valid_versions & {'10.0', '11.0'}:
            return True

        deprecated_directives = {
            't-esc-options',
            't-field-options',
            't-raw-options',
        }
        directive_attrs = '|'.join('@%s' % d for d in deprecated_directives)
        xpath = '|'.join(
            '/%s//template//*[%s]' % (tag, directive_attrs)
            for tag in ('odoo', 'openerp')
        )

        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=False):
            doc = self.parse_xml(xml_file)
            for node in doc.xpath(xpath):
                # Find which directive was used exactly.
                directive = next(
                    iter(set(node.attrib) & deprecated_directives))
                self.msg_args.append((
                    '%s:%d' % (xml_file, node.sourceline), directive))
        return not bool(self.msg_args)
