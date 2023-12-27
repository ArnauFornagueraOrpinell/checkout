from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_maximum_hours_per_day = fields.Float(
        string='Attendance Maximum Hours Per Day',
        digits=(2, 2), default=11.0)
