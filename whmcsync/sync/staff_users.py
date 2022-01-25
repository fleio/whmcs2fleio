from django.contrib.auth import get_user_model
from django.db import transaction

from .utils import FieldToSync
from .utils import sync_fields
from ..models import Tbladmins
from ..utils import WHMCS_LOGGER
try:
    from plugins.tickets.models import StaffSignature
except (ImportError, RuntimeError):
    StaffSignature = None

AppUser = get_user_model()


class UserField(FieldToSync):
    record_name = 'User'


def sync_staff_users(fail_fast):
    exception_list = []
    user_list = []

    for whmcs_staff_user in Tbladmins.objects.all():
        created = False
        try:
            with transaction.atomic():
                fleio_user = AppUser.objects.filter(email=whmcs_staff_user.email, is_staff=True).first()
                if not fleio_user:
                    created = True
                    # create staff user as inactive so that his permissions can be reviewed by a super admin
                    fleio_user = AppUser(is_staff=True, is_active=False)

                user_fields_to_sync = []
                if created:
                    # don't change these fields if we only update the user
                    user_fields_to_sync.append(UserField(fleio_key='email', whmcs_key='email', fleio_max_length=254))
                    user_fields_to_sync.append(UserField(
                        fleio_key='username', whmcs_key='username', fleio_max_length=150)
                    )
                    user_fields_to_sync.append(UserField(fleio_key='password', whmcs_key='passwordhash'))
                user_fields_to_sync.append(
                    UserField(fleio_key='first_name', whmcs_key='firstname', fleio_max_length=150)
                )
                user_fields_to_sync.append(UserField(fleio_key='last_name', whmcs_key='lastname', fleio_max_length=150))
                # process user fields
                sync_fields(fleio_record=fleio_user, whmcs_record=whmcs_staff_user, fields_to_sync=user_fields_to_sync)
                fleio_user.save()

                user_list.append(fleio_user)
                if created:
                    WHMCS_LOGGER.info(
                        'Created (inactive) Fleio staff user {} ({}) from WHMCS ({})'.format(
                            fleio_user.username, fleio_user.id, whmcs_staff_user.id
                        )
                    )
                else:
                    WHMCS_LOGGER.info(
                        'Updated Fleio staff user {} ({}) from WHMCS ({})'.format(
                            fleio_user.username, fleio_user.id, whmcs_staff_user.id
                        )
                    )

                if StaffSignature and whmcs_staff_user.signature:
                    # set tickets global signature
                    StaffSignature.objects.update_or_create(
                        user=fleio_user,
                        department=None,
                        defaults=dict(
                            content=whmcs_staff_user.signature.replace('\n', '<br>')
                        )
                    )
                    WHMCS_LOGGER.info('Imported tickets global signature for staff user {}'.format(fleio_user.username))

        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break

    return user_list, exception_list

