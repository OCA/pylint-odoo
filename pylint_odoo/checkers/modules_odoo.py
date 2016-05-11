"""Visit module to add odoo checks
"""

import os

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
    'W%d01' % settings.BASE_OMODULE_ID: (
        'Dangerous filter without explicit `user_id` in xml_id %s',
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
        'Duplicate id "%s" in ir.model.access.csv file',
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
}


DFTL_README_TMPL_URL = 'https://github.com/OCA/maintainer-tools' + \
    '/blob/master/template/module/README.rst'
DFTL_EXTFILES_TO_LINT = ['xml', 'csv', 'po', 'js', 'mako']


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
            'default': DFTL_EXTFILES_TO_LINT,
            'help': 'List of extension files to check separated by a comma.'
        }),
    )

    @utils.check_messages(*(ODOO_MSGS.keys()))
    def visit_module(self, node):
        self.wrapper_visit_module(node)

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
        for csv_file in self.filter_files_ext('csv', relpath=False):
            if os.path.basename(csv_file) == 'ir.model.access.csv':
                all_csv_ids.extend(self.get_field_csv(csv_file))
        duplicated_id_csv = self.get_duplicated_items(all_csv_ids)
        if duplicated_id_csv:
            self.msg_args = duplicated_id_csv
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
                        xml_file + ':' + ir_filter_record.get('id'),)
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
            for user_record in user_records:
                context = {}
                try:
                    context = eval(user_record.get('context') or '{}')
                except NameError:
                    pass
                except SyntaxError:
                    pass
                if user_record.xpath("field[@name='name']"):
                    # if exists field="name" then is a new record
                    # then should be context
                    if not context.get('no_reset_password', False):
                        self.msg_args.append((
                            xml_file, user_record.sourceline))
        if self.msg_args:
            return False
        return True

    def _check_javascript_lint(self):
        """Check javascript lint
        :return: False if exists errors and
                 add list of errors in self.msg_args
        """
        self.msg_args = []
        for js_file in self.filter_files_ext('js', relpath=True):
            errors = self.check_js_lint(
                os.path.join(self.module_path, js_file))
            for error in errors:
                self.msg_args.append((
                    js_file + error))
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
                    if os.stat(ext_file).st_size > 0:
                        fp.seek(-2, os.SEEK_END)
                        last_line = fp.readline()
                        if not (last_line.endswith('\n') or
                                last_line.endswith('\r')):
                            self.msg_args.append((ext_file_rel,))
        if self.msg_args:
            return False
        return True
