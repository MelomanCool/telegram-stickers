import model
from model.exceptions import Unauthorized
from utils import inject_quoted_sticker_id

sticker_storage = model.get_storage()


@inject_quoted_sticker_id
def delete(_, update, quoted_sticker_id):
    """Deletes a sticker"""

    message = update.message

    try:
        sticker_storage.delete_by_file_id(quoted_sticker_id, message.from_user.id)

    except KeyError:
        message.reply_text("I don't know that sticker, sorry.")
        return

    except Unauthorized:
        message.reply_text("Sorry, you can only delete the stickers you added yourself.")
        return

    message.reply_text('The sticker has been deleted.')
