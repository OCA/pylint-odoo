import ast
import csv
import os
import re
import string
import subprocess
import inspect

from distutils.version import LooseVersion
from lxml import etree
from pylint.checkers import BaseChecker, BaseTokenChecker
from pylint.interfaces import UNDEFINED
from pylint.interfaces import IAstroidChecker, ITokenChecker
try:
    # sha 5805a73 pylint 2.9
    from pylint.lint.expand_modules import _is_in_ignore_list_re
except ImportError:
    try:
        # sha 63ca0597 pylint 2.8
        from pylint.lint.expand_modules import (
            _basename_in_ignore_list_re as _is_in_ignore_list_re)
    except ImportError:
        try:
            # sha d19c77337 pylint 2.7
            from pylint.utils.utils import (
                _basename_in_ignore_list_re as _is_in_ignore_list_re)
        except ImportError:
            # Compatibility with pylint<=2.6.0
            from pylint.utils import (
                _basename_in_blacklist_re as _is_in_ignore_list_re)
from restructuredtext_lint import lint_file as rst_lint
from six import string_types

from . import settings

try:
    from shutil import which  # python3.x
except ImportError:
    from whichcraft import which

try:
    import isort.api

    HAS_ISORT_5 = True
except ImportError:  # isort < 5
    import isort

    HAS_ISORT_5 = False

