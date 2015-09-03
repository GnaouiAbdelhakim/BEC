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

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    _order="name desc"

    _columns = {

     'state': fields.selection([('draftt', 'Draft'), ('in_pro', 'Confirmed'),('in_progress2','Approbation Responsable'),
                                ('in_progress3','Approbation Département'), ('done', 'Terminé'),
                                   ('ddddddddddederer', 'Cancelled')],
                                  'Status', track_visibility='onchange', required=True,
                                  copy=False),""
     'site_id':fields.many2one("site",required=False,string="Chantier"),
     'department_id':fields.many2one("hr.department",required=False,string="Département"),
     'req_output':fields.selection([('ti','Transfert interne'),('dp','Demande de prix'),('ti_dp','Transfert et achat')],string="Nature du traitement"),
     'department_dest_id':fields.many2one("hr.department",required=False,string="Département destinatrice"),
     }

    def create(self,cr,uid,data, context=None):

        if data['department_id']==False and data['site_id']==False:
            raise osv.except_osv(_('Attention'),_(' il faut obligatoirement  choisir un département ou un chantier pour efféctuer cette opération (création) '))
        else:
            print "traitement 2"

        return super(purchase_requisition, self).create(cr, uid, data, context)

    def write(self, cr, user, ids, vals, context=None):

        return super(purchase_requisition, self).write(cr, user, ids, vals,context=context)

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        supplier_pricelist = supplier.property_product_pricelist_purchase
        return {
            'origin': requisition.name,
            'date_order': requisition.date_end or fields.datetime.now(),
            'partner_id': supplier.id,
            'site_id':requisition.site_id.id,
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

    def tender_in_progress2(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'in_progress2'}, context=context)

    def tender_in_progress3(self, cr, uid, ids, context=None):
         record=self.browse(cr,uid, ids)
         for line in record.line_ids :
             if line.product_qty >0:
                    if line.qty_available>=line.product_qty :
                        qty_to_purchase=0
                        qty_to_move=line.product_qty
                    else :
                        qty_to_purchase=line.product_qty-line.qty_available
                        qty_to_move=line.qty_available
                    line.write({'qty_to_purchase':qty_to_purchase,'qty_to_move':qty_to_move})
         return self.write(cr, uid, ids, {'state': 'in_progress3'}, context=context)

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
        qty = product_uom._compute_qty(cr, uid, requisition_line.product_uom_id.id, requisition_line.qty_to_purchase, default_uom_po_id)
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

    def make_purchase_order(self, cr, uid, ids, partner_id,line, context=None):
        """
        Create New RFQ for Supplier
        """
        context = dict(context or {})
        assert partner_id, 'Supplier should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            #if not requisition.multiple_rfq_per_supplier and supplier.id in filter(lambda x: x, [rfq.state != 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
             #   raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner %s, you must cancel this purchase order to create a new quotation.')%(rfq.state,supplier.name))
            context.update({'mail_create_nolog': True})
            purchase_id = purchase_order.create(cr, uid, self._prepare_purchase_order(cr, uid, requisition, supplier, context=context), context=context)
            purchase_order.message_post(cr, uid, [purchase_id], body=_("RFQ created"), context=context)
            res[requisition.id] = purchase_id
            if line.qty_to_purchase>0 :
                    purchase_order_line.create(cr, uid, self._prepare_purchase_order_line(cr, uid, requisition, line, purchase_id, supplier, context=context), context=context)
        return res

    def tender_open(self, cr, uid, ids, context=None):
        req_id=self.browse(cr,uid,ids)
        picking_obj = self.pool.get('stock.picking')
        req_obj=self.pool.get('purchase.requisition')
        move_obj = self.pool.get('stock.move')
        pick_name = self.pool.get('ir.sequence').get(cr,uid,'stock.picking.in')
        pick_type_id = self.pool.get('stock.picking.type').search(cr,uid,[('code','=','internal')])
        picking_type=self.pool.get('stock.picking.type').browse(cr,uid,pick_type_id)
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        sum_line_to_move=0
        sum_line_to_purchase=0
        location_id=False

        for line in req_id.line_ids :

            if line.qty_to_move>0 :
                sum_line_to_move=sum_line_to_move+1

            if line.qty_to_purchase >0 :
                sum_line_to_purchase=sum_line_to_purchase+1

        if sum_line_to_move >0 :
            record_pick = {
                        'name': pick_name,
                        'origin': req_id.name,
                        'site_id':req_id.site_id.id,
                        'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'picking_type_id': pick_type_id[0],
                        'picking_type_code': 'internal',
                       # 'partner_id': picking.partner_id.id,
                        #'note': picking.note,
                        }
            if req_id.department_id.location_dest_id:
                location_id=req_id.department_id.location_dest_id.id
            else:
                location_id=req_id.site_id.location_id.id
            picking_id = picking_obj.create(cr,uid,record_pick)
            for line in req_id.line_ids :
                if line.qty_to_move>0 :
                    record_move = {
                        'name': line.product_id.name,
                        'picking_id': picking_id,
                        'material_id':line.material_id,
                        'product_id': line.product_id.id,
                        #'account_analytic_id':move.move_id.account_analytic_id.id,
                        'product_uom_qty':line.qty_to_move,
                        'product_uom': line.product_uom_id.id,
                        'product_uos_qty': line.qty_to_move,
                       # 'product_uos': (move.move_id.product_uos and move.move_id.product_uos.id) or move.move_id.product_uom.id,
                      #  'partner_id': self.picking_id.partner_id.id,
                        'location_id': picking_type.default_location_src_id.id,
                        'location_dest_id': req_id.site_id.location_id.id ,
                        'state': 'draft',
                        'location_dest_id':location_id,
                    }
                    move_obj.create(cr,uid,record_move)
        if sum_line_to_purchase >0 :
            for line in req_id.line_ids :
                if line.qty_to_purchase >0 :
                    if line.select_type =='manual' :
                        for partner in line.partner_id :
                            res=req_obj.make_purchase_order(cr, uid, req_id.id,partner.id,line, context=context)
                    else :
                        for seller in line.product_id.seller_ids :
                                purchase_id = purchase_order.create(cr, uid,self._prepare_purchase_order(cr,uid,req_id,seller.name))
                                purchase_order_line.create(cr, uid, self._prepare_purchase_order_line(cr, uid, req_id, line, purchase_id, seller.name, context=context), context=context)

        if sum_line_to_purchase >0 and sum_line_to_move >0 :
            req_output='ti_dp'

        elif  sum_line_to_purchase ==0 and sum_line_to_move >0:
            req_output='ti'
        elif sum_line_to_purchase >0 and sum_line_to_move ==0:
             req_output='dp'
        else :
             raise osv.except_osv(_("Erreur de configuration"),_('Merci de vérifier les quantités que vous avez saisi'))



        return self.write(cr, uid, ids, {'state': 'done','req_output':req_output}, context=context)

    def _get_default_applicant(self, cr, uid, ids, context=None):
        if not uid:
            return False
        else :
            return uid

    _defaults={

        'user_id':_get_default_applicant,
    }

    def onchange_user(self, cr, uid, ids,user, context=None):
        if not user:
            return {}
        hr_employee_id=self.pool.get('hr.employee').search(cr,uid,[('user_id','=',user)])
        if hr_employee_id:
            hr_employee_id=self.pool.get('hr.employee').browse(cr,uid,hr_employee_id)
            return { 'value':{'department_id': hr_employee_id.department_id.id} }
        else:
            return { 'value':{'department_id': False} }


    _defaults={

        'user_id':_get_default_applicant,
        'schedule_date':datetime.now(),

    }

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = {}.fromkeys(ids, 0.0)
        product_obj = self.pool.get('product.product')
        if context is None:
            context = {}

        for id in ids:
            record= self.browse(cr,uid,id)
            stock = product_obj._product_available(cr, uid, [record.product_id.id], context=context)
            qty_available=stock.get(record.product_id.id)['qty_available']
            res[id] = qty_available
        return res

    def _check_qty(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        records = self.browse(cr, uid, ids, context=context)
        for rec in records:
            if rec.qty_to_purchase+rec.qty_to_move <0 :
                return False
        return True

    def onchange_product_qty(self,cr,uid,ids,product_qty,context=None):
        if not product_qty :
            return {}
        if product_qty >0:
                rec=self.browse(cr,uid,ids)
                if rec.qty_available>=product_qty :
                    qty_to_purchase=0
                    qty_to_move=product_qty
                else :
                    qty_to_purchase=product_qty-rec.qty_available
                    qty_to_move=rec.qty_available

                return { 'value': {'qty_to_purchase':qty_to_purchase,'qty_to_move':qty_to_move}}

    _columns={
        'motif':fields.char("Motif de la demande"),
        'material_id':fields.char("Matériel"),
        'qty_available': fields.function(_product_available,type='float', string='Quantité en stock',store=True),
        'qty_to_purchase':fields.float("Quantité à acheter",required=True),
        'qty_to_move':fields.float("Quantité à transferer",required=True) ,
        'partner_id': fields.many2many('res.partner', 'req_line_partner_rel','req_id','sup_id','Suppliers',required=False,domain=[('supplier', '=', True)]),
        'select_type':fields.selection([('product','Fiche produit'),('manual',"Selection manuelle")],required=False,string="Fournisseurs")
    }
    #_constraints=[
     #    (_check_qty, 'Erreur de Configuration !\nLa somme des quantités à acheter et à transferer doit être inférieure ou égale à la quantité demandée.', ['qty_to_move','qty_to_purchase']),
    #]

    _defaults={

        'select_type':'product',
    }


class pucrhase_order(osv.osv):
    _inherit="purchase.order"

    _columns={
        'site_id':fields.many2one("site",string="Chantier"),
    }

class pucrhase_order_line(osv.osv):
    _inherit="purchase.order.line"

    _columns={
        'material_id':fields.char("Matériel"),
    }

class hr_department(osv.osv):
    _inherit="hr.department"

    _columns={

        'location_dest_id':fields.many2one("stock.location",string="Emplacement de stock",),

    }
