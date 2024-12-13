from odoo import exceptions, _


def util_method():
    raise exceptions.ValidationError(
        _(
            "The request to the service timed out. Please contact the author of the app.",
        )
    )
