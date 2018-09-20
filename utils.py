from functools import wraps

import re


def inject_quoted_sticker_id(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        quoted_message = update.message.reply_to_message
        if not quoted_message or not quoted_message.sticker:
            update.message.reply_text('You should reply to a sticker with this command.')
            return
        return func(bot, update, *args, quoted_sticker_id=quoted_message.sticker.file_id, **kwargs)
    return wrapped


def filter_tag(tag: str):
    # remove all characters except alphanumeric and "_"
    return (re.sub(r'\W+', '', tag)
            .lower())


def extract_tags(tag_str):
    tags = (tag for tag in re.split('[\s,]+', tag_str)
            if tag)
    tags = (filter_tag(tag) for tag in tags)
    return list(tags)
