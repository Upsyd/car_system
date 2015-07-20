from openerp.report import report_sxw
from openerp.osv import osv
from datetime import time,date,datetime

class car_entry_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(car_entry_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                                  'time' : time,
                                  })
                                  
        
class car_entry_report_template_id(osv.AbstractModel):
    _name='report.car_system.car_entry_report_template_id'
    _inherit='report.abstract_report'
    _template='car_system.car_entry_report_template_id'
    _wrapped_report_class=car_entry_report
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
