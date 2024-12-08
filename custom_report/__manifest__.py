{
    'name': "Custom Report",
    'summary': """Custom Report""",
    'description': """Custom Report""",
    'author': "Egel Software",
    'website': "www.egel.in",
    'category': 'Uncategorized',
    'version': '0.1.0',
    "license": "LGPL-3",
    'depends': ['sale_management', 'sale_pdf_quote_builder', 'account_accountant', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'report/ir_actions_report.xml',
        'report/custom_layout.xml',
        'report/payment_receipt_report.xml',
        'report/sale_order_reprot.xml',
        'report/tax_invoice_report.xml',
        'report/purchase_order_report.xml',
        'views/res_company.xml',
        'views/sale_order_views.xml',
        'views/account.xml'
    ],
    'application': False,
    'auto_install': True,
}
