from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import IO, AnyStr, Iterator
from urllib.parse import ParseResult, urljoin, urlparse

from podmaker.config import LocalConfig
from podmaker.storage import ObjectInfo, Storage
from podmaker.storage.core import EMPTY_FILE

logger = logging.getLogger(__name__)
lock = threading.Lock()


class Local(Storage):
    _db: sqlite3.Connection
    _file_buffering = 10 * 1024 * 1024  # 10MB

    def __init__(self, config: LocalConfig):
        self.public_endpoint = str(config.public_endpoint)
        self.base_dir = Path(config.base_dir)
        self.data_dir = self.base_dir / 'data'

    def start(self) -> None:
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.base_dir.chmod(0o750)
            logger.info(f'created base directory {self.base_dir} (mod: {self.base_dir.stat().st_mode:o})')
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.base_dir.chmod(0o750)
            logger.info(f'created data directory {self.data_dir} (mod: {self.base_dir.stat().st_mode:o})')
        with lock:
            self._db = sqlite3.connect(self.base_dir / 'db.sqlite3')
            self._db.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    key TEXT PRIMARY KEY,
                    type TEXT NOT NULL DEFAULT '',
                    size INTEGER NOT NULL CHECK (size >= 0)
                )
            ''')

    def stop(self) -> None:
        with lock:
            self._db.close()

    def put(self, data: IO[AnyStr], key: str, *, content_type: str = '') -> ParseResult:
        if key.startswith('/'):
            key = key[1:]
        path = self.data_dir / key
        size = 0
        with open(path, 'wb') as f:
            while True:
                chunk = data.read(self._file_buffering)
                if isinstance(chunk, str):
                    chunk_bytes = chunk.encode('utf-8')
                else:
                    chunk_bytes = chunk
                if not chunk_bytes:
                    break
                size += len(chunk_bytes)
                f.write(chunk_bytes)
        path.chmod(0o640)
        data.seek(0)
        info = self.check(key)
        with lock:
            if info is None:
                self._db.execute(
                    'INSERT INTO files (key, type, size) VALUES (?, ?, ?)',
                    (key, content_type, size),
                )
            else:
                self._db.execute(
                    'UPDATE files SET type = ?, size = ? WHERE key = ?',
                    (content_type, size, key),
                )
        url = urljoin(self.public_endpoint, key)
        return urlparse(url)

    def check(self, key: str) -> ObjectInfo | None:
        if key.startswith('/'):
            key = key[1:]
        with lock:
            cursor = self._db.execute(
                'SELECT type, size FROM files WHERE key = ?',
                (key,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        content_type, size = row
        url = urljoin(self.public_endpoint, key)
        return ObjectInfo(type=content_type, uri=urlparse(url), size=size)

    @contextmanager
    def get(self, key: str) -> Iterator[IO[bytes]]:
        if key.startswith('/'):
            key = key[1:]
        path = self.data_dir / key
        if not path.exists():
            yield EMPTY_FILE
        else:
            with open(path, 'rb') as f:
                yield f
