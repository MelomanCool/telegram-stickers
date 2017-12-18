from telegram import InlineQueryResultCachedVoice

import model
import logzero

logger = logzero.setup_logger(__name__)

sticker_storage = model.get_storage()


def inlinequery(_, update):
    query = update.inline_query.query
    logger.info('Inline query: %s', query)

    if query:
        memes = sticker_storage.find(query, max_count=20)
    else:
        memes = sticker_storage.get_most_popular(max_count=20)

    results = [
        InlineQueryResultCachedVoice(meme.id, meme.file_id, title=meme.name)
        for meme in memes
    ]
    update.inline_query.answer(results, cache_time=0)


def chosen_inline_result(_, update):
    sticker_storage.inc_times_used(update.chosen_inline_result.result_id)
