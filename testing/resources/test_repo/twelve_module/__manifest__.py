{
    'name': 'Twelve module for tests',
    'license': 'AGPL-3',
    'author': u'Jesus, Odoo Community Association (OCA)',
    'version': '12.0.1.0.0',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    "assets": {
        "web.assets_common": [
            "twelve_module/static/nonexistent.js",
            "https://shady.cdn.com/somefile.js"
        ],
        "web.assets_frontend": [
            "/twelve_module/hypothetically/good/file.css",
            ("before", "/web/static/src/css/random.css", "https://bad.idea.com/cool.css"),
            ["prepend", "/web/static/src/js/hello.js", "http://insecure.and.bad.idea.com/kiwi.js"]
        ]
    }
}
