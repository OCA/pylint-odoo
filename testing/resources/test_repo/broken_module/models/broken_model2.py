# pylint:disable=prefer-env-translation
from markupsafe import Markup

from odoo import _, models


class TestModel4(models.Model):
    def my_method1411(self):
        Markup(_("Unsafe translated markup %(param1)s", param1=self.name))
        Markup(_("Unsafe translated markup"))
        Markup(self.env._("Unsafe env translated markup %(param1)s", param1=self.name))
        Markup(self.env._("Unsafe aggressive lt translated markup"))
        Markup("Safe translated markup %(param1)s") % {"param1": _("Translated")}
