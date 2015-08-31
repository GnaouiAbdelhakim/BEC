# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns={

     "dp_created":fields.boolean("Achat crée"),
     }

    def _prepare_purchase_order_line(self, cr, uid, order_id, order_line, purchase_id, supplier, context=None):
        if context is None:
            context = {}
        po_line_obj = self.pool.get('purchase.order.line')
        product_uom = self.pool.get('product.uom')
        product = order_line.product_id
        default_uom_po_id = product.uom_po_id.id
        ctx = context.copy()
        ctx['tz'] = order_id.user_id.tz
        date_order = order_id.date_order and fields.datetime.now()
        qty = product_uom._compute_qty(cr, uid, order_line.product_uom.id, order_line.product_uom_qty, default_uom_po_id)
        supplier_pricelist = supplier.property_product_pricelist_purchase and supplier.property_product_pricelist_purchase.id or False
        vals = po_line_obj.onchange_product_id(
            cr, uid, [], supplier_pricelist, product.id, qty, default_uom_po_id,
            supplier.id, date_order=date_order,
            fiscal_position_id=supplier.property_account_position.id,
            date_planned=False,
            name=False, price_unit=False, state='draft', context=context)['value']
        vals.update({
            'order_id': purchase_id,
            'product_id': product.id,
           # 'account_analytic_id': requisition_line.account_analytic_id.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
        })
        return vals

    def create_purchase_orders(self,cr,uid,ids,context=None):
        order_id=self.browse(cr,uid,ids)
        if order_id.dp_created :
            raise osv.except_osv(_("Attention"),_("Vous avez déjà crée des demandes de prix pour ce bon de commande"))
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        pick_type_id = self.pool.get('stock.picking.type').search(cr,uid,[('code','=','incoming')])
        picking_type=self.pool.get('stock.picking.type').browse(cr,uid,pick_type_id)
        for line in order_id.order_line :
            if line.supplier_id :
                 supplier_pricelist = line.supplier_id.property_product_pricelist_purchase
                 purchase_record={
                    'origin': order_id.name,
                    'date_order': fields.datetime.now(),
                    'partner_id': line.supplier_id.id,
                    'pricelist_id': supplier_pricelist.id,
                    'currency_id': supplier_pricelist and supplier_pricelist.currency_id.id or order_id.company_id.currency_id.id,
                    'location_id': picking_type.default_location_dest_id.id,
                    'company_id': order_id.company_id.id,
                    'fiscal_position': line.supplier_id.property_account_position and line.supplier_id.property_account_position.id or False,
                    'picking_type_id': picking_type.id,
                 }
                 purchase_id = purchase_order.create(cr, uid,purchase_record)
                 purchase_order_line.create(cr, uid,self._prepare_purchase_order_line(cr, uid, order_id, line, purchase_id, line.supplier_id, context=context), context=context)

        return self.write(cr,uid,ids,{'dp_created':True})

class sale_order_line(osv.osv):
    _inherit="sale.order.line"

    _columns={

        'supplier_id':fields.many2one('res.partner',string='Fournisseur',domain=[('supplier', '=', True)])
    }