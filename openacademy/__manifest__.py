{
    'name': "Open Academy",
    'summary': """Manage trainings""",
    'description': """
        Open Academy module for managing trainings:
            - training courses
            - training sessions
            - attendees registration
    """,
    'author': "Studer Nicola, brain-tec AG",
    'website': "https://github.com/BT-nstuder/functional-training",
    'category': 'Uncategorized',
    'version': '11.0.0.0.1',
    'depends': ['base',
                'sale',
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/openacademy.xml',
        'views/templates.xml',
        'views/partner.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}