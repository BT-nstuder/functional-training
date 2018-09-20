from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import fields, models, api, _

class AccountReportExtension(models.AbstractModel):
    _inherit = "account.report"

    def apply_cmp_filter(self, options):
        if not options.get('comparison'):
            return options
        options['comparison']['periods'] = []
        cmp_filter = options['comparison'].get('filter')
        print(cmp_filter)
        if not cmp_filter:
            return options
        if cmp_filter == 'no_comparison':
            if options['comparison'].get('date_from') != None:
                options['comparison']['date_from'] = ""
                options['comparison']['date_to'] = ""
            else:
                options['comparison']['date'] = ""
            options['comparison']['string'] = _('No comparison')
            return options
        elif cmp_filter == 'custom':
            date_from = options['comparison'].get('date_from')
            date_to = options['comparison'].get('date_to') or options['comparison'].get('date')
            display_value = self.format_date(date_to, date_from, options, dt_filter='comparison')
            if date_from:
                vals = {'date_from': date_from, 'date_to': date_to, 'string': display_value}
            else:
                vals = {'date': date_to, 'string': display_value}
            options['comparison']['periods'] = [vals]
            return options

        # My extension
        elif cmp_filter == 'budget_comparison':
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
            options['comparison']['periods'].append(vals)
            return options

        else:
            dt_from = False
            options_filter = options['date'].get('filter','')
            if options['date'].get('date_from'):
                dt_from = datetime.strptime(options['date'].get('date_from'), "%Y-%m-%d")
            dt_to = options['date'].get('date_to') or options['date'].get('date')
            dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
            display_value = False
            number_period = options['comparison'].get('number_period', 1) or 0
            for index in range(0, number_period):
                if cmp_filter == 'same_last_year' or options_filter in ('this_year', 'last_year'):
                    if dt_from:
                        dt_from = dt_from + relativedelta(years=-1)
                    dt_to = dt_to + relativedelta(years=-1)
                elif cmp_filter == 'previous_period':
                    if options_filter in ('this_month', 'last_month', 'today'):
                        dt_from = dt_from and (dt_from - timedelta(days=1)).replace(day=1) or dt_from
                        dt_to = dt_to.replace(day=1) - timedelta(days=1)
                    elif options_filter in ('this_quarter', 'last_quarter'):
                        dt_to = dt_to.replace(month=(dt_to.month + 10) % 12, day=1) - timedelta(days=1)
                        dt_from = dt_from and dt_from.replace(month=dt_to.month - 2, year=dt_to.year) or dt_from
                    elif options_filter == 'custom':
                        if not dt_from:
                            dt_to = dt_to.replace(day=1) - timedelta(days=1)
                        else:
                            previous_dt_to = dt_to
                            dt_to = dt_from - timedelta(days=1)
                            dt_from = dt_from - timedelta(days=(previous_dt_to - dt_from).days + 1)
                display_value = self.format_date(dt_to, dt_from, options)

                if dt_from:
                    vals = {'date_from': dt_from.strftime(DEFAULT_SERVER_DATE_FORMAT), 'date_to': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT), 'string': display_value}
                else:
                    vals = {'date': dt_to.strftime(DEFAULT_SERVER_DATE_FORMAT), 'string': display_value}

                options['comparison']['periods'].append(vals)
        if len(options['comparison'].get('periods', [])) > 0:
            for k, v in options['comparison']['periods'][0].items():
                if k in ('date', 'date_from', 'date_to', 'string'):
                    options['comparison'][k] = v
        return options
