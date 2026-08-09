from __future__ import annotations

import os
import re
import stat
import sys
from collections import Counter, defaultdict
from glob import glob
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import astroid
import dill
import pytest
from pylint.reporters.text import TextReporter
from pylint.testutils._run import _Run as Run
from pylint.testutils.utils import _patch_streams

from pylint_odoo import __version__ as version, misc, plugin

RE_CHECK_OUTPUT = re.compile(r"\- \[(?P<check>[\w|-]+)\]")


def dill_supports_code_objects():
    """pylint parallel mode (--jobs) serializes the linter using dill, including the
    code objects of the functions that can not be pickled by reference.
    dill<=0.4.1 still uses "code.co_lnotab", removed in Python 3.15, so pylint --jobs
    crashes there unless the misc.patch_dill_missing_lnotab workaround applies"""
    misc.patch_dill_missing_lnotab()
    try:
        dill.loads(dill.dumps(compile("pass", "<test>", "exec")))
    except Exception:  # pylint: disable=broad-except
        return False
    return True


EXPECTED_ERRORS = {
    "attribute-deprecated": 3,
    "attribute-string-redundant": 33,
    "bad-builtin-groupby": 2,
    "category-allowed-app": 1,
    "consider-merging-classes-inherited": 3,
    "context-overridden": 3,
    "deprecated-inselect-operator": 5,
    "deprecated-name-get": 1,
    "deprecated-odoo-model-method": 2,
    "deprecated-self-cr": 27,
    "development-status-allowed": 1,
    "except-pass": 3,
    "external-request-timeout": 51,
    "inheritable-method-lambda": 2,
    "inheritable-method-string": 4,
    "invalid-commit": 4,
    "invalid-email": 1,
    "license-allowed": 1,
    "manifest-author-string": 1,
    "manifest-behind-migrations": 3,
    "manifest-data-duplicated": 1,
    "manifest-deprecated-key": 1,
    "manifest-external-assets": 3,
    "manifest-maintainers-list": 1,
    "manifest-required-author": 1,
    "manifest-required-key-app": 5,
    "manifest-required-key": 1,
    "manifest-summary-multiline": 2,
    "manifest-superfluous-key": 7,
    "manifest-version-format": 3,
    "method-compute": 2,
    "method-inverse": 2,
    "method-required-super": 8,
    "method-search": 2,
    "missing-odoo-file-app": 1,
    "missing-readme": 1,
    "missing-return": 1,
    "no-raise-unlink": 2,
    "no-search-all": 12,
    "no-wizard-in-models": 1,
    "no-write-in-compute": 16,
    "odoo-addons-relative-import": 4,
    "odoo-exception-warning": 4,
    "prefer-env-translation": 112,
    "print-used": 1,
    "renamed-field-parameter": 2,
    "resource-not-exist": 4,
    "sql-injection": 21,
    "super-method-mismatch": 7,
    "test-folder-imported": 3,
    "translation-contains-variable": 33,
    "translation-field": 3,
    "translation-format-interpolation": 22,
    "translation-format-truncated": 2,
    "translation-fstring-interpolation": 3,
    "translation-injection": 21,
    "translation-not-lazy": 42,
    "translation-positional-used": 30,
    "translation-required": 16,
    "translation-too-few-args": 2,
    "translation-too-many-args": 2,
    "translation-unsupported-format": 2,
    "use-vim-comment": 1,
    "website-manifest-key-not-valid-uri": 2,
}

LOGGING_TRANSLATION_CHECKS = [
    "translation-format-interpolation",
    "translation-format-truncated",
    "translation-fstring-interpolation",
    "translation-not-lazy",
    "translation-too-few-args",
    "translation-too-many-args",
    "translation-unsupported-format",
]

