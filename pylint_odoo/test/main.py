
import os
import stat
import sys
from tempfile import gettempdir

import unittest
from contextlib import contextmanager
from cProfile import Profile

from pylint.lint import Run

from pylint_odoo import misc

EXPECTED_ERRORS = {
    'api-one-deprecated': 4,
    'api-one-multi-together': 2,
    'attribute-deprecated': 3,
    'class-camelcase': 1,
    'consider-merging-classes-inherited': 2,
    'copy-wo-api-one': 2,
    'create-user-wo-reset-password': 1,
    'dangerous-filter-wo-user': 1,
    'dangerous-view-replace-wo-priority': 5,
    'deprecated-openerp-xml-node': 5,
    'duplicate-id-csv': 2,
    'duplicate-xml-fields': 8,
    'duplicate-xml-record-id': 2,
    'file-not-used': 6,
    'incoherent-interpreter-exec-perm': 3,
    'invalid-commit': 4,
    'javascript-lint': 8,
    'license-allowed': 1,
    'manifest-author-string': 1,
    'manifest-deprecated-key': 1,
    'manifest-required-author': 1,
    'manifest-required-key': 1,
    'manifest-version-format': 2,
    'method-compute': 1,
    'method-inverse': 1,
    'method-required-super': 8,
    'method-search': 1,
    'missing-import-error': 3,
    'missing-manifest-dependency': 2,
    'missing-newline-extrafiles': 4,
    'missing-readme': 1,
    'missing-return': 1,
    'no-utf8-coding-comment': 3,
    'odoo-addons-relative-import': 4,
    'old-api7-method-defined': 2,
    'openerp-exception-warning': 3,
    'redundant-modulename-xml': 1,
    'rst-syntax-error': 2,
    'sql-injection': 15,
    'translation-field': 2,
    'translation-required': 4,
    'use-vim-comment': 1,
    'wrong-tabs-instead-of-spaces': 2,
    'eval-referenced': 5,
    'xml-syntax-error': 2,
    'except-pass': 3,
    'attribute-string-redundant': 33,
    'renamed-field-parameter': 2,
    'deprecated-data-xml-node': 5,
    'resource-not-exist': 3,
}


@contextmanager
def profiling(profile):
    profile.enable()
    yield
    profile.disable()


