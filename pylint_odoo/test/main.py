
import os

import unittest

from pylint.lint import Run

from pylint_odoo import misc


EXPECTED_ERRORS = 46


class MainTest(unittest.TestCase):
    def setUp(self):
        self.default_options = [
            '--load-plugins=pylint_odoo', '--report=no',
            '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}',
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
            '--enable=odoolint,pointless-statement',
        ]

    def run_pylint(self, paths, extra_params=None):
        for path in paths:
            if not os.path.exists(path):
                raise OSError('Path "{path}" not found.'.format(path=path))
        if extra_params is None:
            extra_params = self.default_extra_params
        return Run(self.default_options + extra_params + paths, exit=False)

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
        sum_fails_found = misc.get_sum_fails(pylint_res.linter.stats)
        self.assertEqual(
            sum_fails_found, EXPECTED_ERRORS,
            "Errors found {fnd} different to expected {exp}.".format(
                fnd=sum_fails_found, exp=EXPECTED_ERRORS))
        # All odoolint name errors vs found
        msgs_found = pylint_res.linter.stats['by_msg'].keys()
        plugin_msgs = misc.get_plugin_msgs(pylint_res)
        test_missed_msgs = sorted(list(set(plugin_msgs) - set(msgs_found)))
        self.assertEqual(
            test_missed_msgs, [],
            "Checks without test case: {test_missed_msgs}".format(
                test_missed_msgs=test_missed_msgs))

    def test_30_disabling_errors(self):
        # Disabling
        self.default_extra_params.append('--disable=dangerous-filter-wo-user')
        pylint_res = self.run_pylint(self.paths_modules)
        sum_fails_found = misc.get_sum_fails(pylint_res.linter.stats)
        self.assertEqual(
            sum_fails_found, EXPECTED_ERRORS - 1,
            "Errors found {fnd} different to expected {exp}.".format(
                fnd=sum_fails_found, exp=EXPECTED_ERRORS - 1))


if __name__ == '__main__':
    unittest.main()
