from whmcsync.whmcsync.models import Tblticketdepartments
from whmcsync.whmcsync.utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import Department
except (ImportError, RuntimeError):
    Department = None


def sync_ticket_departments(fail_fast):
    exception_list = []
    departments_list = []
    for whmcs_department in Tblticketdepartments.objects.all():
        try:
            fleio_department, created = Department.objects.get_or_create(
                name=whmcs_department.name,
                email=whmcs_department.email,
                defaults=dict(
                    notification_on_ticket_open_to_staff=False,
                    notification_on_staff_user_reply_to_staff=False,
                )
            )
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            departments_list.append(fleio_department)
            if created:
                WHMCS_LOGGER.info('Created department {}.'.format(fleio_department.name))
            else:
                WHMCS_LOGGER.info('Department {} already exists.'.format(fleio_department.name))
    return departments_list, exception_list
