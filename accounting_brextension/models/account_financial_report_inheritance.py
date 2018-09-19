from odoo import fields, models, api, _

class FinancialReportExtension(models.Model):
    _inherit = "account.financial.html.report"

    budget_involvement = fields.Boolean(default=False, help='display the budgets for a specific account')

    def get_columns_name(self, options):
        columns = [{'name': ''}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number'}, {'name': _('Credit'), 'class': 'number'}]
        dt_to = options['date'].get('date_to') or options['date'].get('date')
        columns += [
            {'name': self.format_date(dt_to, options['date'].get('date_from', False), options), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                columns += [{'name': period.get('string'), 'class': 'number'}]
            if options['comparison'].get('number_period') == 1:
                columns += [{'name': '%', 'class': 'number'}]
        if self.budget_involvement:
            columns += [{'name': 'Budget'}]
        return columns

    @api.multi
    def get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        currency_table = self._get_currency_table()
        linesDicts = [{} for _ in range(0, len((options.get('comparison') or {}).get('periods') or []) + 2)]
        res = line_obj.with_context(
            cash_basis=options.get('cash_basis') or self.cash_basis,
        ).get_lines(self, currency_table, options, linesDicts)
        return res