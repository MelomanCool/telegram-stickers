from telegram import InlineQueryResultCachedSticker

import model
import logzero

logger = logzero.setup_logger(__name__)

sticker_storage = model.get_storage()

PAGE_SIZE = 50

# results that have more than PAGE_SIZE stickers, by query
large_results = {}


def inlinequery(_, update):
    inl_q = update.inline_query
    query = inl_q.query
    offset = int(inl_q.offset) if inl_q.offset else 0

    logger.info('Inline query: %s', query)

    if offset == 0 or query not in large_results:
        if query:
            stickers = sticker_storage.find(query)
        else:
            stickers = sticker_storage.get_most_popular()

        if len(stickers) > PAGE_SIZE:
            large_results[query] = stickers

    else:
        stickers = large_results[query]

    have_next_page = bool(len(stickers) - offset > PAGE_SIZE)
    next_offset=str(offset+PAGE_SIZE) if have_next_page else ''
    logger.info('Len: %s, offset: %d, has next page: %d, next offset: %s', len(stickers), offset, have_next_page, next_offset)

    results = [
        InlineQueryResultCachedSticker(sticker.id, sticker.file_id)
        for sticker in stickers[offset:offset+PAGE_SIZE]
    ]
    update.inline_query.answer(results, cache_time=0, next_offset=next_offset)


def chosen_inline_result(_, update):
    sticker_storage.inc_times_used(update.chosen_inline_result.result_id)
