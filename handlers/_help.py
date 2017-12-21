def help_(_, update):
    update.message.reply_text(
        'This bot can remember stickers to help you find them more easily.\n'
        '\n'
        'To add a sticker, just send it here. To manage sticker\'s tags,'
        ' reply to a sticker with commands /add_tags or /delete_tag.'
    )