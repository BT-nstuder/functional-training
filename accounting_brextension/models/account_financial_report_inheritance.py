import copy
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero
from odoo.tools.safe_eval import safe_eval
from odoo import fields, models, api, _
# from odoo.addons.account_reports.models.account_financial_report import FormulaLine


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
                    bid = 1
                    for column in columns:
                        vals = {'date_from': dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                'date_to': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT),
                                'string': column,
                                'budget_id': bid
                                }
                        res['comparison']['periods'].append(vals)
                        bid += 1
                else:
                    for column in columns:
                        vals = {'date': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT), 'string': column}
                        res['comparison']['periods'].append(vals)
                res['comparison']['string'] = 'Budget Comparison'
            else:
                res['comparison']['number_period'] = 0
                res['comparison']['periods'] = []
        return res


class FinancialReportExtensionCalculation(models.Model):
    _inherit = 'account.financial.html.report.line'

    @api.multi
    def get_lines(self, financial_report, currency_table, options, linesDicts):
        # res = super(FinancialReportExtensionCalculation, self).get_lines(financial_report, currency_table,
        #                                                                  options, linesDicts)
        # for line in res:
        #     print(line)
        #     break
        # return res
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.user.company_id.currency_id.rounding
        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0


            # Studer Nicola Extension
            if options['comparison'].get('filter', False) == 'budget_comparison':
                acc_ids = None # Entspricht der Zahl, wenn ein Konto gebraucht wurde
                budget_set_amounts = {} # Entspricht der bis jetzt in der Zeile gesetzten budget amount
                budget_origin_amounts = {} # Entspricht der theoretische Wert von dem Budget in dem vordefinierten Zeitrahmen

                for period in comparison_table:
                    date_from = period.get('date_from', False)
                    date_to = period.get('date_to', False) or period.get('date', False)
                    date_from, date_to, strict_range = line.with_context(date_from=date_from,
                                                                         date_to=date_to)._compute_date_range()

                    # Check if a budget is set
                    budget_id = period.get('budget_id', False)

                    if budget_id and acc_ids is not None:
                        if budget_id != 3:
                            r = line.with_context(date_from=date_from, date_to=date_to, strict_range=strict_range)._eval_formula_budget(
                                financial_report, debit_credit, currency_table, linesDicts[k], acc_ids, budget_id)
                            if budget_id == 2:
                                budget_set_amounts = r
                        else:
                            res_diff = {}
                            balance = 0
                            for key in acc_ids:
                                if str(key).isdigit():
                                    budget_set_amount = budget_set_amounts[key]['balance']
                                    budget_origin_amount = budget_origin_amounts[key]['balance']
                                    res_diff.update({key: {'balance': budget_set_amount + budget_origin_amount, 'amount_residual': 0.0, 'debit': 0.0,
                                                           'credit': 651.0}})
                                    balance += res_diff[key]['balance']
                            res_diff.update({'line': {'balance': balance}})
                            r = res_diff
                    else:
                        r = line.with_context(date_from=date_from, date_to=date_to, strict_range=strict_range)._eval_formula(
                            financial_report, debit_credit, currency_table, linesDicts[k])
                        budget_origin_amounts = r
                    if len(list(r.keys())) > 1:
                        acc_ids = list(r.keys())

                    debit_credit = False
                    res.append(r)
                    domain_ids.update(r)
                    k += 1
            else:
                for period in comparison_table:
                    date_from = period.get('date_from', False)
                    date_to = period.get('date_to', False) or period.get('date', False)
                    date_from, date_to, strict_range = line.with_context(date_from=date_from,
                                                                         date_to=date_to)._compute_date_range()
                    r = line.with_context(date_from=date_from, date_to=date_to,
                                          strict_range=strict_range)._eval_formula(financial_report, debit_credit,
                                                                                   currency_table, linesDicts[k])
                    debit_credit = False
                    res.append(r)
                    domain_ids.update(r)
                    k += 1


            res = line._put_columns_together(res, domain_ids)
            if line.hide_if_zero and all(
                    [float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue
            # Post-processing ; creating line dictionary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'level': line.level,
                'columns': [{'name': l} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
            }
            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    # print("domain_id: %s" % domain_id)
                    # print("res: %s" % res)
                    name = line._get_gb_name(domain_id)
                    vals = {
                        'id': domain_id,
                        'name': name and len(name) >= 45 and name[0:40] + '...' or name,
                        'level': 4,
                        'parent_id': line.id,
                        'columns': [{'name': l} for l in res[domain_id]],
                        'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                    }
                    # print("values: %s" % vals)
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                    lines.append(vals)
                if domain_ids:
                    lines.append({
                        'id': 'total_' + str(line.id),
                        'name': _('Total') + ' ' + line.name,
                        'class': 'o_account_reports_domain_total',
                        'parent_id': line.id,
                        'columns': copy.deepcopy(lines[0]['columns']),
                    })

            for vals in lines:
                if len(comparison_table) == 2:
                    vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])

                # Studer Nicola Extension
                # elif options['comparison'].get('filter', False) == 'budget_comparison' and options['date'].get('date_to', False):
                #     for i in range(3):
                #         vals['columns'].pop()
                #     vals['columns'].append({'name': '300', 'class': 'number'})
                #     vals['columns'].append({'name': '900', 'class': 'number'})
                #     num = float(vals['columns'][0]['name']) - float(vals['columns'][2]['name'])
                #     vals['columns'].append({'name': num, 'class': 'number'})
                # Studer Nicola Extension

                else:
                    vals['columns'] = [line._format(v) for v in vals['columns']]
                if not line.formulas:
                    vals['columns'] = [{'name': ''} for k in vals['columns']]
            if len(lines) == 1:
                new_lines = line.children_ids.get_lines(financial_report, currency_table, options, linesDicts)
                if new_lines and line.level > 0 and line.formulas:
                    divided_lines = self._divide_line(lines[0])
                    result = [divided_lines[0]] + new_lines + [divided_lines[1]]
                else:
                    result = []
                    if line.level > 0:
                        result += lines
                    result += new_lines
                    if line.level <= 0:
                        result += lines
            else:
                result = lines
            final_result_table += result
        return final_result_table

    def _eval_formula_budget(self, financial_report, debit_credit, currency_table, linesDict, acc_ids, budget_id):
        if acc_ids:
            res = {}
            balance = 0
            for key in acc_ids:
                if str(key).isdigit():
                    if budget_id == 1:
                        res.update({key: {'balance': 650.0, 'amount_residual': 0.0, 'debit': 0.0, 'credit': 651.0}})
                    elif budget_id == 2:
                        res.update({key: {'balance': 750.0, 'amount_residual': 0.0, 'debit': 0.0, 'credit': 751.0}})
                    else:
                        res.update({key: {'balance': 850.0, 'amount_residual': 0.0, 'debit': 0.0, 'credit': 851.0}})
                    balance += res[key]['balance']
            res.update({'line': {'balance': balance}})
            return res
        return {'line': {'balance': 0.00}}

