import logzero

import model
from model.exceptions import Unauthorized
from utils import inject_quoted_sticker_id


sticker_storage = model.get_storage()
logger = logzero.setup_logger(__name__)


@inject_quoted_sticker_id
def delete(_, update, quoted_sticker_id):
    message = update.message

    try:
        sticker_storage.delete_by_file_id(quoted_sticker_id, message.from_user.id)

    except Unauthorized:
        message.reply_text("Sorry, you can only delete the stickers you've added yourself.")

    except Exception as e:
        logger.exception(e)

    else:
        message.reply_text('Sticker have been deleted.')
