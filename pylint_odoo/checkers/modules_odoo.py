"""Visit module to add odoo checks
"""

import ast
import os

import astroid
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
        '%s:%s %s',
        'rst-syntax-error',
        settings.DESC_DFLT
    ),
    'E%d02' % settings.BASE_OMODULE_ID: (
        '%s error: %s',
        'xml-syntax-error',
        settings.DESC_DFLT
    ),
    'E%d03' % settings.BASE_OMODULE_ID: (
        '%s',
        'po-syntax-error',
        settings.DESC_DFLT
    ),
    'W%d01' % settings.BASE_OMODULE_ID: (
        '%s Dangerous filter without explicit `user_id` in xml_id %s',
        'dangerous-filter-wo-user',
        settings.DESC_DFLT
    ),
    'W%d02' % settings.BASE_OMODULE_ID: (
        'Duplicate xml record id %s',
        'duplicate-xml-record-id',
        settings.DESC_DFLT
    ),
    'W%d03' % settings.BASE_OMODULE_ID: (
        '%s',
        'javascript-lint',
        settings.DESC_DFLT
    ),
    'W%d04' % settings.BASE_OMODULE_ID: (
        '%s:%d Deprecated <openerp> xml node',
        'deprecated-openerp-xml-node',
        settings.DESC_DFLT
    ),
    'W%d05' % settings.BASE_OMODULE_ID: (
        '%s:%d record res.users without '
        'context="{\'no_reset_password\': True}"',
        'create-user-wo-reset-password',
        settings.DESC_DFLT
    ),
    'W%d06' % settings.BASE_OMODULE_ID: (
        '%s duplicate id "%s"',
        'duplicate-id-csv',
        settings.DESC_DFLT
    ),
    'W%d07' % settings.BASE_OMODULE_ID: (
        'Duplicate xml field "%s"',
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
        '%s:%s Use wrong tabs indentation instead of four spaces',
        'wrong-tabs-instead-of-spaces',
        settings.DESC_DFLT
    ),
    'W%d11' % settings.BASE_OMODULE_ID: (
        '%s',
        'po-lint',
        settings.DESC_DFLT
    ),
    'W%d30' % settings.BASE_OMODULE_ID: (
        '%s not used from manifest',
        'file-not-used',
        settings.DESC_DFLT
    ),
    'R%d80' % settings.BASE_OMODULE_ID: (
        'Consider merging classes inherited to %s.',
        'consider-merging-classes-inherited',
        settings.DESC_DFLT
    ),
}


DFLT_README_TMPL_URL = 'https://github.com/OCA/maintainer-tools' + \
    '/blob/master/template/module/README.rst'
# Files supported from manifest to convert
# Extracted from openerp/tools/convert.py:def convert_file
DFLT_EXTFILES_CONVERT = ['csv', 'sql', 'xml', 'yml']
DFLT_EXTFILES_TO_LINT = DFLT_EXTFILES_CONVERT + ['po', 'js', 'mako']
DFLT_PO_LINT_ENABLE = []
DFLT_PO_LINT_DISABLE = ['unchanged', 'short', 'acronyms',
                        'isfuzzy', 'doublewords', 'simpleplurals',
                        'pythonbraceformat', 'filepaths', 'startpunc',
                        'brackets', 'startcaps', 'puncspacing',
                        'singlequoting', 'sentencecount',
                        ]


