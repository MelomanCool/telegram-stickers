import logging
import re
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Union

import config
from tag_search import find_stickers
from utils import filter_tag
from .exceptions import Unauthorized
from .sticker import Sticker
from .tagged_sticker import TaggedSticker


logger = logging.getLogger(__name__)

_storage = None


def get_storage():
    global _storage
    if not _storage:
        _storage = SqliteStickerStorage(config.DB_PATH)
    return _storage


MaybeTaggedSticker = Union[Sticker, TaggedSticker]


class StickerStorage(ABC):

    @abstractmethod
    def add(self, file_id, owner_id):
        pass

    @abstractmethod
    def add_tags(self, sticker_id, tags, owner_id):
        """Add tags, without overwriting existing ones"""
        pass

    @abstractmethod
    def add_tags_by_file_id(self, file_id, tags, owner_id):
        pass

    @abstractmethod
    def delete_by_file_id(self, file_id, from_user_id):
        """Delete a sticker by file_id"""
        pass

    @abstractmethod
    def delete_tag(self, sticker_id, tag_name, from_user_id):
        pass

    @abstractmethod
    def delete_tag_by_file_id(self, file_id, tag_name, from_user_id):
        pass

    @abstractmethod
    def get(self, sticker_id, tagged=False) -> MaybeTaggedSticker:
        """Get a sticker by it's id"""
        pass

    @abstractmethod
    def get_by_file_id(self, file_id, tagged=False) -> MaybeTaggedSticker:
        """Get a sticker by it's file_id"""
        pass

    @abstractmethod
    def get_for_owner(self, owner_id, max_count, tagged=False) -> List[MaybeTaggedSticker]:
        pass

    @abstractmethod
    def get_most_popular(self, tagged=False) -> List[MaybeTaggedSticker]:
        pass

    @abstractmethod
    def get_many(self, max_count, tagged=False) -> List[MaybeTaggedSticker]:
        pass

    @abstractmethod
    def get_all(self, tagged=False) -> List[MaybeTaggedSticker]:
        """Returns all stickers"""
        pass

    @abstractmethod
    def get_tags(self, sticker_id) -> List[str]:
        pass

    @abstractmethod
    def inc_times_used(self, sticker_id):
        pass

    @abstractmethod
    def replace_file_id(self, old_file_id, new_file_id, from_user_id):
        pass

    @abstractmethod
    def has_sticker_with_file_id(self, file_id) -> bool:
        pass

    def find(self, search_query: str) -> List[Sticker]:
        query_tags = re.split('\s+', search_query)
        query_tags = [filter_tag(tag) for tag in query_tags]
        return find_stickers(
            query_tags,
            [s for s in self.get_all(tagged=True)
             if len(s.tags) != 0]
        )

    def _convert_to_tagged(self, sticker):
        return TaggedSticker(
            tags=self.get_tags(sticker.id),
            **sticker._asdict()
        )


