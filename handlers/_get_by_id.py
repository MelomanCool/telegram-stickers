import model

sticker_storage = model.get_storage()


def get_by_id(_, update, groupdict):
    """Sends sticker by id"""

    try:
        sticker = sticker_storage.get(groupdict['id'])
    except KeyError:
        update.message.reply_text("I don't have sticker with that ID, sorry")
        return

    update.message.reply_sticker(sticker.file_id)
