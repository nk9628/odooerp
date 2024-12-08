# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, _, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """Inheriting the sale order model to add the fields
    and revise quotation button"""

    _inherit = "sale.order"

    is_revised = fields.Boolean(
        string="Is Revised", copy=False, help="Is Order Revised"
    )
    org_sale_id = fields.Many2one(
        "sale.order", string="Origin", copy=False, help="Revised Order Origin"
    )
    rev_sale_ids = fields.One2many(
        "sale.order",
        "org_sale_id",
        string="Sales Revisions",
        copy=False,
        help="Revised Sale Orders",
    )
    rev_ord_count = fields.Integer(
        string="Revised Orders",
        help="Revised order count",
        compute="compute_rev_ord_count",
    )
    rev_confirm = fields.Boolean(
        string="Revised Confirm", copy=False, help="Is Revised Confirm"
    )

    active = fields.Boolean(default=True)

    is_active_res = fields.Boolean(default=False)

    related_orders = fields.One2many(
        comodel_name='sale.order',
        inverse_name='org_sale_id',
        string='Related Orders',
        compute='_compute_related_order_ids',
    )

    sale_order_lines = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        string='Filtered Sale Order Lines',
        compute='_compute_sale_order_lines',
    )

    @api.depends('related_orders')
    def _compute_sale_order_lines(self):
        for record in self:
            sale_order_lines = self.env['sale.order.line']
            for order in record.related_orders:
                sale_order_lines += order.order_line.filtered(
                    lambda line: line.some_condition)  # Add your condition here
            record.sale_order_lines = sale_order_lines

    @api.depends('is_revised')
    def _compute_related_order_ids(self):
        for record in self:
            record.related_orders = record.get_related_orders(record.org_sale_id or record)
            if record.org_sale_id:
                record.related_orders += self.org_sale_id
            record.related_orders -= self

    def action_revise_quotation(self):
        """Revise the current quotation."""
        if not self.org_sale_id:
            revise_name = str(self.name) + "/R" + str(len(self.rev_sale_ids) + 1)
            vals = {"name": revise_name, "org_sale_id": self.id}
            revise_quote = self.copy(default=vals)
            print("Revoking---------------->111111")
            self.is_revised = True
            self.is_active_res = True
            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "sale.order",
                "views": [(False, "form")],
                "res_id": revise_quote.id,
            }

        if not self.is_revised and self.org_sale_id:
            revise_name = str(self.org_sale_id.name) + "/R" + str(len(self.org_sale_id.rev_sale_ids) + 1)
            vals = {"name": revise_name, "org_sale_id": self.org_sale_id.id}
            revise_quote = self.copy(default=vals)
            print("Revoking---------------->22222")
            self.is_revised = True
            self.is_active_res = True
            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "sale.order",
                "views": [(False, "form")],
                "res_id": revise_quote.id,
            }


    def compute_rev_ord_count(self):
        """Compute the number of revised order of the current order."""
        for record in self:
            record.rev_ord_count = len(record.related_orders)

    def get_revised_order_lines(self):
        """Action to open the sale order lines of the related orders."""
        self.ensure_one()

        related_order_ids = self.mapped('related_orders').ids  # Retrieve IDs of related orders
        related_sale_orders = self.env['sale.order'].search([('id', 'in', related_order_ids)])
        sale_order_lines = self.env['sale.order.line'].search([('order_id', 'in', related_sale_orders.ids)])

        # Define the view ID to open
        view_id = self.env.ref('sale_quotation_revision.view_order_line_tree_custom').id

        return {
            "type": "ir.actions.act_window",
            "name": "Related Order Lines",
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "view_id": view_id,  # Use the view ID here
            "domain": [('order_id', 'in', related_sale_orders.ids)],
            # "context": {'search_default_group_order_id': 1},
            'target': 'current',
        }

    # return {
    #     'name': _('Customer'),
    #     'type': 'ir.actions.act_window',
    #     'res_model': 'res.partner',
    #     'res_id': self.partner_id.id,
    #     'view_mode': 'form',
    #     'view_id': self.env.ref('industry_fsm.view_partner_address_form_industry_fsm').id,
    #     'target': 'new',
    # }

    def get_revised_orders(self):
        """Action to open the revised order of the current order."""
        self.ensure_one()

        related_orders = self.mapped('related_orders')  # Retrieve related orders

        # Create domain to filter related orders
        domain = [("id", "in", related_orders.ids)]

        return {
            "type": "ir.actions.act_window",
            "name": "Related Orders",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "domain": domain,
            "context": {"create": False},
        }

        # def unlink(self):
        #     """Override the unlink method to restrict deletion of
        #     original sale order."""
        #     for order in self:
        #         if order.is_revised and order.rev_ord_count > 0:
        #             raise UserError(
        #                 "Cannot delete a sale order with revised orders."
        #                 " Please delete the revised orders first."
        #             )
        #     return super(SaleOrder, self).unlink()

    def action_confirm(self):
        """Override the action_confirm method to handle revised orders."""
        for order in self:
            if not order.rev_confirm:
                related_orders = order.get_related_orders(order)
                if related_orders:
                    # Exclude the original sale order from the list
                    related_orders -= order
                    wizard = self.env["sale.order.confirm.wizard"].create(
                        {
                            "order_id": order.id,
                            "sale_orders_ids": [(6, 0, related_orders.ids)],
                        }
                    )
                    return {
                        "name": "Confirm Related Sale Orders",
                        "type": "ir.actions.act_window",
                        "view_mode": "form",
                        "res_model": "sale.order.confirm.wizard",
                        "res_id": wizard.id,
                        "target": "new",
                    }
            super(SaleOrder, order).action_confirm()

    def get_related_orders(self, order):
        """Get related sale orders."""
        related_orders = order.rev_sale_ids
        if order.org_sale_id:
            related_orders += order.org_sale_id
            # Add related sale orders of order.org_sale_id
            org_related_orders = order.org_sale_id.rev_sale_ids
            related_orders += org_related_orders
        return related_orders


class SaleOrderConfirmWizard(models.TransientModel):
    _name = "sale.order.confirm.wizard"
    _description = "Confirm Sale Order Wizard"

    order_id = fields.Many2one(
        "sale.order",
        string="Sale Orders to Confirm",
        help="Select the sale orders to be conform.",
    )
    sale_orders_ids = fields.Many2many(
        "sale.order",
        string="Sale Orders to Cancel",
        help="Select the sale orders to be canceled.",
    )

    def action_rev_cancel_orders(self):
        """Method to confirm or cancel selected sale orders."""
        for wizard in self:
            wizard.order_id.rev_confirm = True
            wizard.order_id.action_confirm()
            for order in wizard.sale_orders_ids:
                order._action_cancel()
                # order.active = False
                order.is_active_res = True
        return {"type": "ir.actions.act_window_close"}

    def action_rev_keep_orders(self):
        """Method to keep related sale orders."""
        for wizard in self:
            wizard.order_id.rev_confirm = True
            wizard.order_id.action_confirm()
        return {"type": "ir.actions.act_window_close"}
