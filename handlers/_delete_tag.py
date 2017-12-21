import logzero

import model
from model.exceptions import Unauthorized
from utils import inject_quoted_sticker_id


sticker_storage = model.get_storage()
logger = logzero.setup_logger(__name__)


@inject_quoted_sticker_id
def delete_tag(_, update, args, quoted_sticker_id):
    message = update.message
    tag_name = ' '.join(args)

    if not tag_name:
        message.reply_text('Usage: /delete_tag *tag*')
        return

    try:
        sticker_storage.delete_tag_by_file_id(quoted_sticker_id, tag_name, message.from_user.id)

    except Unauthorized:
        message.reply_text("Sorry, you can only delete the tags you've added yourself.")

    except Exception as e:
        logger.exception(e)

    else:
        message.reply_text('Tag {} have been deleted.'.format(tag_name))
