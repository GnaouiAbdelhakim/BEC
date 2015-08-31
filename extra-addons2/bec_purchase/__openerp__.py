# -*- encoding: utf-8 -*-
##############################################################################
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
{
    "name": "BEC PURCHASES",
    "author": "KAZACUBE-ABDELLATIF BENZBIRIA",
    "website": "www.kazacube.com",
    "description": """
This module adds a new workflow states in purchase requisation module
    """,
    "version": "1.0",
    "category": "Purchases & Stock",
    "depends": [
        "purchase_requisition",
    ],
    "data": ["purchase_req_wkf.xml",
             "purchase_req_view.xml",
             "wizard/purchase_requisition_partner_view.xml",
             "sale_order_view.xml",
             "stock_view.xml",
             "security/groups.xml",

    ],
    "installable": True,
}
