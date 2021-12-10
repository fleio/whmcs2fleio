import markdown

from ..exceptions import DBSyncException
from ..models import Tblticketpredefinedcats
from ..models import Tblticketpredefinedreplies
from ..utils import WHMCS_LOGGER

try:
    from plugins.tickets.models import PredefinedReply
    from plugins.tickets.models import PredefinedReplyCategory
except (ImportError, RuntimeError):
    PredefinedReply = None
    PredefinedReplyCategory = None


def sync_predefined_replies(fail_fast):
    exception_list = []
    replies_list = []
    for whmcs_predefined_reply in Tblticketpredefinedreplies.objects.all():
        try:
            whmcs_category = Tblticketpredefinedcats.objects.get(id=whmcs_predefined_reply.catid)
            similar_category = Tblticketpredefinedcats.objects.filter(
                name=whmcs_category.name
            ).order_by('id').first()
            # take into consideration Fleio does not support multiple categories with the same name
            # and from multiple categories having the same name, we've only imported the first
            if similar_category and similar_category.id != whmcs_category.id:
                raise DBSyncException(
                    'Cannot sync predefined reply {} ({}) because related category ({}) was not synced into Fleio '
                    'because there are other categories with the same name and Fleio does not support this.'.format(
                        whmcs_predefined_reply.name, whmcs_predefined_reply.id, whmcs_predefined_reply.catid,
                    )
                )
            fleio_category = PredefinedReplyCategory.objects.get(name=whmcs_category.name)
            fleio_reply, created = PredefinedReply.objects.update_or_create(
                title=whmcs_predefined_reply.name,
                category=fleio_category,
                defaults=dict(
                    content=markdown.markdown(whmcs_predefined_reply.reply)
                )
            )
        except Exception as e:
            WHMCS_LOGGER.exception(e)
            exception_list.append(e)
            if fail_fast:
                break
        else:
            replies_list.append(fleio_reply)
            if created:
                WHMCS_LOGGER.info('Created predefined reply {}'.format(fleio_reply.title))
            else:
                WHMCS_LOGGER.info('Updated reply {}'.format(fleio_reply.title))
    return replies_list, exception_list