class MainTest(unittest.TestCase):
    def setUp(self):
        self.default_options = [
            '--load-plugins=pylint_odoo', '--reports=no', '--msg-template='
            '"{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"',
            '--output-format=colorized',
        ]
        path_modules = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'test_repo')
        self.paths_modules = []
        root, dirs, _ = os.walk(path_modules).next()
        for path in dirs:
            self.paths_modules.append(os.path.join(root, path))
        self.default_extra_params = [
            '--disable=all',
            '--enable=odoolint,pointless-statement,trailing-newlines',
        ]
        self.profile = Profile()
        self.sys_path_origin = list(sys.path)
        self.maxDiff = None
        self.expected_errors = EXPECTED_ERRORS.copy()

    def tearDown(self):
        sys.path = list(self.sys_path_origin)
        test = self._testMethodName
        prefix = os.path.expanduser(os.environ.get('PYLINT_ODOO_STATS',
                                    '~/pylint_odoo_cprofile'))
        fstats = prefix + '_' + test + '.stats'
        if test != 'test_10_path_dont_exist':
            self.profile.dump_stats(fstats)

    def run_pylint(self, paths, extra_params=None):
        for path in paths:
            if not os.path.exists(path):
                raise OSError('Path "{path}" not found.'.format(path=path))
        if extra_params is None:
            extra_params = self.default_extra_params
        sys.path.extend(paths)
        cmd = self.default_options + extra_params + paths
        with profiling(self.profile):
            res = Run(cmd, exit=False)
        return res

    def test_10_path_dont_exist(self):
        """test if path don't exist"""
        path_unexist = u'/tmp/____unexist______'
        with self.assertRaisesRegexp(
                OSError,
                r'Path "{path}" not found.$'.format(path=path_unexist)):
            self.run_pylint([path_unexist])

    def test_20_expected_errors(self):
        """Expected vs found errors"""
        pylint_res = self.run_pylint(self.paths_modules)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(self.expected_errors, real_errors)

    def test_25_checks_without_coverage(self):
        """All odoolint errors vs found"""
        extra_params = ['--valid_odoo_versions=8.0']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        msgs_found = pylint_res.linter.stats['by_msg'].keys()
        plugin_msgs = misc.get_plugin_msgs(pylint_res)
        test_missed_msgs = sorted(list(set(plugin_msgs) - set(msgs_found)))
        self.assertFalse(
            test_missed_msgs,
            "Checks without test case: {test_missed_msgs}".format(
                test_missed_msgs=test_missed_msgs))

    def test_30_disabling_errors(self):
        """Test disabling checkers"""
        self.default_extra_params.append('--disable=dangerous-filter-wo-user')
        pylint_res = self.run_pylint(self.paths_modules)
        real_errors = pylint_res.linter.stats['by_msg']
        self.expected_errors.pop('dangerous-filter-wo-user')
        self.assertEqual(self.expected_errors, real_errors)

    def test_40_deprecated_modules(self):
        """Test deprecated modules"""
        extra_params = ['--disable=all',
                        '--enable=deprecated-module',
                        '--deprecated-modules=openerp.osv']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(real_errors.items(), [('deprecated-module', 4)])

    def test_50_ignore(self):
        """Test --ignore parameter """
        extra_params = ['--ignore=test_module/res_users.xml',
                        '--disable=all',
                        '--enable=deprecated-openerp-xml-node']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(real_errors.items(),
                         [('deprecated-openerp-xml-node', 4)])

    def test_60_ignore_patterns(self):
        """Test --ignore-patterns parameter """
        extra_params = ['--ignore-patterns='
                        '.*\/test_module\/*\/.*xml$',
                        '--disable=all',
                        '--enable=deprecated-openerp-xml-node']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(real_errors.items(),
                         [('deprecated-openerp-xml-node', 3)])

    def test_70_without_jslint_installed(self):
        """Test without jslint installed"""
        # if not self.jslint_bin_content:
        #     return
        # TODO: Use mock to create a monkey patch
        which_original = misc.which

        def my_which(bin_name, *args, **kwargs):
            if bin_name == 'eslint':
                return None
            return which_original(bin_name)
        misc.which = my_which
        my_which("noeslint")
        pylint_res = self.run_pylint(self.paths_modules)
        misc.which = which_original
        real_errors = pylint_res.linter.stats['by_msg']
        self.expected_errors.pop('javascript-lint')
        self.assertEqual(self.expected_errors, real_errors)

    def test_80_with_jslint_error(self):
        """Test with jslint error"""
        # TODO: Use mock to create a monkey patch
        which_original = misc.which

        def my_which(bin_name, *args, **kwargs):
            fname = os.path.join(gettempdir(), 'jslint.bad')
            with open(fname, "w") as f_jslint:
                f_jslint.write("#!/usr/bin/env node\n{}}")
            os.chmod(fname, os.stat(fname).st_mode | stat.S_IEXEC)
            return fname

        misc.which = my_which
        pylint_res = self.run_pylint(self.paths_modules)
        misc.which = which_original
        real_errors = pylint_res.linter.stats['by_msg']
        self.expected_errors.pop('javascript-lint')
        self.assertEqual(self.expected_errors, real_errors)

    def test_90_valid_odoo_versions(self):
        """Test --valid_odoo_versions parameter when is '8.0'"""
        extra_params = ['--valid_odoo_versions=8.0',
                        '--disable=all',
                        '--enable=xml-attribute-translatable']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(real_errors.items(),
                         [('xml-attribute-translatable', 1)])


if __name__ == '__main__':
    unittest.main()
