import model

sticker_storage = model.get_storage()


def my(_, update):
    """Prints stickers added by user"""

    message = update.message
    user_id = update.message.from_user.id

    stickers = sticker_storage.get_for_owner(user_id, max_count=20, tagged=True)

    text = '\n\n'.join(
        'Tags: {tags}\n'
        'Times used: {sticker.times_used}\n'
        '/{sticker.id}'
        .format(
            sticker=sticker,
            tags=', '.join(sticker.tags)
        )
        for sticker in stickers
    )
    message.reply_text(text, parse_mode='HTML')
