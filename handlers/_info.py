import logzero

from utils import inject_quoted_sticker_id
import model


sticker_storage = model.get_storage()
logger = logzero.setup_logger(__name__)


@inject_quoted_sticker_id
def info(_, update, quoted_sticker_id):
    """Sends information about a known sticker"""

    try:
        try:
            sticker = sticker_storage.get_by_file_id(quoted_sticker_id)

        except KeyError:
            update.message.reply_to_message.reply_text("Sorry, I don't know this sticker yet.")

        else:
            tags = sticker_storage.get_tags(sticker.id)

            update.message.reply_to_message.reply_text(
                'Tags: {}\n'.format(', '.join(sorted(tags)))
              + 'Times used: {}'.format(sticker.times_used)
            )

    except Exception as e:
        logger.exception(e)
