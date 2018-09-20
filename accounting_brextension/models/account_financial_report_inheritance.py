import copy
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero
from odoo.tools.safe_eval import safe_eval
from odoo import fields, models, api, _
from odoo.addons.account_reports.models.account_financial_report import FormulaLine

class AccountReportExtension(models.AbstractModel):
    _inherit = "account.report"

    def apply_cmp_filter(self, options):
        res = super(AccountReportExtension, self).apply_cmp_filter(options)
        cmp_filter = options['comparison'].get('filter')
        if cmp_filter == 'budget_comparison':
            res['comparison']['number_period'] = 1
            res['comparison']['periods'] = []
            dt_from = False
            if options['date'].get('date_from'):
                dt_from = datetime.strptime(options['date'].get('date_from'), "%Y-%m-%d")
            dt_to = datetime.strptime(options['date'].get('date_to'), "%Y-%m-%d")
            if dt_from:
                vals = {'date_from': dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'date_to': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'string': 'Budgets'
                        }
            else:
                vals = {'date': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT), 'string': 'Budgets'}
            res['comparison']['periods'].append(vals)
            res['comparison']['string'] = 'Budget Comparison'
            return res
        return res

class FinancialReportExtension(models.Model):
    _inherit = "account.financial.html.report"

    def get_columns_name(self, options):
        res = super(FinancialReportExtension, self).get_columns_name(options)
        if options.get('comparison') and options['comparison'].get('periods'):
            if options['comparison'].get('filter') == 'budget_comparison':
                print("Mein Filter wurde gesetzt.")
                res = res[:len(res)-2]
                res += [{'name': 'Budget Theoretical Amount', 'class': 'number'},
                        {'name': 'Budget Set Amount', 'class': 'number'},
                        {'name': 'Budget Difference', 'class': 'number'}]
        return res

