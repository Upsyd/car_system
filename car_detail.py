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

from openerp import tools
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from openerp import netsvc
SUPERUSER_ID = 1


class car_car(osv.osv):
    _name = 'car.car'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'code': fields.char('Code', size=64, required=True),
        'type_id': fields.many2one('car.type', 'Car Type', required=True),
        'year': fields.char('Year', size=64, help=''),
        'color_id': fields.many2one('car.color', 'Color', required=True),
        'chassis_no': fields.char('Chassis No', size=64, required=True),
        'case': fields.char('Case', size=64, help=''),
        'number_plates': fields.char('Number Plates', size=64, required=True),
        'number_app': fields.char('Num App', size=64, help=''),
        'source': fields.char('Source', size=64, help=''),
        'owner_id': fields.many2one('res.partner', 'Owner', required=True),
        'value': fields.float('Value', digits_compute=dp.get_precision('Account'), required=True),
        'transmission': fields.selection([('auto', 'Automatic'), ('normal', 'Normal')], 'Transmission', required=True),
        'image': fields.binary("Image",),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'car.car': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },),
        'state': fields.selection([('available', 'Available'), ('contract', 'Contract'),  ('entry', 'Entry')], 'State'),
    }
    _defaults = {
        'state': 'available',
    }

    _sql_constraints = [
        ('name_uniq', 'unique (code, name)', _("Car code and name must be unique !!!")),
    ]



