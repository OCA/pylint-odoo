[//]: # (start-badges)

[![Build Status](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/OCA/pylint-odoo/branch/main/graph/badge.svg)](https://codecov.io/gh/OCA/pylint-odoo)
[![code-style-black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![pypi-downloads-monthly](https://img.shields.io/pypi/dm/pylint-odoo.svg?style=flat)](https://pypi.python.org/pypi/pylint-odoo)
[![supported-versions](https://img.shields.io/pypi/pyversions/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![wheel](https://img.shields.io/pypi/wheel/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![commits-since](https://img.shields.io/github/commits-since/OCA/pylint-odoo/v10.0.9.svg)](https://github.com/OCA/pylint-odoo/compare/v10.0.9...main)

[//]: # (end-badges)


# Pylint Odoo plugin

Enable custom checks for Odoo modules.

[//]: # (start-checks)

Short Name | Description | Code
--- | --- | ---
category-allowed | Category "%s" not allowed in manifest file. | C8114
category-allowed-app | Category "%s" not allowed in manifest file for modules with price. | C8117
consider-merging-classes-inherited | Consider merging classes inherited to "%s" from %s. | R8180
manifest-behind-migrations | Manifest version (%s) is lower than migration scripts (%s) | E8145
manifest-required-key-app | Missing required key "%s" in manifest file for modules with price. | C8119
manifest-version-format | Wrong Version Format "%s" in manifest file. Regex to match: "%s" | C8106
missing-odoo-file | Missing %s file | C8115
missing-odoo-file-app | Missing %s file for modules with price | C8118
prohibited-method-override | Prohibited override of "%s" method. | W8107
translation-format-interpolation | Use %s formatting in odoo._ functions | W8302
translation-format-truncated | Logging format string ends in middle of conversion specifier | E8301
translation-fstring-interpolation | Use %s formatting in odoo._ functions | W8303
translation-not-lazy | Use %s formatting in odoo._ functions | W8301
translation-too-few-args | Not enough arguments for odoo._ format string | E8306
translation-too-many-args | Too many arguments for odoo._ format string | E8305
translation-unsupported-format | Unsupported odoo._ format character %r (%#02x) at index %d | E8300


[//]: # (end-checks)


# Install

You do not need to install manually if you use pre-commit-config

But if you even need to install it

    pip install pylint-odoo

# Usage pre-commit-config.yaml

Add to your ".pre-commit-config.yaml" configuration file the following input


```yaml
    - repo: https://github.com/OCA/pylint-odoo
        rev: v10.0.9 # may be a tag or commit hash
        hooks:
        # Add to your .pylintrc file:
        # [MASTER]
        # load-plugins=pylint_odoo
        - id: pylint_odoo
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

    pylint --load-plugins=pylint_odoo --valid-odoo-versions={YOUR_ODOO_VERSION}

with particular odoo version e.g. `"16.0"`

Checks valid only for odoo >= 14.0

    translation-format-interpolation
    translation-format-truncated
    translation-fstring-interpolation
    translation-not-lazy
    translation-too-few-args
    translation-too-many-args
    translation-unsupported-format


[//]: # (start-example)

# Examples


 * category-allowed-app

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/__openerp__.py#L6 Category "No valid for odoo.com/apps" not allowed in manifest file for modules with price.

 * consider-merging-classes-inherited

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/model_inhe2.py#L11 Consider merging classes inherited to "res.company" from testing/resources/test_repo/broken_module/models/model_inhe1.py:8:4, testing/resources/test_repo/broken_module/models/model_inhe2.py:7:4.
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/model_inhe2.py#L19 Consider merging classes inherited to "res.partner" from testing/resources/test_repo/broken_module/models/model_inhe2.py:15:4.
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/model_inhe2.py#L56 Consider merging classes inherited to "stock.warehouse.orderpoint" from testing/resources/test_repo/broken_module/models/model_inhe1.py:19:4.

 * manifest-behind-migrations

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module2/__openerp__.py#L2 Manifest version (1.0) is lower than migration scripts (2.0)
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/eleven_module/__manifest__.py#L1 Manifest version (11.0.1.0.0) is lower than migration scripts (11.0.1.0.1)
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/test_module/__openerp__.py#L2 Manifest version (10.0.1.0.0) is lower than migration scripts (11.0.1.0.0)

 * manifest-required-key-app

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/app_module/__manifest__.py#L1 Missing required key "currency" in manifest file for modules with price.
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/app_module/__manifest__.py#L1 Missing required key "images" in manifest file for modules with price.
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/__openerp__.py#L2 Missing required key "currency" in manifest file for modules with price.

 * manifest-version-format

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/__openerp__.py#L10 Wrong Version Format "8_0.1.0.0" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0|19\.0|20\.0)\.\d+\.\d+\.\d+$"
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module2/__openerp__.py#L10 Wrong Version Format "1.0" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0|19\.0|20\.0)\.\d+\.\d+\.\d+$"
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module3/__openerp__.py#L8 Wrong Version Format "8.0.1.0.0foo" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0|19\.0|20\.0)\.\d+\.\d+\.\d+$"

 * missing-odoo-file-app

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/__openerp__.py#L2 Missing broken_module/static/description/index.html file for modules with price

 * translation-format-interpolation

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L473 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L481 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L506 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-format-truncated

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L774 Logging format string ends in middle of conversion specifier
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L789 Logging format string ends in middle of conversion specifier

 * translation-fstring-interpolation

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L268 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L772 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L787 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-not-lazy

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L471 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L472 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L474 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-too-few-args

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L770 Not enough arguments for odoo._ format string
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L785 Not enough arguments for odoo._ format string

 * translation-too-many-args

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L775 Too many arguments for odoo._ format string
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L790 Too many arguments for odoo._ format string

 * translation-unsupported-format

    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L773 Unsupported odoo._ format character 'y' (0x79) at index 30
    - https://github.com/OCA/pylint-odoo/blob/v10.0.9/testing/resources/test_repo/broken_module/models/broken_model.py#L788 Unsupported odoo._ format character 'y' (0x79) at index 30

[//]: # (end-example)

# Development

To run all the tests run:

    tox

Use extra parameters to change the test behaviour

e.g. particular python version

    tox -e py310

e.g. particular unittest method

    tox -e py310 -- -k test_20_expected_errors

e.g. all the tests at the same time in parallel

    tox -p auto

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