class ModuleChecker(misc.WrapperModuleChecker):
    name = settings.CFG_SECTION
    msgs = ODOO_MSGS
    options = (
        ('readme_template_url', {
            'type': 'string',
            'metavar': '<string>',
            'default': DFLT_README_TMPL_URL,
            'help': 'URL of README.rst template file',
        }),
        ('extfiles_to_lint', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_EXTFILES_TO_LINT,
            'help': 'List of extension files to check separated by a comma.'
        }),
        ('extfiles_convert', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_EXTFILES_CONVERT,
            'help': 'List of extension files supported to convert '
                    'from manifest separated by a comma.'
        }),
        ('po-lint-enable', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_PO_LINT_ENABLE,
            'help': 'List of enabled po-lint checks separated by a comma.'
        }),
        ('po-lint-disable', {
            'type': 'csv',
            'metavar': '<comma separated values>',
            'default': DFLT_PO_LINT_DISABLE,
            'help': 'List of disabled po-lint checks separated by a comma.'
        }),
    )

    @utils.check_messages(*(ODOO_MSGS.keys()))
    def visit_module(self, node):
        self.wrapper_visit_module(node)

    @utils.check_messages('consider-merging-classes-inherited')
    def visit_assign(self, node):
        if not self.odoo_node:
            return
        node_left = node.targets[0]
        if not isinstance(node_left, astroid.node_classes.AssName) or \
                not node_left.name == '_inherit' or \
                not isinstance(node.value, astroid.node_classes.Const):
            return
        key = (self.odoo_node, node.value.value)
        if key in self.inh:
            self.inh_dup.setdefault(key[0], set()).add(key[1])
        else:
            self.inh.append(key)

    def open(self):
        """Define variables to use cache"""
        self.inh = []
        self.inh_dup = {}
        super(ModuleChecker, self).open()

    def close(self):
        """Final process get all cached values and add messages"""
        for odoo_node, class_dup_names in self.inh_dup.items():
            for class_dup_name in class_dup_names:
                self.add_message('consider-merging-classes-inherited',
                                 node=odoo_node,
                                 args=(class_dup_name,))

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
                self.msg_args.append((
                    rst_file, error.line,
                    error.full_message.strip('\n').replace('\n', '|')))
        if self.msg_args:
            return False
        return True

    def _check_missing_readme(self):
        """Check if exists ./README.rst file
        :return: If exists return True else False
        """
        self.msg_args = (self.config.readme_template_url,)
        return os.path.isfile(os.path.join(self.module_path, 'README.rst'))

    def _check_xml_syntax_error(self):
        """Check if xml file there is syntax error
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for xml_file in self.filter_files_ext('xml', relpath=True):
            result = self.parse_xml(os.path.join(self.module_path, xml_file))
            if isinstance(result, basestring):
                self.msg_args.append((
                    xml_file, result.strip('\n').replace('\n', '|')))
        if self.msg_args:
            return False
        return True

    def _check_duplicate_xml_record_id(self):
        """Check duplicate xml record id all xml files of a odoo module.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        all_xml_ids = []
        for xml_file in self.filter_files_ext('xml', relpath=False):
            all_xml_ids.extend(self.get_xml_record_ids(xml_file, self.module))
        duplicated_xml_ids = self.get_duplicated_items(all_xml_ids)
        if duplicated_xml_ids:
            self.msg_args = duplicated_xml_ids
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
            all_xml_ids = self.get_xml_redundant_module_name(xml_file,
                                                             self.module)
            if all_xml_ids:
                self.msg_args.append(
                    (xml_file_rel, ','.join(all_xml_ids)))
        if self.msg_args:
            return False
        return True

    def _check_duplicate_xml_fields(self):
        """Check duplicate field in all record of xml files of a odoo module.
        Important note: this check does not work with inherited views.
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        duplicated_xml_fields = []
        for xml_file in self.filter_files_ext('xml', relpath=False):
            all_xml_fields = (self.get_xml_record_fields(xml_file,
                                                         self.module))
            duplicated_xml_fields.extend(all_xml_fields)
        if duplicated_xml_fields:
            self.msg_args = duplicated_xml_fields
            return False
        return True

    def _check_dangerous_filter_wo_user(self):
        """Check dangeorous filter without a user assigned.
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
                    self.msg_args = (
                        xml_file, ir_filter_record.get('id'),)
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
                (xml_file, user_record.sourceline)
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
            if 'lib' in os.path.dirname(js_file_rel).split(os.sep):
                continue
            js_file = os.path.join(self.module_path, js_file_rel)
            errors = self.check_js_lint(js_file)
            for error in errors:
                self.msg_args.append((js_file_rel + error,))
        if self.msg_args:
            return False
        return True

    def _check_po_syntax_error(self):
        """Check po lint
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []

        for po_file in self.filter_files_ext('po', relpath=True):
            po_path = os.path.join(self.module_path, po_file)
            errors = self.check_po_syntax_error(po_path)
            for error in errors:
                self.msg_args.append((po_file + error))

        if self.msg_args:
            return False
        return True

    def _check_po_lint(self):
        """Check po lint
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        po_lint_enable = self.config.po_lint_enable
        po_lint_disable = self.config.po_lint_disable

        for po_file in self.filter_files_ext('po', relpath=True):
            po_path = os.path.join(self.module_path, po_file)
            errors = self.check_po_lint(po_path,
                                        po_lint_enable,
                                        po_lint_disable)
            for error in errors:
                self.msg_args.append((po_file + error))
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
            openerp_nodes = doc.xpath("/openerp") \
                if not isinstance(doc, basestring) else []
            if openerp_nodes:
                lineno = openerp_nodes[0].sourceline
                self.msg_args.append((
                    xml_file, lineno))
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
                if 'lib' in os.path.dirname(ext_file_rel).split(os.sep):
                    continue

                ext_file = os.path.join(self.module_path, ext_file_rel)
                countline = 0
                with open(ext_file, 'rb') as fp:
                    for line in fp:
                        countline += 1
                        line_space_trip = line.lstrip(' ')
                        if line_space_trip != line_space_trip.lstrip('\t'):
                            self.msg_args.append((ext_file_rel, countline))
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
                with open(ext_file, 'rb') as fp:
                    if os.stat(ext_file).st_size > 1:
                        fp.seek(-2, os.SEEK_END)
                        last_line = fp.readline()
                        if not (last_line.endswith('\n') or
                                last_line.endswith('\r')):
                            self.msg_args.append((ext_file_rel,))
        if self.msg_args:
            return False
        return True

    def _get_manifest_referenced_files(self):
        referenced_files = []
        data_keys = ['data', 'demo', 'demo_xml', 'init_xml', 'test',
                     'update_xml']
        with open(self.manifest_file) as f_manifest:
            manifest_dict = ast.literal_eval(f_manifest.read())
            for key in data_keys:
                referenced_files.extend(manifest_dict.get(key) or [])
        return referenced_files

    def _get_module_files(self):
        module_files = []
        for type_file in self.config.extfiles_convert:
            for ext_file_rel in self.filter_files_ext(type_file, relpath=True):
                module_files.append(ext_file_rel)
        return module_files

    def _check_file_not_used(self):
        """Check if a file is not used from manifest"""
        self.msg_args = []
        module_files = set(self._get_module_files())
        referenced_files = set(self._get_manifest_referenced_files())
        for no_referenced_file in (module_files - referenced_files):
            if not no_referenced_file.startswith('static/'):
                self.msg_args.append((no_referenced_file,))
        if self.msg_args:
            return False
        return True
