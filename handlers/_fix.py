import model
from converter import convert_to_ogg
from model import Meme
from model.exceptions import Unauthorized
from utils import inject_quoted_voice_id, download_file

import logzero

logger = logzero.setup_logger(__name__)

meme_storage = model.get_storage()


@inject_quoted_voice_id
def fix(bot, update, quoted_voice_id):
    """Fixes meme's playback on Android"""

    message = update.message

    try:
        meme = meme_storage.get_by_file_id(quoted_voice_id)
    except KeyError:
        message.reply_text("Sorry, I don't know that meme.")
        return

    try:
        meme_storage.delete_by_file_id(meme.file_id, message.from_user.id)
    except Unauthorized:
        message.reply_text("Sorry, you can only fix the memes you added yourself.")
        return

    try:
        audio_file = download_file(bot, quoted_voice_id)
        fixed_file = convert_to_ogg(audio_file)
        response = message.reply_voice(fixed_file)
        fixed_file_id = response.voice.file_id
        meme_storage.add(Meme(
            name=meme.name,
            file_id=fixed_file_id,
            owner_id=meme.owner_id
        ))

        message.reply_text('The meme has been fixed')

    except Exception as e:
        logger.exception(e)