class SqliteStickerStorage(StickerStorage):

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS stickers ('
            ' id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
            ' file_id    TEXT NOT NULL UNIQUE,'
            ' owner_id   INTEGER NOT NULL,'
            ' times_used INTEGER NOT NULL DEFAULT 0'
            ')'
        )
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS tags ('
            ' id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
            ' sticker_id INTEGER NOT NULL,'
            ' name       TEXT NOT NULL,'
            ' owner_id   INTEGER NOT NULL,'
            ' FOREIGN KEY(sticker_id)'
            '  REFERENCES stickers(id)'
            '  ON DELETE CASCADE'
            ')'
        )
        self.connection.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS sticker_tag'
            ' ON tags (sticker_id, name)'
        )

    def add(self, file_id, owner_id):
        try:
            with self.connection:
                return self.connection.execute(
                    'INSERT INTO stickers (file_id, owner_id)'
                    ' VALUES (?, ?)',
                    (file_id, owner_id)
                ).lastrowid
        except sqlite3.IntegrityError:
            raise ValueError('Sticker with this file_id is already in storage')

    def add_tags(self, sticker_id, tags, owner_id):
        existing_tags = self.get_tags(sticker_id)
        new_tags = set(tags) - set(existing_tags)

        if not new_tags:
            return

        with self.connection:
            for tag in new_tags:
                self.connection.execute(
                    'INSERT INTO tags (sticker_id, name, owner_id)'
                    ' VALUES (?, ?, ?)',
                    (sticker_id, tag, owner_id)
                )

    def add_tags_by_file_id(self, file_id, tags, owner_id):
        sticker = self.get_by_file_id(file_id)
        self.add_tags(sticker.id, tags, owner_id)

    def delete_tag_without_check(self, sticker_id, tag_name):
        with self.connection:
            self.connection.execute(
                'DELETE FROM tags'
                ' WHERE sticker_id = ?'
                '  AND name = ?',
                (sticker_id, tag_name)
            )

    def delete_tag(self, sticker_id, tag_name, from_user_id):
        if from_user_id != self.get(sticker_id).owner_id:
            raise Unauthorized

        self.delete_tag_without_check(sticker_id, tag_name)

    def delete_tag_by_file_id(self, file_id, tag_name, from_user_id):
        sticker = self.get_by_file_id(file_id)
        self.delete_tag(sticker.id, tag_name, from_user_id)

    def delete_without_check(self, sticker_id):
        with self.connection:
            self.connection.execute(
                'DELETE FROM stickers '
                ' WHERE id = ?',
                (sticker_id,)
            )

    def delete_by_file_id(self, file_id, from_user_id):
        if from_user_id != self.get_by_file_id(file_id).owner_id:
            raise Unauthorized

        self.delete_without_check(self.get_by_file_id(file_id).id)

    def get(self, sticker_id, tagged=False) -> MaybeTaggedSticker:
        row = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE id = ?',
            (sticker_id,)
        ).fetchone()

        if row is None:
            raise KeyError

        return self.row_to_sticker(row, tagged=tagged)

    def get_by_file_id(self, file_id, tagged=False) -> MaybeTaggedSticker:
        row = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE file_id = ?',
            (file_id, )
        ).fetchone()

        if row is None:
            raise KeyError

        return self.row_to_sticker(row, tagged=tagged)

    def get_for_owner(self, owner_id, max_count, tagged=False) -> List[MaybeTaggedSticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE owner_id = :owner_id'
            ' LIMIT :max_count',
            {'owner_id': owner_id, 'max_count': max_count}
        ).fetchall()

        return [self.row_to_sticker(row, tagged=tagged)
                for row in rows]

    def get_most_popular(self, tagged=False) -> List[MaybeTaggedSticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' ORDER BY times_used DESC'
        ).fetchall()
        return [self.row_to_sticker(row, tagged=tagged)
                for row in rows]

    def get_many(self, max_count, tagged=False) -> List[MaybeTaggedSticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' LIMIT ?',
            (max_count,)
        ).fetchall()
        return [self.row_to_sticker(row, tagged=tagged)
                for row in rows]

    def get_all(self, tagged=False) -> List[MaybeTaggedSticker]:
        rows = self.connection.execute('SELECT * FROM stickers').fetchall()
        return [self.row_to_sticker(row, tagged=tagged)
                for row in rows]

    def get_tags(self, sticker_id) -> List[str]:
        rows = self.connection.execute(
            'SELECT name FROM tags'
            ' WHERE sticker_id = ?',
            (sticker_id,)
        )
        return [row['name'] for row in rows]

    def inc_times_used(self, sticker_id):
        with self.connection:
            self.connection.execute(
                'UPDATE stickers'
                ' SET times_used = times_used + 1'
                ' WHERE id = ?',
                (sticker_id,)
            )

    def replace_file_id(self, old_file_id, new_file_id, from_user_id):
        if from_user_id != self.get_by_file_id(old_file_id).owner_id:
            raise Unauthorized

        self.connection.execute(
            'UPDATE stickers'
            ' SET file_id = :new_file_id'
            ' WHERE file_id = :old_file_id',
            {'new_file_id': new_file_id, 'old_file_id': old_file_id}
        )

    def has_sticker_with_file_id(self, file_id) -> bool:
        row = self.connection.execute(
            'SELECT EXISTS('
            ' SELECT 1 FROM stickers'
            ' WHERE file_id = ?'
            ')',
            (file_id,)
        ).fetchone()
        exists = list(row)[0]  # returns 1 or 0
        return bool(exists)

    def row_to_sticker(self, row, tagged=False) -> MaybeTaggedSticker:
        if tagged:
            return TaggedSticker(tags=self.get_tags(row['id']),
                                 **row)
        else:
            return Sticker(**row)
