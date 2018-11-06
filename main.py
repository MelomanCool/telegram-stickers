import logging

import logzero
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, \
    ChosenInlineResultHandler, RegexHandler, Filters

import config
import handlers
from custom_filters import is_in_database

logger = logzero.setup_logger(__name__, level=logging.INFO)


def error_handler(_, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(config.TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler(['start', 'help'], handlers.help_))
    dp.add_handler(handlers.conversation)
    dp.add_handler(MessageHandler(Filters.private & Filters.sticker & is_in_database, handlers.sticker))
    dp.add_handler(CommandHandler(['info', 'stats'], handlers.info))
    dp.add_handler(CommandHandler('add_tags', handlers.add_tags, pass_args=True))
    dp.add_handler(CommandHandler('delete_tag', handlers.delete_tag, pass_args=True))
    dp.add_handler(CommandHandler('delete', handlers.delete))
    dp.add_handler(CommandHandler('my', handlers.my))
    dp.add_handler(CommandHandler('admin_delete_tag', handlers.admin_delete_tag, pass_args=True))
    dp.add_handler(RegexHandler('/(?P<id>\d+)', handlers.get_by_id, pass_groupdict=True))
    dp.add_handler(InlineQueryHandler(handlers.inlinequery))
    dp.add_handler(ChosenInlineResultHandler(handlers.chosen_inline_result))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
