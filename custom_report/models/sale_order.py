# -*- coding: utf-8 -*-
from odoo import _, api, fields, tools, models, SUPERUSER_ID
from odoo.fields import Command
from num2words import num2words
import logging
from odoo import SUPERUSER_ID




class AccountMove(models.Model):
    _inherit = 'account.move'

    show_section = fields.Boolean("Show Section", default=True)
    show_subject = fields.Boolean("Show Subject", default=True)
    show_prepared = fields.Boolean("Show Prepared By", default=True)
    show_approved = fields.Boolean("Show Approved By", default=True)
    show_project = fields.Boolean("Show Project", default=True)
    creation_account = fields.Boolean("Creation Account", default=True)
    stamp_signature = fields.Boolean("Stamp Signature", default=True)
    name_signature = fields.Boolean("Name Signature", default=True)
    show_description = fields.Boolean("Show Description", default=True)
    show_qty = fields.Boolean("Show Quantity", default=True)
    show_rate = fields.Boolean("Show Rate", default=True)
    show_amount = fields.Boolean("Show Amount", default=True)
    show_taxes = fields.Boolean("Show Taxes", default=False)
    show_slno = fields.Boolean("Show Sl NO", compute="_compute_show_slno")
    cus_signature = fields.Boolean("Signature", default=True)
    show_discount = fields.Boolean("Show Discount", default=True)
    cust_section = fields.Many2one('custom.section', "Section")
    greeting_text = fields.Text("Greeting Text")
    subject = fields.Many2one('custom.subject', "Subject")
    project = fields.Many2one('custom.project', "Project")
    acc_name = fields.Many2one('custom.account', "Account Name")
    bank_details = fields.Text("Bank Details")
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sale Order", compute='_compute_sale_order_id',
                                    store=True)

    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_sale_order_id(self):
        for rec in self:
            rec.sale_order_id = rec.mapped('invoice_line_ids.sale_line_ids.order_id')[:1]


    @api.onchange('acc_name')
    def onchange_account_name(self):
        if self.acc_name:
            self.bank_details = (
                'Account Name : ' + str(self.acc_name.acc_name or '') + '\n' +
                'Bank Name : ' + str(self.acc_name.bank_name or '') + '\n' +
                'Account Number : ' + str(self.acc_name.acc_number or '') + '\n' +
                'IBAN : ' + str(self.acc_name.acc_iban or '')
            )

    @api.model
    def get_service_product_total(self, move):
        total = 0
        for line in move.invoice_line_ids:
            if line.product_id.type == 'service':
                total += line.price_total
        return total

    @api.depends('show_description', 'show_qty', 'show_rate', 'show_amount')
    def _compute_show_slno(self):
        for rec in self:
            if rec.show_description or rec.show_qty or rec.show_rate or rec.show_amount:
                rec.show_slno = True
            else:
                rec.show_slno = False

    invoice_line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string='Invoice lines',
        copy=False,
        domain=[('display_type', 'in', ('product', 'line_section', 'line_note')),
                ('quantity', '>', 0)],
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_section = fields.Boolean("Show Section", default=True)
    show_subject = fields.Boolean("Show Subject", default=True)
    show_prepared = fields.Boolean("Show Prepared By", default=True)
    show_approved = fields.Boolean("Show Approved By", default=True)
    creation_account = fields.Boolean("Creation Account", default=True)
    stamp_signature = fields.Boolean("Stamp Signature", default=True)
    name_signature = fields.Boolean("Name Signature", default=True)
    show_project = fields.Boolean("Show Project", default=True)
    show_description = fields.Boolean("Show Description", default=True)
    show_qty = fields.Boolean("Show Quantity", default=True)
    show_rate = fields.Boolean("Show Rate", default=True)
    show_amount = fields.Boolean("Show Amount", default=True)
    show_taxes = fields.Boolean("Show Taxes", default=False)
    show_slno = fields.Boolean("Show Sl NO", compute="_compute_show_slno")
    show_discount = fields.Boolean("Show Discount", default=True)
    cust_section = fields.Many2one('custom.section', "Section")
    greeting_text = fields.Text("Greeting Text")
    subject = fields.Many2one('custom.subject', "Subject")
    project = fields.Many2one('custom.project', "Project")
    acc_name = fields.Many2one('custom.account', "Account Name")
    bank_details = fields.Text("Bank Details")
    cus_signature = fields.Boolean("Signature", default=True)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['subject'] = self.subject.id
        invoice_vals['project'] = self.project.id
        invoice_vals['cust_section'] = self.cust_section.id
        return invoice_vals

    


    @api.model
    def get_service_products_total(self, order):
        total = 0
        for line in order.order_line:
            if line.product_id.type == 'service':
                total += line.price_total
        return total

    @api.onchange('acc_name')
    def onchange_account_name(self):
        if self.acc_name:
            self.bank_details = (
                'Account Name : ' + str(self.acc_name.acc_name or '') + '\n' +
                'Bank Name : ' + str(self.acc_name.bank_name or '') + '\n' +
                'Account Number : ' + str(self.acc_name.acc_number or '') + '\n' +
                'IBAN : ' + str(self.acc_name.acc_iban or '')
            )

    @api.depends('show_description', 'show_qty', 'show_rate', 'show_amount')
    def _compute_show_slno(self):
        for rec in self:
            if rec.show_description or rec.show_qty or rec.show_rate or rec.show_amount:
                rec.show_slno = True
            else:
                rec.show_slno = False


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    show_section = fields.Boolean("Show Section", default=True)
    show_subject = fields.Boolean("Show Subject", default=True)
    show_prepared = fields.Boolean("Show Prepared By", default=True)
    show_approved = fields.Boolean("Show Approved By", default=True)
    show_project = fields.Boolean("Show Project", default=True)
    show_description = fields.Boolean("Show Description", default=True)
    show_qty = fields.Boolean("Show Quantity", default=True)
    show_rate = fields.Boolean("Show Rate", default=True)
    show_amount = fields.Boolean("Show Amount", default=True)
    show_taxes = fields.Boolean("Show Taxes", default=False)
    show_slno = fields.Boolean("Show Sl NO", compute="_compute_show_slno")
    show_discount = fields.Boolean("Show Discount", default=True)
    cust_section = fields.Many2one('custom.section', "Section")
    greeting_text = fields.Text("Greeting Text")
    subject = fields.Many2one('custom.subject', "Subject")
    project = fields.Many2one('custom.project', "Project")
    acc_name = fields.Many2one('custom.account', "Account Name")
    bank_details = fields.Text("Bank Details")
    cus_signature = fields.Boolean("Signature", default=True)
    creation_account = fields.Boolean("Creation Account", default=True)

    @api.model
    def get_service_product_total(self, order):
        total = 0
        for line in order.order_line:
            if line.product_id.type == 'service':
                total += line.price_total
        return total

    @api.onchange('acc_name')
    def onchange_account_name(self):
        if self.acc_name:
            self.bank_details = (
                'Account Name : ' + str(self.acc_name.acc_name or '') + '\n' +
                'Bank Name : ' + str(self.acc_name.bank_name or '') + '\n' +
                'Account Number : ' + str(self.acc_name.acc_number or '') + '\n' +
                'IBAN : ' + str(self.acc_name.acc_iban or '')
            )

    @api.depends('show_description', 'show_qty', 'show_rate', 'show_amount')
    def _compute_show_slno(self):
        for rec in self:
            if rec.show_description or rec.show_qty or rec.show_rate or rec.show_amount:
                rec.show_slno = True
            else:
                rec.show_slno = False


