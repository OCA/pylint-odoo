[//]: # (start-badges)

[![Build Status](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/OCA/pylint-odoo/actions/workflows/test.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/OCA/pylint-odoo/branch/main/graph/badge.svg)](https://codecov.io/gh/OCA/pylint-odoo)
[![version](https://img.shields.io/pypi/v/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![wheel](https://img.shields.io/pypi/wheel/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![supported-versions](https://img.shields.io/pypi/pyversions/pylint-odoo.svg)](https://pypi.org/project/pylint-odoo)
[![commits-since](https://img.shields.io/github/commits-since/OCA/pylint-odoo/v8.0.4.svg)](https://github.com/OCA/pylint-odoo/compare/v8.0.4...main)
[![code-style-black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[//]: # (end-badges)


# Pylint Odoo plugin

Enable custom checks for Odoo modules.

[//]: # (start-checks)

Code | Description | short name
--- | --- | ---
C8101 | One of the following authors must be present in manifest: %s | manifest-required-author
C8102 | Missing required key "%s" in manifest file | manifest-required-key
C8103 | Deprecated key "%s" in manifest file | manifest-deprecated-key
C8105 | License "%s" not allowed in manifest file. | license-allowed
C8106 | Wrong Version Format "%s" in manifest file. Regex to match: "%s" | manifest-version-format
C8107 | String parameter on "%s" requires translation. Use %s_(%s) | translation-required
C8108 | Name of compute method should start with "_compute_" | method-compute
C8109 | Name of search method should start with "_search_" | method-search
C8110 | Name of inverse method should start with "_inverse_" | method-inverse
C8111 | Manifest key development_status "%s" not allowed. Use one of: %s. | development-status-allowed
C8112 | Missing ./README.rst file. Template here: %s | missing-readme
E8101 | The author key in the manifest file must be a string (with comma separated values) | manifest-author-string
E8102 | Use of cr.commit() directly - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#never-commit-the-transaction | invalid-commit
E8103 | SQL injection risk. Use parameters if you can. - More info https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#no-sql-injection | sql-injection
E8104 | The maintainers key in the manifest file must be a list of strings | manifest-maintainers-list
E8106 | Use of external request method `%s` without timeout. It could wait for a long time | external-request-timeout
E8130 | Test folder imported in module %s | test-folder-imported
F8101 | File "%s": "%s" not found. | resource-not-exist
R8101 | `odoo.exceptions.Warning` is a deprecated alias to `odoo.exceptions.UserError` use `from odoo.exceptions import UserError` | odoo-exception-warning
R8180 | Consider merging classes inherited to "%s" from %s. | consider-merging-classes-inherited
W8103 | Translation method _("string") in fields is not necessary. | translation-field
W8105 | attribute "%s" deprecated | attribute-deprecated
W8106 | Missing `super` call in "%s" method. | method-required-super
W8110 | Missing `return` (`super` is used) in method %s. | missing-return
W8111 | Field parameter "%s" is no longer supported. Use "%s" instead. | renamed-field-parameter
W8113 | The attribute string is redundant. String parameter equal to name of variable | attribute-string-redundant
W8114 | Website "%s" in manifest key is not a valid URI | website-manifest-key-not-valid-uri
W8115 | Translatable term in "%s" contains variables. Use %s instead | translation-contains-variable
W8116 | Print used. Use `logger` instead. | print-used
W8120 | Translation method _(%s) is using positional string printf formatting. Use named placeholder `_("%%(placeholder)s")` instead. | translation-positional-used
W8121 | Context overridden using dict. Better using kwargs `with_context(**%s)` or `with_context(key=value)` | context-overridden
W8125 | The file "%s" is duplicated %d times from manifest key "%s" | manifest-data-duplicated
W8138 | pass into block except. If you really need to use the pass consider logging that exception | except-pass
W8150 | Same Odoo module absolute import. You should use relative import with "." instead of "odoo.addons.%s" | odoo-addons-relative-import
W8202 | Use of vim comment | use-vim-comment

[//]: # (end-checks)


# Install

``# pip install --upgrade git+https://github.com/oca/pylint-odoo.git``

Or

``# pip install --upgrade --pre pylint-odoo``

# Usage pre-commit-config.yaml

Add to your ".pre-commit-config.yaml" configuration file the following input


```yaml
    - repo: https://github.com/OCA/pylint-odoo
        rev: v8.0.4
        hooks:
        # Add to your .pylintrc file:
        # [MASTER]
        # load-plugins=pylint.extensions.docstyle, pylint.extensions.mccabe
        - id: pylint
```

# Usage

``pylint --load-plugins=pylint_odoo -e odoolint path/to/test``

or use configuration file (find example configuration in https://github.com/OCA/pylint-odoo/tree/master/pylint_odoo/examples/.pylintrc):

``pylint --rcfile=.pylintrc path/to/test``

Example to test just odoo-lint case:

``touch {ADDONS-PATH}/__init__.py``

``pylint --load-plugins=pylint_odoo -d all -e odoolint {ADDONS-PATH}``


[//]: # (start-example)

[//]: # (end-example)

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
