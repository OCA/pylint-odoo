{
    "name": "Lodi : Multiple product SKU's for customer invoices and xml file.",
    "summary": """product SKU's for customers""",
    "description": """
Lodi : Multiple product SKU's for customer invoices and xml file.
=================================================================
- Adds a new model to store SKU per partner and product.
- Adds SKU to invoice report if product has an specific sku for product and partner.
- Adds SKU to xml file (l10n_mx) if product has an specific sku for product and partner.

- Developer: JEFE
- Ticket ID: 2821684
        """,
    "author": "Odoo, Inc",
    "website": "https://www.odoo.com/",
    "category": "Custom Development",
    "version": "1.0.1",
    "license": "OPL-1",
    "depends": [
        "sale_management",
        "l10n_mx_edi_extended_40",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/invoice_report_templates.xml",
        "report/sale_report_templates.xml",
        "views/cfdi_views.xml",
        "views/product_partner_sku_views.xml",
        "views/product_views.xml",
    ],
}
