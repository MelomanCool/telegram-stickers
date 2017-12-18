from telegram import InlineQueryResultCachedSticker

import model
import logzero

logger = logzero.setup_logger(__name__)

sticker_storage = model.get_storage()


def inlinequery(_, update):
    query = update.inline_query.query
    logger.info('Inline query: %s', query)

    if query:
        stickers = sticker_storage.find(query, max_count=20)
    else:
        stickers = sticker_storage.get_most_popular(max_count=20)

    results = [
        InlineQueryResultCachedSticker(sticker.id, sticker.file_id)
        for sticker in stickers
    ]
    update.inline_query.answer(results, cache_time=0)


def chosen_inline_result(_, update):
    sticker_storage.inc_times_used(update.chosen_inline_result.result_id)
