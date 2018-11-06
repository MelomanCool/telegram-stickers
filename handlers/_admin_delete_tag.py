import logzero

import model
from utils import inject_quoted_sticker_id


sticker_storage = model.get_storage()
logger = logzero.setup_logger(__name__)


@inject_quoted_sticker_id
def admin_delete_tag(_, update, args, quoted_sticker_id):
    message = update.message
    tag_name = ' '.join(args)

    if not tag_name:
        message.reply_text('Usage: /admin_delete_tag *tag*')
        return

    sticker_storage.delete_tag_without_check(
        sticker_storage.get_by_file_id(quoted_sticker_id).id,
        tag_name
    )

    message.reply_text(
        ('Tag {} have been deleted.\n\n'
         + 'Current tags: {}')
        .format(tag_name, ', '.join(sticker_storage.get_by_file_id(quoted_sticker_id, tagged=True).tags))
    )
