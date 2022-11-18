class MyController(odoo.http.Controller):
    @odoo.http.route('/some_url', auth='public')
    def handler(self):
        return True
