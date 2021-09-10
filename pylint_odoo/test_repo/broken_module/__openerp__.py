# -*- coding: utf-8 -*-
{
    'name': 'Broken module for tests',
    # missing license
    'author': 'Vauxoo, Many People',  # Missing oca author
    'development_status': 'Alpha',
    'description': 'Should be a README.rst file',
    'version': '8_0.1.0.0',
    'website': 'https://odoo-community.org',
    'depends': ['base'],
    'data': [
        'model_view.xml', 'model_view2.xml', 'model_view_odoo.xml',
        'model_view_odoo2.xml',
        'file_no_exist.xml',
        'skip_xml_check.xml',
        'skip_xml_check_2.xml',
        'skip_xml_check_3.xml',
        'report.xml',
        'template1.xml',
    ],
    'demo': ['demo/duplicated_id_demo.xml', 'file_no_exist.xml'],
    'test': ['file_no_exist.yml'],
    'installable': True,
    'name': 'Duplicated value',
    'active': True,  # Deprecated active key
}
