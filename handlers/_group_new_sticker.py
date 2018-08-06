import logzero

import model


logger = logzero.setup_logger(__name__)
sticker_storage = model.get_storage()


def group_new_sticker(bot, update):
    sticker_storage.add(
        file_id=update.message.sticker.file_id,
        tags=[],
        owner_id=update.message.from_user.id
    )
