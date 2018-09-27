{
    'name': "Budget Extension",
    'summary': """Add budget extensions for reports""",
    'description': """
        Budget Extension module for extending reports:
            - Create new extended budgets
            - Include budgets in the profit & loss
            - Dynamic calculations for time periods
    """,
    'author': "Studer Nicola, brain-tec AG",
    'website': "https://github.com/BT-nstuder/functional-training",
    'category': 'Advanced Reporting',
    'version': '11.0.0.0.1',
    'depends': ['account_reports',
                ],
    'data': [
        'views/account_financial_report_inheritance.xml',
    ],
    'license': 'LGPL-3',
}