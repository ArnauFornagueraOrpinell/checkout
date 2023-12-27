from odoo import models, fields, api

class ResouceCalendar(models.Model):
    _inherit = 'resource.calendar'

    lunch_start_time  = fields.Float('Lunch Start Time')
    lunch_end_time = fields.Float('Lunch End Time')