class CustomSection(models.Model):
    _name = 'custom.section'
    _description = "Section"
    _rec_name = "name"

    name = fields.Char("Name")


class CustomSubject(models.Model):
    _name = 'custom.subject'
    _description = "Subject"
    _rec_name = "name"

    name = fields.Char("Name")


class CustomProject(models.Model):
    _name = 'custom.project'
    _description = "Project"
    _rec_name = "name"

    customer_id = fields.Char(string='Customer')
    customer_street = fields.Char(string="Street")
    customer_city = fields.Char(string="City")
    customer_zip = fields.Char(string="ZIP")
    customer_state_id = fields.Many2one('res.country.state', string="State")
    customer_country_id = fields.Many2one('res.country', string="Country")

    name = fields.Char("Name")
    image = fields.Image("Image")

    invoice_ids = fields.One2many('account.move', 'project', check_company=True)
    sale_ids = fields.One2many('sale.order', 'project', check_company=True)
    purchase_ids = fields.One2many('purchase.order', 'project', check_company=True)

    invoice_count = fields.Integer("Invoice Count", compute='_compute_invoice_count')
    vendor_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_vendor_bill_count')
    sale_count = fields.Integer("Sale Count", compute='_compute_sale_count')
    purchase_count = fields.Integer("Purchase Count", compute='_compute_purchase_count')
    due_amount = fields.Float(string='Due Amount', compute='_compute_due_amount')

    def view_due_amount(self):
        pass

    @api.depends('invoice_ids')
    def _compute_due_amount(self):
        for record in self:
            customer_invoices_total = sum(
                inv.amount_total for inv in record.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice'))
            vendor_bills_total = sum(
                inv.amount_total for inv in record.invoice_ids.filtered(lambda inv: inv.move_type == 'in_invoice'))
            record.due_amount = customer_invoices_total - vendor_bills_total

    def action_view_invoice(self):
        user = self.env.user
        domain = None

        if self.env.user.has_group('account.group_account_manager'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('account_consolidation.group_consolidation_user'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('account.group_account_user'):
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        else:
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('account.view_out_invoice_tree').id, 'tree'),
                      (False, 'form')],
            'res_model': 'account.move',
            'domain': domain,
            'context': {'move_type': 'out_invoice', 'create': False},
            'type': 'ir.actions.act_window',
        }


    def action_view_vendor_bill(self):
        user = self.env.user
        domain = None

        if self.env.user.has_group('account.group_account_manager'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('account_consolidation.group_consolidation_user'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('account.group_account_user'):
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        else:
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        return {
            'name': _('Vendor Bill'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('account.view_out_invoice_tree').id, 'tree'),
                      (False, 'form')],
            'res_model': 'account.move',
            'domain': domain,
            'context': {'move_type': 'in_invoice', 'create': False},
            'type': 'ir.actions.act_window',
        }

    def action_view_sale_orders(self):
        user = self.env.user
        domain = None

        if self.env.user.has_group('sales_team.group_sale_manager'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('sales_team.group_sale_salesman'):
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        else:
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]
        return {
            'name': _('Sale Orders'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('sale.view_quotation_tree_with_onboarding').id, 'tree'),
                      (False, 'form')],
            'res_model': 'sale.order',
            'domain': domain,
            'context': {'create': False},
            'type': 'ir.actions.act_window',
        }

    def action_view_purchase_orders(self):
        user = self.env.user
        domain = None

        if self.env.user.has_group('purchase.group_purchase_manager'):
            domain = [('project', '=', self.id)]

        elif self.env.user.has_group('purchase.group_purchase_user'):
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]

        else:
            domain = [('project', '=', self.id), ('user_id', '=', user.id)]


        return {
            'name': _('Purchase Orders'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('purchase.purchase_order_kpis_tree').id, 'tree'),
                      (False, 'form')],
            'res_model': 'purchase.order',
            'domain': domain,
            'context': {'create': False},
            'type': 'ir.actions.act_window',
        }

    # Compute methods
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice'))

    @api.depends('invoice_ids')
    def _compute_vendor_bill_count(self):
        for record in self:
            record.vendor_bill_count = len(record.invoice_ids.filtered(lambda inv: inv.move_type == 'in_invoice'))

    @api.depends('sale_ids')
    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.sale_ids)

    @api.depends('purchase_ids')
    def _compute_purchase_count(self):
        for record in self:
            record.purchase_count = len(record.purchase_ids)




