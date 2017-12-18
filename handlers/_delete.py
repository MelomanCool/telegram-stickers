import model
from model.exceptions import Unauthorized
from utils import inject_quoted_sticker_id

sticker_storage = model.get_storage()


@inject_quoted_sticker_id
def delete(_, update, quoted_sticker_id):
    """Deletes a meme by voice file"""

    message = update.message

    try:
        meme_name = sticker_storage.get_by_file_id(quoted_sticker_id).name
    except KeyError:
        message.reply_text("I don't know that meme, sorry.")
        return

    try:
        sticker_storage.delete_by_file_id(quoted_sticker_id, message.from_user.id)
    except Unauthorized:
        message.reply_text("Sorry, you can only delete the memes you added yourself.")
        return

    message.reply_text('The meme "{name}" has been deleted.'.format(name=meme_name))
