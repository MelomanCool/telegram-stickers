import model


sticker_storage = model.get_storage()


def meme_handler(_, update):
    """Handles known memes, returns their names"""
    meme = sticker_storage.get_by_file_id(update.message.voice.file_id)
    update.message.reply_text('Name: "{}"'.format(meme.name))
