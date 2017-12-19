import model
from utils import inject_quoted_sticker_id, extract_tags


sticker_storage = model.get_storage()


@inject_quoted_sticker_id
def add_tags(_, update, args, quoted_sticker_id):
    message = update.message
    arg_str = ' '.join(args)

    tags = extract_tags(arg_str)

    try:
        sticker_storage.add_tags_by_file_id(
            file_id=quoted_sticker_id,
            tags=tags,
            owner_id=message.from_user.id
        )
    except ValueError:
        result_message = 'No new tags have been added.'
    else:
        result_message = 'Tags have been added!'

    sticker = sticker_storage.get_by_file_id(file_id=quoted_sticker_id, tagged=True)
    message.reply_text(
        '{result}\n'
        'Full list of tags: {tags}'
        .format(result=result_message, tags=', '.join(sticker.tags))
    )
