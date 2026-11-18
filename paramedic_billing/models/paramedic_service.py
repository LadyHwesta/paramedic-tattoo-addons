# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ParamedicService(models.Model):
    _inherit = "paramedic.service"

    product_id = fields.Many2one(
        "product.product", string="Billed As", ondelete="restrict",
        domain=[("type", "=", "service")],
        help="The product this service is invoiced as. Created for you when "
             "you give the service a price.")
    list_price = fields.Float(
        string="Price", digits="Product Price", compute="_compute_list_price",
        inverse="_inverse_list_price")

    @api.depends("product_id.lst_price")
    def _compute_list_price(self):
        for service in self:
            service.list_price = service.product_id.lst_price

    def _inverse_list_price(self):
        for service in self:
            if not service.product_id and service.list_price:
                service.product_id = self.env["product.product"].create({
                    "name": service.name, "type": "service", "sale_ok": True,
                    "purchase_ok": False, "list_price": service.list_price,
                })
            elif service.product_id:
                service.product_id.lst_price = service.list_price
