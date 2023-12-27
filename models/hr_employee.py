from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    no_autoclose = fields.Boolean(string='Don\'t Auto Checkout Attendances')
    lunch_checkout = fields.Boolean('Lunch Auto Checkout?', help='It checks the lunch time from Working Hours Calendar')
