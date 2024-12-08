# -*- coding: utf-8 -*-
from odoo import _, api, fields, tools, models, SUPERUSER_ID
from odoo.fields import Command
from num2words import num2words
import logging
from datetime import datetime


import ast



class account_journal(models.Model):
    _inherit = "account.journal"

    import ast

    def open_action(self):
        """Return action based on type for related journals"""
        self.ensure_one()
        action_name = self._select_action_to_open()

        # Set 'account.' prefix if missing.
        if not action_name.startswith("account."):
            action_name = 'account.%s' % action_name

        action = self.env["ir.actions.act_window"]._for_xml_id(action_name)

        context = self._context.copy()
        if 'context' in action and isinstance(action['context'], str):
            try:
                context.update(ast.literal_eval(action['context']))
            except ValueError:
                # Handle the error gracefully
                pass
        else:
            context.update(action.get('context', {}))
        action['context'] = context
        action['context'].update({
            'default_journal_id': self.id,
        })
        domain_type_field = action[
                                'res_model'] == 'account.move.line' and 'move_id.move_type' or 'move_type'  # The model can be either account.move or account.move.line

        # Override the domain only if the action was not explicitly specified in order to keep the
        # original action domain.
        if action.get('domain') and isinstance(action['domain'], str):
            try:
                action['domain'] = ast.literal_eval(action['domain'] or '[]')
            except ValueError:
                # Handle the error gracefully
                action['domain'] = []

        if not self._context.get('action_name'):
            if self.type == 'sale':
                action['domain'] = [(domain_type_field, 'in', ('out_invoice', 'out_refund', 'out_receipt'))]
            elif self.type == 'purchase':
                action['domain'] = [(domain_type_field, 'in', ('in_invoice', 'in_refund', 'in_receipt', 'entry'))]

        action['domain'] = (action['domain'] or []) + [('journal_id', '=', self.id)]
        return action
    
    
class SaleAdvancePaymentInvCustom(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    payment_name = fields.Char(string="Payment Name", default=lambda self: self._default_payment_name())

    advance_payment_method = fields.Selection(
        selection=[
            ('delivered', "Regular invoice"),
            ('percentage', "Down payment (percentage)"),
            ('fixed', "Down payment (fixed amount)"),
        ],
        string="Create Invoice",
        default='percentage',
        required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing,"
             "according to their invoicing policy (based on ordered or delivered quantity).")

    def _default_payment_name(self):
        if self.advance_payment_method == 'percentage' or self.advance_payment_method == 'fixed':
            return _("Down payment of %s%% on %s") % (self.amount, datetime.now().strftime("%d-%m-%Y"))
        else:
            return _('Down Payment')


    def _get_down_payment_description(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage' or self.advance_payment_method == 'fixed':
            name = self.payment_name
        else:
            name = _('Down Payment')
        del context
        return name

class res_partner(models.Model):
    _inherit = 'res.partner'

    cutom_total_invoiced = fields.Monetary(compute='_invoice_total_cutom', string="Total Invoiced")

    def _invoice_total_cutom(self):
        for rec in self:
            total_amount = 0
            user = self.env.user
            domain = None
            all_child = rec.with_context(active_test=False).search([('id', 'child_of', self.ids)])
            if rec.env.user.has_group('account.group_account_manager'):
                domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                          ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

            elif rec.env.user.has_group('account_consolidation.group_consolidation_user'):
                domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                          ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

            elif rec.env.user.has_group('account.group_account_user'):
                domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                          ('create_uid', '=', user.id), ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

            else:
                domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                          ('create_uid', '=', user.id), ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

            amount_ids = rec.env['account.move'].search(domain)
            total_amount = sum(amount_ids.mapped('amount_total'))
            rec.cutom_total_invoiced = total_amount

    def custom_action_view_partner_invoices(self):
        self.ensure_one()
        user = self.env.user
        domain = None

        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        if self.env.user.has_group('account.group_account_manager'):
            domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                      ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

        elif self.env.user.has_group('account_consolidation.group_consolidation_user'):
            domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                      ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

        elif self.env.user.has_group('account.group_account_user'):
            domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                      ('create_uid', '=', user.id), ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

        else:
            domain = [('company_id', '=', self.env.company.id), ('move_type', '=', 'out_invoice'),
                      ('create_uid', '=', user.id), ('state', '=', 'posted'), ('partner_id', 'in', all_child.ids)]

        action['domain'] = domain


        # action['domain'] = [
        #     ('move_type', 'in', ('out_invoice', 'out_refund')),
        #     ('partner_id', 'in', all_child.ids)
        # ]
        action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale',
                             'search_default_unpaid': 1}
        return action


