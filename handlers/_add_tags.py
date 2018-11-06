import model
from utils import inject_quoted_sticker_id, extract_tags


sticker_storage = model.get_storage()


@inject_quoted_sticker_id
def add_tags(_, update, args, quoted_sticker_id):
    message = update.message
    arg_str = ' '.join(args)

    tags = extract_tags(arg_str)
    if not tags:
        message.reply_text('Usage: /add_tags *tags*')
        return

    if not sticker_storage.has_sticker_with_file_id(quoted_sticker_id):
        sticker_storage.add(
            file_id=quoted_sticker_id,
            owner_id=message.from_user.id
        )

    old_tags = sticker_storage.get_by_file_id(file_id=quoted_sticker_id, tagged=True).tags

    try:
        sticker_storage.add_tags_by_file_id(
            file_id=quoted_sticker_id,
            tags=tags,
            owner_id=message.from_user.id
        )
    except ValueError:  # no new tags added
        pass

    current_tags = sticker_storage.get_by_file_id(file_id=quoted_sticker_id, tagged=True).tags

    added_tags = set(current_tags) - set(old_tags)
    if added_tags:
        result_message = ('Tags have been added!\n'
                          + 'New tags: ' + ', '.join(added_tags))
    else:
        result_message = 'No new tags have been added.'

    message.reply_text(
        result_message + '\n'
        + 'Full list of tags: ' + ', '.join(current_tags)
    )
