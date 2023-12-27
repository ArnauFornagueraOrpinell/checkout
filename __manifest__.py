{
    'name': 'HR Attendance Auto Checkout',
    'version': '15.0.0.0',
    'category': 'Human Resources',
    'summary': 'Auto Checkout Attendance',
    'website': 'https://tkopen.com',
    'author': 'TKOpen',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'hr_attendance',
    ],
    'data': [
        'views/hr_employee.xml',
        'data/hr_attendance.xml',
        'views/res_company_view.xml',
        'views/resource_calendar_view.xml',
    ],
}