CHECKS_BY_ODOO_VERSION = [
    # (odoo_version, checks2exclude)
    (
        "13.0",
        [
            "deprecated-inselect-operator",
            "deprecated-name-get",
            "deprecated-odoo-model-method",
            "deprecated-self-cr",
            "manifest-summary-multiline",
            "no-raise-unlink",
            "prefer-env-translation",
            *LOGGING_TRANSLATION_CHECKS,
        ],
    ),
    (
        "14.0",
        [
            "deprecated-inselect-operator",
            "deprecated-name-get",
            "deprecated-odoo-model-method",
            "deprecated-self-cr",
            "manifest-summary-multiline",
            "no-raise-unlink",
            "prefer-env-translation",
            "translation-contains-variable",
        ],
    ),
    (
        "15.0",
        [
            "deprecated-inselect-operator",
            "deprecated-name-get",
            "deprecated-odoo-model-method",
            "deprecated-self-cr",
            "manifest-summary-multiline",
            "prefer-env-translation",
            "translation-contains-variable",
        ],
    ),
    (
        "17.0",
        [
            "deprecated-inselect-operator",
            "deprecated-self-cr",
            "manifest-summary-multiline",
            "prefer-env-translation",
            "translation-contains-variable",
        ],
    ),
    (
        "18.0",
        [
            "deprecated-self-cr",
            "manifest-summary-multiline",
            "translation-contains-variable",
        ],
    ),
    (
        "19.0",
        [
            "manifest-summary-multiline",
            "translation-contains-variable",
        ],
    ),
    (
        "20.0",
        [
            "translation-contains-variable",
        ],
    ),
]


