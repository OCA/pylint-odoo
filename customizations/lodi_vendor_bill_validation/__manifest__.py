{
    "name": "Lodi : Vendor bill XML validation",
    "summary": """Vendor bill validation""",
    "description": """
Lodi : Vendor bill XML validation
=================================
Adds a wizard to import xml files of bills to create and validate them as a bill in Odoo.
It validates status of the bill with SAT.

:Developer: JEFE
:Ticket ID: 2842360
        """,
    "author": "Odoo PS",
    "website": "https://www.odoo.com/",
    "category": "Custom Development",
    "version": "1.0.0",
    "license": "OPL-1",
    "depends": [
        "account",
        "l10n_mx_edi",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/account_tax_views.xml",
        "views/res_partner_views.xml",
        "wizard/vendor_bill_attachment_wizard_views.xml",
    ],
}
