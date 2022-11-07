[//]: # (start-badges)

[![Build Status](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/OCA/pylint-odoo/branch/main/graph/badge.svg)](https://codecov.io/gh/OCA/pylint-odoo)
[![code-style-black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![pypi-downloads-monthly](https://img.shields.io/pypi/dm/pylint-odoo.svg?style=flat)](https://pypi.python.org/pypi/pylint-odoo)
[![supported-versions](https://img.shields.io/pypi/pyversions/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![wheel](https://img.shields.io/pypi/wheel/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![commits-since](https://img.shields.io/github/commits-since/OCA/pylint-odoo/v8.0.14.svg)](https://github.com/OCA/pylint-odoo/compare/v8.0.14...main)

[//]: # (end-badges)


# Pylint Odoo plugin

Enable custom checks for Odoo modules.

[//]: # (start-checks)

Short Name | Description | Code
--- | --- | ---
attribute-deprecated | attribute "%s" deprecated | W8105
attribute-string-redundant | The attribute string is redundant. String parameter equal to name of variable | W8113
consider-merging-classes-inherited | Consider merging classes inherited to "%s" from %s. | R8180
context-overridden | Context overridden using dict. Better using kwargs `with_context(**%s)` or `with_context(key=value)` | W8121
development-status-allowed | Manifest key development_status "%s" not allowed. Use one of: %s. | C8111
except-pass | pass into block except. If you really need to use the pass consider logging that exception | W8138
external-request-timeout | Use of external request method `%s` without timeout. It could wait for a long time | E8106
invalid-commit | Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction | E8102
license-allowed | License "%s" not allowed in manifest file. | C8105
manifest-author-string | The author key in the manifest file must be a string (with comma separated values) | E8101
manifest-data-duplicated | The file "%s" is duplicated in lines %s from manifest key "%s" | W8125
manifest-deprecated-key | Deprecated key "%s" in manifest file | C8103
manifest-maintainers-list | The maintainers key in the manifest file must be a list of strings | E8104
manifest-required-author | One of the following authors must be present in manifest: %s | C8101
manifest-required-key | Missing required key "%s" in manifest file | C8102
manifest-version-format | Wrong Version Format "%s" in manifest file. Regex to match: "%s" | C8106
method-compute | Name of compute method should start with "_compute_" | C8108
method-inverse | Name of inverse method should start with "_inverse_" | C8110
method-required-super | Missing `super` call in "%s" method. | W8106
method-search | Name of search method should start with "_search_" | C8109
missing-readme | Missing ./README.rst file. Template here: %s | C8112
missing-return | Missing `return` (`super` is used) in method %s. | W8110
no-wizard-in-models | No wizard class for model directory. See the complete structure https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#complete-structure | C8113
no-write-in-compute | Compute method calling `write`. Use `update` instead. | E8135
odoo-addons-relative-import | Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.%s" | W8150
odoo-exception-warning | `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError` | R8101
print-used | Print used. Use `logger` instead. | W8116
renamed-field-parameter | Field parameter "%s" is no longer supported. Use "%s" instead. | W8111
resource-not-exist | File "%s": "%s" not found. | F8101
sql-injection | SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection | E8103
test-folder-imported | Test folder imported in module %s | E8130
translation-contains-variable | Translatable term in "%s" contains variables. Use %s instead | W8115
translation-field | Translation method _("string") in fields is not necessary. | W8103
translation-format-interpolation | Use %s formatting in odoo._ functions | W8302
translation-format-truncated | Logging format string ends in middle of conversion specifier | E8301
translation-fstring-interpolation | Use %s formatting in odoo._ functions | W8303
translation-not-lazy | Use %s formatting in odoo._ functions | W8301
translation-positional-used | Translation method _(%s) is using positional string printf formatting. Use named placeholder `_("%%(placeholder)s")` instead. | W8120
translation-required | String parameter on "%s" requires translation. Use %s_(%s) | C8107
translation-too-few-args | Not enough arguments for odoo._ format string | E8306
translation-too-many-args | Too many arguments for odoo._ format string | E8305
translation-unsupported-format | Unsupported odoo._ format character %r (%#02x) at index %d | E8300
use-vim-comment | Use of vim comment | W8202
website-manifest-key-not-valid-uri | Website "%s" in manifest key is not a valid URI | W8114


[//]: # (end-checks)


# Install

You do not need to install manually if you use pre-commit-config

But if you even need to install it

    pip install pylint-odoo

# Usage pre-commit-config.yaml

Add to your ".pre-commit-config.yaml" configuration file the following input


```yaml
    - repo: https://github.com/OCA/pylint-odoo
        rev: v8.0.14
        hooks:
        # Add to your .pylintrc file:
        # [MASTER]
        # load-plugins=pylint_odoo
        - id: pylint
```

# Usage

    pylint --load-plugins=pylint_odoo -e odoolint path/to/test

or use configuration file you can generate the OCA one using the following template repository:

    https://github.com/OCA/oca-addons-repo-template

Then running

    pylint --rcfile=.pylintrc path/to/test


Example to test only pylint_odoo checks:

    pylint --load-plugins=pylint_odoo -d all -e odoolint {ADDONS-PATH}/*

There are checks only valid for a particular Odoo version
To know what version of odoo are you running pylint needs the parameter

    pylint --load-plugins=pylint_odoo --valid_odoo_versions={YOUR_ODOO_VERSION}

with particular odoo version e.g. `"16.0"`

Checks valid only for odoo >= 14.0

    translation-format-interpolation
    translation-format-truncated
    translation-fstring-interpolation
    translation-not-lazy
    translation-too-few-args
    translation-too-many-args
    translation-unsupported-format

Checks valid only for odoo <= 13.0

    translation-contains-variable


[//]: # (start-example)

[//]: # (end-example)

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
