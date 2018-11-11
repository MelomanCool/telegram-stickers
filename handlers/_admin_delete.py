import logzero

import model
from utils import inject_quoted_sticker_id


sticker_storage = model.get_storage()
logger = logzero.setup_logger(__name__)


@inject_quoted_sticker_id
def admin_delete(_, update, quoted_sticker_id):
    sticker_storage.delete_by_file_id_without_check(quoted_sticker_id)
    update.message.reply_text('Sticker have been deleted.')
