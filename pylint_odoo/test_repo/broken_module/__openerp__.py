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
        'file_no_exist.xml'
    ],
    'demo': ['demo/duplicated_id_demo.xml', 'file_no_exist.xml'],
    'test': ['file_no_exist.yml'],
    'installable': True,
    'name': 'Duplicated value',
    'active': True,  # Deprecated active key
}
