# coding: utf-8
{
    'name': 'Empty module for tests',
    'license': 'AGPL-3',
    'author': u'Moisés, Odoo Community Association (OCA), author2',
    'version': '10.0.1.0.0',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'bin': [
            'sh',
        ],
        'python': [
            'os',
        ],
    },
}
