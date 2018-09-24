import copy
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero
from odoo.tools.safe_eval import safe_eval
from odoo import fields, models, api, _
from odoo.addons.account_reports.models.account_financial_report import FormulaLine

class AccountReportExtension(models.AbstractModel):
    _inherit = "account.financial.html.report"

    def apply_cmp_filter(self, options):
        res = super(AccountReportExtension, self).apply_cmp_filter(options)
        cmp_filter = options['comparison'].get('filter', False)
        if cmp_filter == 'budget_comparison':
            dt_to = options['date'].get('date_to', False)
            if dt_to:
                columns = ["Budget Theoretical Amount", "Budget Set Amount", "Budget Difference"]
                res['comparison']['number_period'] = len(columns)
                res['comparison']['periods'] = []
                dt_from = False
                if options['date'].get('date_from'):
                    dt_from = datetime.strptime(options['date'].get('date_from'), "%Y-%m-%d")
                dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
                if dt_from:
                    for column in columns:
                        vals = {'date_from': dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                'date_to': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                'string': column
                                }
                        res['comparison']['periods'].append(vals)
                else:
                    for column in columns:
                        vals = {'date': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT), 'string': column}
                        res['comparison']['periods'].append(vals)
                res['comparison']['string'] = 'Budget Comparison'
            else:
                res['comparison']['number_period'] = 0
                res['comparison']['periods'] = []
        return res
