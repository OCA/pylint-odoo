[//]: # (start-badges)

[![Build Status](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/OCA/pylint-odoo/branch/main/graph/badge.svg)](https://codecov.io/gh/OCA/pylint-odoo)
[![code-style-black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/pypi/v/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![pypi-downloads-monthly](https://img.shields.io/pypi/dm/pylint-odoo.svg?style=flat)](https://pypi.python.org/pypi/pylint-odoo)
[![supported-versions](https://img.shields.io/pypi/pyversions/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![wheel](https://img.shields.io/pypi/wheel/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![commits-since](https://img.shields.io/github/commits-since/OCA/pylint-odoo/v9.3.6.svg)](https://github.com/OCA/pylint-odoo/compare/v9.3.6...main)

[//]: # (end-badges)


# Pylint Odoo plugin

Enable custom checks for Odoo modules.

[//]: # (start-checks)

Short Name | Description | Code
--- | --- | ---
attribute-deprecated | attribute "%s" deprecated | W8105
attribute-string-redundant | The attribute string is redundant. String parameter equal to name of variable | W8113
bad-builtin-groupby | Used builtin function `itertools.groupby`. Prefer `odoo.tools.groupby` instead. More info about https://github.com/odoo/odoo/issues/105376 | W8155
category-allowed | Category "%s" not allowed in manifest file. | C8114
consider-merging-classes-inherited | Consider merging classes inherited to "%s" from %s. | R8180
context-overridden | Context overridden using dict. Better using kwargs `with_context(**%s)` or `with_context(key=value)` | W8121
deprecated-name-get | 'name_get' is deprecated. Use '_compute_display_name' instead. More info at https://github.com/odoo/odoo/pull/122085. | E8146
deprecated-odoo-model-method | %s has been deprecated by Odoo. Please look for alternatives. | W8160
development-status-allowed | Manifest key development_status "%s" not allowed. Use one of: %s. | C8111
except-pass | pass into block except. If you really need to use the pass consider logging that exception | W8138
external-request-timeout | Use of external request method `%s` without timeout. It could wait for a long time | E8106
inheritable-method-lambda | Use `%s=lambda self: self.%s()` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126 | E8148
inheritable-method-string | Use string method name `"%s"` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126 | E8147
invalid-commit | Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction | E8102
license-allowed | License "%s" not allowed in manifest file. | C8105
manifest-author-string | The author key in the manifest file must be a string (with comma separated values) | E8101
manifest-behind-migrations | Manifest version (%s) is lower than migration scripts (%s) | E8145
manifest-data-duplicated | The file "%s" is duplicated in lines %s from manifest key "%s" | W8125
manifest-deprecated-key | Deprecated key "%s" in manifest file | C8103
manifest-external-assets | Asset %s should be distributed with module's source code. More info at https://httptoolkit.com/blog/public-cdn-risks/ | W8162
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
no-raise-unlink | No exceptions should be raised inside unlink() functions | E8140
no-wizard-in-models | No wizard class for model directory. See the complete structure https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#complete-structure | C8113
no-write-in-compute | Compute method calling `write`. Use `update` instead. | E8135
odoo-addons-relative-import | Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.%s" | W8150
odoo-exception-warning | `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError` | R8101
prefer-env-translation | Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844 | W8161
print-used | Print used. Use `logger` instead. | W8116
prohibited-method-override | Prohibited override of "%s" method. | W8107
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
translation-positional-used | Translation method _(%s) is using positional string printf formatting with multiple arguments. Use named placeholder `_("%%(placeholder)s")` instead. | W8120
translation-required | String parameter on "%s" requires translation. Use %s_(%s) | C8107
translation-too-few-args | Not enough arguments for odoo._ format string | E8306
translation-too-many-args | Too many arguments for odoo._ format string | E8305
translation-unsupported-format | Unsupported odoo._ format character %r (%#02x) at index %d | E8300
use-vim-comment | Use of vim comment | W8202
website-manifest-key-not-valid-uri | Website "%s" in manifest key is not a valid URI. %s | W8114


[//]: # (end-checks)


# Install

You do not need to install manually if you use pre-commit-config

But if you even need to install it

    pip install pylint-odoo

# Usage pre-commit-config.yaml

Add to your ".pre-commit-config.yaml" configuration file the following input


```yaml
    - repo: https://github.com/OCA/pylint-odoo
        rev: v9.3.6 # may be a tag or commit hash
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

Check valid only for odoo >= 18.0

   prefer-env-translation

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

# Examples


 * attribute-deprecated

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L128 attribute "_columns" deprecated
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L129 attribute "_defaults" deprecated
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L130 attribute "length" deprecated

 * attribute-string-redundant

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L196 The attribute string is redundant. String parameter equal to name of variable
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L244 The attribute string is redundant. String parameter equal to name of variable
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L254 The attribute string is redundant. String parameter equal to name of variable

 * bad-builtin-groupby

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L133 Used builtin function `itertools.groupby`. Prefer `odoo.tools.groupby` instead. More info about https://github.com/odoo/odoo/issues/105376
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L134 Used builtin function `itertools.groupby`. Prefer `odoo.tools.groupby` instead. More info about https://github.com/odoo/odoo/issues/105376

 * consider-merging-classes-inherited

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/model_inhe2.py#L11 Consider merging classes inherited to "res.company" from testing/resources/test_repo/broken_module/models/model_inhe1.py:8:4, testing/resources/test_repo/broken_module/models/model_inhe2.py:7:4.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/model_inhe2.py#L19 Consider merging classes inherited to "res.partner" from testing/resources/test_repo/broken_module/models/model_inhe2.py:15:4.

 * context-overridden

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L227 Context overridden using dict. Better using kwargs `with_context(**{'overwrite_context': True})` or `with_context(key=value)`
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L229 Context overridden using dict. Better using kwargs `with_context(**ctx)` or `with_context(key=value)`
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L231 Context overridden using dict. Better using kwargs `with_context(**ctx2)` or `with_context(key=value)`

 * deprecated-name-get

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/twelve_module/models.py#L7 'name_get' is deprecated. Use '_compute_display_name' instead. More info at https://github.com/odoo/odoo/pull/122085.

 * deprecated-odoo-model-method

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L114 fields_view_get has been deprecated by Odoo. Please look for alternatives.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/eleven_module/models.py#L17 fields_view_get has been deprecated by Odoo. Please look for alternatives.

 * development-status-allowed

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__openerp__.py#L6 Manifest key development_status "InvalidDevStatus" not allowed. Use one of: Alpha, Beta, Mature, Production/Stable.

 * except-pass

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/except_pass.py#L11 pass into block except. If you really need to use the pass consider logging that exception
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/except_pass.py#L53 pass into block except. If you really need to use the pass consider logging that exception
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/except_pass.py#L62 pass into block except. If you really need to use the pass consider logging that exception

 * external-request-timeout

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L1009 Use of external request method `smtplib.SMTP` without timeout. It could wait for a long time
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L1010 Use of external request method `smtplib.SMTP` without timeout. It could wait for a long time
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L1011 Use of external request method `smtplib.SMTP` without timeout. It could wait for a long time

 * inheritable-method-lambda

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L104 Use `default=lambda self: self._default()` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L107 Use `domain=lambda self: self._domain()` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126

 * inheritable-method-string

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L181 Use string method name `"_compute_name"` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L182 Use string method name `"_search_name"` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L183 Use string method name `"_inverse_name"` to preserve inheritability. More info at https://github.com/OCA/odoo-pre-commit-hooks/issues/126

 * invalid-commit

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L572 Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L573 Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L574 Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction

 * license-allowed

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__openerp__.py#L4 License "unknow license" not allowed in manifest file.

 * manifest-author-string

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module3/__openerp__.py#L5 The author key in the manifest file must be a string (with comma separated values)

 * manifest-behind-migrations

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__openerp__.py#L2 Manifest version (1.0) is lower than migration scripts (2.0)
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/eleven_module/__manifest__.py#L1 Manifest version (11.0.1.0.0) is lower than migration scripts (11.0.1.0.1)
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/__openerp__.py#L2 Manifest version (10.0.1.0.0) is lower than migration scripts (11.0.1.0.0)

 * manifest-data-duplicated

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L18 The file "duplicated.xml" is duplicated in lines 19 from manifest key "data"

 * manifest-deprecated-key

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L7 Deprecated key "description" in manifest file

 * manifest-external-assets

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/twelve_module/__manifest__.py#L15 Asset https://shady.cdn.com/somefile.js should be distributed with module's source code. More info at https://httptoolkit.com/blog/public-cdn-risks/
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/twelve_module/__manifest__.py#L19 Asset https://bad.idea.com/cool.css should be distributed with module's source code. More info at https://httptoolkit.com/blog/public-cdn-risks/
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/twelve_module/__manifest__.py#L20 Asset http://insecure.and.bad.idea.com/kiwi.js should be distributed with module's source code. More info at https://httptoolkit.com/blog/public-cdn-risks/

 * manifest-maintainers-list

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module3/__openerp__.py#L6 The maintainers key in the manifest file must be a list of strings

 * manifest-required-author

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L5 One of the following authors must be present in manifest: 'Odoo Community Association (OCA)'

 * manifest-required-key

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L2 Missing required key "license" in manifest file

 * manifest-version-format

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L8 Wrong Version Format "8_0.1.0.0" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0)\.\d+\.\d+\.\d+$"
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__openerp__.py#L8 Wrong Version Format "1.0" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0)\.\d+\.\d+\.\d+$"
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module3/__openerp__.py#L8 Wrong Version Format "8.0.1.0.0foo" in manifest file. Regex to match: "(4\.2|5\.0|6\.0|6\.1|7\.0|8\.0|9\.0|10\.0|11\.0|12\.0|13\.0|14\.0|15\.0|16\.0|17\.0|18\.0)\.\d+\.\d+\.\d+$"

 * method-compute

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L190 Name of compute method should start with "_compute_"

 * method-inverse

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L192 Name of inverse method should start with "_inverse_"

 * method-required-super

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L40 Missing `super` call in "copy" method.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L44 Missing `super` call in "create" method.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L48 Missing `super` call in "write" method.

 * method-search

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L191 Name of search method should start with "_search_"

 * missing-readme

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L2 Missing ./README.rst file. Template here: https://github.com/OCA/maintainer-tools/blob/master/template/module/README.rst

 * missing-return

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L24 Missing `return` (`super` is used) in method inherited_method.

 * no-raise-unlink

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/res_partner_unlink.py#L9 No exceptions should be raised inside unlink() functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/sale_order_unlink.py#L14 No exceptions should be raised inside unlink() functions

 * no-wizard-in-models

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L1056 No wizard class for model directory. See the complete structure https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#complete-structure

 * no-write-in-compute

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L137 Compute method calling `write`. Use `update` instead.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L139 Compute method calling `write`. Use `update` instead.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L142 Compute method calling `write`. Use `update` instead.

 * odoo-addons-relative-import

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L51 Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.broken_module"
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L52 Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.broken_module"
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L53 Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.broken_module"

 * odoo-exception-warning

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L10 `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError`
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L11 `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError`
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L8 `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError`

 * prefer-env-translation

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L172 Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L188 Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L354 Better using self.env._ More info at https://github.com/odoo/odoo/pull/174844

 * print-used

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/test_module/except_pass.py#L20 Print used. Use `logger` instead.

 * renamed-field-parameter

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L244 Field parameter "digits_compute" is no longer supported. Use "digits" instead.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L244 Field parameter "select" is no longer supported. Use "index" instead.

 * resource-not-exist

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L14 File "data": "file_no_exist.xml" not found.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L18 File "data": "duplicated.xml" not found.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__openerp__.py#L23 File "demo": "file_no_exist.xml" not found.

 * sql-injection

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L803 SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L805 SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L807 SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection

 * test-folder-imported

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/__init__.py#L5 Test folder imported in module broken_module
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__init__.py#L3 Test folder imported in module broken_module2
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/eleven_module/__init__.py#L3 Test folder imported in module eleven_module

 * translation-contains-variable

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L406 Translatable term in "'Variable not translatable: %s' % variable1" contains variables. Use _('Variable not translatable: %s') % variable1 instead
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L407 Translatable term in "'Variables not translatable: %s, %s' % (variable1, variable2)" contains variables. Use _('Variables not translatable: %s, %s') % (variable1, variable2) instead
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L409 Translatable term in "'Variable not translatable: %s' % variable1" contains variables. Use _('Variable not translatable: %s') % variable1 instead

 * translation-field

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L172 Translation method _("string") in fields is not necessary.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L188 Translation method _("string") in fields is not necessary.

 * translation-format-interpolation

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L415 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L416 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L479 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-format-truncated

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L681 Logging format string ends in middle of conversion specifier
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L696 Logging format string ends in middle of conversion specifier

 * translation-fstring-interpolation

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L679 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L694 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-not-lazy

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L380 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L381 Use lazy % or .format() or % formatting in odoo._ functions
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L383 Use lazy % or .format() or % formatting in odoo._ functions

 * translation-positional-used

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L407 Translation method _('Variables not translatable: %s, %s' % (variable1, variable2)) is using positional string printf formatting with multiple arguments. Use named placeholder `_("%(placeholder)s")` instead.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L410 Translation method _('Variables not translatable: %s %s' % (variable1, variable2)) is using positional string printf formatting with multiple arguments. Use named placeholder `_("%(placeholder)s")` instead.
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L413 Translation method _('Variables not translatable: %s, %s' % (variable1, variable2)) is using positional string printf formatting with multiple arguments. Use named placeholder `_("%(placeholder)s")` instead.

 * translation-required

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L357 String parameter on "message_post" requires translation. Use body=_('Body not translatable %s')
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L357 String parameter on "message_post" requires translation. Use subject=_('Subject not translatable')
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L359 String parameter on "message_post" requires translation. Use body=_('Body not translatable {}')

 * translation-too-few-args

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L677 Not enough arguments for odoo._ format string
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L692 Not enough arguments for odoo._ format string

 * translation-too-many-args

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L682 Too many arguments for odoo._ format string
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L697 Too many arguments for odoo._ format string

 * translation-unsupported-format

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L680 Unsupported odoo._ format character 'y' (0x79) at index 30
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/models/broken_model.py#L695 Unsupported odoo._ format character 'y' (0x79) at index 30

 * use-vim-comment

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module/pylint_oca_broken.py#L108 Use of vim comment

 * website-manifest-key-not-valid-uri

    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module2/__openerp__.py#L7 Website "https://odoo-community.org,https://odoo.com" in manifest key is not a valid URI. Domain 'odoo-community.org,https:' contains invalid characters
    - https://github.com/OCA/pylint-odoo/blob/v9.3.6/testing/resources/test_repo/broken_module3/__openerp__.py#L7 Website "htt://odoo-community.com" in manifest key is not a valid URI. URL needs to start with 'http[s]://'

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
