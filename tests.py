import pytest

from model.sticker_storage import SqliteStickerStorage


@pytest.fixture
def sticker_storage():
    return SqliteStickerStorage(':memory:')


def test_that_get_tags_returns_added_tags(sticker_storage):
    tags = ['lorem', 'ipsum', 'dolor', 'sit', 'amet']
    file_id = '1'

    sticker_storage.add(
        file_id=file_id,
        tags=tags,
        owner_id=1
    )
    sticker = sticker_storage.get_by_file_id(file_id, tagged=True)

    assert set(tags) == set(sticker.tags)
