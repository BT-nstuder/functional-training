from odoo import models, fields, api

class Course(models.Model):
    # 1. Private attributes
    _name = 'openacademy.course'

    # 2. Default methods

    # 3. Fields Declaration
    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    # 4. Compute and search fields, in the same order that fields declaration
    # @api.depends('value')

    # 5. Constraints and onchange methods

    # 6. CRUD Methods

    # 7. Action methods
    # def _value_pc(self):
    #     self.value2 = float(self.value) / 100

    # 8. Business methods
