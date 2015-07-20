# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    "name" : "Car Management System",
    "version" : "1.0",
    "depends" : ['account_voucher', 'mail','account_analytic_analysis'],
    "author": "Browseinfo",
    "description": """
        Car Management System By Browseinfo
    """,
    "website" : "www.browseinfo.in",
    "data" :[
            'security/hidden_menu_security.xml',
            'security/ir.model.access.csv',
			'car_detail_view.xml',
			'views/car_report_view.xml',
			'views/car_entry_report_view.xml',
			'report/car_report_menu.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
