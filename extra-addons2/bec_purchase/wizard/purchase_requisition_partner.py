# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_requisition_partner(osv.osv_memory):
    _inherit = "purchase.requisition.partner"
    _columns = {
        'partner_id': fields.many2many('res.partner', 'req_partner_rel','req_id','sup_id','Suppliers',required=False,domain=[('supplier', '=', True)]),
        'select_type':fields.selection([('product','Fiche produit'),('manual',"Selection manuelle")],required=True,string="Fournieseurs")
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(purchase_requisition_partner, self).view_init(cr, uid, fields_list, context=context)
        record_id = context and context.get('active_id', False) or False
        tender = self.pool.get('purchase.requisition').browse(cr, uid, record_id, context=context)
        if not tender.line_ids:
            raise osv.except_osv(_('Error!'), _('Define product(s) you want to include in the call for bids.'))
        return res

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        supplier_pricelist = supplier.property_product_pricelist_purchase
        return {
            'origin': requisition.name,
            'date_order': requisition.date_end or fields.datetime.now(),
            'site_id':requisition.site_id.id,
            'partner_id': supplier.id,
            'pricelist_id': supplier_pricelist.id,
            'currency_id': supplier_pricelist and supplier_pricelist.currency_id.id or requisition.company_id.currency_id.id,
            'location_id': requisition.procurement_id and requisition.procurement_id.location_id.id or requisition.picking_type_id.default_location_dest_id.id,
            'company_id': requisition.company_id.id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'requisition_id': requisition.id,
            'notes': requisition.description,
            'picking_type_id': requisition.picking_type_id.id
        }

    def _prepare_purchase_order_line(self, cr, uid, requisition, requisition_line, purchase_id, supplier, context=None):
        if context is None:
            context = {}
        po_line_obj = self.pool.get('purchase.order.line')
        product_uom = self.pool.get('product.uom')
        product = requisition_line.product_id
        default_uom_po_id = product.uom_po_id.id
        ctx = context.copy()
        ctx['tz'] = requisition.user_id.tz
        date_order = requisition.ordering_date and fields.date.date_to_datetime(self, cr, uid, requisition.ordering_date, context=ctx) or fields.datetime.now()
        qty = product_uom._compute_qty(cr, uid, requisition_line.product_uom_id.id, requisition_line.product_qty, default_uom_po_id)
        supplier_pricelist = supplier.property_product_pricelist_purchase and supplier.property_product_pricelist_purchase.id or False
        vals = po_line_obj.onchange_product_id(
            cr, uid, [], supplier_pricelist, product.id, qty, default_uom_po_id,
            supplier.id, date_order=date_order,
            fiscal_position_id=supplier.property_account_position.id,
            date_planned=requisition_line.schedule_date,
            name=False, price_unit=False, state='draft', context=context)['value']
        vals.update({
            'order_id': purchase_id,
            'product_id': product.id,
             'material_id':requisition_line.material_id,
            'account_analytic_id': requisition_line.account_analytic_id.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
        })
        return vals

    def create_order(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data =  self.browse(cr, uid, ids, context=context)[0]
        req_obj=self.pool.get('purchase.requisition')
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        if data.select_type =='manual' :
            for partner in data.partner_id :
                req_obj.make_purchase_order(cr, uid, active_ids,partner.id, context=context)
        else :
            requisition_id=req_obj.browse(cr,uid,active_ids)
            for line in requisition_id.line_ids :
                for seller in line.product_id.seller_ids :
                    purchase_id = purchase_order.create(cr, uid,self._prepare_purchase_order(cr,uid,requisition_id,seller.name))
                    purchase_order_line.create(cr, uid, self._prepare_purchase_order_line(cr, uid, requisition_id, line, purchase_id, seller.name, context=context), context=context)
        req_obj.write(cr,uid,active_ids,{'state':'done','req_output':'dp'})
        return {'type': 'ir.actions.act_window_close'}





purchase_requisition_partner()


