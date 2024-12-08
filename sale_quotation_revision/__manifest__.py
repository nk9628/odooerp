{
    "name": "Sale Quotation Revision",
    "version": "1.0",
    "category": "Sales",
    "summary": "Revise and track the history of sales orders.",
    "description": "This module helps users to create various revisions of sales order data and conveniently access all related order revisions.",
    "author": "Cybrosys Techno Solutions",
    "maintainer": "Cybrosys Techno Solutions",
    "website": "https://www.cybrosys.com",
    "depends": ["sale_management", "sale"],
    "data": [
        "security/ir.model.access.csv",
        # "views/res_config_settings_views.xml",
        "views/sale_order_views.xml"
    ],
    "images": ["static/description/banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False
}