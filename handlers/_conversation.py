from enum import Enum

import logzero
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler

import model
from custom_filters import is_in_database
from utils import extract_tags


logger = logzero.setup_logger(__name__)

States = Enum('States', 'TAGS')


sticker_storage = model.get_storage()


def cmd_cancel(_, update):
    update.message.reply_text('Current operation has been canceled.')

    return ConversationHandler.END


def sticker_handler(bot, update, user_data):
    message = update.message

    user_data['sticker_file_id'] = message.sticker.file_id
    message.reply_text('Okay, now send me a list of tags for the sticker'
                       ' (separate them with comma).')

    return States.TAGS


def tags_handler(_, update, user_data):
    message = update.message

    text = message.text.strip()
    tags = extract_tags(text)

    sticker_id = sticker_storage.add(
        file_id=user_data['sticker_file_id'],
        owner_id=message.from_user.id
    )
    sticker_storage.add_tags(
        sticker_id=sticker_id,
        tags=tags,
        owner_id=message.from_user.id
    )
    message.reply_text('Sticker has been added.')

    return ConversationHandler.END


conversation = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.private & Filters.sticker & (~is_in_database),
        sticker_handler,
        pass_user_data=True
    )],

    states={
        States.TAGS: [MessageHandler(
            Filters.text,
            tags_handler,
            pass_user_data=True
        )]
    },

    fallbacks=[CommandHandler('cancel', cmd_cancel)]
)
