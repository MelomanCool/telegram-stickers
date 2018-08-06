from telegram.ext import BaseFilter

import model


class IsInDatabase(BaseFilter):
    def __init__(self, storage):
        self.storage = storage

    def filter(self, message):
        return self.storage.has_sticker_with_file_id(message.sticker.file_id)


is_in_database = IsInDatabase(storage=model.get_storage())
