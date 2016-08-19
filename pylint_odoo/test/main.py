
import os
import sys
import unittest
from contextlib import contextmanager
from cProfile import Profile

from pylint.lint import Run

from pylint_odoo import misc

EXPECTED_ERRORS = {
    'api-one-deprecated': 4,
    'api-one-multi-together': 2,
    'attribute-deprecated': 2,
    'class-camelcase': 1,
    'consider-merging-classes-inherited': 2,
    'copy-wo-api-one': 2,
    'create-user-wo-reset-password': 1,
    'dangerous-filter-wo-user': 1,
    'dangerous-view-replace-wo-priority': 5,
    'deprecated-openerp-xml-node': 5,
    'duplicate-id-csv': 2,
    'duplicate-xml-fields': 6,
    'duplicate-xml-record-id': 2,
    'file-not-used': 8,
    'incoherent-interpreter-exec-perm': 3,
    'invalid-commit': 4,
    'javascript-lint': 2,
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
    'missing-newline-extrafiles': 3,
    'missing-readme': 1,
    'no-utf8-coding-comment': 3,
    'odoo-addons-relative-import': 4,
    'old-api7-method-defined': 2,
    'openerp-exception-warning': 3,
    'redundant-modulename-xml': 1,
    'rst-syntax-error': 2,
    'sql-injection': 6,
    'translation-field': 2,
    'translation-required': 4,
    'use-vim-comment': 1,
    'wrong-tabs-instead-of-spaces': 2,
    'xml-syntax-error': 2,
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
        "self-test if path don't exist"
        path_unexist = u'/tmp/____unexist______'
        with self.assertRaisesRegexp(
                OSError,
                r'Path "{path}" not found.$'.format(path=path_unexist)):
            self.run_pylint([path_unexist])

    def test_20_expected_errors(self):
        pylint_res = self.run_pylint(self.paths_modules)
        # Expected vs found errors
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(sorted(real_errors.items()),
                         sorted(EXPECTED_ERRORS.items()))
        # All odoolint name errors vs found
        msgs_found = pylint_res.linter.stats['by_msg'].keys()
        plugin_msgs = misc.get_plugin_msgs(pylint_res)
        test_missed_msgs = sorted(list(set(plugin_msgs) - set(msgs_found)))
        self.assertEqual(
            test_missed_msgs, [],
            "Checks without test case: {test_missed_msgs}".format(
                test_missed_msgs=test_missed_msgs))
        sum_fails_found = misc.get_sum_fails(pylint_res.linter.stats)
        sum_fails_expected = sum(EXPECTED_ERRORS.values())
        self.assertEqual(sum_fails_found, sum_fails_expected)

    def test_30_disabling_errors(self):
        # Disabling
        self.default_extra_params.append('--disable=dangerous-filter-wo-user')
        pylint_res = self.run_pylint(self.paths_modules)
        real_errors = pylint_res.linter.stats['by_msg']
        global EXPECTED_ERRORS
        EXPECTED_ERRORS.pop('dangerous-filter-wo-user')
        self.assertEqual(sorted(real_errors.items()),
                         sorted(EXPECTED_ERRORS.items()))
        sum_fails_found = misc.get_sum_fails(pylint_res.linter.stats)
        sum_fails_expected = sum(EXPECTED_ERRORS.values())
        self.assertEqual(sum_fails_found, sum_fails_expected)

    def test_40_deprecated_modules(self):
        """Test deprecated modules"""
        extra_params = ['--disable=all',
                        '--enable=deprecated-module',
                        '--deprecated-modules=openerp.osv']
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats['by_msg']
        self.assertEqual(real_errors.items(), [('deprecated-module', 4)])


if __name__ == '__main__':
    unittest.main()