class CustomAccount(models.Model):
    _name = 'custom.account'
    _description = "Account"
    _rec_name = "acc_name"

    acc_name = fields.Char("Account Name")
    bank_name = fields.Char("Bank Name")
    acc_number = fields.Char("Account No")
    acc_iban = fields.Char("IBAN")


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        self.ensure_one()
        if self.advance_payment_method == 'delivered':
            return sale_orders._create_invoices(final=self.deduct_down_payments, grouped=not self.consolidated_billing)
        else:
            self.sale_order_ids.ensure_one()
            self = self.with_company(self.company_id)
            order = self.sale_order_ids

            # Create deposit product if necessary
            if not self.product_id:
                self.company_id.sale_down_payment_product_id = self.env['product.product'].create(
                    self._prepare_down_payment_product_values()
                )
                self._compute_product_id()

            # Create down payment section if necessary
            SaleOrderline = self.env['sale.order.line'].with_context(sale_no_log_for_new_lines=True)
            if not any(line.display_type and line.is_downpayment for line in order.order_line):
                SaleOrderline.create(
                    self._prepare_down_payment_section_values(order)
                )

            down_payment_lines = SaleOrderline.create(
                self._prepare_down_payment_lines_values(order)
            )

            invoice = self.env['account.move'].sudo().create(
                self._prepare_invoice_values(order, down_payment_lines)
            ).with_user(self.env.uid)  # Unsudo the invoice after creation

            sale_order_lines = self.env['sale.order.line'].search([
                ('order_id', '=', order.id),
                ('product_id.type', '!=', 'service')
            ])
            for line in sale_order_lines:
                self.env['account.move.line'].create({
                    'move_id': invoice.id,
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'quantity': 0.0,
                })

            if self.advance_payment_method == 'fixed':
                delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
                if not order.currency_id.is_zero(delta_amount):
                    receivable_line = invoice.line_ids\
                        .filtered(lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                    product_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.display_type == 'product')
                    tax_lines = invoice.line_ids\
                        .filtered(lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))

                    if product_lines and tax_lines and receivable_line:
                        line_commands = [Command.update(receivable_line.id, {
                            'amount_currency': receivable_line.amount_currency + delta_amount,
                        })]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                            (product_lines, 'price_total', -1),
                            (tax_lines, 'amount_currency', 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if order.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                    break
                                amt = delta_sign * max(
                                    order.currency_id.rounding,
                                    abs(order.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                        invoice.line_ids = line_commands

            poster = self.env.user._is_internal() and self.env.user.id or SUPERUSER_ID
            invoice.with_user(poster).message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': invoice, 'origin': order},
                subtype_xmlid='mail.mt_note',
            )

            title = _("Down payment invoice")
            order.with_user(poster).message_post(
                body=_("%s has been created", invoice._get_html_link(title=title)),
            )

            return invoice


class ResUsers(models.Model):
    _inherit = "res.users"

    custom_signature = fields.Binary(string="Image Signature")


class ResCurrency(models.Model):

    _inherit = "res.currency"

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang = tools.get_lang(self.env)
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=self.currency_unit_label,
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + _('and') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word=self.currency_subunit_label,
            )

        amount_words += ' Only'
        return  "(" +amount_words+ ")"