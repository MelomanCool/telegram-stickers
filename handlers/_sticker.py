import model


sticker_storage = model.get_storage()


def sticker_handler(_, update):
    """Handles known memes, returns their names"""

    sticker = sticker_storage.get_by_file_id(update.message.sticker.file_id)
    tags = sticker_storage.get_tags(sticker.id)

    update.message.reply_text(
        'Tags: {}\n'.format(', '.join(tags))
      + 'Times used: {}'.format(sticker.times_used)
    )
