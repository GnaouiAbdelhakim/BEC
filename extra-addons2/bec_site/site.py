
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv,fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class site(osv.osv):

    _name="site"

    _columns = {
            'name':fields.char('Nom du Chantier',required=True),
            'type':fields.selection([('metre','Au metré'),('forfait','Au forfait')],string="type"),
            'number':fields.char('Num. Chantier',required=True),
            'project_chef_id':fields.many2one('res.users','Chef de Projet'),
            'site_chef_id':fields.many2one('res.users','Chef de Chantier'),
            'partner_id':fields.many2one('res.partner','Client',domain=[('customer','=',True)],required=True),
            'deposit_number':fields.float('Restitution d\'accompte'),
            'guaranty_number':fields.float('Rétention de garantie'),
            'assurance_number':fields.float('Assurance'),
            'state' : fields.selection([('draft','Brouillon'),('ouvert','Ouvert'),('cloture','Cloturé')], string="status"),
            # 'sale_ids':fields.one2many('sale.order', 'chantier_id', 'bordereaux de prix'),
            # 'invoice_client_ids':fields.one2many('account.invoice', 'chantier_id', 'Factures clients',domain=[('type','=','out_invoice')]),
            # 'purchase_ids':fields.one2many('purchase.order', 'chantier_id', 'Commandes fournisseurs',domain=[('state','=','approved')]),
            # 'invoice_fournsseur_ids':fields.one2many('account.invoice', 'chantier_id', 'Factures fournisseurs',domain=[('type','=','in_invoice')]),
            # 'attachement_ids':fields.one2many('stock.picking', 'chantier_id', 'Attachements',domain=[('picking_type_code','=','outgoing')]),
             'location_id':fields.many2one("stock.location",string="Emplacement de stock",domain=[('usage','=','internal')]),
            # 'internal_move_ids':fields.one2many('stock.picking', 'chantier_id', 'Transfers vers Chantier',domain=[('picking_type_code','=','internal')]),
            # 'analytic_lines_created':fields.boolean('Analytic lines created ?'),
                    }

    _defaults = {
                 'state':'draft',
                 'number':lambda obj, cr, uid, context: '/',
                 'analytic_lines_created': False,
                 }

