import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import List

import config
from .sticker import Sticker
from .exceptions import Unauthorized


logger = logging.getLogger(__name__)

_storage = None


def get_storage():
    global _storage
    if not _storage:
        _storage = SqliteStickerStorage(config.DB_PATH)
    return _storage


class StickerStorage(ABC):

    @abstractmethod
    def add(self, file_id, tags, owner_id):
        pass

    @abstractmethod
    def add_tags(self, sticker_id, tags):
        pass

    @abstractmethod
    def add_tags_by_file_id(self, file_id, tags):
        pass

    @abstractmethod
    def delete_by_file_id(self, file_id, from_user_id):
        """Delete a sticker by file_id"""
        pass

    @abstractmethod
    def get(self, sticker_id) -> Sticker:
        """Get a sticker by it's id"""
        pass

    @abstractmethod
    def get_by_file_id(self, file_id) -> Sticker:
        """Get a sticker by it's file_id"""
        pass

    @abstractmethod
    def get_for_owner(self, owner_id, max_count) -> List[Sticker]:
        pass

    @abstractmethod
    def get_most_popular(self, max_count) -> List[Sticker]:
        pass

    @abstractmethod
    def get_many(self, max_count) -> List[Sticker]:
        pass

    @abstractmethod
    def get_all(self):
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

    def find(self, search_query: str, max_count) -> List[Sticker]:
        raise NotImplementedError


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
            ' FOREIGN KEY(sticker_id)'
            '  REFERENCES stickers(id)'
            '  ON DELETE CASCADE'
            ')'
        )

    def add(self, file_id, tags, owner_id):

        with self.connection:
            sticker_id = self.connection.execute(
                'INSERT INTO stickers (file_id, owner_id)'
                ' VALUES (?, ?)',
                (file_id, owner_id)
            ).lastrowid

        self.add_tags(sticker_id, tags)

    def add_tags(self, sticker_id, tags):
        with self.connection:
            for tag in tags:
                self.connection.execute(
                    'INSERT INTO tags (sticker_id, name)'
                    ' VALUES (?, ?)',
                    (sticker_id, tag)
                )

    def add_tags_by_file_id(self, file_id, tags):
        sticker = self.get_by_file_id(file_id)
        self.add_tags(sticker.id, tags)

    def delete_by_file_id(self, file_id, from_user_id):
        if from_user_id != self.get_by_file_id(file_id).owner_id:
            raise Unauthorized

        with self.connection:
            self.connection.execute(
                'DELETE FROM stickers '
                ' WHERE file_id = ?',
                (file_id,)
            )

    def get(self, sticker_id) -> Sticker:
        row = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE id = ?',
            (sticker_id,)
        ).fetchone()

        if row is None:
            raise KeyError

        return Sticker(**row)

    def get_by_file_id(self, file_id) -> Sticker:
        row = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE file_id = ?',
            (file_id, )
        ).fetchone()

        if row is None:
            raise KeyError

        return Sticker(**row)

    def get_for_owner(self, owner_id, max_count) -> List[Sticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' WHERE owner_id = :owner_id'
            ' LIMIT :max_count',
            {'owner_id': owner_id, 'max_count': max_count}
        ).fetchall()

        return [Sticker(**r) for r in rows]

    def get_most_popular(self, max_count) -> List[Sticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' ORDER BY times_used DESC'
            ' LIMIT ?',
            (max_count,)
        ).fetchall()
        return [Sticker(**r) for r in rows]

    def get_many(self, max_count) -> List[Sticker]:
        rows = self.connection.execute(
            'SELECT * FROM stickers'
            ' LIMIT ?',
            (max_count,)
        ).fetchall()
        return [Sticker(**r) for r in rows]

    def get_all(self):
        rows = self.connection.execute('SELECT * FROM stickers').fetchall()
        return [Sticker(**r) for r in rows]

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
