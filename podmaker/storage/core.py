from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO
from typing import IO, AnyStr, Iterator
from urllib.parse import ParseResult


@dataclass
class ObjectInfo:
    # Fully-qualified URL of the object.
    uri: ParseResult
    # Size of the object in bytes.
    size: int
    # The standard MIME type of the object.
    type: str


EMPTY_FILE = BytesIO(b'')


class Storage(ABC):
    @abstractmethod
    def put(self, data: IO[AnyStr], key: str, *, content_type: str = '') -> ParseResult:
        """
        :return: data uri
        """
        raise NotImplementedError

    @abstractmethod
    def check(self, key: str) -> ObjectInfo | None:
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def get(self, key: str) -> Iterator[IO[bytes]]:
        """
        :return: file-like object, return `EMPTY_FILE` if not found
        """
        raise NotImplementedError

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
