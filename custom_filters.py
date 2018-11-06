from functools import wraps

from telegram.ext import BaseFilter

import model


class IsInDatabase(BaseFilter):
    def __init__(self, storage):
        self.storage = storage

    def filter(self, message):
        return self.storage.has_sticker_with_file_id(message.sticker.file_id)


is_in_database = IsInDatabase(storage=model.get_storage())


def user_ids(user_ids, func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        if update.message.from_user.id in user_ids:
            return func(bot, update, *args, **kwargs)
    return wrapped
