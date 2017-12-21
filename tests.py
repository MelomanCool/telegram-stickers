import pytest

from model import TaggedSticker
from model.sticker_storage import SqliteStickerStorage


@pytest.fixture
def sticker_storage():
    return SqliteStickerStorage(':memory:')


@pytest.fixture
def prepared_storage(sticker_storage, prepared_sticker):
    sticker_storage.add(prepared_sticker.file_id, prepared_sticker.tags, prepared_sticker.owner_id)
    return sticker_storage


@pytest.fixture
def prepared_sticker():
    return TaggedSticker(
        id=None,
        file_id='1',
        owner_id=1,
        times_used=0,
        tags=['lorem', 'ipsum', 'dolor', 'sit', 'amet']
    )


def test_that_get_tags_returns_added_tags(prepared_storage: SqliteStickerStorage, prepared_sticker):
    sticker = prepared_storage.get_by_file_id(prepared_sticker.file_id, tagged=True)

    assert set(prepared_sticker.tags) == set(sticker.tags)


def test_that_delete_tag_deletes_tag(prepared_storage: SqliteStickerStorage, prepared_sticker):
    tag_to_delete = 'dolor'
    assert tag_to_delete in prepared_sticker.tags

    prepared_storage.delete_tag_by_file_id(
        prepared_sticker.file_id, tag_to_delete, prepared_sticker.owner_id)

    sticker = prepared_storage.get_by_file_id(prepared_sticker.file_id, tagged=True)
    assert tag_to_delete not in sticker.tags


def test_that_add_tags_adds_only_new_tags_to_sticker(
        prepared_storage: SqliteStickerStorage, prepared_sticker):

    already_added_tag = 'amet'
    assert already_added_tag in prepared_sticker.tags

    tags_to_add = ['pickle', 'rick', already_added_tag]

    prepared_storage.add_tags_by_file_id(prepared_sticker.file_id,
                                         tags_to_add, owner_id=2)

    sticker = prepared_storage.get_by_file_id(prepared_sticker.file_id, tagged=True)
    assert sticker.tags.count(already_added_tag) == 1


def test_that_one_sticker_can_only_be_added_once(sticker_storage: SqliteStickerStorage,
                                                 prepared_sticker):
    sticker_storage.add(prepared_sticker.file_id, prepared_sticker.tags, prepared_sticker.owner_id)
    with pytest.raises(ValueError):
        sticker_storage.add(prepared_sticker.file_id, prepared_sticker.tags, prepared_sticker.owner_id)

    assert len(sticker_storage.get_all()) == 1
