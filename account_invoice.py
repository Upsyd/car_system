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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp



class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        self.write({'state': 'open'})
        if self:
            car_contract_id = self.env['car.contract'].search(['|',('customer_invoice_id', '=', self.id),('supplier_invoice_id', '=', self.id)])
            if car_contract_id:
                if car_contract_id.customer_invoice_id.state == 'open' and  car_contract_id.supplier_invoice_id.state == 'open':
                    car_contract_id.write({'state':'paid'})
        return True