class car_contract(osv.osv):
    _name = 'car.contract'
    _inherit = ['mail.thread']

    _columns = {
        'car_id': fields.many2one('car.car', 'Car'),
        'owner_id': fields.many2one('res.partner', 'Owner'),
        'archive_no': fields.char('No. Archive', size=64),
        'date_invoice': fields.date('Invoice Date',help="Keep empty to use the current date"),
        'partner_id': fields.many2one('res.partner','Buyer',required=True),
        'car_value': fields.float('Value', digits_compute=dp.get_precision('Account')),
        'commission': fields.float('Commission', digits_compute=dp.get_precision('Account')),
        'other_value': fields.float('Other Value', digits_compute=dp.get_precision('Account')),
        'acc_car_id': fields.many2one('account.account', 'Account Car', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'journal_id': fields.many2one('account.journal', 'Journal Sale', required=True),
        'purchase_id': fields.many2one('account.journal', 'Journal Purchase'),
        'account_id': fields.many2one('account.account', 'Account Buyer', required=True),
        'account_owner_id': fields.many2one('account.account', 'Account Owner'),
        'acc_comm_id': fields.many2one('account.account', 'Account Commission', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'acc_other_id': fields.many2one('account.account', 'Account Other Value', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'feedback': fields.text('Accounting feedback'),
        'payment_owner_ids': fields.many2many('account.move.line', 'rel_owner_account_move', 'owner_id', 'move_id', 'Payments Owner'),
        'payment_buyer_ids': fields.many2many('account.move.line', 'rel_buyer_account_move', 'buyer_id', 'move_id', 'Payments Buyer'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'state': fields.selection([('draft','Draft'),('open','Open'),('paid','Paid'),('cancel','Cancel')],'Status'),
        'validation_id': fields.many2one('res.users', 'Validation', ),
        'type_contract': fields.selection([('contract', 'Contract'), ('entry', 'Entry')], 'Type'),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account'),
        'user_id': fields.many2one('res.users', 'Salesperson'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Terms'),
        'customer_invoice_id': fields.many2one('account.invoice', 'Customer Invoice'),
        'supplier_invoice_id': fields.many2one('account.invoice', 'Supplier Invoice'),
        }

    _defaults  = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'car.contract', context=c),
    }


    def onchange_car(self, cr, uid, ids, car_id, context=None):
        if context is None:
            context = {}
        result = {}
        car = self.pool.get('car.car').browse(cr, uid, car_id, context=context)
        if car:
            result = {'value': {
                'owner_id': car.owner_id.id,
                'car_value': car.value,
            }}
        return result

    def onchange_owner_id(self, cr, uid, ids, owner_id, context=None):
        """Onchange owner id
        :param owner_id: owner_id
        :return:
        """
        if context is None:
            context = {}
        result = {}
        partner_id = self.pool.get('res.partner').browse(cr, uid, owner_id, context=context)
        if partner_id:
            result = {
                'account_owner_id': partner_id.property_account_payable.id
            }
        return {
            'value': result
        }

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state':'cancel'},context=context)

    def validate_car_contract(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        analytic_obj = self.pool.get('account.analytic.account')
        config_car_contract_obj = self.pool.get('setting.car.contract')
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        company_id = user.company_id.id
        currency_id = user.company_id.currency_id.id
        config_car_contract_ids = config_car_contract_obj.search(cr,uid,[('active_setting','=',True)],context=context)
        if not config_car_contract_ids:
            raise osv.except_osv(('Error!'),("Please Configure Car Contract in Car / Setting / Setting Car Contract"))
        if config_car_contract_ids:
            config_car_contract_id = config_car_contract_ids[0]
            config_car_contract_browse = config_car_contract_obj.browse(cr,uid,config_car_contract_id,context=context)
            for car in self.browse(cr,uid,ids,context=context):
                cust_inv_values = {
                    'name': 'car contract',
                    'origin': car.car_id.name,
                    'account_id': car.account_owner_id and car.account_owner_id.id or False,
                    'currency_id': currency_id,
                    'partner_id': car.owner_id and car.owner_id.id or False,
                    'type': 'out_invoice',
                    'journal_id': config_car_contract_browse.journal_id and config_car_contract_browse.journal_id.id or False,
                    'state': 'draft',
                    'date_invoice': car.date_invoice or False,
                }
                cust_inv_id = inv_obj.create(cr, uid, cust_inv_values, context)
                cust_inv_line_values = {
                    'invoice_id': cust_inv_id,
                    'quantity': 1,
                    'price_unit': car.car_value or 0.0,
                    'name': car.car_id.name,
                    'account_id': config_car_contract_browse.acc_car_id and config_car_contract_browse.acc_car_id.id or False,
                }
                inv_line_obj.create(cr, uid, cust_inv_line_values, context)

                supplier_in_vals = {
                    'name': 'car contract',
                    'origin': car.car_id.name,
                    'account_id': car.account_id and car.account_id.id or False,
                    'currency_id': currency_id,
                    'partner_id': car.partner_id and car.partner_id.id or False,
                    'journal_id': config_car_contract_browse.purchase_id and config_car_contract_browse.purchase_id.id or False,
                    'type': 'in_invoice',
                    'state': 'draft',
                    'date_invoice': car.date_invoice or False,
                }
                supplier_inv_id = inv_obj.create(cr, uid, supplier_in_vals, context)
                supp_inv_line_values = {
                    'invoice_id': supplier_inv_id,
                    'quantity': 1,
                    'price_unit': car.car_value or 0.0,
                    'name': car.car_id.name,
                    'account_id': config_car_contract_browse.acc_car_id and config_car_contract_browse.acc_car_id.id or False,
                }
                inv_line_obj.create(cr, uid, supp_inv_line_values, context)

                contract_vals = {
                    'name': car.car_id.name,
                    'code': car.car_id.code,
                    'partner_id': car.account_owner_id and car.account_owner_id.id or False,
                    'type': 'contract',
                    'user_id': car.user_id and car.user_id.id or False,
                    'manager_id': car.user_id and car.user_id.id or False,
                    'description': car.car_id.name,
                    'balance': car.car_value or 0.0,
                    'debit': car.car_value or 0.0,
                    'credit': car.car_value or 0.0,
                    'quantity': 1,
                    'quantity_max': 1,
                    'date_start': car.date_invoice or False,
                    'date': car.date_invoice or False,
                    'state': 'open',
                    'currency_id': currency_id,
                    'company_id': company_id,
                    'use_timesheets': True,
                    'use_phases': False,
                    'use_tasks': False,
                    'use_issues': False,
                         }

                analytic_obj.create(cr, uid, contract_vals, context=context)
                self.write(cr,uid,car.id,{'state':'open','customer_invoice_id':cust_inv_id,'supplier_invoice_id':supplier_inv_id},context=context)
            return True

class car_entry(osv.osv):
    _name = 'car.entry'
    _inherit = ['mail.thread']
    _columns = {
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account'),
        'user_id': fields.many2one('res.users', 'Salesperson'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Terms'),
        'car_value': fields.char('Car Value'),
        'date_invoice': fields.date('Invoice Date'),
        'car_id': fields.many2one('car.car', 'Car'),
        'name': fields.char('Description', size=64, readonly=True),
        'comment': fields.text('Comment'),
        'archive_no': fields.char('No. Archive', size=64),
        'partner_id': fields.many2one('res.partner', 'Buyer', required=True),
        'owner_id': fields.many2one('res.partner', 'Owner'),
        'car_value': fields.float('Value', digits_compute=dp.get_precision('Account')),
        'commission': fields.float('Commission', digits_compute=dp.get_precision('Account')),
        'other_value': fields.float('Other Value', digits_compute=dp.get_precision('Account')),
        'account_id': fields.many2one('account.account', 'Account Buyer', required=True),
        'account_owner_id': fields.many2one('account.account', 'Account Owner'),
        'acc_car_id': fields.many2one('account.account', 'Account Car', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'acc_comm_id': fields.many2one('account.account', 'Account Commission', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'acc_other_id': fields.many2one('account.account', 'Account Other Value', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'validation_id': fields.many2one('res.users', 'Validation', ),
        'type_contract': fields.selection([('contract', 'Contract'), ('entry', 'Entry')], 'Type'),
        'journal_id': fields.many2one('account.journal', 'Journal Sale', required=True),
        'purchase_id': fields.many2one('account.journal', 'Journal Purchase'),
        'invoice_owner_id': fields.many2one('account.invoice', 'Invoice Owner'),
        'payment_owner_ids': fields.many2many('account.move.line', 'rel_contract_account_move', 'contract_id', 'move_id', 'Payments Owner'),
        'feedback': fields.text('Accounting feedback'),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('paid','Paid'),
            ],'Status'),
        }

    _defaults  = {
        'state': 'draft',
    }
    def onchange_car_entry(self, cr, uid, ids, car_id, context=None):
        if context is None:
            context = {}
        result = {}
        car = self.pool.get('car.car').browse(cr, uid, car_id, context=context)
        if car:
            result = {'value': {
                'partner_id': car.owner_id.id,
            }}
        return result

class car_type(osv.osv):
    _name = 'car.type'
    _columns = {
        'name': fields.char('Type', size=64),
    }


class car_color(osv.osv):
    _name = 'car.color'
    _columns = {
        'name': fields.char('Color', size=64),
    }



class setting_car_contract(osv.osv):
    _name = 'setting.car.contract'
    _rec_name = 'sequence_id'

    _columns = {
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence',required=True),
        'journal_id': fields.many2one('account.journal', 'Journal Sale', required=True),
        'purchase_id': fields.many2one('account.journal', 'Journal Purchase'),
        'acc_car_id': fields.many2one('account.account', 'Account Car', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'acc_comm_id': fields.many2one('account.account', 'Account Commission', domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'acc_other_id': fields.many2one('account.account', 'Account Other Value',domain=[('type', 'not in', ['view', 'receivable', 'payable'])]),
        'type': fields.selection([('contract', 'Contract'), ('entry', 'Entry')], 'Type', help=''),
        'active_setting': fields.boolean('Active'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        if vals.get('active_setting', False):
            setting_ids = self.search(cr, uid, [('id', '!=', ids), ('type', '=', context.get('type', False))])
            for obj in self.browse(cr, uid, setting_ids):
                self.write(cr, uid,obj.id, {'active_setting': False})
        return super(setting_car_contract, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        result = super(setting_car_contract, self).create(cr, uid, vals, context=context)
        if context.get('type', False):
            self.write(cr, uid, [result], {'type': context['type']})
        if vals.get('active_setting', False):
            ids = self.search(cr, uid, [('id', '!=', result), ('type', '=', context['type'])])
            for obj in self.browse(cr, uid, ids):
                self.write(cr, uid,obj.id, {'active_setting': False})
        return result


class setting_car_entry(osv.osv):
    _name = 'setting.car.entry'
    _columns = {
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence',required=True),
        'journal_id': fields.many2one('account.journal', 'Journal',),
        'acc_process_id': fields.many2one('account.account', 'Account Process',),
        'active': fields.boolean('Active'),
    }

    def create_sequence(self, cr, uid, vals, context=None):
        """ Create new no_gap entry sequence for every new Joural
        """
        prefix = vals['code'].upper()
        seq = {
            'name': vals['name'],
            'implementation':'no_gap',
            'prefix': prefix + "/%(year)s/",
            'padding': 4,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, seq)

    def create(self, cr, uid, vals, context=None):
        if not 'sequence_id' in vals or not vals['sequence_id']:
            # if we have the right to create a journal, we should be able to
            # create it's sequence.
            vals.update({'sequence_id': self.create_sequence(cr, SUPERUSER_ID, vals, context)})
        return super(setting_car_entry, self).create(cr, uid, vals, context)


