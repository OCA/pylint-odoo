# -*- coding: utf-8 -*-
{
    'name': 'Broken module for tests',
    # missing license
    'author': 'Many People',  # Missing oca author
    'description': 'Should be a README.rst file',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'model_view.xml', 'model_view2.xml', 'model_view_odoo.xml',
        'model_view_odoo2.xml',
    ],
    'demo': ['demo/duplicated_id_demo.xml'],
    'test': ['test.yml'],
    'installable': True,
    'name': 'Duplicated value',
    'active': True,  # Deprecated active key
}