DFTL_VALID_ODOO_VERSIONS = [
    '4.2', '5.0', '6.0', '6.1', '7.0', '8.0', '9.0', '10.0', '11.0', '12.0',
    '13.0', '14.0', '15.0',
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
        if hasattr(msgs_store, '_messages'):
            return pylint_run_res.linter.msgs_store._messages
        # pylint 2.3.0 renamed _messages to _messages_definitions in:
        # https://github.com/PyCQA/pylint/commit/75cecdb1b88cc759223e83fd325aeafd09fec37e  # noqa
        if hasattr(msgs_store, '_messages_definitions'):
            return pylint_run_res.linter.msgs_store._messages_definitions
        raise ValueError(  # pragma: no cover
            'pylint.utils.MessagesStore does not have a '
            '_messages/_messages_definitions attribute')

    messages = get_messages()

    all_plugin_msgs = []
    for key in messages:
        message = messages[key]
        if hasattr(message, 'checker'):
            checker_name = message.checker.name
        elif hasattr(message, 'msgid'):
            # pylint 2.5.3 renamed message.checker.name (symbol) to message.msgid
            checker_name = message.msgid
        else:
            raise ValueError('Message does not have a checker name')  # pragma: no cover
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

    def set_ext_files(self):
        """Create `self.ext_files` dictionary with {extension_file: [files]}
            and exclude files using --ignore and --ignore-patterns parameters
        """
        self.ext_files = {}
        for root, _, filenames in os.walk(self.module_path, followlinks=True):
            for filename in filenames:
                fext = os.path.splitext(filename)[1].lower()
                fname = os.path.join(root, filename)
                # If the file is within black_list_re is ignored
                if _is_in_ignore_list_re(fname, self.linter.config.black_list_re):
                    continue
                # If the file is within ignores is ignored
                find = False
                for ignore in self.linter.config.black_list:
                    if ignore in fname:
                        find = True
                        break
                if not find:
                    fname_rel = os.path.relpath(fname, self.module_path)
                    self.ext_files.setdefault(fext, []).append(fname_rel)

    def set_caches(self):
        self.ext_files = {}
        if self.is_main_odoo_module:
            self.set_ext_files()

    def clear_caches(self):
        self.ext_files = None

    def leave_module(self, node):
        """Clear caches"""
        self.clear_caches()

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
        self.set_caches()
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
            if callable(check_method) and (is_odoo_check or is_py_check):
                if not check_method():
                    if not isinstance(self.msg_args, list):
                        self.msg_args = [self.msg_args]
                    for msg_args in self.msg_args:
                        node_file_original = node.file
                        node_lineno_original = node.lineno
                        msg_args_extra = self.set_extra_file(node, msg_args,
                                                             msg_code)
                        self.add_message(name_key, line=node.lineno, node=node,
                                         args=msg_args_extra)
                        node.file = node_file_original
                        node.lineno = node_lineno_original

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
        if not self._is_version_supported(short_version, msg_id):
            return
        return super(PylintOdooChecker, self).add_message(
            msg_id, line, node, args, confidence)

    def _is_version_supported(self, version, name_check):
        if not version or not hasattr(self, 'odoo_check_versions'):
            return True
        odoo_check_versions = self.odoo_check_versions.get(name_check, {})
        if not odoo_check_versions:
            return True
        version = LooseVersion(version)
        min_odoo_version = LooseVersion(odoo_check_versions.get(
            'min_odoo_version', DFTL_VALID_ODOO_VERSIONS[0]))
        max_odoo_version = LooseVersion(odoo_check_versions.get(
            'max_odoo_version', DFTL_VALID_ODOO_VERSIONS[-1]))
        return min_odoo_version <= version <= max_odoo_version


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

    def set_extra_file(self, node, msg_args, msg_code):
        if isinstance(msg_args, string_types):
            msg_args = (msg_args,)
        first_arg = msg_args and msg_args[0] or ""
        fregex_str = \
            r"(?P<file>^[\w|\-|\.|/ \\]+):?(?P<lineno>\d+)?:?(?P<colno>\d+)?"
        fregex = re.compile(fregex_str)
        fmatch = fregex.match(first_arg)

        msgs_store = self.linter.msgs_store

        def get_message_definitions(message_id_or_symbol):
            if hasattr(msgs_store, 'check_message_id'):
                return [msgs_store.check_message_id(message_id_or_symbol)]
            # pylint 2.0 renamed check_message_id to get_message_definition in:
            # https://github.com/PyCQA/pylint/commit/5ccbf9eaa54c0c302c9180bdfb745566c16e416d  # noqa
            if hasattr(msgs_store, 'get_message_definition'):  # pragma: no cover
                return \
                    [msgs_store.get_message_definition(message_id_or_symbol)]
            # pylint 2.3.0 renamed get_message_definition to get_message_definitions in:  # noqa
            # https://github.com/PyCQA/pylint/commit/da67a9da682e51844fbc674229ff6619eb9c816a  # noqa
            if hasattr(msgs_store, 'get_message_definitions'):
                return \
                    msgs_store.get_message_definitions(message_id_or_symbol)
            else:
                raise ValueError(  # pragma: no cover
                    'pylint.utils.MessagesStore does not have a '
                    'get_message_definition(s) method')

        msg = get_message_definitions(msg_code)[0].msg.strip('"\' ')
        if not fmatch or not msg.startswith(r"%s"):
            return msg_args
        module_path = os.path.dirname(self.manifest_file or node.file)
        fname = fmatch.group('file')
        fpath = os.path.join(module_path, fname)
        node.file = fpath if os.path.isfile(fpath) else module_path
        node.lineno = int(fmatch.group('lineno') or 0)
        msg_strip = re.sub(fregex_str, '', first_arg, 1).strip(': ')
        return (msg_strip,) + msg_args[1:]

    def filter_files_ext(self, fext, relpath=True, skip_examples=True):
        """Filter files of odoo modules with a file extension.
        :param fext: Extension name of files to filter.
        :param relpath: Boolean to choose absolute path or relative path
                        If relpath is True then return relative paths
                        else return absolute paths
        :param skip_examples: Boolean to skip "examples" folder
        :return: List of paths of files matched
                 with extension fext.
        """
        dirnames_to_skip = []
        if skip_examples:
            dirnames_to_skip.extend([
                'example', 'examples', 'sample', 'samples', 'lib', 'libs',
                'doc', 'docs', 'template', 'templates',
            ])
        if not fext.startswith('.'):
            fext = '.' + fext
        fext = fext.lower()
        fnames = self._skip_files_ext(fext, self.ext_files.get(fext, []))
        for fname in list(fnames):
            dirnames = os.path.dirname(fname).split(os.sep)
            for dirname_to_skip in dirnames_to_skip:
                if dirname_to_skip in dirnames:
                    fnames.remove(fname)
                    break
        if not relpath:
            # Unused section is not delete it for compatibility
            fnames = [  # pragma: no cover
                os.path.join(self.module_path, fname)
                for fname in fnames]
        return fnames

    def _skip_files_ext(self, fext, fnames):
        """Detected inside the resource the skip message
        Eg: '<!-- pylint-odoo:disable=deprecated-data-xml-node -->'
        inside the xml resource"""
        if fext != '.xml':
            return fnames
        info_called = [item[3] for item in inspect.stack() if
                       'modules_odoo' in item[1] and
                       item[3].startswith('_check_')]
        method_called = (info_called[0].replace(
            '_check_', '').replace('_', '-') if info_called else False)
        if method_called:
            for fname in list(fnames):
                full_name = os.path.join(self.module_path, fname)
                if not os.path.isfile(full_name):
                    continue

                class PylintCommentTarget(object):
                    def __init__(self):
                        self.comments = []

                    def comment(self, text):
                        match = re.search(
                            r'(pylint:disable=|pylint: disable=|'
                            'pylint : disable=)', text)
                        if match:
                            text = match.re.split(text)[-1].replace(
                                '_', '-').strip()
                            self.comments.extend([item.strip() for item in
                                                  text.split(',')])

                    def close(self):
                        return self.comments

                parser = etree.XMLParser(target=PylintCommentTarget())
                try:
                    with open(full_name, 'rb') as xml_file:
                        skips = etree.parse(xml_file, parser)
                except etree.XMLSyntaxError:
                    skips = []
                if method_called in skips and fname in fnames:
                    fnames.remove(fname)
        return fnames

    def check_rst_syntax(self, fname):
        """Check syntax in rst files.
        :param fname: String with file name path to check
        :return: Return list of errors.
        """
        return rst_lint(fname, encoding='UTF-8')

    def npm_which_module(self, module):
        module_bin = which(module)
        npm_bin = which('npm')
        if not module_bin and npm_bin:
            npm_bin_paths = []
            for cmd in ([npm_bin, 'bin'], [npm_bin, 'bin', '-g']):
                process = subprocess.Popen(cmd,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                output, err = process.communicate()
                output = output.decode('UTF-8')
                err = err.decode('UTF-8')
                npm_bin_path = output.strip('\n ')
                if os.path.isdir(npm_bin_path) and not err:
                    npm_bin_paths.append(npm_bin_path)
            if npm_bin_paths:
                module_bin = which(module, path=os.pathsep.join(npm_bin_paths))
        return module_bin

    def check_js_lint(self, fname, frc=None):
        """Check javascript lint in fname.
        :param fname: String with full path of file to check
        :param frc: String with full path of configuration file for
            the javascript-lint tool
        :return: Return list of errors.
        """
        lint_bin = self.npm_which_module('eslint')
        if not lint_bin:
            return []
        cmd = [lint_bin, '--format=unix', fname]
        if frc:
            cmd.append('--config=' + frc)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, err = process.communicate()
        output = output.decode('UTF-8')
        err = err.decode('UTF-8')
        if process.returncode != 0 and err:
            output = err.replace('\n', '\\n')
        # Strip multi-line output https://github.com/eslint/eslint/issues/6810
        for old in re.findall(r"`(.*)` instead.", output, re.DOTALL):
            new = old.split('\n')[0][:20] + '...'
            output = output.replace(old, new)
        output = output.replace(fname, '')
        output_spplited = []
        if output:
            output_spplited.extend(
                output.strip('\n').split('\n')[:-2])
        return output_spplited

    def get_duplicated_items(self, items):
        """Get duplicated items
        :param items: Iterable items
        :return: List with tiems duplicated
        """
        unique_items = set()
        duplicated_items = set()
        for item in items:
            if item in unique_items:
                duplicated_items.add(item)
            else:
                unique_items.add(item)
        return list(duplicated_items)

    def parse_xml(self, xml_file, raise_if_error=False):
        """Get xml parsed.
        :param xml_file: Path of file xml
        :return: Doc parsed (lxml.etree object)
            if there is syntax error return string error message
        """
        if not os.path.isfile(xml_file):
            return etree.Element("__empty__")
        try:
            with open(xml_file, "rb") as f_obj:
                doc = etree.parse(f_obj)
        except etree.XMLSyntaxError as xmlsyntax_error_exception:
            if raise_if_error:
                raise xmlsyntax_error_exception
            return etree.Element("__empty__")
        return doc

    def get_xml_records(self, xml_file, model=None, more=None):
        """Get tag `record` of a openerp xml file.
        :param xml_file: Path of file xml
        :param model: String with record model to filter.
                      if model is None then get all.
                      Default None.
        :return: List of lxml `record` nodes
            If there is syntax error return []
        """
        xml_file = self._skip_files_ext('.xml', [xml_file])
        if not xml_file:
            return []
        xml_file = xml_file[0]
        if model is None:
            model_filter = ''
        else:
            model_filter = "[@model='{model}']".format(model=model)
        if more is None:
            more_filter = ''
        else:
            more_filter = more
        doc = self.parse_xml(xml_file)
        return doc.xpath("/openerp//record" + model_filter + more_filter) + \
            doc.xpath("/odoo//record" + model_filter + more_filter)

    def get_field_csv(self, csv_file, field='id'):
        """Get xml ids from csv file
        :param csv_file: Path of file csv
        :param field: Field to search
        :return: List of string with field rows
        """
        with open(csv_file, 'r') as csvfile:
            lines = csv.DictReader(csvfile)
            return [line[field] for line in lines if field in line]

    def get_xml_redundant_module_name(self, xml_file, module=None):
        """Get xml redundant name module in xml_id of a openerp xml file
        :param xml_file: Path of file xml
        :param module: String with record model to filter.
                       If model is None then return a empty list.
                       Default None.
        :return: List of tuples with (string, integer) with
            (module.xml_id, lineno) found
        """
        xml_ids = []
        for record in self.get_xml_records(xml_file):
            ref = record.get('id', '')
            xml_module, xml_id = ref.split('.') if '.' in ref else ['', ref]
            if module and xml_module == module:
                xml_ids.append((xml_id, record.sourceline))
        return xml_ids

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

    @staticmethod
    def parse_printf(main_str, secondary_str):
        """Compute args and kwargs of main_str to parse secondary_str
        Using secondary_str%_get_printf_str_args_kwargs(main_str)
        """
        printf_args = WrapperModuleChecker._get_printf_str_args_kwargs(main_str)
        if not printf_args:
            return
        try:
            main_str % printf_args
        except Exception:  # pragma: no cover
            # The original source string couldn't be parsed correctly
            # So return early without error in order to avoid a false error
            return
        try:
            secondary_str % printf_args
        except Exception as exc:
            # The translated string couldn't be parsed correctly
            # with the args and kwargs of the original string
            # so it is a real error
            raise StringParseError(repr(exc))

    @staticmethod
    def parse_format(main_str, secondary_str):
        """Compute args and kwargs of main_str to parse secondary_str
        Using secondary_str.format(_get_printf_str_args_kwargs(main_str))
        """
        msgid_args, msgid_kwargs = (
            WrapperModuleChecker._get_format_str_args_kwargs(main_str))
        if not msgid_args and not msgid_kwargs:
            return
        try:
            main_str.format(*msgid_args, **msgid_kwargs)
        except Exception:
            # The original source string couldn't be parsed correctly
            # So return early without error in order to avoid a false error
            return
        try:
            secondary_str.format(*msgid_args, **msgid_kwargs)
        except Exception as exc:
            # The translated string couldn't be parsed correctly
            # with the args and kwargs of the original string
            # so it is a real error
            raise StringParseError(repr(exc))


class IsortDriver:
    """
    A wrapper around isort API that changed between versions 4 and 5.
    Taken of https://git.io/Jt3dw
    """

    def __init__(self):
        if HAS_ISORT_5:
            self.isort5_config = isort.api.Config()
        else:
            self.isort4_obj = isort.SortImports(  # pylint: disable=no-member
                file_contents=""
            )

    def place_module(self, package):
        if HAS_ISORT_5:
            return isort.api.place_module(package, self.isort5_config)
        return self.isort4_obj.place_module(package)