class TestMain:
    def setup_method(self, method):
        self.default_options = [
            "--load-plugins=pylint_odoo",
            "--reports=no",
            "--score=no",
            "--msg-template={path}:{line} {msg} - [{symbol}]",
            "--persistent=no",
        ]
        self.root_path_modules = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "testing",
            "resources",
            "test_repo",
        )
        # Similar to pre-commit way
        self.paths_modules = glob(os.path.join(self.root_path_modules, "**", "*.py"), recursive=True)
        self.odoo_namespace_addons_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "testing",
            "resources",
            "test_repo_odoo_namespace",
            "odoo",
        )
        self.default_extra_params = [
            "--disable=all",
            "--enable=odoolint,pointless-statement,trailing-newlines",
        ]
        self.sys_path_origin = list(sys.path)
        self.maxDiff = None
        self.expected_errors = EXPECTED_ERRORS.copy()

    def teardown_method(self, method):
        sys.path = list(self.sys_path_origin)

    def assert_dict_equal(self, d1, d2, msg=None):
        """Similar to assert_dict_equal from unittest method
        show the correct item diff
        Using ordered list it is showing the diff better"""
        # real_dict2list = [(i, d1[i]) for i in sorted(d1)]
        # expected_dict2list = [(i, d2[i]) for i in sorted(d2)]

        diff = []
        all_keys = sorted(set(d1) | set(d2))

        for key in all_keys:
            if key not in d2:
                diff.append(f"- {key}: {d1[key]}")
            elif key not in d1:
                diff.append(f"+ {key}: {d2[key]}")
            elif d1[key] != d2[key]:
                diff.append(f"~ {key}: {d1[key]} -> {d2[key]}")

        assert not diff, f"{msg or ''}  {diff}".strip()

    def run_pylint(self, paths, extra_params: list | None = None, verbose=False, rcfile: str = ""):
        for path in paths:
            if not os.path.exists(path):
                raise OSError('Path "{path}" not found.'.format(path=path))

        if extra_params is None:
            extra_params = self.default_extra_params
        if rcfile:
            extra_params.append(f"--rcfile={rcfile}")

        sys.path.extend(paths)
        cmd = self.default_options + extra_params + paths
        reporter = TextReporter(StringIO())
        with open(os.devnull, "w", encoding="UTF-8") as f_dummy:
            self._run_pylint(cmd, f_dummy, reporter=reporter)
        if verbose:
            reporter.out.seek(0)
            print(reporter.out.read())
        return reporter

    @staticmethod
    def _run_pylint(args, out, reporter):
        with pytest.raises(SystemExit) as ctx_mgr:
            if sys.gettrace() is None:  # No pdb enabled
                with _patch_streams(out):
                    Run(args, reporter=reporter)
            else:  # pdb enabled
                Run(args, reporter=reporter)
        return int(ctx_mgr.value.code)

    def test_10_path_dont_exist(self):
        """test if path don't exist"""
        path_unexist = "/tmp/____unexist______"
        with pytest.raises(OSError, match=rf'Path "{path_unexist}" not found\.$'):  # noqa: B907
            self.run_pylint([path_unexist])

    def test_20_expected_errors(self):
        """Expected vs found errors"""
        pylint_res = self.run_pylint(self.paths_modules, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        assert self.expected_errors == real_errors

    @pytest.mark.parametrize(["odoo_version", "checks2exclude"], CHECKS_BY_ODOO_VERSION)
    def test_25_checks_excluding_by_odoo_version(self, odoo_version, checks2exclude):
        """All odoolint errors vs found but excluding based on Odoo version"""
        self.default_extra_params += [f"--valid-odoo-versions={odoo_version}"]
        pylint_res = self.run_pylint(self.paths_modules)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = self.expected_errors.copy()
        for excluded_msg in checks2exclude:
            expected_errors.pop(excluded_msg)
        expected_errors.update({"manifest-version-format": 6})
        assert expected_errors == real_errors

    @pytest.mark.parametrize(["odoo_version", "checks2exclude"], CHECKS_BY_ODOO_VERSION)
    def test_35_checks_emiting_by_odoo_version(self, odoo_version, checks2exclude):
        """All odoolint errors vs found but see if were not excluded for valid odoo version"""
        self.default_extra_params += [f"--valid-odoo-versions={odoo_version}"]
        pylint_res = self.run_pylint(self.paths_modules)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = self.expected_errors.copy()
        expected_errors.update({"manifest-version-format": 6})
        for excluded_msg in checks2exclude:
            expected_errors.pop(excluded_msg)
        assert expected_errors == real_errors

    def test_85_valid_odoo_version_format(self):
        """Test --manifest-version-format parameter"""
        # First, run Pylint for version 8.0
        extra_params = [
            r'--manifest-version-format="8\.0\.\d+\.\d+.\d+$"',
            "--valid-odoo-versions=8.0",
            "--disable=all",
            "--enable=manifest-version-format",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "manifest-version-format": 6,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        # Now for version 11.0
        extra_params[0] = r'--manifest-version-format="11\.0\.\d+\.\d+.\d+$"'
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "manifest-version-format": 5,
        }
        self.assert_dict_equal(real_errors, expected_errors)

    def test_90_valid_odoo_versions(self):
        """Test --valid-odoo-versions parameter when it's '8.0' & '11.0'"""
        # First, run Pylint for version 8.0
        extra_params = [
            "--valid-odoo-versions=8.0",
            "--disable=all",
            "--enable=manifest-version-format",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "manifest-version-format": 6,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        # Now for version 11.0
        extra_params[0] = "--valid-odoo-versions=11.0"
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "manifest-version-format": 5,
        }
        self.assert_dict_equal(real_errors, expected_errors)

    def test_110_manifest_required_authors(self):
        """Test --manifest-required-authors using a different author and
        multiple authors separated by commas
        """
        # First, run Pylint using a different author
        extra_params = [
            "--manifest-required-authors=Vauxoo",
            "--disable=all",
            "--enable=manifest-required-author",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "manifest-required-author": 5,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        # Then, run it using multiple authors
        extra_params[0] = "--manifest-required-authors=Vauxoo,Other"
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors["manifest-required-author"] -= 1
        self.assert_dict_equal(real_errors, expected_errors)

        # Testing deprecated attribute
        extra_params[0] = "--manifest-required-author=Odoo Community Association (OCA)"
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors_deprecated = {
            "manifest-required-author": (EXPECTED_ERRORS["manifest-required-author"]),
        }
        self.assert_dict_equal(real_errors, expected_errors_deprecated)

    def test_manifest_summary_multiline_version_limit(self):
        """Test manifest-summary-multiline check version limits:
        19.0- (no errors) vs 20.0+ (errors found)
        """
        # Run with v19.0: should not emit manifest-summary-multiline
        extra_params = [
            "--valid-odoo-versions=19.0",
            "--disable=all",
            "--enable=manifest-summary-multiline",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        assert "manifest-summary-multiline" not in real_errors

        # Run with v20.0: should emit manifest-summary-multiline
        extra_params = [
            "--valid-odoo-versions=20.0",
            "--disable=all",
            "--enable=manifest-summary-multiline",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        assert real_errors.get("manifest-summary-multiline") == 2

    def test_140_check_suppress_migrations(self):
        """Test migrations path supress checks"""
        extra_params = [
            "--disable=all",
            "--enable=invalid-name,unused-argument",
        ]
        path_modules = [
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "testing",
                "resources",
                "test_repo",
                "test_module",
                "migrations",
                "10.0.1.0.0",
                "pre-migration.py",
            )
        ]

        # Messages suppressed with plugin for migration
        pylint_res = self.run_pylint(path_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "unused-argument": 1,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        # Messages raised without plugin
        self.default_options.remove("--load-plugins=pylint_odoo")
        pylint_res = self.run_pylint(path_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "invalid-name": 1,
            "unused-argument": 2,
        }
        self.assert_dict_equal(real_errors, expected_errors)

    def test_140_check_migrations_is_not_odoo_module(self):
        """Checking that migrations folder is not considered a odoo module
        Related to https://github.com/OCA/pylint-odoo/issues/357"""
        extra_params = [
            "--disable=all",
            "--enable=missing-readme",
        ]
        test_module = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "testing",
            "resources",
            "test_repo",
            "test_module",
        )
        path_modules = [
            os.path.join(test_module, "__init__.py"),
            os.path.join(test_module, "migrations", "10.0.1.0.0", "pre-migration.py"),
        ]
        pylint_res = self.run_pylint(path_modules, extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {}
        self.assert_dict_equal(real_errors, expected_errors)

    def test_checks_odoo180(self):
        """prefer-env-translation and deprecated-inselect-operator are only valid
        for odoo v18.0+ but not for older odoo versions"""
        extra_params = [
            "--disable=all",
            "--enable=prefer-env-translation,deprecated-inselect-operator",
        ]
        pylint_res = self.run_pylint(self.paths_modules, ["--valid-odoo-versions=18.0"] + extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "prefer-env-translation": self.expected_errors.get("prefer-env-translation"),
            "deprecated-inselect-operator": self.expected_errors.get("deprecated-inselect-operator"),
        }
        assert expected_errors == real_errors

        pylint_res = self.run_pylint(self.paths_modules, ["--valid-odoo-versions=17.0"] + extra_params)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {}
        assert expected_errors == real_errors

    @pytest.mark.skipif(sys.platform.startswith("win"), reason="TODO: Fix with windows")  # TODO: Fix it
    def test_145_check_fstring_sqli(self):
        """Verify the linter is capable of finding SQL Injection vulnerabilities
        when using fstrings.
        Related to https://github.com/OCA/pylint-odoo/issues/363"""
        extra_params = ["--disable=all", "--enable=sql-injection"]
        queries = """
def fstring_sqli(self):
   self.env.cr.execute(f"SELECT * FROM TABLE WHERE SQLI = {self.table}")
   self.env.cr.execute(
       f"SELECT * FROM TABLE WHERE SQLI = {'hello' + self.name}"
   )
   self.env.cr.execute(f"SELECT * FROM {self.name} WHERE SQLI = {'hello'}")
   death_wish = f"SELECT * FROM TABLE WHERE SQLI = {self.name}"
   self.env.cr.execute(death_wish)
def fstring_no_sqli(self):
   self.env.cr.execute(f"SELECT * FROM TABLE WHERE SQLI = {'hello'}")
   self.env.cr.execute(
       f"CREATE VIEW {self._table} AS (SELECT * FROM res_partner)"
   )
   self.env.cr.execute(f"SELECT NAME FROM res_partner LIMIT 10")
           """
        with NamedTemporaryFile(mode="w") as tmp_f:
            tmp_f.write(queries)
            tmp_f.flush()
            pylint_res = self.run_pylint([tmp_f.name], extra_params)

        real_errors = pylint_res.linter.stats.by_msg
        self.assert_dict_equal(real_errors, {"sql-injection": 4})

    @pytest.mark.parametrize("expected_error_name", EXPECTED_ERRORS)
    def test_150_check_only_enabled_one_check(self, expected_error_name):
        """Checking -d all -e ONLY-ONE-CHECK"""
        disable = "--disable=all"
        expected_error_value = EXPECTED_ERRORS[expected_error_name]
        enable = "--enable=%s" % expected_error_name
        pylint_res = self.run_pylint(self.paths_modules, [disable, enable])
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {expected_error_name: expected_error_value}
        self.assert_dict_equal(real_errors, expected_errors)

    @pytest.mark.skipif(
        not dill_supports_code_objects(),
        reason="pylint parallel mode crashes since dill is not able to serialize code objects"
        " for this python version (e.g. py3.15 removed code.co_lnotab)",
    )
    @pytest.mark.parametrize("expected_error_name", EXPECTED_ERRORS)
    def test_155_check_only_enabled_one_check_jobs(self, expected_error_name):
        """Checking -d all -e ONLY-ONE-CHECK --jobs=2"""
        disable = "--disable=all"
        expected_error_value = EXPECTED_ERRORS[expected_error_name]
        enable = "--enable=%s" % expected_error_name
        pylint_res = self.run_pylint(self.paths_modules, [disable, enable, "--jobs=2"])
        res = self._get_messages_from_output(pylint_res)
        real_errors = {check: len(lines) for check, lines in res.items()}
        expected_errors = {expected_error_name: expected_error_value}
        self.assert_dict_equal(real_errors, expected_errors)

    @pytest.mark.parametrize("disable_error", EXPECTED_ERRORS)
    def test_160_check_only_disabled_one_check(self, disable_error):
        """Checking -d all -e odoolint -d ONLY-ONE-CHECK"""
        expected_errors = self.expected_errors.copy()
        enable = "--disable=%s" % disable_error
        pylint_res = self.run_pylint(self.paths_modules, self.default_extra_params + [enable])
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors.pop(disable_error)
        self.assert_dict_equal(real_errors, expected_errors)

    @pytest.mark.skipif(
        not dill_supports_code_objects(),
        reason="pylint parallel mode crashes since dill is not able to serialize code objects"
        " for this python version (e.g. py3.15 removed code.co_lnotab)",
    )
    @pytest.mark.parametrize("disable_error", EXPECTED_ERRORS)
    def test_162_check_only_disabled_one_check_jobs(self, disable_error):
        """Checking -d all -e odoolint -d ONLY-ONE-CHECK --jobs=2"""
        expected_errors = self.expected_errors.copy()
        enable = "--disable=%s" % disable_error
        pylint_res = self.run_pylint(self.paths_modules, self.default_extra_params + [enable, "--jobs=2"])
        res = self._get_messages_from_output(pylint_res)
        real_errors = {check: len(lines) for check, lines in res.items()}
        expected_errors.pop(disable_error)
        self.assert_dict_equal(real_errors, expected_errors)

    def test_165_no_raises_unlink(self):
        extra_params = ["--disable=all", "--enable=no-raise-unlink"]
        test_repo = os.path.join(self.root_path_modules, "test_module")

        self.assert_dict_equal(
            self.run_pylint([test_repo], extra_params).linter.stats.by_msg,
            {"no-raise-unlink": 2},
        )

        # This check is only valid for Odoo 15.0 and upwards
        extra_params.append("--valid-odoo-versions=14.0")
        assert not self.run_pylint([test_repo], extra_params).linter.stats.by_msg

    # Test category-allowed with and without error
    def test_170_category_allowed(self):
        extra_params = [
            "--disable=all",
            "--enable=category-allowed-app",
            "--category-allowed-app=Category 00",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "category-allowed-app": 1,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        expected_errors = {
            "category-allowed-app": 1,
        }
        extra_params = [
            "--disable=all",
            "--enable=category-allowed-app",
            "--category-allowed-app=Category 01",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        self.assert_dict_equal(real_errors, expected_errors)

        extra_params = [
            "--disable=all",
            "--enable=category-allowed",
            "--category-allowed=Category 00",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "category-allowed": 1,
        }
        self.assert_dict_equal(real_errors, expected_errors)

        expected_errors = {}
        extra_params = [
            "--disable=all",
            "--enable=category-allowed",
            "--category-allowed-app=Category 01",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        self.assert_dict_equal(real_errors, expected_errors)

    def test_option_odoo_deprecated_model_method(self):
        pylint_res = self.run_pylint(
            self.paths_modules,
            rcfile=os.path.abspath(
                os.path.join(
                    __file__,
                    "..",
                    "..",
                    "testing",
                    "resources",
                    ".pylintrc-odoo-deprecated-model-methods",
                )
            ),
        )

        assert 4 == pylint_res.linter.stats.by_msg["deprecated-odoo-model-method"]

    def test_175_prohibited_method_override(self):
        """Test --prohibited_override_methods parameter"""
        extra_params = [
            "--disable=all",
            "--enable=prohibited-method-override",
            "--prohibited-method-override=test_base_method_1,test_base_method_3",
        ]
        pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {
            "prohibited-method-override": 2,
        }
        self.assert_dict_equal(real_errors, expected_errors)

    @pytest.mark.skipif(
        not dill_supports_code_objects(),
        reason="pylint parallel mode crashes since dill is not able to serialize code objects"
        " for this python version (e.g. py3.15 removed code.co_lnotab)",
    )
    def test_180_jobs(self):
        """Using jobs must generate the same messages and stats than the serial mode"""
        serial_pylint_res = self.run_pylint(self.paths_modules, list(self.default_extra_params), verbose=True)
        serial_messages = self._get_messages_from_output(serial_pylint_res)

        self.default_extra_params += ["--jobs=10"]
        pylint_res = self.run_pylint(self.paths_modules, verbose=True)
        # pylint_res.linter.stats.by_msg can not be used with --jobs because of
        # an upstream issue. LinterStats.reset_message_count() does not reset by_msg
        # so each worker returns cumulative snapshots per file and merge_stats
        # over-counts them. The messages of the output are used instead
        jobs_messages = self._get_messages_from_output(pylint_res)
        real_errors = {check: len(lines) for check, lines in jobs_messages.items()}
        assert self.expected_errors == real_errors
        for check, lines in jobs_messages.items():
            duplicated_lines = [line for line, count in Counter(lines).items() if count > 1]
            assert not duplicated_lines, f"{check} duplicated. Lines {duplicated_lines}"

        serial_messages = {check: sorted(lines) for check, lines in serial_messages.items()}
        jobs_messages = {check: sorted(lines) for check, lines in jobs_messages.items()}
        assert serial_messages == jobs_messages

    def test_185_jobs_worker_paths(self):
        """Run in-process the parallel mode paths executed inside the workers
        since they are subprocesses not measured by coverage"""
        paths = [os.path.join(self.root_path_modules, "broken_module", "models", "model_inhe1.py")]
        pylint_res = self.run_pylint(paths, ["--disable=all", "--enable=consider-merging-classes-inherited"])
        linter = pylint_res.linter

        # Registering the plugin again over the same linter must be skipped
        # like in a parallel worker restoring the linter with the checkers
        checkers_before = len(list(linter.get_checkers()))
        plugin.register(linter)
        assert checkers_before == len(list(linter.get_checkers()))

        checker = next(
            checker for checker in linter.get_checkers() if isinstance(checker, plugin.checkers.odoo_addons.OdooAddons)
        )
        module_node = astroid.parse(
            "class ResCompany:\n    _inherit = 'res.company'\n\nclass ResCompany2:\n    _inherit = 'res.company'\n",
            module_name="fake_module.models.res_company",
        )
        module_node.file = os.path.join(self.root_path_modules, "fake_module", "models", "res_company.py")
        # _inherit='other.model' _name='model.name' nodes are skipped because is valid
        named_module_node = astroid.parse(
            "class ResCompanyNamed:\n    _inherit = 'res.company'\n",
            module_name="fake_module.models.res_company_named",
        )
        named_module_node.file = os.path.join(self.root_path_modules, "fake_module", "models", "res_company_named.py")
        named_module_node.odoo_attribute_name = "res.company.named"
        checker._odoo_inherit_items = defaultdict(set)
        checker._odoo_inherit_items[("fake_module/__manifest__.py", "res.company")].update(
            module_node.body + named_module_node.body
        )

        # close() must not emit partial messages in parallel mode
        linter.config.jobs = 10
        checker.close()
        assert checker._odoo_inherit_items

        data = checker.get_map_data()
        assert len(data) == 2
        assert not checker._odoo_inherit_items

        errors_before = linter.stats.by_msg.get("consider-merging-classes-inherited", 0)
        checker.reduce_map_data(linter, [data])
        errors_after = linter.stats.by_msg.get("consider-merging-classes-inherited", 0)
        assert errors_after == errors_before + 1

    def test_format_version_value_error(self):
        """Test --valid-odoo-versions to force a value error exception"""
        extra_params = [
            "--valid-odoo-versions=8.0saas",
            "--disable=all",
            "--enable=manifest-version-format",
        ]
        with pytest.warns(UserWarning) as warn:
            pylint_res = self.run_pylint(self.paths_modules, extra_params, verbose=True)
        real_errors = pylint_res.linter.stats.by_msg
        expected_errors = {"manifest-version-format": 6}
        self.assert_dict_equal(real_errors, expected_errors)
        assert any("Invalid manifest versions format ['8.0saas']" in str(w.message) for w in warn.list)

    def test_top_path(self):
        """Test the top level path is inferred from the first parent path containing a ".git" entry"""
        with TemporaryDirectory() as tmp_dir:
            repo_path = os.path.join(tmp_dir, "repo")
            module_path = os.path.join(repo_path, "module", "models")
            os.makedirs(module_path)
            os.makedirs(os.path.join(repo_path, ".git"))
            assert misc.top_path(module_path) == repo_path
            assert misc.top_path(repo_path) == repo_path
            # A child of a top level path already found re-uses it directly
            # based on the path prefix without checking ".git" again
            nested_repo_path = os.path.join(module_path, "nested_repo")
            os.makedirs(os.path.join(nested_repo_path, ".git"))
            assert misc.top_path(nested_repo_path) == repo_path
            # Without a .git parent path the top is the root/drive
            no_repo_path = os.path.join(tmp_dir, "no_repo")
            os.makedirs(no_repo_path)
            assert misc.top_path(no_repo_path) == (Path(no_repo_path).root or Path(no_repo_path).drive)

    def test_walk_up(self):
        """Test the manifest is found walking up limited by the top path"""
        with TemporaryDirectory() as tmp_dir:
            repo_path = os.path.join(tmp_dir, "repo")
            module_path = os.path.join(repo_path, "module")
            models_path = os.path.join(module_path, "models")
            os.makedirs(models_path)
            os.makedirs(os.path.join(repo_path, ".git"))
            manifest_path = os.path.join(module_path, "__manifest__.py")
            with open(manifest_path, "w", encoding="utf-8") as f_manifest:
                f_manifest.write("{}")
            top = misc.top_path(models_path)
            assert top == repo_path
            assert misc.walk_up(models_path, tuple(misc.MANIFEST_FILES), top) == manifest_path
            # A child of a parent path where the manifest was already found
            # re-uses it directly without checking the filesystem again
            wizards_path = os.path.join(module_path, "wizards")
            os.makedirs(wizards_path)
            assert misc.walk_up(wizards_path, tuple(misc.MANIFEST_FILES), top) == manifest_path
            # No manifest between the path and the top
            no_module_path = os.path.join(repo_path, "no_module")
            os.makedirs(no_module_path)
            assert misc.walk_up(no_module_path, tuple(misc.MANIFEST_FILES), top) is None

    @pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason="Windows works a little different with executable files",
    )
    def test_invalid_name_executable(self):
        """Test valid case for file name of executable-file instead of executable_file.py"""
        extra_params = [
            "--disable=all",
            "--enable=invalid-name",
        ]
        with NamedTemporaryFile(mode="w", prefix="executable-", suffix=".py") as tmp_f:
            os.chmod(tmp_f.name, os.stat(tmp_f.name).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            tmp_f.write("#!/usr/bin/env python3")
            tmp_f.flush()
            pylint_res = self.run_pylint([tmp_f.name], extra_params)
            real_errors = pylint_res.linter.stats.by_msg
            self.assert_dict_equal(
                real_errors,
                {},
                "The file is a valid executable with executable permissions, "
                "name with -, with py extension and with shebang. It should not raise the check",
            )

        with NamedTemporaryFile(mode="w", prefix="executable-") as tmp_f:
            tmp_f.write("#!/usr/bin/env python3")
            tmp_f.flush()
            pylint_res = self.run_pylint([tmp_f.name], extra_params)
            real_errors = pylint_res.linter.stats.by_msg
            self.assert_dict_equal(
                real_errors,
                {"invalid-name": 1},
                "The file doens't have executable permissions so should raise the check",
            )

        with NamedTemporaryFile(mode="w", prefix="executable-") as tmp_f:
            os.chmod(
                tmp_f.name,
                os.stat(tmp_f.name).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
            )
            tmp_f.write("#!/usr/bin/env python3")
            tmp_f.flush()
            pylint_res = self.run_pylint([tmp_f.name], extra_params)
            real_errors = pylint_res.linter.stats.by_msg
            self.assert_dict_equal(
                real_errors,
                {},
                "The file is a valid executable with executable permissions, "
                "name with -, without py extension and with shebang. It should not raise the check",
            )

    @staticmethod
    def re_replace(sub_start, sub_end, substitution, content):
        re_sub = re.compile(rf"^{re.escape(sub_start)}$.*^{re.escape(sub_end)}$", re.M | re.S)
        if not re_sub.findall(content):
            raise UserWarning("No matched content")
        substitution = substitution.replace("\\", "\\\\")
        new_content = re_sub.sub(f"{sub_start}\n\n{substitution}\n\n{sub_end}", content)
        return new_content

    def _get_messages_from_output(self, pylint_res):
        pylint_res.out.seek(0)
        all_check_errors_merged = defaultdict(list)
        for line in pylint_res.out:
            checks_found = RE_CHECK_OUTPUT.findall(line)
            if not checks_found:
                continue
            line = RE_CHECK_OUTPUT.sub("", line).strip()
            all_check_errors_merged[checks_found[0]].append(line)
        return all_check_errors_merged

    @pytest.mark.skipif(
        not os.environ.get("BUILD_README"),
        reason="BUILD_README environment variable not enabled",
    )
    def test_build_docstring(self):
        messages_content = plugin.messages2md()
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "README.md")
        with open(readme_path, encoding="UTF-8") as f_readme:
            readme_content = f_readme.read()

        new_readme = self.re_replace(
            "[//]: # (start-checks)",
            "[//]: # (end-checks)",
            messages_content,
            readme_content,
        )

        pylint_res = self.run_pylint(self.paths_modules, verbose=True)
        all_check_errors_merged = self._get_messages_from_output(pylint_res)
        check_example_content = ""
        for check_error, msgs in sorted(all_check_errors_merged.items(), key=lambda a: a[0]):
            check_example_content += f"\n\n * {check_error}\n"
            for msg in sorted(msgs)[:3]:
                msg = msg.replace(":", "#L", 1)
                check_example_content += f"\n    - https://github.com/OCA/pylint-odoo/blob/v{version}/{msg}"
        check_example_content = f"# Examples\n{check_example_content}"
        new_readme = self.re_replace(
            "[//]: # (start-example)",
            "[//]: # (end-example)",
            check_example_content,
            new_readme,
        )

        with open(readme_path, "w", encoding="UTF-8") as f_readme:
            f_readme.write(new_readme)
        assert (
            readme_content == new_readme
        ), "The README was updated! Don't panic only failing for CI purposes. Run the same test again."
