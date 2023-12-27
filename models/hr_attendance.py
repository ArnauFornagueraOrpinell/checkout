# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from datetime import datetime
from datetime import timedelta
import pytz
import random

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    checkout_type = fields.Selection([('s', 'System Checkout'), ('m', 'Manual Checkout')], default='m',
                                     string='Checkout Type')
    present_days = fields.Integer('Present Days',compute='_compute_worked_hours', store = True)

    def chek_attendane_validity(self):
        for attendance in self:
            present_days = 0
            today = attendance.check_in.replace(hour=0, minute=0, second=0)
            previous_check_ins = self.search([('employee_id','=',attendance.employee_id.id),('check_in','<',attendance.check_in),('check_in','>',today)])
            if not previous_check_ins:
                present_days = 1
            self.env.cr.execute("update hr_attendance set present_days=%s where id=%s" %(present_days, attendance.id))
        return True


    @api.depends('check_out', 'check_in')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                worked_hours = delta.total_seconds() / 3600.0
            else:
                delta = datetime.now() - attendance.check_in
                worked_hours = delta.total_seconds() / 3600.0
            attendance.worked_hours = worked_hours

            ### check attendance validity
            today = attendance.check_in.replace(hour=0,minute=0,second=0)
            end = attendance.check_in.replace(hour=23, minute=59, second=59)
            attendances = self.search([('employee_id','=',attendance.employee_id.id),('check_in','>',today),('check_in','<',end)])
            attendances.chek_attendane_validity()
        return True

    #open_worked_hours = fields.Float(string='Worked hours', compute='_compute_open_worked_hours',)

    def autoclose_attendance(self):
        self.ensure_one()
        max_hours = self.employee_id.contract_id.resource_calendar_id.hours_per_day or \
                    self.employee_id.company_id.attendance_maximum_hours_per_day
        leave_time = self.check_in + timedelta(hours=max_hours)
        if leave_time <= datetime.now():
            vals = {'check_out': leave_time, 'checkout_type': 's'}
            self.write(vals)
        return True

    def autocheckout_lunch(self, checkout_time= False):
        self.ensure_one()
        if not checkout_time:
            checkout_time = datetime.now()
        vals = {'check_out': checkout_time, 'checkout_type': 's'}
        self.write(vals)
        return True


    def needs_autoclose(self):
        self.ensure_one()
        if self.employee_id.contract_id.resource_calendar_id.hours_per_day:
            max_hours = self.employee_id.contract_id.resource_calendar_id.hours_per_day
        else:
            max_hours = self.employee_id.company_id. \
                attendance_maximum_hours_per_day
        close = not self.employee_id.no_autoclose
        ## Taking 3 hours as margin in max_house to not
        ## auto-close considering that employee is staying longer
        return close and max_hours and self.worked_hours > (max_hours +3 )

    @api.model
    def check_for_incomplete_attendances(self, co_type='s'):
        stale_attendances = self.search([('check_out', '=', False)])
        ## Check Lunch Attendance

        for att in stale_attendances.filtered(lambda a: a.employee_id.lunch_checkout == True):
            work_calendar = att.employee_id.resource_calendar_id


            if work_calendar.lunch_start_time and work_calendar.lunch_end_time:

                local_tz = pytz.timezone(work_calendar.tz or 'GMT')
                current_time = datetime.now(local_tz)
                start_time = timedelta(hours=work_calendar.lunch_start_time)
                end_time = timedelta(hours=work_calendar.lunch_end_time)
                lunch_start_time = datetime.today().replace(hour=0, minute=0, second=0) + start_time
                lunch_end_time = datetime.today().replace(hour=0, minute=0, second=0) + end_time
                lunch_start_time = local_tz.localize(lunch_start_time, is_dst=None)
                lunch_end_time = local_tz.localize(lunch_end_time, is_dst=None)
                if lunch_start_time <= current_time < lunch_end_time:
                    ## Employee is in lunch hour
                    ## checking employee working hours are at least half an hour
                    ## so We don't checkout again
                    if (att.worked_hours > 0.2):
                        checkout_time = lunch_start_time + timedelta(minutes=random.randrange(-10, 10))
                        ## Convert back to UTC to store in Database
                        att.autocheckout_lunch(checkout_time.astimezone(pytz.UTC))

        ##auto close attendances
        for att in stale_attendances.filtered(lambda a: a.needs_autoclose()):
            att.autoclose_attendance()




