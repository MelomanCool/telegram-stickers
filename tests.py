from model.sticker_storage import SqliteStickerStorage


def test_that_get_tag_returns_added_tags():
    tags = ['lorem', 'ipsum', 'dolor', 'sit', 'amet']
    file_id = '1'

    sticker_storage = SqliteStickerStorage(':memory:')
    sticker_storage.add(
        file_id=file_id,
        tags=tags,
        owner_id=1
    )
    sticker = sticker_storage.get_by_file_id(file_id)

    assert set(tags) == set(sticker_storage.get_tags(sticker.id))


if __name__ == '__main__':
    test_that_get_tag_returns_added_tags()
