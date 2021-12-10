from ..exceptions import DBSyncException
from ..models import Tblticketpredefinedcats
from ..utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import PredefinedReplyCategory
except (ImportError, RuntimeError):
    PredefinedReplyCategory = None


def sync_predefined_reply_categories(fail_fast):
    exception_list = []
    categories_list = []
    for whmcs_category in Tblticketpredefinedcats.objects.all():
        try:
            fleio_category, created = PredefinedReplyCategory.objects.get_or_create(name=whmcs_category.name)
            if not created and fleio_category.name in categories_list:
                # we already processed a category that had this same name
                raise DBSyncException(
                    'Cannot import WHMCS ticket predefined reply category {} ({}) '
                    'because Fleio does not allow multiple categories with the same name'.format(
                        whmcs_category.name, whmcs_category.id
                    )
                )
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            categories_list.append(fleio_category.name)
            if created:
                WHMCS_LOGGER.info('Created predefined reply category {}'.format(fleio_category.name))
            else:
                WHMCS_LOGGER.info('Predefined reply category {} already exists'.format(fleio_category.name))
    return categories_list, exception_list

