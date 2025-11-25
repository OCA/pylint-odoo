# coding: utf-8
"""Test file for env-ref-assigned-variable check"""

from odoo import models, fields


class EnvRefTest(models.Model):
    _name = 'env.ref.test'

    def test_bad_direct_assignment(self):
        # Should trigger warning
        Product = self.env["product.product"]
        Partner = self.env["res.partner"]
        return Product, Partner

    def test_bad_constant_assignment(self):
        # Should trigger warning
        PRODUCT_MODEL = "product.product"
        Product = self.env[PRODUCT_MODEL]
        return Product

    def test_good_direct_usage(self):
        # Should NOT trigger warning - this is the preferred pattern
        products = self.env["product.product"].search([])
        partners = self.env["res.partner"].browse([1, 2, 3])
        return products, partners

    def test_good_chained_usage(self):
        # Should NOT trigger warning
        product_name = self.env["product.product"].browse(1).name
        return product_name
